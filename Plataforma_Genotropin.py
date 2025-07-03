import streamlit as st
import math
import pandas as pd
import base64

# Cargar imagen de fondo y convertir a base64
with open("Fondo_Profar2.jpg", "rb") as f:
    data = f.read()
    encoded = base64.b64encode(data).decode()
    bg_img = f"data:image/jpg;base64,{encoded}"

# Ocultar menú lateral, header y footer de Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Estilos personalizados con fondo en base64
st.markdown(f'''
    <style>
    .stApp {{
        background-image: url('{bg_img}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    [data-testid="stStatusWidget"] {{display: none !important;}}
    header {{background: none !important;}}
    .stButton>button {{
        background-color: #0DA7EE;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5em 2em;
        font-size: 1.1em;
        font-weight: bold;
    }}
    .stButton>button:hover {{
        background-color: #0688E2;
        color: #fff;
    }}
    .stTable, .stDataFrame {{
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(13,167,238,0.08);
        margin-bottom: 2em;
    }}
    .titulo-pen {{
        color: #0688E2;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 0.5em;
    }}
    .titulo-app {{
        color: #0DA7EE;
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }}
    .subtitulo {{
        color: #797C89;
        font-size: 1.1em;
        margin-bottom: 1em;
    }}
    </style>
''', unsafe_allow_html=True)

# Logo centrado
st.image("Profar.png", width=180)

# Título principal
st.markdown("<div class='titulo-app'>Simulador Dosis Genotropin</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Calcula la dosificación y cobertura de tratamiento para los dispositivos Genotropin.</div>", unsafe_allow_html=True)

# Campos de entrada (sin card)
st.markdown("<h4 style='color: #005baa;'>Ingresar dosis diaria</h4>", unsafe_allow_html=True)

# Datos de conversión
# Pen 5,3 mg o 16 UI
pen_53_clicks = list(range(1, 21))
pen_53_ui = [0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.2, 4.5, 4.8, 5.1, 5.4, 5.7, 6.0]
pen_53_mg = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

# Pen 12 mg o 36 UI
pen_12_clicks = list(range(1, 21))
pen_12_ui = [0.6, 1.2, 1.8, 2.4, 3.0, 3.6, 4.2, 4.8, 5.4, 6.0, 6.6, 7.2, 7.8, 8.4, 9.0, 9.6, 10.2, 10.8, 11.4, 12.0]
pen_12_mg = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0]

# Funciones de conversión

def mg_to_ui(mg, pen_mg, pen_ui):
    # Busca la equivalencia más cercana
    if mg <= 0:
        return 0
    difs = [abs(m - mg) for m in pen_mg]
    idx = difs.index(min(difs))
    return pen_ui[idx], pen_53_clicks[idx]

def ui_to_mg(ui, pen_ui, pen_mg):
    if ui <= 0:
        return 0
    difs = [abs(u - ui) for u in pen_ui]
    idx = difs.index(min(difs))
    return pen_mg[idx], pen_53_clicks[idx]

def cartuchos_necesarios(dosis_diaria, total_ui_cartucho, dias=30):
    if dosis_diaria <= 0:
        return 0
    return math.ceil((dosis_diaria * dias) / total_ui_cartucho)

def dias_cubiertos(cartuchos, total_ui_cartucho, dosis_diaria):
    if dosis_diaria <= 0:
        return 0
    return int((total_ui_cartucho * cartuchos) / dosis_diaria) if dosis_diaria > 0 else 0

# Determinar máximos según la tabla
max_mg_53 = max(pen_53_mg)
max_mg_12 = max(pen_12_mg)
max_mg = max(max_mg_53, max_mg_12)
max_ui_53 = max(pen_53_ui)
max_ui_12 = max(pen_12_ui)
max_ui = max(max_ui_53, max_ui_12)

# Estado para los campos
if 'dosis_mg' not in st.session_state:
    st.session_state['dosis_mg'] = 0
if 'dosis_ui' not in st.session_state:
    st.session_state['dosis_ui'] = 0

col1, col2 = st.columns(2)

with col1:
    disabled_mg = st.session_state['dosis_ui'] != 0
    dosis_mg = st.number_input("Dosis diaria (mg)", min_value=0.0, max_value=max_mg, step=0.1, format="%.1f", key="dosis_mg", disabled=disabled_mg)
with col2:
    disabled_ui = st.session_state['dosis_mg'] != 0
    dosis_ui = st.number_input("Dosis diaria (UI)", min_value=0.0, max_value=max_ui, step=0.1, format="%.1f", key="dosis_ui", disabled=disabled_ui)

