import streamlit as st
from pathlib import Path

from utils.cache import cache_resource
from utils.data_loader import request_dataset, request_layer, request_series
from components.sidebar import render_sidebar
from components.map_view import render_map
from components.metrics import render_metrics
from components.series_view import render_series
from components.roadmap_expander import render_roadmap

st.set_page_config(
    page_title="ERA5 Climate Explorer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state for first load
if 'is_first_load' not in st.session_state:
    st.session_state.is_first_load = True


# ---------- 1. UI (sidebar) ----------
selection = render_sidebar()
print(f"Selection: {selection}")
# On first load, trigger a default request
if st.session_state.is_first_load:
    st.session_state.is_first_load = False
    st.session_state.update({
        'dataset': request_dataset(selection),
        'layer': None,
        'series': None
    })

# ---------- 2. Request dataset ----------
ds = st.session_state.get('dataset')
print(f"Dataset: {ds}")
if ds is None or selection != st.session_state.get('last_selection', {}):
    ds = request_dataset(selection)
    st.session_state.dataset = ds
    st.session_state.last_selection = selection.copy()

# ---------- 3. request layer and series ----------
layer = st.session_state.get('layer')
series = st.session_state.get('series')

if layer is None or selection != st.session_state.get('last_selection', {}):
    print(f"Requesting layer for selection: {selection}")
    layer = request_layer(ds, selection)
    print(f"Requesting series for selection: {selection}")
    series = request_series(ds, selection)
    st.session_state.layer = layer
    st.session_state.series = series

# ---------- 4. Visualización ----------
label = f"{selection['source_name']} - {selection['var_name']}"
title_suffix = f"{selection['start_date'].strftime('%Y-%m-%d')} - {selection['end_date'].strftime('%Y-%m-%d')}"

st.title("Visor de Datos Climáticos ERA5")
st.markdown(f"**{label}**")

title = f"{label} ({ds.attrs.get('units','')}) – {title_suffix}"
print(layer)
render_map(layer, title)


# ---------- 7. Series temporales ----------
st.divider()
render_series(series, series.attrs.get("units", ""))

# ---------- 8. Roadmap / footer ----------
render_roadmap()