import logging
from hdbcli import dbapi
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import configparser

# Configuración del logging
fecha_hora = datetime.now().strftime("%d-%m-%Y %H_%M")
nombre_log = f"Trazabilidad_CMK_{fecha_hora}.log"
ruta_log_normal = r"C:\Users\Administrador\Desktop\Log Python\Trazabilidad_CMK"
ruta_log_error = r"C:\Users\Administrador\Desktop\Log Python\-Errores_Script"

# Asegurarse de que los directorios existen
os.makedirs(ruta_log_normal, exist_ok=True)
os.makedirs(ruta_log_error, exist_ok=True)

# Configurar el logging con la ruta completa del archivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(ruta_log_normal, nombre_log), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Función para manejar errores y mover el log
def manejar_error(error):
    """Maneja errores moviendo el archivo de log a la carpeta de errores"""
    try:
        # Cerrar los handlers actuales
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
        
        # Mover el archivo de log a la carpeta de errores
        archivo_original = os.path.join(ruta_log_normal, nombre_log)
        archivo_destino = os.path.join(ruta_log_error, nombre_log)
        
        if os.path.exists(archivo_original):
            os.rename(archivo_original, archivo_destino)
            
        # Configurar nuevo logging para errores
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(archivo_destino, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logging.error(f"Error en el proceso: {str(error)}")
    except Exception as e:
        print(f"Error al manejar el archivo de log: {str(e)}")

def conectar_hana():
    """Establece conexión con SAP HANA"""
    try:
        conn = dbapi.connect(
            address='159.138.116.7',
            port=30015,
            user='POWERBI',
            password='o2dzL3d94bj6'
        )
        return conn, conn.cursor()
    except Exception as e:
        logging.error(f"Error al conectar con SAP HANA: {str(e)}")
        raise

def conectar_mysql():
    """Establece conexión con MySQL"""
    try:
        conn = mysql.connector.connect(
            host='33.33.40.71',
            user='nmartinez',
            password='Nicolas1993',
            database='dw_holding',
            # Optimizaciones de conexión
            pool_size=20,
            pool_reset_session=True,
            consume_results=True,
            # Optimizaciones de rendimiento
            buffered=True,
            raise_on_warnings=True,
            # Timeouts más largos
            connection_timeout=180,
            # Optimizaciones adicionales
            autocommit=False,
            get_warnings=False
        )
        return conn, conn.cursor()
    except Exception as e:
        logging.error(f"Error al conectar con MySQL: {str(e)}")
        raise

def obtener_hora_actual():
    """Obtiene la hora actual y determina el tipo de proceso"""
    hora_actual = datetime.now().hour
    #hora_actual = 1  # Forzamos borrado completo temporalmente
    return hora_actual

def borrar_datos_mysql(cursor, conn, borrado_completo=False):
    """Borra los datos de la tabla en MySQL según el tipo de proceso"""
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        
        if borrado_completo:
            cursor.execute("TRUNCATE TABLE CMK_Trazabilidad_OV")
            filas_borradas = cursor.rowcount
            logging.info("[OK] Tabla CMK_Trazabilidad_OV limpiada completamente")
        else:
            # Borrar solo los últimos 14 días
            fecha_limite = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            cursor.execute("""
                DELETE FROM CMK_Trazabilidad_OV 
                WHERE Fecha_Creacion_OV >= %s
            """, (fecha_limite,))
            filas_borradas = cursor.rowcount
            logging.info(f"[OK] Borrados registros de los últimos 14 días desde {fecha_limite}")
        
        conn.commit()
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        return filas_borradas
    except Exception as e:
        conn.rollback()
        logging.error(f"Error al borrar datos en MySQL: {str(e)}")
        raise

def obtener_datos_trazabilidad(cursor, borrado_completo=False):
    """Obtiene datos de trazabilidad de SAP HANA y los convierte en DataFrame"""
    try:
        query = """
        SELECT 
            "Bodega_Factura" as "Bodega_Factura",
            "Bodega_GD" as "Bodega_GD",
            "BODEGA_OV" as "BODEGA_OV",
            "Calle_OV" as "Calle_OV",
            "CANCELED" as "CANCELED",
            "Cantidad_Abierta_Linea_OV" as "Cantidad_Abierta_Linea_OV",
            "Cantidad_Factura" as "Cantidad_Factura",
            "Cantidad_GD" as "Cantidad_GD",
            "Cantidad_OV" as "Cantidad_OV",
            "Codigo_Cliente_OV" as "Codigo_Cliente_OV",
            "Comuna_OV" as "Comuna_OV",
            "DelivrdQty_OV" as "DelivrdQty_OV",
            "Destino_GD" as "Destino_GD",
            "DiscPrcnt_OV" as "DiscPrcnt_OV",
            "Estado_Documento_OV" as "Estado_Documento_OV",
            "Estado_Linea_OV" as "Estado_Linea_OV",
            "Fecha_Creacion_OV" as "Fecha_Creacion_OV",
            "Fecha_Entrega_OV" as "Fecha_Entrega_OV",
            "Fecha_Factura" as "Fecha_Factura",
            "Fecha_GD" as "Fecha_GD",
            "Fecha_OV" as "Fecha_OV",
            "Folio_Factura" as "Folio_Factura",
            "Folio_GD" as "Folio_GD",
            "Hora_Factura" as "Hora_Factura",
            "Hora_GD" as "Hora_GD",
            "Hora_OV" as "Hora_OV",
            "IDWEB" as "IDWEB",
            "ItemCode" as "ItemCode",
            "Linea_Factura" as "Linea_Factura",
            "Linea_GD" as "Linea_GD",
            "Linea_OV" as "Linea_OV",
            "LinManClsd_OV" as "LinManClsd_OV",
            "Nombre_origen_venta_OV" as "Nombre_origen_venta_OV",
            "Nombre_Tipo_Operacion_OV" as "Nombre_Tipo_Operacion_OV",
            "Nombre_Usuario_OV" as "Nombre_Usuario_OV",
            "Numero_Interno_OV" as "Numero_Interno_OV",
            "Numero_Referencia_OV" as "Numero_Referencia_OV",
            "Numero_SAP_Factura" as "Numero_SAP_Factura",
            "Numero_SAP_GD" as "Numero_SAP_GD",
            "Numero_SAP_OV" as "Numero_SAP_OV",
            "Precio_Antes_Descuento_OV" as "Precio_Antes_Descuento_OV",
            "Precio_OV" as "Precio_OV",
            "REFACTURACION" as "REFACTURACION",
            "Ruta_OV" as "Ruta_OV",
            "Stock_Comprometido" as "Stock_Comprometido",
            "Tipo_Resolucion" as "Tipo_Resolucion",
            "Usuario_Factura" as "Usuario_Factura",
            "Usuario_GD" as "Usuario_GD"
        FROM "_SYS_BIC"."BI_CMK/CMK_TRAZABILIDAD_OV"
        """
        
        if not borrado_completo:
            fecha_limite = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            query += f" WHERE \"Fecha_Creacion_OV\" >= '{fecha_limite}' AND \"Fecha_Creacion_OV\" <= '{fecha_actual}'"
            logging.info(f"[INFO] Consultando registros desde {fecha_limite} hasta {fecha_actual}")
        
        # Usar solo el hint más básico y seguro
        query += " WITH HINT(NO_INLINE)"
        
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=column_names)
        
        # Optimizar la conversión de fechas usando vectorización y paralelismo
        date_columns = ['Fecha_Creacion_OV', 'Fecha_Entrega_OV', 'Fecha_Factura', 
                       'Fecha_GD', 'Fecha_OV']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=False).dt.date
        
        return df
    except Exception as e:
        logging.error(f"Error al obtener datos de trazabilidad de SAP HANA: {str(e)}")
        raise

