import streamlit as st

ROADMAP_MD = """
- **Selección espacial:** clic o dibujo de polígonos para extraer datos.
- **Series temporales e índices:** cálculo instantáneo y overlay de varias curvas.
- **Descarga CSV:** datos filtrados o agregados con un clic.
- **Personalización avanzada:** paletas de color, más proyecciones, umbrales.
- **Soporte de datasets grandes:** integración con Dask, chunking adaptativo.
"""

def render_roadmap():
    st.divider()
    with st.expander("Próximos pasos y funcionalidades futuras"):
        st.markdown(ROADMAP_MD)