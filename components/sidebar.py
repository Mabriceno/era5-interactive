import streamlit as st
from datetime import date
import pandas as pd
from typing import Dict, Any

from database.db_utils import get_available_datasets
from utils.cache import cache_data

@cache_data
def get_datasets_cache():
    """Cache the datasets to avoid multiple database calls"""
    return get_available_datasets()

def get_default_selection():
    """Returns the default selection for first load"""
    available_datasets = get_datasets_cache()
    if not available_datasets:
        return None
    
    # Get first available source
    first_source = next(iter({(d.source_id, d.source_name) for d in available_datasets}))
    
    # Get first variable for that source
    first_var = next(
        (d for d in available_datasets if d.source_id == first_source[0]), 
        None
    )
    
    if not first_var:
        return None

    # Default dates
    start_date = pd.to_datetime("1979-01-01").date()
    end_date = pd.to_datetime("2024-12-31").date()

    return {
        "source_id": first_source[0],
        "source_name": first_source[1],
        "var_id": first_var.variable_id,
        "var_name": first_var.variable_name,
        "var_key": first_var.variable_key,
        "label": first_var.long_name,
        "unit": first_var.unit,
        "start_date": start_date,
        "end_date": end_date,
        "agg": "mean",
    }

def render_sidebar() -> Dict[str, Any]:
    """Renders the sidebar controls and returns user selection."""
    st.sidebar.title("🌍 ERA5 Explorer")
    st.sidebar.markdown("Configure la visualización de datos.")

    # Get available datasets from database
    available_datasets = get_datasets_cache()
    
    if not available_datasets:
        st.sidebar.error("No hay datasets disponibles en la base de datos.")
        st.stop()

    # Get default selection for first load
    default_selection = get_default_selection()
    if not default_selection:
        st.sidebar.error("No se pudo obtener una selección por defecto.")
        st.stop()

    # 1️⃣ Source Selection
    unique_sources = list({(d.source_id, d.source_name) for d in available_datasets})
    default_source_index = next(
        (i for i, s in enumerate(unique_sources) if s[0] == default_selection["source_id"]), 
        0
    )
    
    source_id, source_name = st.sidebar.selectbox(
        "Fuente de datos",
        unique_sources,
        format_func=lambda x: x[1],
        key="source_select",
        index=default_source_index
    )

    # 2️⃣ Variable Selection
    variables_for_source = [
        (d.variable_id, d.variable_name, d.long_name, d.unit, d.variable_key) 
        for d in available_datasets 
        if d.source_id == source_id
    ]
    
    default_var_index = next(
        (i for i, v in enumerate(variables_for_source) if v[0] == default_selection["var_id"]), 
        0
    )
    
    selected_var = st.sidebar.selectbox(
        "Variable",
        variables_for_source,
        format_func=lambda x: f"{x[2]} ({x[1]})",
        key="var_select",
        index=default_var_index
    )
    var_id, var_name, long_name, unit, var_key = selected_var

    # 3️⃣ Date Range 1979-01-01 - 2024-12-31
    start_date, end_date = pd.to_datetime("1979-01-01"), pd.to_datetime("2024-12-31")

    selected_start = st.sidebar.date_input(
        "Fecha de inicio",
        min_value=start_date.date(),
        max_value=end_date.date(),
        value=default_selection["start_date"],
        key="start_date",
    )
    
    selected_end = st.sidebar.date_input(
        "Fecha de fin",
        min_value=start_date.date(),
        max_value=end_date.date(),
        value=default_selection["end_date"],
        key="end_date",
    )

    if selected_start > selected_end:
        st.sidebar.error("La fecha de fin no puede ser anterior a la de inicio.")
        st.stop()

    # 4️⃣ Aggregation Method
    agg = st.sidebar.selectbox(
        "Agregación",
        ["mean", "sum"],
        key="agg_method",
        index=0
    )

    # Return selection dictionary
    return {
        "source_id": source_id,
        "source_name": source_name,
        "var_id": var_id,
        "var_name": var_name,
        "var_key": var_key,
        "label": long_name,
        "unit": unit,
        "start_date": selected_start,
        "end_date": selected_end,
        "agg": agg,
    }