def insertar_datos_mysql(cursor, conn, df):
    """Inserta datos en MySQL"""
    try:
        # Optimización de la preparación de datos usando operaciones vectorizadas
        df = df.replace({pd.NA: None, pd.NaT: None, 'nan': None, 'NaN': None, 'NULL': None})
        df = df.where(pd.notnull(df), None)
        
        # Convertir columnas numéricas a enteros de manera más eficiente
        columnas_enteras = [
            'Cantidad_Abierta_Linea_OV',
            'Cantidad_Factura',
            'Cantidad_GD',
            'Cantidad_OV',
            'DelivrdQty_OV',
            'Stock_Comprometido',
            'Precio_Antes_Descuento_OV',
            'Precio_OV',
            'Hora_Factura',
            'Hora_GD',
            'Hora_OV',
            'Folio_Factura',
            'Folio_GD',
            'Usuario_Factura',
            'Usuario_GD',
            'Numero_SAP_Factura',
            'Destino_GD'
        ]
        
        # Procesar columnas numéricas de manera vectorizada
        for col in columnas_enteras:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(0).astype('Int64')
                df[col] = df[col].where(pd.notnull(df[col]), None)
        
        # Manejar el campo DiscPrcnt_OV de manera vectorizada
        if 'DiscPrcnt_OV' in df.columns:
            df['DiscPrcnt_OV'] = pd.to_numeric(df['DiscPrcnt_OV'], errors='coerce')
            df['DiscPrcnt_OV'] = df['DiscPrcnt_OV'].clip(0, 100).round(2)
            df['DiscPrcnt_OV'] = df['DiscPrcnt_OV'].where(pd.notnull(df['DiscPrcnt_OV']), None)
        
        # Asegurar que no haya valores natype en el DataFrame
        df = df.replace({pd.NA: None, pd.NaT: None})
        
        # Depuración: imprimir el tipo de datos de la columna 'Folio_Factura'
        if 'Folio_Factura' in df.columns:
            logging.info(f"Tipo de datos de 'Folio_Factura' antes de la inserción: {df['Folio_Factura'].dtype}")
        
        # Preparar la consulta de inserción
        columnas = df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columnas))
        insert_query = f"""
        INSERT INTO CMK_Trazabilidad_OV (
            {', '.join(f'`{col}`' for col in columnas)}
        ) VALUES ({placeholders})
        """
        
        # Convertir DataFrame a lista de tuplas de manera más eficiente
        valores = [tuple(x) for x in df.values]
        total_registros = len(valores)
        
        # Aumentar el tamaño del lote para mejor rendimiento
        batch_size = 50000  # Aumentado de 20000 a 50000
        registros_insertados = 0
        filas_inyectadas = 0
        
        # Desactivar temporalmente las restricciones y optimizaciones
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.execute("SET UNIQUE_CHECKS=0")
        cursor.execute("SET AUTOCOMMIT=0")
        cursor.execute("SET SESSION bulk_insert_buffer_size=536870912")  # 512MB buffer
        
        for i in range(0, total_registros, batch_size):
            batch = valores[i:i + batch_size]
            cursor.executemany(insert_query, batch)
            conn.commit()
            registros_insertados += len(batch)
            filas_inyectadas += cursor.rowcount
            logging.info(f"[OK] Insertados registros {i+1} a {i + len(batch)} de {total_registros}")

        # Reactivar las restricciones y optimizaciones
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        cursor.execute("SET UNIQUE_CHECKS=1")
        cursor.execute("SET AUTOCOMMIT=1")
        
        return registros_insertados, filas_inyectadas

    except Exception as e:
        conn.rollback()
        logging.error(f"Error al insertar datos en MySQL: {str(e)}")
        raise

