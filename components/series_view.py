import streamlit as st
from .series_plot import plot_time_series

def render_series(da, units=""):
    """
    Renderiza un expander con el gráfico de series temporales.
    
    Args:
        da: xarray DataArray con la variable seleccionada
        units: unidades de la variable
    """
    with st.expander("Ver serie temporal", expanded=False):
        fig = plot_time_series(da, units)
        st.plotly_chart(fig, use_container_width=True)