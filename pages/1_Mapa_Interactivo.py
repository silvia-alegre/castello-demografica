import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import json
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_poblacion, _arreglar_nombre

st.set_page_config(page_title="Mapa Castellon", page_icon="🗺️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');
h1,h2,h3 { font-family: 'Inter', sans-serif; font-weight: 600; letter-spacing: -0.5px; }
body, p, div { font-family: 'DM Sans', sans-serif; font-weight: 400; }
section[data-testid="stSidebar"] { background: #1a1a2e; }
section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("# 🗺️ Mapa de Población")
st.markdown("Distribución de la población en los municipios de la provincia de Castellón.")

CSV_PATH     = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "2865.csv")
GEOJSON_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "castellon_municipios.geojson")

# cargar datos
df = load_poblacion()
COL_MUN = "municipio"
COL_ANY = "año"
COL_POB = "total"

years = sorted(df[COL_ANY].dropna().unique().astype(int))

# menú izquierda
with st.sidebar:
    st.markdown("## Parámetros del mapa")
    selected_year = st.select_slider(
        "Año", options=years, value=years[-1],
        help="Selecciona el año del padrón municipal"
    )
    metrica = st.radio(
        "Métrica visualizada",
        options=["Población total", "Variación respecto al año anterior (%)"],
    )

# preparar datos para el mapa
df_year = df[df[COL_ANY] == selected_year].copy()

if metrica == "Variación respecto al año anterior (%)":
    idx = years.index(selected_year)
    if idx > 0:
        prev = years[idx - 1]
        df_prev = df[df[COL_ANY] == prev][[COL_MUN, COL_POB]].rename(columns={COL_POB: "pob_prev"})
        df_year = df_year.merge(df_prev, on=COL_MUN, how="left")
        df_year["valor"] = ((df_year[COL_POB] - df_year["pob_prev"]) / df_year["pob_prev"] * 100).round(2)
        legend_name = "Variacion (%)"
        color_scale = "RdYlGn"
    else:
        st.warning("No hay año anterior disponible. Mostrando población total.")
        df_year["valor"] = df_year[COL_POB]
        legend_name = "Poblacion"
        color_scale = "YlOrRd"
else:
    df_year["valor"] = df_year[COL_POB]
    legend_name = "Poblacion"
    color_scale = "YlOrRd"

df_year = df_year.dropna(subset=["valor"])

# cabecera de resumen de métricas
total_pob = int(df_year[COL_POB].sum())
n_municipios = df_year[COL_MUN].nunique()
idx_max = df_year[COL_POB].idxmax()
idx_min = df_year[COL_POB].idxmin()
mun_mayor = df_year.loc[idx_max, COL_MUN]
pob_mayor = int(df_year.loc[idx_max, COL_POB])
mun_menor = df_year.loc[idx_min, COL_MUN]
pob_menor = int(df_year.loc[idx_min, COL_POB])
pob_media = int(df_year[COL_POB].mean())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("👥 Población total", f"{total_pob:,}".replace(",", "."))
c2.metric("🏘️ Municipios", n_municipios)
c3.metric("📊 Pobl. media", f"{pob_media:,}".replace(",", "."))
c4.markdown(f"""
<div style="font-size:0.85rem; color:#555;">🏆 Más poblado</div>
<div style="font-size:1.1rem; font-weight:600; color:#1a1a2e; line-height:1.3;">{mun_mayor}<br><span style="font-size:0.85rem; color:#666;">{pob_mayor:,} hab.</span></div>
""".replace(",", "."), unsafe_allow_html=True)
c5.markdown(f"""
<div style="font-size:0.85rem; color:#555;">🔻 Menos poblado</div>
<div style="font-size:1.1rem; font-weight:600; color:#1a1a2e; line-height:1.3;">{mun_menor}<br><span style="font-size:0.85rem; color:#666;">{pob_menor:,} hab.</span></div>
""".replace(",", "."), unsafe_allow_html=True)

st.markdown("---")

# cargar datos geojson
@st.cache_data(show_spinner="Cargando geometria de municipios...")
def get_geojson():
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)

geojson_castellon = get_geojson()

# construir el codigo para el mapa
raw = pd.read_csv(CSV_PATH, sep=";", encoding="latin-1", thousands=".", decimal=",")
raw.columns = [c.strip() for c in raw.columns]
raw = raw[raw["Sexo"].str.strip() == "Total"].copy()
raw["codigo"] = raw["Municipios"].astype(str).str.extract(r"^(\d+)\s+")[0].str.zfill(5)
raw = raw[raw["codigo"] != "00012"]
raw["nombre"] = (raw["Municipios"].astype(str)
                 .str.replace(r"^\d+\s+", "", regex=True)
                 .str.strip()
                 .apply(_arreglar_nombre))
codigo_map = dict(zip(raw["nombre"], raw["codigo"]))

df_year["mun_code"] = df_year[COL_MUN].map(codigo_map).fillna("")
df_choro = df_year[df_year["mun_code"] != ""].copy()
df_choro["mun_code"] = df_choro["mun_code"].astype(str)
df_choro["valor"] = pd.to_numeric(df_choro["valor"], errors="coerce")
df_choro = df_choro.dropna(subset=["valor"]).reset_index(drop=True)

# mapa
vmax = float(np.percentile(df_choro["valor"].dropna(), 95))
vmin = float(df_choro["valor"].min())

fig = px.choropleth_mapbox(
    df_choro,
    geojson=geojson_castellon,
    locations="mun_code",
    featureidkey="properties.mun_code",
    color="valor",
    color_continuous_scale=color_scale,
    range_color=(vmin, vmax),
    mapbox_style="carto-positron",
    zoom=7.5,
    center={"lat": 40.1, "lon": -0.1},
    opacity=0.75,
    hover_name=COL_MUN,
    hover_data={"mun_code": False, COL_POB: ":,.0f", "valor": ":.1f"},
    labels={COL_POB: "Población", "valor": legend_name},
    title=f"{legend_name} por municipio — {selected_year}",
)
fig.update_layout(
    margin={"r": 0, "t": 40, "l": 0, "b": 0},
    height=580,
    coloraxis_colorbar=dict(title=legend_name),
    font_family="Source Sans 3",
    title_font_family="Playfair Display",
    title_font_size=16,
)
st.plotly_chart(fig, use_container_width=True)

# visualizar tabla completa de datos
st.markdown("---")
with st.expander("📋 Ver tabla de datos completa"):
    if legend_name == "Poblacion":
        tabla = df_year[[COL_MUN, COL_POB]].copy()
        tabla = tabla.sort_values(COL_POB, ascending=False).reset_index(drop=True)
        tabla.columns = ["Municipio", "Población"]
    else:
        tabla = df_year[[COL_MUN, COL_POB, "valor"]].copy()
        tabla = tabla.sort_values(COL_POB, ascending=False).reset_index(drop=True)
        tabla.columns = ["Municipio", "Población", legend_name]
    st.dataframe(tabla, use_container_width=True, height=350)