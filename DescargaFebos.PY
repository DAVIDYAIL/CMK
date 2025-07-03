import os
import time
import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# ✅ Obtener la fecha actual y calcular los nombres de los archivos
hoy = datetime.today()
fecha_mes_anterior = hoy - relativedelta(months=1)

meses_es = {
    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

mes_actual_nombre = meses_es[calendar.month_name[hoy.month]]
anio_actual = hoy.year

mes_anterior_nombre = meses_es[calendar.month_name[fecha_mes_anterior.month]]
anio_anterior = fecha_mes_anterior.year

nombre_archivo_mes_actual = f"{mes_actual_nombre}-{anio_actual}.csv"
nombre_archivo_mes_anterior = f"{mes_anterior_nombre}-{anio_anterior}.csv"

# ✅ Directorio destino (descarga directa)
destination_directory = r"C:\Users\David Yail\Clinical Market\Control Gestión - Documentos\Power BI\Tablas\Doc-Febos"
nombre_original = "ExportadoFebos.csv"  # 📌 Nombre con el que se descarga

# ✅ Configuración del navegador en modo **headless** (sin interfaz)
options = Options()
options.add_argument('--headless=new')  # 🛠 Ejecutar sin interfaz gráfica
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--disable-software-rasterizer')
options.add_argument('--window-size=1920,1080')

# ✅ Configuración de descarga
prefs = {
    "download.default_directory": destination_directory,  # 📌 Se guarda directamente en la carpeta destino
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_values.automatic_downloads": 1
}
options.add_experimental_option("prefs", prefs)

# ✅ Iniciar el navegador con Selenium
print("Iniciando el navegador en modo headless...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

# ✅ Iniciar sesión en la plataforma
print("Abriendo la página de inicio de sesión...")
login_page_url = 'https://portal.febos.cl/produccion/web#/cloud/ingreso'
driver.get(login_page_url)

print("Esperando los campos de inicio de sesión...")
correo_input = wait.until(EC.presence_of_element_located((By.ID, 'login_username')))
clave_input = driver.find_element(By.ID, 'login_password')

# 🔑 Ingresar credenciales
correo_input.send_keys('nmartinez@clinicalmarket.cl')
clave_input.send_keys('NMartinez*01')

# 📌 Hacer clic en el botón de inicio de sesión
print("Iniciando sesión...")
boton_entrar = driver.find_element(By.CSS_SELECTOR, 'button[data-cy="get-in"]')
boton_entrar.click()
time.sleep(10)

# ✅ Selección de empresa
print("Esperando la selección de empresa...")
empresa_element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-cy="company-name"] .md-list-heading.ng-binding')))
print("Seleccionando la empresa 'CLINICAL MARKET S.A.'...")
empresa_element.click()
time.sleep(10)

# ✅ Función para descargar documentos y renombrarlos después
def descargar_documentos(url, nombre_archivo):
    print(f"Redirigiendo a la página de documentos electrónicos: {url}")
    driver.get(url)
    time.sleep(5)
    driver.refresh()
    time.sleep(15)
    

    print("Esperando que cargue la página de documentos...")
    time.sleep(10)

    print("Abriendo el menú de acciones...")
    boton_abrir_menu = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.md-fab.md-fab-primary.ng-scope')))
    driver.execute_script("arguments[0].click();", boton_abrir_menu)
    time.sleep(2)

    print("Abriendo el modal de descarga de reportes...")
    boton_descargar_reportes = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[ng-click="abrirModalDescargarReportes()"]')))
    driver.execute_script("arguments[0].click();", boton_descargar_reportes)
    time.sleep(2)

    print("Iniciando la descarga del reporte...")
    boton_confirmar_descarga = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[ng-click^="descargarReporte"]')))
    driver.execute_script("arguments[0].click();", boton_confirmar_descarga)

    # 📌 Contador regresivo de 60 segundos
    print(f"Esperando 60 segundos para que se descargue {nombre_archivo}...")
    for i in range(60, 0, -1):
        print(f"\r⏳ Tiempo restante: {i} segundos...", end="", flush=True)
        time.sleep(1)
    print("\n✅ Descarga completada.")

    # 🔄 Verificar si el archivo de destino ya existe y eliminarlo
    new_path = os.path.join(destination_directory, nombre_archivo)
    if os.path.exists(new_path):
        print(f"⚠️ El archivo {new_path} ya existe. Eliminándolo para evitar duplicados...")
        os.remove(new_path)

    # 🔄 Renombrar el archivo descargado
    original_path = os.path.join(destination_directory, nombre_original)
    if os.path.exists(original_path):
        os.rename(original_path, new_path)
        print(f"✅ Archivo renombrado a {new_path}")
    else:
        print(f"⚠️ No se encontró {nombre_original}, verifica si la descarga fue exitosa.")

# ✅ URLs de documentos electrónicos
doc_mes_anterior = 'https://portal.febos.cl/produccion/web#/cloud/documentos/electronicos/recibidos/todos?pagina=1&itemsPorPagina=20&orden=-fechaCreacion&filtros=rutReceptor:76111113-2%7CtipoDocumento:33,34,43,46,56,61,110,111,112%7CestadoSii:4,5%7Cincompleto:N%7CfechaEmision:%5BelMesPasado%5D'
doc_mes_actual = 'https://portal.febos.cl/produccion/web#/cloud/documentos/electronicos/recibidos/todos?pagina=1&itemsPorPagina=20&orden=-fechaCreacion&filtros=rutReceptor:76111113-2%7CtipoDocumento:33,34,43,46,56,61,110,111,112%7CestadoSii:4,5%7Cincompleto:N%7CfechaEmision:%5BesteMes%5D'

# ✅ Descargar documentos y renombrarlos correctamente
descargar_documentos(doc_mes_anterior, nombre_archivo_mes_anterior)
descargar_documentos(doc_mes_actual, nombre_archivo_mes_actual)

# ✅ Cerrar el navegador
print("Cerrando el navegador...")
driver.quit()



