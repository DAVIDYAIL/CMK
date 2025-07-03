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
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 0.1em;
        margin-top: 0.2em;
        text-shadow: 1px 1px 6px #fff, 0 0 2px #0DA7EE;
    }
    .subtitulo {
        color: #797C89;
        font-size: 1em;
        margin-bottom: 0.5em;
        text-shadow: 1px 1px 6px #fff;
    }
    .titulo-pen {
        color: #0688E2;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 0.3em;
        text-shadow: 1px 1px 6px #fff;
    }
    .stButton>button {
        background-color: #0DA7EE;
        color: white !important;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-size: 1.2em;
        font-weight: bold;
        border: none;
        transition: background 0.2s, color 0.2s;
    }
    .stButton>button:hover, .stButton>button:active, .stButton>button:focus {
        background-color: #0688E2;
        color: white !important;
    }
    /* Caja de resultados moderna y amplia */
    .resultados-box {
        background: #eaf6fd;
        border-radius: 18px;
        box-shadow: 0 2px 16px rgba(13,167,238,0.10);
        padding: 1.2em 1em 1em 1em;
        margin-top: 0.5em;
        margin-bottom: 1em;
        width: 98vw;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        transition: box-shadow 0.2s;
    }
    .resultados-box:hover {
        box-shadow: 0 8px 40px rgba(13,167,238,0.18);
    }
    /* Tabla moderna y responsive con nueva paleta */
    .resultados-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: #f7fbfd;
        font-size: 0.98em;
        margin-bottom: 0.5em;
        border-radius: 12px;
        overflow: hidden;
    }
    .resultados-table th, .resultados-table td {
        padding: 0.6em 0.3em;
        text-align: center;
        border-bottom: 1px solid #e0e7ef;
    }
    .resultados-table th {
        background: #eaf6fd;
        color: #0688E2;
        font-weight: bold;
        font-size: 1em;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }
    .resultados-table tr:last-child td {
        border-bottom: none;
    }
    .resultados-table tr:nth-child(even) td {
        background: #f4f8fb;
    }
    .resultados-table tr:nth-child(odd) td {
        background: #ffffff;
    }
    .resultados-table td {
        color: #222;
        font-size: 0.98em;
    }
    .resultados-table td:first-child {
        color: #0688E2;
        font-weight: bold;
        background: #eaf6fd;
        text-align: left;
        border-left: 2px solid #0DA7EE22;
    }
    .resultados-table .resaltado {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.18em;
    }
    @media (max-width: 900px) {
        .resultados-box { width: 99vw; padding: 1em 0.2em; }
        .resultados-table th, .resultados-table td { font-size: 0.98em; padding: 0.5em 0.2em; }
    }
    /* Contraste para los inputs */
    input[type="number"] {
        background: #fff !important;
        border: 2px solid #0DA7EE !important;
        border-radius: 8px !important;
        color: #222 !important;
        font-size: 1em !important;
        box-shadow: 0 1px 4px #0da7ee22;
    }
    </style>
""", unsafe_allow_html=True)

# Mostrar logo
st.image("Profar.png", width=140)

# Título
st.markdown("<div class='titulo-app'>Simulador De Dosis Genotropin</div>", unsafe_allow_html=True)

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
    dosis_mg = st.number_input("Dosis diaria (mg)", 0.0, 4.1, 0.0, 0.1, format="%.1f", key="dosis_mg", disabled=disabled_mg)
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
        return f"<span class='resaltado'>{c:.2f}</span>" if abs(c - round(c)) > 1e-6 else str(int(round(c)))

    st.markdown("<div class='titulo-pen'>Resultados de dosificación</div>", unsafe_allow_html=True)
    # Tabla moderna en HTML
    tabla_html = f'''
    <div class="resultados-box">
    <table class="resultados-table">
        <thead>
            <tr>
                <th></th>
                <th>Pen 5,3 mg o 16 UI</th>
                <th>Pen 12 mg o 36 UI</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><b>Dosis diaria</b></td>
                <td>{dosis_53}</td>
                <td>{dosis_12}</td>
            </tr>
            <tr>
                <td><b>Click Pen</b></td>
                <td>{format_clicks(clicks_53_real)}</td>
                <td>{format_clicks(clicks_12_real)}</td>
            </tr>
            <tr>
                <td><b>Cartuchos para 30 días de tto</b></td>
                <td>{cartuchos_53}</td>
                <td>{cartuchos_12}</td>
            </tr>
            <tr>
                <td><b>Días Totales Cubiertos por despacho</b></td>
                <td>{dias_53}</td>
                <td>{dias_12}</td>
            </tr>
        </tbody>
    </table>
    '''
    # Mensajes de advertencia
    if abs(clicks_53_real - round(clicks_53_real)) > 1e-6:
        tabla_html += "<div style='color:#e74c3c;font-weight:bold;margin-top:0.5em'>No es posible dosificar esta dosis exacta con el Pen 5,3 mg o 16 UI.</div>"
    if abs(clicks_12_real - round(clicks_12_real)) > 1e-6:
        tabla_html += "<div style='color:#e74c3c;font-weight:bold;margin-top:0.5em'>No es posible dosificar esta dosis exacta con el Pen 12 mg o 36 UI.</div>"
    tabla_html += "</div>"
    st.markdown(tabla_html, unsafe_allow_html=True)
