import streamlit as st
from components.map_plot import plot_spatial_map  # ya existente

def render_map(da, title):
    """Genera la figura y la muestra ocupando todo el ancho disponible."""
    fig = plot_spatial_map(
        da,
        title=title,
        projection="robinson",
        color_scale="Spectral_r",
    )
    st.plotly_chart(fig, use_container_width=True)