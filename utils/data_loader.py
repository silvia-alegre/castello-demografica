import re
import os
import streamlit as st
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "2865.csv")
CODIGO_PROVINCIAL = "12"

def _arreglar_nombre(nombre: str) -> str:
    m = re.match(r"^(.+),\s+(el|la|los|las|els|les|l'|l´)$", nombre, re.IGNORECASE)
    if m:
        base, art = m.group(1).strip(), m.group(2).strip()
        if art.lower() in ("l'", "l´"):
            return f"L'{base}"
        return f"{art.capitalize()} {base}"
    if "/" in nombre:
        return nombre.split("/")[0].strip()
    return nombre


@st.cache_data(show_spinner="Cargando datos de población...")
def load_poblacion() -> pd.DataFrame:
    try:
        df = pd.read_csv(CSV_PATH, sep=";", encoding="latin-1",
                         thousands=".", decimal=",")
    except FileNotFoundError:
        st.error(f"Datos no encontrados")
        st.stop()

    df.columns = [c.strip() for c in df.columns]

    # extraer código INE
    df["_codigo"] = df["Municipios"].astype(str).str.extract(r"^(\d+)\s+")[0]
    df = df[df["_codigo"] != CODIGO_PROVINCIAL].copy()

    # limpieza de nombres de municipios
    df["municipio"] = (
        df["Municipios"]
        .astype(str)
        .str.replace(r"^\d+\s+", "", regex=True)
        .str.strip()
        .apply(_arreglar_nombre)
    )

    # cambios de formatos de variables
    df["Total"] = pd.to_numeric(df["Total"], errors="coerce")
    df["Periodo"] = pd.to_numeric(df["Periodo"], errors="coerce").astype("Int64")

    # separar por sexos y crear dataset final
    df_total   = df[df["Sexo"] == "Total"  ][["municipio", "Periodo", "Total"]].rename(columns={"Total": "total",   "Periodo": "año"})
    df_hombres = df[df["Sexo"] == "Hombres"][["municipio", "Periodo", "Total"]].rename(columns={"Total": "hombres", "Periodo": "año"})
    df_mujeres = df[df["Sexo"] == "Mujeres"][["municipio", "Periodo", "Total"]].rename(columns={"Total": "mujeres", "Periodo": "año"})

    resultado = (
        df_total
        .merge(df_hombres, on=["municipio", "año"], how="left")
        .merge(df_mujeres,  on=["municipio", "año"], how="left")
    )

    resultado = resultado.dropna(subset=["total"])
    resultado = resultado.sort_values(["municipio", "año"]).reset_index(drop=True)
    return resultado[["municipio", "año", "total", "hombres", "mujeres"]]