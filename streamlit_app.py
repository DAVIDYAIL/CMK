import streamlit as st
import math
import pandas as pd

# URL del fondo desde GitHub
bg_img = "https://raw.githubusercontent.com/DAVIDYAIL/CMK/main/Fondo_Profar2.jpg"

# Ocultar menú, header y footer
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background-image: url('""" + bg_img + """');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    .titulo-app {
        color: #0DA7EE;
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 0.2em;
    }
    .subtitulo {
        color: #797C89;
        font-size: 1.1em;
        margin-bottom: 1em;
    }
    .titulo-pen {
        color: #0688E2;
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 0.5em;
    }
    .stButton>button {
        background-color: #0DA7EE;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-size: 1.1em;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0688E2;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar logo
st.image("Profar.png", width=180)

# Título
st.markdown("<div class='titulo-app'>Simulador Dosis Genotropin</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Calcula la dosificación y cobertura de tratamiento para los dispositivos Genotropin.</div>", unsafe_allow_html=True)

# Datos de conversión
pen_53_clicks = list(range(1, 21))
pen_53_ui = [0.3 * i for i in pen_53_clicks]
pen_53_mg = [0.1 * i for i in pen_53_clicks]
pen_12_clicks = list(range(1, 21))
pen_12_ui = [0.6 * i for i in pen_12_clicks]
pen_12_mg = [0.2 * i for i in pen_12_clicks]

# Funciones
def mg_to_ui(mg, pen_mg, pen_ui):
    if mg <= 0:
        return 0, 0
    difs = [abs(m - mg) for m in pen_mg]
    idx = difs.index(min(difs))
    return pen_ui[idx], pen_53_clicks[idx]

def ui_to_mg(ui, pen_ui, pen_mg):
    if ui <= 0:
        return 0, 0
    difs = [abs(u - ui) for u in pen_ui]
    idx = difs.index(min(difs))
    return pen_mg[idx], pen_53_clicks[idx]

def cartuchos_necesarios(dosis_diaria, total_ui_cartucho, dias=30):
    return math.ceil((dosis_diaria * dias) / total_ui_cartucho) if dosis_diaria > 0 else 0

def dias_cubiertos(cartuchos, total_ui_cartucho, dosis_diaria):
    return int((total_ui_cartucho * cartuchos) / dosis_diaria) if dosis_diaria > 0 else 0

# Entradas
if 'dosis_mg' not in st.session_state:
    st.session_state['dosis_mg'] = 0
if 'dosis_ui' not in st.session_state:
    st.session_state['dosis_ui'] = 0

col1, col2 = st.columns(2)
with col1:
    disabled_mg = st.session_state['dosis_ui'] != 0
    dosis_mg = st.number_input("Dosis diaria (mg)", 0.0, max(pen_12_mg), 0.0, 0.1, format="%.1f", key="dosis_mg", disabled=disabled_mg)
with col2:
    disabled_ui = st.session_state['dosis_mg'] != 0
    dosis_ui = st.number_input("Dosis diaria (UI)", 0.0, max(pen_12_ui), 0.0, 0.1, format="%.1f", key="dosis_ui", disabled=disabled_ui)

# Botón de reseteo
def resetear():
    st.session_state['dosis_mg'] = 0
    st.session_state['dosis_ui'] = 0
st.button("Resetear", on_click=resetear)

# Procesar resultados
if dosis_mg > 0 and dosis_ui == 0:
    ui_53, clicks_53 = mg_to_ui(dosis_mg, pen_53_mg, pen_53_ui)
    ui_12, clicks_12 = mg_to_ui(dosis_mg, pen_12_mg, pen_12_ui)
    clicks_53_real = dosis_mg / 0.1
    clicks_12_real = dosis_mg / 0.2
    cartuchos_53 = cartuchos_necesarios(ui_53, 16)
    dias_53 = dias_cubiertos(cartuchos_53, 16, ui_53)
    cartuchos_12 = cartuchos_necesarios(ui_12, 36)
    dias_12 = dias_cubiertos(cartuchos_12, 36, ui_12)
    dosis_53 = f"{dosis_mg:.1f} mg ≈ {ui_53:.1f} UI"
    dosis_12 = f"{dosis_mg:.1f} mg ≈ {ui_12:.1f} UI"
elif dosis_ui > 0 and dosis_mg == 0:
    mg_53, clicks_53 = ui_to_mg(dosis_ui, pen_53_ui, pen_53_mg)
    mg_12, clicks_12 = ui_to_mg(dosis_ui, pen_12_ui, pen_12_mg)
    clicks_53_real = dosis_ui / 0.3
    clicks_12_real = dosis_ui / 0.6
    cartuchos_53 = cartuchos_necesarios(dosis_ui, 16)
    dias_53 = dias_cubiertos(cartuchos_53, 16, dosis_ui)
    cartuchos_12 = cartuchos_necesarios(dosis_ui, 36)
    dias_12 = dias_cubiertos(cartuchos_12, 36, dosis_ui)
    dosis_53 = f"{mg_53:.1f} mg ≈ {dosis_ui:.1f} UI"
    dosis_12 = f"{mg_12:.1f} mg ≈ {dosis_ui:.1f} UI"
else:
    dosis_53 = dosis_12 = clicks_53_real = clicks_12_real = cartuchos_53 = dias_53 = cartuchos_12 = dias_12 = 0

# Mostrar resultados
if (dosis_mg > 0 and dosis_ui == 0) or (dosis_ui > 0 and dosis_mg == 0):
    def format_clicks(c):
        return f"<span style='color:red;font-weight:bold'>{c:.2f}</span>" if abs(c - round(c)) > 1e-6 else str(int(round(c)))

    st.markdown("<div class='titulo-pen'>Resultados de dosificación</div>", unsafe_allow_html=True)
    df = pd.DataFrame({
        'Pen 5,3 mg o 16 UI': [dosis_53, format_clicks(clicks_53_real), cartuchos_53, dias_53],
        'Pen 12 mg o 36 UI': [dosis_12, format_clicks(clicks_12_real), cartuchos_12, dias_12]
    }, index=[
        'Dosis diaria',
        'Click Pen',
        'Cartuchos para 30 días de tto',
        'Días Totales Cubiertos por despacho'
    ])
    st.write(df.to_html(escape=False), unsafe_allow_html=True)

    if abs(clicks_53_real - round(clicks_53_real)) > 1e-6:
        st.markdown("<span style='color:red'>No es posible dosificar esta dosis exacta con el Pen 5,3 mg o 16 UI.</span>", unsafe_allow_html=True)
    if abs(clicks_12_real - round(clicks_12_real)) > 1e-6:
        st.markdown("<span style='color:red'>No es posible dosificar esta dosis exacta con el Pen 12 mg o 36 UI.</span>", unsafe_allow_html=True)
