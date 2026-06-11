import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Población de Castellón",
    page_icon="🏘️",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    font-weight: 400;
}

h1, h2, h3 {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    letter-spacing: -0.5px;
}

section[data-testid="stSidebar"] {
    background: #1a1a2e;
    color: white;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

.main .block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# imágen de fondo para el título de la página
img_path = os.path.join(os.path.dirname(__file__), "images", "casaNova.jpg")

if os.path.exists(img_path):
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    bg_style = f"background-image: linear-gradient(rgba(15,30,60,0.32), rgba(15,30,60,0.32)), url('data:image/jpeg;base64,{img_b64}'); background-size: cover; background-position: center 65%;"
else:
    bg_style = "background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);"

st.markdown(f"""
<div style="
    {bg_style}
    border-radius: 16px;
    padding: 4rem 2rem;
    margin-bottom: 2rem;
    text-align: center;
">
    <h1 style="
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        color: #e2b96f;
        margin: 0 0 0.5rem 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
    ">Población de la Provincia de Castellón</h1>
    <p style="
        font-family: 'DM Sans', sans-serif;
        font-size: 1.2rem;
        color: #e0e0e0;
        margin: 0;
        text-shadow: 0 1px 4px rgba(0,0,0,0.4);
    ">Evolución demográfica de los municipios castellonenses · 1996 – 2025</p>
</div>
""", unsafe_allow_html=True)

# bloques explicativos de qué se encuentra en la página
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background:#f7f3ec; border-left: 4px solid #e2b96f; border-radius:8px; padding:1.2rem;">
        <h3 style="margin:0; color:#1a1a2e;">🗺️ Mapa interactivo</h3>
        <p style="color:#555; margin:0.5rem 0 0 0;">Mapa de coropletas con la evolución de la población por municipio. Puedes seleccionar el año y la métrica a visualizar !</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background:#f7f3ec; border-left: 4px solid #e2b96f; border-radius:8px; padding:1.2rem;">
        <h3 style="margin:0; color:#1a1a2e;">📊 Gráficas y análisis</h3>
        <p style="color:#555; margin:0.5rem 0 0 0;">Evolución temporal, rankings, comparativas entre municipios y distribución demográfica.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
**Navega usando el menú de la izquierda** para explorar el mapa interactivo y las gráficas de análisis.

**Fuente de datos:** Instituto Nacional de Estadística (INE)
""")