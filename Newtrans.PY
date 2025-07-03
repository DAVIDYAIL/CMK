import os
import time
import calendar
import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import win32com.client
import pythoncom

def descargar_periodo(fecha_desde, fecha_hasta, nombre_archivo):
    # 📁 Carpeta destino
    carpeta_destino = rf"C:\Users\David Yail\Clinical Market\Control Gestión - Documentos\Respaldo Vistas\{fecha_desde.year}\Transporte\Newtrans"
    ruta_final = os.path.join(carpeta_destino, nombre_archivo)

    # 🧹 Eliminar si ya existe
    if os.path.exists(ruta_final):
        os.remove(ruta_final)

    # 📌 Buscar archivos .xls existentes
    def verificar_archivos_xls(directorio):
        archivos_xls = [f for f in os.listdir(directorio) if f.endswith(".xls")]
        return len(archivos_xls)

    # Verificar si hay archivos .xls existentes
    archivos_existentes = verificar_archivos_xls(carpeta_destino)
    if archivos_existentes > 0:
        print(f"❌ Se encontraron {archivos_existentes} archivos .xls en la carpeta. Por favor, elimínelos antes de continuar.")
        return False

    # ⚙️ Configurar Edge
    options = EdgeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    options.use_chromium = True
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')

    prefs = {
        "download.default_directory": carpeta_destino,
        "download.prompt_for_download": False,
        "safebrowsing.enabled": False,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.geolocation": 2,
        "profile.default_content_setting_values.mixed_script": 1,
        "profile.default_content_setting_values.cookies": 1
    }
    options.add_experimental_option("prefs", prefs)

    # 🚀 Iniciar navegador
    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 20)

    try:
        # 🌐 Login
        driver.get("http://nt.newtrans.cl/v2/index.php?i=8cc716455ff1f05cf3086de68b7d07b667a58d863e072badf7dd1dc30270c5e0&act=a")
        wait.until(EC.presence_of_element_located((By.ID, "ag_usu"))).send_keys("cmk")
        driver.find_element(By.ID, "ag_pass").send_keys("cmk01")
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Ingresar"]').click()
        print("🔐 Login realizado.")
        time.sleep(10)

        # 📂 Órdenes de Servicio
        icono = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "i.fa-paper-plane")))
        boton_ordenes = icono.find_element(By.XPATH, "./ancestor::a")
        boton_ordenes.click()
        print("📁 Acceso a Órdenes de Servicio.")
        time.sleep(5)

        # 📅 Ingresar fechas
        wait.until(EC.presence_of_element_located((By.ID, "desde"))).send_keys(fecha_desde.strftime("%d-%m-%Y"))
        driver.find_element(By.ID, "hasta").send_keys(fecha_hasta.strftime("%d-%m-%Y"))
        driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Listar OS"]').click()
        print(f"📅 Fechas ingresadas: {fecha_desde.strftime('%d-%m-%Y')} a {fecha_hasta.strftime('%d-%m-%Y')}")
        time.sleep(5)

        # 📄 Detalle
        boton_detalle = wait.until(EC.element_to_be_clickable((By.ID, "detalle6")))
        boton_detalle.click()
        print("📄 Detalle abierto.")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])  # Nueva pestaña

        # 📥 Descargar XLS
        img_descarga = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[src='img/iconos/boton_xls_verde.png']")))
        link_descarga = img_descarga.find_element(By.XPATH, "./ancestor::a")
        link_descarga.click()
        print("📥 Descarga iniciada...")

        # 📌 Buscar archivo .xls más reciente
        def obtener_ultimo_archivo_xls(directorio):
            archivos = [f for f in os.listdir(directorio) if f.endswith(".xls")]
            if not archivos:
                return None
            if len(archivos) > 1:
                print("❌ Se encontró más de un archivo .xls. Por favor, elimine los archivos adicionales.")
                return None
            archivos.sort(key=lambda f: os.path.getmtime(os.path.join(directorio, f)), reverse=True)
            return os.path.join(directorio, archivos[0])

        # ⏳ Esperar descarga
        ruta_descargada = None
        tiempo_espera = 0
        while tiempo_espera < 120:
            print(f"\r⏳ Esperando descarga... {120-tiempo_espera} segundos", end="", flush=True)
            posible_archivo = obtener_ultimo_archivo_xls(carpeta_destino)
            if posible_archivo:
                try:
                    with open(posible_archivo, 'rb') as f:
                        contenido = f.read()
                        if len(contenido) > 1000:
                            ruta_descargada = posible_archivo
                            break
                except:
                    pass
            time.sleep(1)
            tiempo_espera += 1
        print()

        # 🔄 Convertir y guardar como .xlsx
        if ruta_descargada and os.path.exists(ruta_descargada):
            try:
                print("🔄 Convirtiendo archivo a .xlsx...")
                time.sleep(5)
                
                pythoncom.CoInitialize()
                
                excel = win32com.client.Dispatch("Excel.Application")
                excel.Visible = False
                excel.DisplayAlerts = False
                excel.ScreenUpdating = False
                excel.EnableEvents = False
                excel.Interactive = False
                excel.WindowState = -4137
                
                try:
                    print("Abriendo archivo con Excel...")
                    wb = excel.Workbooks.Open(ruta_descargada)
                    
                    print("Renombrando hoja a 'Data'...")
                    wb.Sheets(1).Name = "Data"
                    
                    print("Guardando como xlsx...")
                    wb.SaveAs(ruta_final, FileFormat=51)
                    
                    wb.Close()
                    excel.Quit()
                    
                    os.remove(ruta_descargada)
                    print(f"✅ Archivo final guardado como: {ruta_final}")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error al convertir con Excel: {e}")
                    try:
                        print("Intentando método alternativo...")
                        df = pd.read_excel(ruta_descargada, engine='xlrd')
                        df.to_excel(ruta_final, index=False, sheet_name="Data", engine='openpyxl')
                        os.remove(ruta_descargada)
                        print(f"✅ Archivo convertido exitosamente usando método alternativo")
                        return True
                    except Exception as e2:
                        print(f"❌ Error en método alternativo: {e2}")
                        return False
                finally:
                    pythoncom.CoUninitialize()
            except Exception as e:
                print(f"❌ Error general: {e}")
                return False
        else:
            print("❌ No se encontró el archivo descargado.")
            return False

    finally:
        driver.quit()

# 📅 Fechas para ambos períodos
hoy = datetime.today()
mes_actual = hoy.month
anio_actual = hoy.year

# Mes actual
primer_dia_mes = hoy.replace(day=1)
ultimo_dia_mes = hoy

# Mes anterior
primer_dia_mes_anterior = (primer_dia_mes - relativedelta(months=1))
ultimo_dia_mes_anterior = primer_dia_mes - relativedelta(days=1)

meses_es = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Descargar mes actual
nombre_mes_actual = f"{meses_es[mes_actual]}-{anio_actual}.xlsx"
print(f"\n📥 Descargando mes actual: {meses_es[mes_actual]} {anio_actual}")
descargar_periodo(primer_dia_mes, ultimo_dia_mes, nombre_mes_actual)

# Descargar mes anterior
nombre_mes_anterior = f"{meses_es[primer_dia_mes_anterior.month]}-{primer_dia_mes_anterior.year}.xlsx"
print(f"\n📥 Descargando mes anterior: {meses_es[primer_dia_mes_anterior.month]} {primer_dia_mes_anterior.year}")
descargar_periodo(primer_dia_mes_anterior, ultimo_dia_mes_anterior, nombre_mes_anterior)

print("\n✅ Proceso completado.")