# Botón para resetear ambos campos
def resetear():
    st.session_state['dosis_mg'] = 0
    st.session_state['dosis_ui'] = 0

st.button("Resetear", on_click=resetear)

# Si el usuario ingresa mg, calcula UI y viceversa
if dosis_mg > 0 and dosis_ui == 0:
    # Pen 5,3 mg
    ui_53, clicks_53 = mg_to_ui(dosis_mg, pen_53_mg, pen_53_ui)
    # Pen 12 mg
    ui_12, clicks_12 = mg_to_ui(dosis_mg, pen_12_mg, pen_12_ui)
    dosis_ui = 0  # Para evitar confusión
elif dosis_ui > 0 and dosis_mg == 0:
    # Pen 5,3 mg
    mg_53, clicks_53 = ui_to_mg(dosis_ui, pen_53_ui, pen_53_mg)
    # Pen 12 mg
    mg_12, clicks_12 = ui_to_mg(dosis_ui, pen_12_ui, pen_12_mg)
    dosis_mg = 0
else:
    ui_53 = mg_53 = clicks_53 = 0
    ui_12 = mg_12 = clicks_12 = 0

# Resultados en formato tabla para ambos pen
if (dosis_mg > 0 and dosis_ui == 0) or (dosis_ui > 0 and dosis_mg == 0):
    st.markdown("<div class='titulo-pen'>Resultados de dosificación</div>", unsafe_allow_html=True)
    # Preparar datos para Pen 5,3 mg o 16 UI
    if dosis_mg > 0:
        dosis_53 = f"{dosis_mg:.1f} mg ≈ {ui_53:.1f} UI"
        # Calcular clicks reales (puede ser decimal)
        clicks_53_real = dosis_mg / 0.1
        cartuchos_53 = cartuchos_necesarios(ui_53, 16)
        dias_53 = dias_cubiertos(cartuchos_53, 16, ui_53)
    else:
        dosis_53 = f"{mg_53:.1f} mg ≈ {dosis_ui:.1f} UI"
        clicks_53_real = dosis_ui / 0.3
        cartuchos_53 = cartuchos_necesarios(dosis_ui, 16)
        dias_53 = dias_cubiertos(cartuchos_53, 16, dosis_ui)
    # Preparar datos para Pen 12 mg o 36 UI
    if dosis_mg > 0:
        dosis_12 = f"{dosis_mg:.1f} mg ≈ {ui_12:.1f} UI"
        clicks_12_real = dosis_mg / 0.2
        cartuchos_12 = cartuchos_necesarios(ui_12, 36)
        dias_12 = dias_cubiertos(cartuchos_12, 36, ui_12)
    else:
        dosis_12 = f"{mg_12:.1f} mg ≈ {dosis_ui:.1f} UI"
        clicks_12_real = dosis_ui / 0.6
        cartuchos_12 = cartuchos_necesarios(dosis_ui, 36)
        dias_12 = dias_cubiertos(cartuchos_12, 36, dosis_ui)

    # Revisar si los clicks son enteros
    def format_clicks(clicks):
        if abs(clicks - round(clicks)) < 1e-6:
            return f"{int(round(clicks))}"
        else:
            return f"<span style='color:red;font-weight:bold'>{clicks:.2f}</span>"
    click_53_str = format_clicks(clicks_53_real)
    click_12_str = format_clicks(clicks_12_real)

    # Crear DataFrame con HTML para resaltar
    df = pd.DataFrame({
        'Pen 5,3 mg o 16 UI': [dosis_53, click_53_str, cartuchos_53, dias_53],
        'Pen 12 mg o 36 UI': [dosis_12, click_12_str, cartuchos_12, dias_12]
    }, index=[
        'Dosis diaria',
        'Click Pen',
        'Cartuchos para 30 días de tto',
        'Días Totales Cubiertos por despacho'
    ])
    st.write(df.to_html(escape=False), unsafe_allow_html=True)

    # Mensajes de advertencia
    if not abs(clicks_53_real - round(clicks_53_real)) < 1e-6:
        st.markdown("<span style='color:red'>No es posible dosificar esta dosis exacta con el Pen 5,3 mg o 16 UI.</span>", unsafe_allow_html=True)
    if not abs(clicks_12_real - round(clicks_12_real)) < 1e-6:
        st.markdown("<span style='color:red'>No es posible dosificar esta dosis exacta con el Pen 12 mg o 36 UI.</span>", unsafe_allow_html=True)
