from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
from selenium.webdriver.support.select import Select

def crear_carpetas_año(año):
    base_path = r"G:\Mi unidad\Tablas Power BI\GESMED PBI\GESMED-PBI\BASE MK"
    carpeta_año = os.path.join(base_path, f"Movimientos_{año}")
    if not os.path.exists(carpeta_año):
        os.makedirs(carpeta_año)
    return carpeta_año

def obtener_datos_por_periodo(driver, wait, fecha_desde, fecha_hasta, carpeta_destino):
    try:
        print(f"Obteniendo datos desde {fecha_desde} hasta {fecha_hasta}")
        
        # Verificar que estamos en el iframe correcto
        try:
            driver.switch_to.default_content()
            iframe = wait.until(EC.presence_of_element_located((By.ID, "ifrmMostrador")))
            driver.switch_to.frame(iframe)
            time.sleep(2)
        except Exception as e:
            print(f"Error al cambiar al iframe: {str(e)}")
            return None
        
        # Establecer fechas
        try:
            print("Configurando fechas...")
            desde_input = wait.until(EC.presence_of_element_located((By.ID, "Desde")))
            hasta_input = wait.until(EC.presence_of_element_located((By.ID, "Hasta")))
            
            driver.execute_script("arguments[0].value = arguments[1];", desde_input, fecha_desde)
            driver.execute_script("arguments[0].value = arguments[1];", hasta_input, fecha_hasta)
            time.sleep(2)
        except Exception as e:
            print(f"Error al configurar fechas: {str(e)}")
            return None
        
        # Hacer clic en exportar y esperar la descarga
        try:
            print("Haciendo clic en exportar...")
            driver.execute_script("TraerInforme()")
            
            # Esperar a que aparezca el archivo en la carpeta de descargas
            download_path = r"G:\Mi unidad\Tablas Power BI\GESMED PBI\GESMED-PBI\BASE MK"
            tiempo_espera = 0
            archivo_encontrado = False
            
            while tiempo_espera < 30 and not archivo_encontrado:  # Máximo 30 segundos de espera
                archivos = [f for f in os.listdir(download_path) if f.endswith('.xls') or f.endswith('.xlsx')]
                if archivos:
                    archivo_encontrado = True
                    print("Archivo descargado detectado")
                else:
                    time.sleep(1)
                    tiempo_espera += 1
            
            if not archivo_encontrado:
                print("Tiempo de espera agotado - No se detectó la descarga")
                return None
            
            # Dar tiempo adicional para que se complete la descarga
            time.sleep(5)
            
        except Exception as e:
            print(f"Error al hacer clic en exportar: {str(e)}")
            return None
        
        # Procesar el archivo descargado
        try:
            print("Procesando archivo descargado...")
            archivos = sorted(
                [f for f in os.listdir(download_path) if f.endswith('.xls') or f.endswith('.xlsx')],
                key=lambda x: os.path.getmtime(os.path.join(download_path, x))
            )
            
            if archivos:
                archivo_reciente = os.path.join(download_path, archivos[-1])
                # Extraer mes y año de la fecha
                mes = fecha_desde.split('-')[1]
                año = fecha_desde.split('-')[2]
                nuevo_nombre = f"Movimientos_{mes}-{año}.xlsx"
                nuevo_path = os.path.join(carpeta_destino, nuevo_nombre)
                
                # Asegurarse de que el archivo esté completamente descargado
                tiempo_espera = 0
                while tiempo_espera < 30:
                    try:
                        # Intentar abrir el archivo para verificar que no está bloqueado
                        with open(archivo_reciente, 'rb') as f:
                            break
                    except:
                        time.sleep(1)
                        tiempo_espera += 1
                
                # Si existe un archivo con el mismo nombre, lo eliminamos
                if os.path.exists(nuevo_path):
                    os.remove(nuevo_path)
                
                # Mover y renombrar el archivo
                os.rename(archivo_reciente, nuevo_path)
                print(f"Archivo guardado como: {nuevo_nombre}")
                
                # Leer el archivo para el DataFrame
                try:
                    print("Intentando leer el archivo Excel...")
                    # Intentar primero con engine='openpyxl'
                    try:
                        df = pd.read_excel(nuevo_path, engine='openpyxl')
                    except:
                        print("Intentando con engine='xlrd'...")
                        # Si falla, intentar con xlrd
                        df = pd.read_excel(nuevo_path, engine='xlrd')
                    
                    print(f"Filas leídas: {len(df)}")
                except Exception as e:
                    print(f"Error al leer el archivo Excel: {str(e)}")
                    print("Intentando leer como CSV...")
                    try:
                        # Si falla como Excel, intentar como CSV
                        df = pd.read_csv(nuevo_path, encoding='latin-1')
                        print(f"Archivo leído como CSV. Filas leídas: {len(df)}")
                    except Exception as e:
                        print(f"Error al leer el archivo como CSV: {str(e)}")
                        return None
                
                # Refrescar la página y volver a cargar el módulo
                print("Refrescando página para siguiente descarga...")
                driver.switch_to.default_content()
                driver.execute_script(
                    "cargarModulo(0,0,'https://gesmed.masterkey.cl/Modulo/Consultas/','Normal','Exportador','Index','','ExportadorExcels');"
                )
                time.sleep(5)  # Esperar que cargue el módulo
                
                # Volver al iframe
                iframe = wait.until(EC.presence_of_element_located((By.ID, "ifrmMostrador")))
                driver.switch_to.frame(iframe)
                time.sleep(10)
                
                return df
            else:
                print("No se encontraron archivos Excel en la carpeta")
                return None
        except Exception as e:
            print(f"Error al procesar archivo: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Error general en obtener_datos_por_periodo: {str(e)}")
        return None

