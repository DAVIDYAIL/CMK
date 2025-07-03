import mysql.connector
import pandas as pd

def conectar_bd():
    """Establece conexión con la base de datos MySQL"""
    try:
        # Configura los parámetros de conexión
        servidor = '33.33.34.196'  # Reemplazar con tu servidor
        base_datos = 'dw_holding'  # Reemplazar con tu base de datos
        usuario = 'dmunoz'  # Reemplazar con tu usuario
        contraseña = 'David2025'  # Reemplazar con tu contraseña
        puerto = 3306  # Puerto predeterminado de MySQL
        
        # Establecer conexión
        conexion = mysql.connector.connect(
            host=servidor,
            database=base_datos,
            user=usuario,
            password=contraseña,
            port=puerto
        )
        
        print("Conexión establecida correctamente")
        return conexion
    
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def consultar_datos(conexion, tabla, limite=10):
    """Consulta datos de una tabla específica"""
    try:
        # Crear cursor
        cursor = conexion.cursor(dictionary=True)
        
        # Ejecutar consulta
        consulta = f"SELECT * FROM {tabla} LIMIT {limite}"
        cursor.execute(consulta)
        
        # Obtener filas
        filas = cursor.fetchall()
        
        # Crear DataFrame para mejor visualización
        df = pd.DataFrame(filas)
        
        # Cerrar cursor
        cursor.close()
        
        return df
    
    except Exception as e:
        print(f"Error al consultar datos: {e}")
        return None

def main():
    # Nombre de la tabla a consultar
    nombre_tabla = "cmk_trazabilidad_etiqueta"
    
    # Establecer conexión
    conexion = conectar_bd()
    
    if conexion:
        # Consultar datos
        datos = consultar_datos(conexion, nombre_tabla)
        
        if datos is not None:
            print(f"\nMuestra de datos de la tabla '{nombre_tabla}':")
            print(datos)
        
        # Cerrar conexión
        conexion.close()
        print("Conexión cerrada")

if __name__ == "__main__":
    main()
