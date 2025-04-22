import streamlit as st
from pathlib import Path

from utils.cache import cache_resource
from utils.data_loader import load_era5_data, preprocess_era5_data
from utils.aggregations import aggregate_time
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

DATA_PATH = Path("data/era5_subset.nc")  # ajusta la ruta si es necesario


# ---------- 1. Carga y preprocesamiento ----------
@cache_resource
def load_preprocess_all(path: Path):
    ds = load_era5_data(path)
    processed = {
        v: preprocess_era5_data(ds, v)
        for v in ds.data_vars
    }
    return processed

processed_data = load_preprocess_all(DATA_PATH)


# ---------- 2. UI (sidebar) ----------
selection = render_sidebar({v: da for v, da in processed_data.items()
                            if v == selection['var']} if 'selection' in locals() else processed_data)

label = selection["label"]
var   = selection["var"]
da    = processed_data[var]


# ---------- 3. Subset temporal ----------
da_sel = da.sel(valid_time=slice(str(selection["start_date"]),
                                 str(selection["end_date"])))
if da_sel.valid_time.size == 0:
    st.warning("No hay datos para el rango seleccionado.")
    st.stop()

# ---------- 4. Agregación ----------
agg = selection["agg"]
if agg == "Promedio":
    da_plot = aggregate_time(da_sel, "mean", time_dim="valid_time")
    title_suffix = "Promedio"
elif agg == "Suma":
    da_plot = aggregate_time(da_sel, "sum", time_dim="valid_time")
    title_suffix = "Suma"
else:  # Último paso
    da_plot = da_sel.isel(valid_time=-1)
    ts = str(da_plot.valid_time.values)
    title_suffix = f"al {ts[:16]}"

# ---------- 5. Visualización ----------
st.title("Visor de Datos Climáticos ERA5")
st.markdown(f"**{label}**")

title = f"{label} ({da.attrs.get('units','')}) – {title_suffix}"
render_map(da_plot, title)

# ---------- 6. Métricas resumen ----------
st.divider()
st.subheader("Métricas resumen")
render_metrics(da_sel, da.attrs.get("units", ""))

# ---------- 7. Series temporales ----------
st.divider()
render_series(da, da.attrs.get("units", ""))

# ---------- 8. Roadmap / footer ----------
render_roadmap()