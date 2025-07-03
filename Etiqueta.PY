import requests
import pandas as pd
import mysql.connector
import time
import warnings
from datetime import datetime, timedelta
import os
from openpyxl import load_workbook, Workbook

# Desactivar advertencias SSL
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# URL de la API
url = "https://cmk.cloudseidor.com:8000/cmketiquetas/public/api/TrazavilidadFacturasPorFecha"

# Configuración de la conexión a MySQL
servidor = '33.33.34.196'
base_datos = 'dw_holding'
usuario = 'dmunoz'
contraseña = 'David2025'
puerto = 3306
tabla_destino = 'cmk_trazabilidad_etiqueta'

# Configuración del Excel de monitoreo
excel_path = r"C:\Users\David Yail\Clinical Market\Control Gestión - Documentos\Power BI\0-Varios\David\logs\Monitoreo_MYSQL.xlsx"
hoja_monitoreo = "monitoreo"

# Configuración de días a procesar
DIAS_DESPUES_3AM = 4  # Número de días a procesar después de las 3:00 AM
DIAS_ANTES_3AM = 15   # Número de días a procesar antes de las 3:00 AM

# Función para conectar a MySQL
def conectar_bd():
    """Establece conexión con la base de datos MySQL"""
    try:
        # Establecer conexión
        conexion = mysql.connector.connect(
            host=servidor,
            database=base_datos,
            user=usuario,
            password=contraseña,
            port=puerto
        )
        
        print("Conexión a MySQL establecida correctamente")
        return conexion
    
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Función para crear la tabla si no existe
def crear_tabla(conexion):
    try:
        cursor = conexion.cursor()
        
        # Definir la estructura de la tabla según el esquema proporcionado
        query = f"""
        CREATE TABLE IF NOT EXISTS {tabla_destino} (
            id BIGINT AUTO_INCREMENT,
            id_etiqueta VARCHAR(100),
            num_factura INT,
            nota_venta INT,
            fecha_nota_venta DATE,
            fecha_hora_impresion DATE,
            hora_impresion TIME,
            cant_bultos INT,
            fecha_ruta DATE,
            folio_ruta INT,
            hora_ruta TIME,
            fecha_acopio DATE,
            hora_acopio TIME,
            usuario_etiqueta VARCHAR(100),
            os_newtrans VARCHAR(50),
            PRIMARY KEY (id, fecha_hora_impresion)
        )
        """
        cursor.execute(query)
        conexion.commit()
        cursor.close()
        
        print(f"Tabla {tabla_destino} verificada/creada correctamente")
        return True
    except Exception as e:
        print(f"Error al crear la tabla: {str(e)}")
        return False