def main():
    """Función principal"""
    hana_conn = None
    hana_cursor = None
    mysql_conn = None
    mysql_cursor = None
    inicio_proceso = datetime.now()

    try:
        # Determinar tipo de proceso basado en la hora
        hora_actual = obtener_hora_actual()
        borrado_completo = 0 <= hora_actual < 3
        
        # Conexión a MySQL
        mysql_conn, mysql_cursor = conectar_mysql()
        logging.info("Conexión exitosa a MySQL")

        # Borrar datos según el tipo de proceso
        filas_borradas = borrar_datos_mysql(mysql_cursor, mysql_conn, borrado_completo)
        tipo_borrado = "COMPLETO" if borrado_completo else "PARCIAL (últimos 14 días)"

        # Conexión a SAP HANA
        hana_conn, hana_cursor = conectar_hana()
        logging.info("Conexión exitosa a SAP HANA")

        # Obtener datos de trazabilidad
        df = obtener_datos_trazabilidad(hana_cursor, borrado_completo)
        registros_obtenidos = len(df)

        # Insertar datos en MySQL
        registros_insertados, filas_inyectadas = insertar_datos_mysql(mysql_cursor, mysql_conn, df)
        
        # Calcular tiempo de ejecución
        tiempo_total = datetime.now() - inicio_proceso
        horas = tiempo_total.total_seconds() // 3600
        minutos = (tiempo_total.total_seconds() % 3600) // 60
        segundos = tiempo_total.total_seconds() % 60
        
        # Imprimir resumen final
        print("\n" + "="*60)
        print("RESUMEN DE OPERACIONES")
        print("="*60)
        print(f"Tipo de borrado: {tipo_borrado}")
        print(f"Inicio del proceso: {inicio_proceso.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Fin del proceso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duración: {int(horas)} horas, {int(minutos)} minutos, {int(segundos)} segundos")
        print(f"Filas borradas en MySQL: {filas_borradas:,}")
        print(f"Filas obtenidas de HANA: {registros_obtenidos:,}")
        print(f"Filas inyectadas en MySQL: {filas_inyectadas:,}")
        print("="*60 + "\n")
        
        # Agregar resumen detallado al log
        logging.info("\n" + "="*60)
        logging.info("RESUMEN DETALLADO DEL PROCESO")
        logging.info("="*60)
        logging.info(f"Tipo de borrado: {tipo_borrado}")
        logging.info(f"INICIO DEL PROCESO: {inicio_proceso.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info(f"FIN DEL PROCESO: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("-"*60)
        logging.info("ESTADÍSTICAS DE OPERACIÓN:")
        logging.info(f"Filas borradas en MySQL: {filas_borradas:,}")
        logging.info(f"Filas obtenidas de HANA: {registros_obtenidos:,}")
        logging.info(f"Filas inyectadas en MySQL: {filas_inyectadas:,}")
        logging.info("-"*60)
        logging.info("DURACIÓN DEL PROCESO:")
        logging.info(f"Total: {tiempo_total}")
        logging.info(f"Horas: {int(horas)}")
        logging.info(f"Minutos: {int(minutos)}")
        logging.info(f"Segundos: {int(segundos)}")
        logging.info("="*60 + "\n")
        
        logging.info("Proceso completado exitosamente")

    except Exception as e:
        manejar_error(e)
        raise
    finally:
        # Cerrar conexiones
        for conn, cursor, name in [(hana_conn, hana_cursor, "HANA"), 
                                 (mysql_conn, mysql_cursor, "MySQL")]:
            try:
                if cursor: cursor.close()
                if conn: conn.close()
                logging.info(f"Conexión con {name} cerrada correctamente")
            except Exception as e:
                logging.error(f"Error al cerrar conexión con {name}: {str(e)}")

if __name__ == "__main__":
    main()
