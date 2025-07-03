import os
import pandas as pd
from pathlib import Path

# Ruta donde buscaremos los archivos .pbix
ruta = r"C:\Users\David Yail\Clinical Market\Control Gestión - Documentos\Power BI\Desktop"

# Listas para almacenar la información
rutas_completas = []
carpetas_finales = []
nombres_reportes = []

# Recorrer la ruta y sus subcarpetas
for raiz, dirs, archivos in os.walk(ruta):
    for archivo in archivos:
        if archivo.endswith('.pbix'):
            # Obtener la ruta completa
            ruta_completa = os.path.join(raiz, archivo)
            rutas_completas.append(ruta_completa)
            
            # Obtener la carpeta final (último directorio)
            carpeta_final = Path(raiz).name
            carpetas_finales.append(carpeta_final)
            
            # Obtener el nombre del reporte (sin la extensión .pbix)
            nombre_reporte = os.path.splitext(archivo)[0]
            nombres_reportes.append(nombre_reporte)

# Crear un DataFrame con la información
df = pd.DataFrame({
    'Ruta': rutas_completas,
    'Carpeta Final': carpetas_finales,
    'Nombre del Reporte': nombres_reportes
})

# Guardar en Excel
nombre_excel = 'inventario_reportes_powerbi.xlsx'
df.to_excel(nombre_excel, index=False)

print(f"Se encontraron {len(rutas_completas)} archivos .pbix")
print(f"La información se ha guardado en '{nombre_excel}'")