# Función para insertar datos en MySQL
def insertar_datos(conexion, df, fecha_consulta):
    try:
        tiempo_inicio_insercion = time.time()
        
        # Preparar los datos para la inserción
        cursor = conexion.cursor()
        
        # No truncamos la tabla para mantener el histórico
        # Solo eliminamos los registros del día que estamos procesando para evitar duplicados
        cursor.execute(f"DELETE FROM {tabla_destino} WHERE fecha_nota_venta = %s", (fecha_consulta,))
        conexion.commit()
        
        # Contador de registros insertados
        registros_insertados = 0
        
        # Insertar los datos fila por fila
        for index, row in df.iterrows():
            # Preparar los valores para la inserción
            query = f"""
            INSERT INTO {tabla_destino} (
                id_etiqueta, num_factura, nota_venta, fecha_nota_venta, 
                fecha_hora_impresion, hora_impresion, cant_bultos, 
                fecha_ruta, folio_ruta, hora_ruta, 
                fecha_acopio, hora_acopio, usuario_etiqueta, os_newtrans
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # Convertir NaN a None para MySQL
            values = [
                None if pd.isna(row.get('id_etiqueta')) else str(row.get('id_etiqueta')),
                None if pd.isna(row.get('num_factura')) else int(float(row.get('num_factura'))),
                None if pd.isna(row.get('nota_venta')) else int(float(row.get('nota_venta'))),
                None if pd.isna(row.get('fecha_nota_venta')) else row.get('fecha_nota_venta'),
                None if pd.isna(row.get('fecha_hora_impresion')) else row.get('fecha_hora_impresion'),
                None if pd.isna(row.get('hora_impresion')) else row.get('hora_impresion'),
                None if pd.isna(row.get('cant_bultos')) else int(float(row.get('cant_bultos'))),
                None if pd.isna(row.get('fecha_ruta')) else row.get('fecha_ruta'), 
                None if pd.isna(row.get('folio_ruta')) else int(float(row.get('folio_ruta'))),
                None if pd.isna(row.get('hora_ruta')) else row.get('hora_ruta'),
                None if pd.isna(row.get('fecha_acopio')) else row.get('fecha_acopio'),
                None if pd.isna(row.get('hora_acopio')) else row.get('hora_acopio'),
                None if pd.isna(row.get('usuario_etiqueta')) or row.get('usuario_etiqueta') == 'nan' else row.get('usuario_etiqueta'),
                None if pd.isna(row.get('os_newtrans')) or row.get('os_newtrans') == 'nan' else row.get('os_newtrans')
            ]
            
            cursor.execute(query, values)
            registros_insertados += 1
            
            # Commit cada 100 registros para evitar transacciones muy grandes
            if registros_insertados % 100 == 0:
                conexion.commit()
                print(f"Insertados {registros_insertados} registros...")
        
        # Commit final
        conexion.commit()
        cursor.close()
        
        tiempo_insercion = time.time() - tiempo_inicio_insercion
        print(f"Tiempo de inserción en MySQL: {tiempo_insercion:.2f} segundos")
        print(f"Total de registros insertados: {registros_insertados}")
        
        return registros_insertados
    except Exception as e:
        print(f"Error al insertar datos: {str(e)}")
        return 0

# Función para consultar la API y procesar los datos
def procesar_dia(fecha):
    fecha_str = fecha.strftime("%Y-%m-%d")
    
    try:
        # Parámetros de consulta para el día específico
        params = {
            "fechaInicio": fecha_str,
            "fechaTermino": fecha_str
        }
        
        print(f"\n{'='*50}")
        print(f"Procesando fecha: {fecha_str}")
        print(f"{'='*50}")
        
        # Medir tiempo de inicio
        tiempo_inicio = time.time()
        
        # Realizar la solicitud a la API sin verificar SSL
        print("Iniciando solicitud a la API...")
        response = requests.get(url, params=params, verify=False)
        
        # Calcular tiempo de respuesta
        tiempo_respuesta = time.time() - tiempo_inicio
        print(f"Tiempo de respuesta de la API: {tiempo_respuesta:.2f} segundos")
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Convertir la respuesta JSON a un diccionario de Python
            data = response.json()
            
            # Extraer los datos y convertirlos en un DataFrame
            if "data" in data and isinstance(data["data"], list):
                df = pd.DataFrame(data["data"])
                
                if df.empty:
                    print(f"No hay datos para la fecha {fecha_str}")
                    return 0
                
                # Convertir tipos de datos
                if not df.empty:
                    # Convertir columnas de fecha y hora
                    date_columns = ["fecha_nota_venta", "fecha_hora_impresion", "fecha_acopio","fecha_ruta"]
                    time_columns = ["hora_impresion", "hora_acopio", "hora_ruta"]
                    
                    for col in date_columns:
                        if col in df.columns:
                            # Usar dayfirst=True para formato dd-mm-yyyy
                            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True).dt.date
                    
                    for col in time_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], format="%H:%M:%S", errors='coerce').dt.time
                    
                    # Convertir columnas numéricas
                    numeric_columns = ["cant_bultos", "num_factura", "nota_venta", "folio_ruta"]
                    for col in numeric_columns:
                        if col in df.columns:
                            # Primero convertir a float y luego a int para manejar números decimales
                            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float).astype(int)
                    
                    # Asegurar que id_etiqueta sea string
                    if 'id_etiqueta' in df.columns:
                        df['id_etiqueta'] = df['id_etiqueta'].astype(str)
                    
                    # Asegurar que los campos de texto sean string y manejar valores nulos
                    text_columns = ["id_etiqueta", "num_factura", "nota_venta", "folio_ruta", "usuario_etiqueta", "os_newtrans"]
                    for col in text_columns:
                        if col in df.columns:
                            # Convertir NaN a None y luego a string
                            df[col] = df[col].fillna('')
                            df[col] = df[col].astype(str)
                            # Reemplazar 'nan' por cadena vacía
                            df[col] = df[col].replace('nan', '')
                
                print(f"\nTotal de registros obtenidos: {len(df)}")
                
                # Conectar a MySQL e insertar datos
                conexion = conectar_bd()
                registros_insertados = 0
                if conexion:
                    if crear_tabla(conexion):
                        registros_insertados = insertar_datos(conexion, df, fecha)
                    conexion.close()
                    print("Conexión a MySQL cerrada")
                
                # Tiempo total
                tiempo_total = time.time() - tiempo_inicio
                print(f"\nTiempo total de ejecución: {tiempo_total:.2f} segundos")
                
                return registros_insertados
            else:
                print("No se encontraron datos en la respuesta de la API")
                return 0
        else:
            print(f"Error en la solicitud: {response.status_code}")
            print(response.text)
            return 0
    except Exception as e:
        print(f"Error al procesar el día {fecha_str}: {str(e)}")
        return 0

def crear_excel_si_no_existe():
    """Crea el Excel con la estructura necesaria si no existe"""
    try:
        if not os.path.exists(excel_path):
            # Crear un nuevo workbook
            wb = Workbook()
            ws = wb.active
            ws.title = hoja_monitoreo
            
            # Agregar encabezados
            headers = ["Tabla", "Fecha Ejecución", "Registros", "Estado", "Duración"]
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            
            # Guardar el archivo
            wb.save(excel_path)
            print(f"Archivo Excel creado en: {excel_path}")
    except Exception as e:
        print(f"Error al crear el Excel: {str(e)}")

def registrar_ejecucion(cantidad_registros, estado, duracion):
    """Registra la ejecución en el Excel de monitoreo"""
    try:
        # Asegurar que el Excel existe
        crear_excel_si_no_existe()

        # Cargar el workbook existente
        wb = load_workbook(excel_path)
        
        # Verificar si la hoja existe
        if hoja_monitoreo not in wb.sheetnames:
            print(f"Error: La hoja '{hoja_monitoreo}' no existe en el archivo")
            return
            
        ws = wb[hoja_monitoreo]
        
        # Encontrar la última fila con datos
        ultima_fila = 1
        for row in range(1, ws.max_row + 1):
            if ws.cell(row=row, column=1).value is not None:
                ultima_fila = row + 1
        
        # Insertar los datos en la siguiente fila vacía
        ws.cell(row=ultima_fila, column=1, value="cmk_trazabilidad_etiqueta")
        ws.cell(row=ultima_fila, column=2, value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ws.cell(row=ultima_fila, column=3, value=cantidad_registros)
        ws.cell(row=ultima_fila, column=4, value=estado)
        ws.cell(row=ultima_fila, column=5, value=f"{duracion:.2f}")
        
        # Actualizar el rango de la tabla Tabla1
        if "Tabla1" in ws.tables:
            # Obtener la tabla existente
            tabla = ws.tables["Tabla1"]
            # Actualizar el rango de la tabla para incluir la nueva fila
            tabla.ref = f"A1:E{ultima_fila}"
        
        # Guardar el workbook
        try:
            wb.save(excel_path)
            print(f"Registro de ejecución guardado en el Excel (fila {ultima_fila})")
        except PermissionError:
            print(f"Error: No se puede guardar el archivo porque está abierto en otro programa")
        except Exception as e:
            print(f"Error al guardar el archivo: {str(e)}")
            
    except Exception as e:
        print(f"Error al registrar en el Excel: {str(e)}")

def main():
    try:
        # Iniciar el contador de tiempo
        tiempo_inicio = time.time()
        
        # Obtener la hora actual
        hora_actual = datetime.now().time()
        
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()
        
        # Definir el rango de fechas según la hora
        if hora_actual >= datetime.strptime('00:00', '%H:%M').time() and hora_actual <= datetime.strptime('03:00', '%H:%M').time():
            # Entre 00:00 y 03:00 - procesar últimos DIAS_ANTES_3AM días
            fecha_fin = fecha_actual
            fecha_inicio = fecha_actual - timedelta(days=DIAS_ANTES_3AM-1)  # -1 porque incluye el día actual
            print(f"Procesando últimos {DIAS_ANTES_3AM} días (entre 00:00 y 03:00)")
        else:
            # Después de 03:00 - procesar últimos DIAS_DESPUES_3AM días
            fecha_fin = fecha_actual
            fecha_inicio = fecha_actual - timedelta(days=DIAS_DESPUES_3AM-1)  # -1 porque incluye el día actual
            print(f"Procesando últimos {DIAS_DESPUES_3AM} días (después de 03:00)")
        
        # Crear la tabla si no existe
        conexion = conectar_bd()
        if conexion:
            crear_tabla(conexion)
            
            # Borrar registros del rango de fechas
            try:
                cursor = conexion.cursor()
                
                # Primero, verificar qué fechas existen en la tabla
                query_verificar = f"""
                SELECT DISTINCT fecha_hora_impresion 
                FROM {tabla_destino} 
                WHERE fecha_hora_impresion >= %s 
                AND fecha_hora_impresion <= %s
                ORDER BY fecha_hora_impresion
                """
                cursor.execute(query_verificar, (fecha_inicio, fecha_fin))
                fechas_existentes = cursor.fetchall()
                
                print("\nFechas encontradas en la tabla para el rango seleccionado:")
                for fecha in fechas_existentes:
                    print(f"- {fecha[0]}")
                
                # Realizar el borrado usando fecha_hora_impresion
                query_borrar = f"""
                DELETE FROM {tabla_destino} 
                WHERE fecha_hora_impresion >= %s 
                AND fecha_hora_impresion <= %s
                """
                cursor.execute(query_borrar, (fecha_inicio, fecha_fin))
                registros_borrados = cursor.rowcount
                conexion.commit()
                
                print(f"\nRango de fechas para borrado:")
                print(f"Fecha inicio: {fecha_inicio}")
                print(f"Fecha fin: {fecha_fin}")
                print(f"Total de registros borrados: {registros_borrados}")
                
                cursor.close()
            except Exception as e:
                print(f"Error al borrar registros: {str(e)}")
                duracion = time.time() - tiempo_inicio
                registrar_ejecucion(0, "NO OK", duracion)
                return
            
            conexion.close()
        
        # Contador total de registros
        total_registros = 0
        
        # Procesar día por día
        fecha_actual = fecha_inicio
        while fecha_actual <= fecha_fin:
            registros_dia = procesar_dia(fecha_actual)
            total_registros += registros_dia
            
            # Esperar un poco entre solicitudes para no sobrecargar la API
            if fecha_actual < fecha_fin:
                print(f"Esperando 2 segundos antes de la siguiente solicitud...")
                time.sleep(2)
            
            # Avanzar al siguiente día
            fecha_actual += timedelta(days=1)
        
        # Calcular duración total
        duracion = time.time() - tiempo_inicio
        
        print(f"\n{'='*50}")
        print(f"Proceso completado. Total de registros insertados: {total_registros}")
        print(f"Tiempo total de ejecución: {duracion:.2f} segundos")
        print(f"{'='*50}")
        
        # Registrar ejecución exitosa
        registrar_ejecucion(total_registros, "OK", duracion)
        
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        # Registrar ejecución fallida
        duracion = time.time() - tiempo_inicio
        registrar_ejecucion(0, "NO OK", duracion)

if __name__ == "__main__":
    main()