def iniciar_sesion_y_descargar(usuario, contraseña):
    try:
        print("Configurando el navegador...")
        options = Options()
        
        # Desactivar el modo headless para ver la interfaz de usuario
        options.add_argument('--headless=new')  # Comentado para activar la interfaz de usuario
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--window-size=1920,1080')
        
        # Configuración de descarga
        prefs = {
            "download.default_directory": r"G:\Mi unidad\Tablas Power BI\GESMED PBI\GESMED-PBI\BASE MK",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1  # Permitir descargas automáticas
        }
        options.add_experimental_option('prefs', prefs)
        
        print("Iniciando navegador...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)
        
        # Obtener fechas actuales
        hoy = datetime.now()
        año_actual = hoy.year
        año_anterior = año_actual - 1
        
        # DataFrames para almacenar resultados
        df_año_anterior = []
        df_año_actual = []
        
        try:
            print("Accediendo a la página de login...")
            driver.get("https://gesmed.masterkey.cl/Login?msg=CerrarSesion")
            
            print("Iniciando sesión...")
            usuario_input = wait.until(EC.element_to_be_clickable((By.ID, "Usuario")))
            contraseña_input = wait.until(EC.element_to_be_clickable((By.ID, "Clave")))
            
            usuario_input.send_keys(usuario)
            contraseña_input.send_keys(contraseña)
            driver.execute_script("AutenticarSesion()")
            time.sleep(5)
            
            print("Navegando al módulo Exportador Excel...")
            driver.execute_script(
                "cargarModulo(0,0,'https://gesmed.masterkey.cl/Modulo/Consultas/','Normal','Exportador','Index','','ExportadorExcels');"
            )
            time.sleep(5)
            
            print("Cambiando al iframe...")
            iframe = wait.until(EC.presence_of_element_located((By.ID, "ifrmMostrador")))
            driver.switch_to.frame(iframe)
            time.sleep(3)
            
            # Crear carpetas para cada año
            carpeta_año_anterior = crear_carpetas_año(año_anterior)
            carpeta_año_actual = crear_carpetas_año(año_actual)
            
            # Procesar año anterior mes por mes
            print(f"Procesando año {año_anterior}...")
            for mes in range(1, 13):
                ultimo_dia = calendar.monthrange(año_anterior, mes)[1]
                fecha_desde = f"01-{mes:02d}-{año_anterior}"
                fecha_hasta = f"{ultimo_dia:02d}-{mes:02d}-{año_anterior}"
                
                df = obtener_datos_por_periodo(driver, wait, fecha_desde, fecha_hasta, carpeta_año_anterior)
                if df is not None:
                    df_año_anterior.append(df)
                    print(f"Mes {mes} del año {año_anterior} procesado correctamente")
            
            # Procesar año actual hasta la fecha
            print(f"Procesando año {año_actual}...")
            for mes in range(1, hoy.month + 1):
                if mes == hoy.month:
                    ultimo_dia = hoy.day
                else:
                    ultimo_dia = calendar.monthrange(año_actual, mes)[1]
                
                fecha_desde = f"01-{mes:02d}-{año_actual}"
                fecha_hasta = f"{ultimo_dia:02d}-{mes:02d}-{año_actual}"
                
                df = obtener_datos_por_periodo(driver, wait, fecha_desde, fecha_hasta, carpeta_año_actual)
                if df is not None:
                    df_año_actual.append(df)
                    print(f"Mes {mes} del año {año_actual} procesado correctamente")
            
            # Crear consolidados
            #if df_año_anterior:
            #    df_final_anterior = pd.concat(df_año_anterior, ignore_index=True)
            #    ruta_consolidado = os.path.join(carpeta_año_anterior, f"Consolidado_Movimientos_{año_anterior}.xlsx")
            #    df_final_anterior.to_excel(ruta_consolidado, index=False)
            #    print(f"Consolidado del año {año_anterior} creado exitosamente")
            
            #if df_año_actual:
            #    df_final_actual = pd.concat(df_año_actual, ignore_index=True)
            #    ruta_consolidado = os.path.join(carpeta_año_actual, f"Consolidado_Movimientos_{año_actual}.xlsx")
            #    df_final_actual.to_excel(ruta_consolidado, index=False)
            #    print(f"Consolidado del año {año_actual} creado exitosamente")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            driver.save_screenshot("error_screenshot.png")
            print("Se ha guardado una captura del error")
            
        finally:
            print("Cerrando navegador...")
            driver.quit()
            
    except Exception as e:
        print(f"Error al configurar el navegador: {str(e)}")

if __name__ == "__main__":
    usuario = "crioseco"
    contraseña = "cr01"
    iniciar_sesion_y_descargar(usuario, contraseña)
