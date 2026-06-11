import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.data_loader import load_poblacion

st.set_page_config(page_title="Gráficas · Castellón", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');
h1,h2,h3 { font-family: 'Inter', sans-serif; font-weight: 600; letter-spacing: -0.5px; }
body, p, div { font-family: 'DM Sans', sans-serif; font-weight: 400; }
section[data-testid="stSidebar"] { background: #1a1a2e; }
section[data-testid="stSidebar"] * { color: white !important; }
</style>
""", unsafe_allow_html=True)

PALETTE = ["#e2b96f","#0f3460","#e94560","#16213e","#533483",
           "#2ec4b6","#f4a261","#a8dadc","#457b9d","#1d3557"]

MUNICIPIOS_DEFAULT = ["Llucena", "Vilafamés", "Vistabella del Maestrat", "Cinctorres"]

st.markdown("# Análisis Demográfico")
st.markdown("Evolución, comparativas y tendencias de la población en la provincia de Castellón.")

# cargar datos
df = load_poblacion()
COL_MUN = "municipio"
COL_ANY = "año"
COL_POB = "total"

years      = sorted(df[COL_ANY].unique().astype(int))
municipios = sorted(df[COL_MUN].unique().tolist())

defaults_validos = [m for m in MUNICIPIOS_DEFAULT if m in municipios]
if len(defaults_validos) < len(MUNICIPIOS_DEFAULT):
    for d in MUNICIPIOS_DEFAULT:
        if d not in defaults_validos:
            match = next((m for m in municipios if d.lower() in m.lower()), None)
            if match and match not in defaults_validos:
                defaults_validos.append(match)

# menú de la izquierda
with st.sidebar:
    st.markdown("## Filtros")
    municipios_sel = st.multiselect(
        "Municipios",
        options=municipios,
        default=defaults_validos,
    )
    year_range = st.slider(
        "Rango de años",
        min_value=int(min(years)), max_value=int(max(years)),
        value=(int(min(years)), int(max(years))),
    )
    st.markdown("---")
    st.markdown("**Fuente:** INE · Diputació de Castelló")

df_f = df[(df[COL_ANY] >= year_range[0]) & (df[COL_ANY] <= year_range[1])].copy()

# GRÁFICA 1: líneas de evolución temporal
st.markdown("## Evolución temporal de la población")
if municipios_sel:
    df_evol = df_f[df_f[COL_MUN].isin(municipios_sel)].sort_values(COL_ANY)
    ultimo_anio = df_evol[COL_ANY].max()
    orden = (df_evol[df_evol[COL_ANY] == ultimo_anio]
             .sort_values(COL_POB, ascending=False)[COL_MUN].tolist())
    resto = [m for m in municipios_sel if m not in orden]
    orden_final = orden + resto

    fig1 = px.line(
        df_evol, x=COL_ANY, y=COL_POB, color=COL_MUN,
        markers=True, color_discrete_sequence=PALETTE,
        labels={COL_ANY:"Año", COL_POB:"Población", COL_MUN:"Municipio"},
        title=f"Evolución de la población ({year_range[0]}–{year_range[1]})",
        category_orders={COL_MUN: orden_final},
    )
    fig1.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Source Sans 3", title_font_family="Playfair Display",
        title_font_size=18, hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    fig1.update_traces(line_width=2.5, marker_size=6)
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("Selecciona al menos un municipio en el panel lateral.")

# GRÁFICA 2: datos desglosados por sexo
st.markdown("## Desglose por sexo")
if municipios_sel and "hombres" in df.columns:
    year_sexo = st.select_slider(
        "Año para el desglose por sexo",
        options=years, value=years[-1], key="year_sexo"
    )
    df_sexo = df[(df[COL_ANY] == year_sexo) & (df[COL_MUN].isin(municipios_sel))][
        [COL_MUN, "hombres", "mujeres"]].dropna()
    df_sexo_long = df_sexo.melt(
        id_vars=COL_MUN, value_vars=["hombres", "mujeres"],
        var_name="Sexo", value_name="Población"
    )
    fig2 = px.bar(
        df_sexo_long, x=COL_MUN, y="Población", color="Sexo", barmode="group",
        color_discrete_map={"hombres": "#0f3460", "mujeres": "#e2b96f"},
        labels={COL_MUN: "Municipio"},
        title=f"Población por sexo en {year_sexo}",
    )
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font_family="Source Sans 3", title_font_family="Playfair Display",
        title_font_size=18,
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Selecciona municipios en el panel lateral para ver el desglose por sexo.")

st.markdown("---")

# GRÁFICA 3: barras con top N municipios más/menos poblados
st.markdown("## Ranking de municipios por población")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 2, 1])
with col_ctrl1:
    top_n = st.slider("Número de municipios", min_value=5, max_value=20, value=10, key="top_n")
with col_ctrl2:
    year_top = st.select_slider(
        "Año para el ranking", options=years, value=years[-1], key="year_top"
    )
with col_ctrl3:
    orden_ranking = st.radio(
        "Ordenar por",
        options=["Mayor población", "Menor población"],
        key="orden_ranking"
    )

df_ranking = df[df[COL_ANY] == year_top]
if orden_ranking == "Mayor población":
    df_ranking = df_ranking.nlargest(top_n, COL_POB)
    color_scale = ["#16213e", "#e2b96f"]
    titulo_ranking = f"Top {top_n} municipios más poblados ({year_top})"
else:
    df_ranking = df_ranking.nsmallest(top_n, COL_POB)
    color_scale = ["#e2b96f", "#16213e"]
    titulo_ranking = f"Top {top_n} municipios menos poblados ({year_top})"

fig3 = px.bar(
    df_ranking.sort_values(COL_POB, ascending=(orden_ranking == "Mayor población")),
    x=COL_POB, y=COL_MUN, orientation="h",
    color=COL_POB, color_continuous_scale=color_scale,
    labels={COL_POB: "Población", COL_MUN: "Municipio"},
    title=titulo_ranking, text=COL_POB,
)
fig3.update_traces(texttemplate="%{text:,.0f}", textposition="outside", marker_line_width=0)
fig3.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="Source Sans 3", title_font_family="Playfair Display",
    title_font_size=18, coloraxis_showscale=False,
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(showgrid=False), margin=dict(l=10, r=90),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# GRÁFICA 4: municipios con más variación positiva y negativa
st.markdown(f"## Cambio de población entre {year_range[0]} y {year_range[1]}")
df_ini = df[df[COL_ANY]==year_range[0]][[COL_MUN,COL_POB]].rename(columns={COL_POB:"pob_ini"})
df_fin = df[df[COL_ANY]==year_range[1]][[COL_MUN,COL_POB]].rename(columns={COL_POB:"pob_fin"})
df_cambio = df_ini.merge(df_fin, on=COL_MUN, how="inner").dropna()
df_cambio["cambio_pct"] = ((df_cambio["pob_fin"] - df_cambio["pob_ini"]) / df_cambio["pob_ini"] * 100).round(1)

n_show = min(top_n // 2, 8)
df_ext = pd.concat([
    df_cambio.nlargest(n_show, "cambio_pct"),
    df_cambio.nsmallest(n_show, "cambio_pct")
]).drop_duplicates().sort_values("cambio_pct")
df_ext["color"] = df_ext["cambio_pct"].apply(lambda x: "#2ec4b6" if x >= 0 else "#e94560")

fig4 = go.Figure(go.Bar(
    x=df_ext["cambio_pct"], y=df_ext[COL_MUN], orientation="h",
    marker_color=df_ext["color"].tolist(),
    text=df_ext["cambio_pct"].apply(lambda x: f"{x:+.1f}%"),
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Variación: %{x:.1f}%<extra></extra>",
))
fig4.add_vline(x=0, line_width=1.5, line_color="#333")
fig4.update_layout(
    title=f"Municipios con mayor crecimiento y pérdida<br><sup>{year_range[0]} → {year_range[1]}</sup>",
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="Source Sans 3", title_font_family="Playfair Display",
    title_font_size=18, height=500,
    xaxis=dict(title="Variación (%)", showgrid=True, gridcolor="#f0f0f0"),
    yaxis=dict(showgrid=False), margin=dict(l=10, r=80),
)
st.plotly_chart(fig4, use_container_width=True)

# GRÁFICA 5: heatmap de variación por municipio
st.markdown("## Heatmap de variacion anual por municipio")
st.markdown("Cada celda muestra la variacion de poblacion respecto al año anterior. Rojo = perdida, verde = crecimiento.")

col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    n_mun_heat = st.slider(
        "Numero de municipios a mostrar",
        min_value=10, max_value=50, value=25, step=5, key="n_mun_heat"
    )
with col_h2:
    criterio_heat = st.radio(
        "Seleccionar municipios por",
        options=["Mas poblados", "Mas variacion"],
        key="criterio_heat"
    )

# calcular variacion anual
df_sorted = df.sort_values(["municipio", "año"])
df_sorted["variacion"] = df_sorted.groupby("municipio")["total"].pct_change() * 100
df_sorted["variacion"] = df_sorted["variacion"].round(1)

df_heat = df_sorted[
    (df_sorted[COL_ANY] >= year_range[0]) &
    (df_sorted[COL_ANY] <= year_range[1])
].dropna(subset=["variacion"])

if criterio_heat == "Mas poblados":
    top_muns = (df[df[COL_ANY] == year_range[1]]
                .nlargest(n_mun_heat, COL_POB)[COL_MUN].tolist())
else:
    top_muns = (df_heat.groupby(COL_MUN)["variacion"]
                .apply(lambda x: x.abs().mean())
                .nlargest(n_mun_heat).index.tolist())

df_heat_fil = df_heat[df_heat[COL_MUN].isin(top_muns)].copy()

pivot = df_heat_fil.pivot_table(
    index=COL_MUN, columns=COL_ANY, values="variacion", aggfunc="first"
)

orden_muns = (df[df[COL_MUN].isin(top_muns)]
              .groupby(COL_MUN)[COL_POB].mean()
              .sort_values(ascending=True).index.tolist())
pivot = pivot.reindex(orden_muns)

fig5 = go.Figure(go.Heatmap(
    z=pivot.values,
    x=[str(c) for c in pivot.columns],
    y=pivot.index.tolist(),
    colorscale="RdYlGn",
    zmid=0,
    zmin=-15,
    zmax=15,
    colorbar=dict(title="Variacion (%)"),
    hovertemplate="<b>%{y}</b><br>Año: %{x}<br>Variacion: %{z:.1f}%<extra></extra>",
))

fig5.update_layout(
    title="Variacion anual de poblacion por municipio",
    plot_bgcolor="white", paper_bgcolor="white",
    font_family="Source Sans 3",
    title_font_family="Playfair Display",
    title_font_size=18,
    height=max(400, n_mun_heat * 22),
    xaxis=dict(title="Año", tickangle=-45),
    yaxis=dict(title="", tickfont=dict(size=11)),
    margin=dict(l=150, r=20, t=60, b=60),
)

st.plotly_chart(fig5, use_container_width=True)