import os
import time
import psutil
import win32com.client
import calendar
from datetime import datetime, timedelta

# 📌 Obtener la fecha actual y calcular el mes anterior
hoy = datetime.today()
fecha_mes_anterior = hoy.replace(day=1) - timedelta(days=1)

# 🔹 Diccionario para convertir nombres de mes al español
meses_es = {
    "January": "Enero", "February": "Febrero", "March": "Marzo", "April": "Abril",
    "May": "Mayo", "June": "Junio", "July": "Julio", "August": "Agosto",
    "September": "Septiembre", "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

mes_actual = hoy.month
mes_actual_nombre = meses_es[calendar.month_name[hoy.month]]
anio_actual = hoy.year


# 📌 Construcción dinámica de nombres de archivos
#BEETRACK_MES_ACTUAL = rf"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Respaldo Vistas\{anio_actual}\Transporte\Beetrack\{mes_actual}-{mes_actual_nombre}.xlsx"

# 📌 Lista de archivos de Excel con mes dinámico
archivos_excel = [
    rf"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Respaldo Vistas\{anio_actual}\Transporte\Beetrack\{mes_actual}-{mes_actual_nombre}.xlsx",
    r"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Power BI\Tablas\Alerta_MONTO_OC.xlsx",
    r"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Power BI\Tablas\Detalle_Alertas_Facturacion_CMK_PROFAR.xlsx",
    r"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Power BI\Tablas\Ventas_B2B_Alertas.xlsx",
    r"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Power BI\Tablas\Bodegas_Detalle.xlsx",
    r"C:\Users\Administrador\Clinical Market\Control Gestión - Documentos\Power BI\Tablas\SKU_ECOMMERCE.xlsx"
    
]

# 📌 Cerrar cualquier instancia previa de Excel (forzado, sin validación)
print("❌ Cerrando todas las instancias de Excel (forzado)...")
os.system("taskkill /IM EXCEL.EXE /F")
time.sleep(5)  # Esperar a que Excel se cierre completamente

# 📌 Iniciar Excel en segundo plano
print("🚀 Iniciando Excel en segundo plano...")
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = True  # Mantener Excel en segundo plano

# 📌 Intentar abrir los archivos con reintentos en caso de error
workbooks = []
max_retries = 3  # Número máximo de intentos
retry_wait = 5  # Tiempo de espera entre intentos en segundos

for archivo in archivos_excel:
    if os.path.exists(archivo):
        intentos = 0
        while intentos < max_retries:
            try:
                print(f"📂 Intentando abrir {os.path.basename(archivo)}... (Intento {intentos + 1}/{max_retries})")
                wb = excel.Workbooks.Open(archivo)
                workbooks.append(wb)
                time.sleep(2)  # Evita que Excel colapse por abrir varios archivos simultáneamente
                break  # Si se abre correctamente, salimos del bucle
            except Exception as e:
                print(f"⚠️ Error al abrir {os.path.basename(archivo)}: {e}")
                intentos += 1
                time.sleep(retry_wait)  # Esperar antes de reintentar

        if intentos == max_retries:
            print(f"❌ No se pudo abrir {os.path.basename(archivo)} después de {max_retries} intentos.")

# ⏳ Esperar 180 segundos antes de actualizar con contador
print("⌛ Esperando 15 segundos antes de actualizar los archivos...")
for i in range(15, 0, -1):
    print(f"\r⏳ Tiempo restante: {i} segundos", end="", flush=True)
    time.sleep(1)
print("\n✅ Listo para actualizar.")

# 📌 Ordenar actualización en todos los archivos abiertos
for wb in workbooks:
    archivo_nombre = os.path.basename(wb.FullName)
    print(f"🔄 Dando la orden de actualización en {archivo_nombre}...")
    try:
        wb.RefreshAll()
    except Exception as e:
        print(f"⚠️ Error al actualizar {archivo_nombre}: {e}")

# ⏳ Esperar 5 minutos antes de cerrar los archivos con contador
print("⌛ Esperando 3 minutos para completar la actualización...")
for i in range(180, 0, -1):
    minutos = i // 60
    segundos = i % 60
    print(f"\r⏳ Tiempo restante: {minutos:02}:{segundos:02} minutos", end="", flush=True)
    time.sleep(1)
print("\n✅ Todos los archivos han completado la actualización.")

# 📌 Guardar y cerrar cada archivo uno por uno
for wb in workbooks:
    archivo_nombre = os.path.basename(wb.FullName)
    try:
        wb.Save()
        print(f"✅ {archivo_nombre} guardado.")
        wb.Close()
        print(f"❌ {archivo_nombre} cerrado.")
    except Exception as e:
        print(f"⚠️ Error al cerrar {archivo_nombre}: {e}")

# 📌 Cerrar Excel completamente al final (forzado, sin validación)
print("❌ Cerrando Excel en segundo plano (forzado)...")
os.system("taskkill /IM EXCEL.EXE /F")
print("✅ Proceso completado.")