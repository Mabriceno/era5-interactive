import streamlit as st
from datetime import date
import pandas as pd

from utils.cache import cache_data

# Diccionario de variables visualizables
ERA5_VARIABLES = {
    "Temperatura a 2 m (sst)": "sst",
    "Presión a nivel del mar (msl)": "msl",
    "Precipitación total (tp)": "tp",
}

def render_sidebar(ds):
    """Dibuja controles y devuelve un diccionario con la selección del usuario."""
    st.sidebar.title("🌍 ERA5 Explorer")
    st.sidebar.markdown("Configure la visualización de datos.")

    # 1️⃣ Variable
    available_labels = [lbl for lbl, var in ERA5_VARIABLES.items() if var in ds.data_vars]
    if not available_labels:
        st.sidebar.error("Ninguna variable del diccionario está en el archivo NetCDF.")
        st.stop()

    label = st.sidebar.selectbox("Variable", available_labels, key="var_select")
    var_name = ERA5_VARIABLES[label]

    # 2️⃣ Fechas
    time_index = pd.to_datetime(ds[var_name].valid_time.values)
    unique_dates = sorted({t.date() for t in time_index})
    start_date = st.sidebar.date_input(
        "Fecha de inicio",
        min_value=min(unique_dates),
        max_value=max(unique_dates),
        value=min(unique_dates),
        key="start_date",
    )
    end_date = st.sidebar.date_input(
        "Fecha de fin",
        min_value=min(unique_dates),
        max_value=max(unique_dates),
        value=max(unique_dates),
        key="end_date",
    )
    if start_date > end_date:
        st.sidebar.error("La fecha de fin no puede ser anterior a la de inicio.")
        st.stop()

    # 3️⃣ Agregación temporal
    agg = st.sidebar.selectbox(
        "Agregación",
        ["Último paso", "Promedio", "Suma"],
        key="agg_method",
    )

    return {
        "label": label,
        "var": var_name,
        "start_date": start_date,
        "end_date": end_date,
        "agg": agg,
    }
