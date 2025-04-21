import streamlit as st

# Carga pesada (datasets, modelos) – se mantiene viva toda la sesión
def cache_resource(func):
    return st.cache_resource(show_spinner=False)(func)

# Resultados de cómputo relativamente ligeros
def cache_data(func):
    return st.cache_data(show_spinner=False)(func)
