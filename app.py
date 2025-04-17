import streamlit as st
import xarray as xr
import pandas as pd

import sys
import os
#sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import plotly.express as px


from utils.data_loader import load_era5_data, preprocess_era5_data
from utils.aggregations import aggregate_time
from utils.visualizations import plot_spatial_map

# --- Config ---
st.set_page_config(layout="wide")

# --- Sidebar: Variable and Temporal Selection ---
st.sidebar.title("ERA5 Explorer")
st.sidebar.markdown("Select a variable and time range")

# Load variable configuration
era5_variables = {
    "2m Temperature": "sst",
    "Mean Sea Level Pressure": "sst",
    "Total Precipitation": "sst"
}

selected_label = st.sidebar.selectbox("Variable", list(era5_variables.keys()))
selected_var = era5_variables[selected_label]

data_path = "data/era5_subset.nc"

# --- Load Data ---
@st.cache_data
def load_and_preprocess_data(file_path, variable):
    ds = load_era5_data(file_path)
    print(ds)
    if variable not in ds:
        raise ValueError(f"Variable '{variable}' not found in dataset.")
    da = preprocess_era5_data(ds, variable)
    return da

try:
    da = load_and_preprocess_data(data_path, selected_var)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Temporal Controls ---
time = pd.to_datetime(da.valid_time.values)
st.sidebar.markdown("---")
st.sidebar.markdown("Select a date or range")

aggregation_method = st.sidebar.selectbox("Aggregation method", ["None", "Mean", "Sum"])

date_options = [str(t.date()) for t in time]
start_date = st.sidebar.selectbox("Start date", date_options, index=0)
end_date = st.sidebar.selectbox("End date", date_options, index=len(date_options) - 1)

# Filter time
start_idx = time.get_loc(pd.to_datetime(start_date))
end_idx = time.get_loc(pd.to_datetime(end_date)) + 1
da_selected = da.isel(valid_time=slice(start_idx, end_idx))

# Apply aggregation
if aggregation_method == "Mean":
    da_agg = aggregate_time(da_selected, method="mean", time_dim="valid_time")
elif aggregation_method == "Sum":
    da_agg = aggregate_time(da_selected, method="sum", time_dim="valid_time")
else:
    da_agg = da_selected[-1]  # Show most recent frame

# --- Plot Map ---
st.title(f"{selected_label} - ERA5 Map Viewer")
try:
    fig = plot_spatial_map(da_agg, title=f"{selected_label} ({aggregation_method})")
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error generating plot: {e}")

# --- Placeholder for next steps ---
st.markdown("### Next steps")
st.markdown("- Add spatial selection\n- Add index generation and time series\n- Add CSV export option")