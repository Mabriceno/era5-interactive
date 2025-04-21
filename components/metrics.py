import streamlit as st

def render_metrics(da, units):
    mean_val = float(da.mean())
    min_val = float(da.min())
    max_val = float(da.max())

    col1, col2, col3 = st.columns(3)
    col1.metric(f"Promedio ({units})", f"{mean_val:.2f}")
    col2.metric(f"Mínimo ({units})", f"{min_val:.2f}")
    col3.metric(f"Máximo ({units})", f"{max_val:.2f}")