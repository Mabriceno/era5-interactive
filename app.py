import streamlit as st
import pandas as pd

from utils.data_loader import load_era5_data, preprocess_era5_data
from utils.aggregations import aggregate_time
from components.map_plot import plot_spatial_map


import streamlit as st
import pandas as pd
import xarray as xr # Asegúrate de importar xarray si no lo hacías en utils
from datetime import date # Necesario para st.date_input



# --- Configuración de la Página ---
st.set_page_config(
    page_title="ERA5 Climate Explorer",
    page_icon="🌍", # Puedes usar emojis como iconos
    layout="wide",  # Mantenemos el layout ancho para el mapa
    initial_sidebar_state="expanded" # Sidebar abierta por defecto
)

# --- Estilo CSS Opcional (para un look más "pro") ---
# st.markdown("""
# <style>
#     /* Puedes añadir CSS aquí para personalizar más */
#     .stSidebar {
#         background-color: #f0f2f6; /* Un gris claro para el sidebar */
#     }
#     .stButton>button {
#         /* Estilo para botones */
#         border-radius: 5px;
#     }
#     /* Más estilos... */
# </style>
# """, unsafe_allow_html=True)

# --- Sidebar: Controles Principales ---
st.sidebar.title("🌍 ERA5 Explorer")
st.sidebar.markdown("Configure la visualización de datos.")

# --- Sección de Selección de Variable ---
st.sidebar.subheader("1. Selección de Variable")

# MODIFICADO: Corregido el diccionario para tener sentido (asume estas variables existen en tu .nc)
# Si solo tienes 'sst', deberías ajustar esto o tu archivo .nc
era5_variables = {
    "Temperatura a 2m (sst)": "sst", # Asumiendo que 'sst' es tu variable interna para temp.
    "Presión Nivel del Mar (msl)": "msl", # Asumiendo que tienes 'msl'
    "Precipitación Total (tp)": "tp"      # Asumiendo que tienes 'tp'
}
# NOTA: Los valores ('sst', 'msl', 'tp') DEBEN coincidir con los nombres de las variables DENTRO de tu archivo netCDF.
#       Si tu archivo solo tiene 'sst', las otras opciones darán error al cargar.

# Asegúrate de que las claves del diccionario (los textos) sean únicas.
# Los valores ('sst') son los que usas para acceder a los datos en el xarray Dataset.
# selected_label = st.sidebar.selectbox("Variable", list(era5_variables.keys()), key="var_select")
# selected_var = era5_variables[selected_label] # Nombre interno de la variable

# --- Carga de Datos ---
data_path = "data/era5_subset.nc" # Asegúrate que la ruta sea correcta

@st.cache_data # Cache para eficiencia
def load_and_preprocess_data(file_path):
    """Carga y preprocesa todo el dataset una vez."""
    try:
        ds = load_era5_data(file_path)
        # Preprocesa todas las variables disponibles que definiste
        processed_das = {}
        available_vars_in_file = list(ds.data_vars)
        for label, var_name in era5_variables.items():
             if var_name in available_vars_in_file:
                 processed_das[var_name] = preprocess_era5_data(ds, var_name)
             else:
                 st.warning(f"Variable '{var_name}' (etiqueta: '{label}') no encontrada en {file_path}. Omitiendo.")
        if not processed_das:
             raise ValueError("No se encontraron variables válidas en el archivo NetCDF según la configuración.")
        return processed_das
    except FileNotFoundError:
        st.error(f"Error: Archivo no encontrado en '{file_path}'. Verifica la ruta.")
        st.stop()
    except Exception as e:
        st.error(f"Error al cargar o preprocesar datos: {e}")
        st.stop()

# Carga todos los DataArrays procesados
all_processed_data = load_and_preprocess_data(data_path)

# Ahora el usuario selecciona cuál de los cargados visualizar
available_labels = [label for label, var_name in era5_variables.items() if var_name in all_processed_data]
if not available_labels:
    st.error("No hay variables disponibles para mostrar según la configuración y el archivo.")
    st.stop()

selected_label = st.sidebar.selectbox("Variable", available_labels, key="var_select")
selected_var = era5_variables[selected_label] # Nombre interno de la variable

# Obtiene el DataArray seleccionado ya preprocesado
da = all_processed_data[selected_var]

# --- Sección de Selección Temporal ---
st.sidebar.subheader("2. Selección Temporal")

# Extraer fechas únicas disponibles
time_coords = pd.to_datetime(da.valid_time.values)
unique_dates = sorted(list(set(t.date() for t in time_coords)))

# Convertir fechas a formato date para date_input
min_date = min(unique_dates)
max_date = max(unique_dates)

# MODIFICADO: Usar st.date_input para una mejor UX
start_date_dt = st.sidebar.date_input("Fecha de Inicio", min_value=min_date, max_value=max_date, value=min_date, key="start_date")
end_date_dt = st.sidebar.date_input("Fecha de Fin", min_value=min_date, max_value=max_date, value=max_date, key="end_date")

# Validar que la fecha de fin no sea anterior a la de inicio
if start_date_dt > end_date_dt:
    st.sidebar.error("La fecha de fin no puede ser anterior a la fecha de inicio.")
    st.stop()

# Filtrar el DataArray por el rango de fechas seleccionado
# Asegúrate de que la comparación funcione con las fechas/timestamps
da_selected = da.sel(valid_time=slice(str(start_date_dt), str(end_date_dt)))

if da_selected.valid_time.size == 0:
    st.warning("No hay datos para el rango de fechas seleccionado.")
    st.stop()


# --- Sección de Agregación ---
st.sidebar.subheader("3. Agregación Temporal")
aggregation_method = st.sidebar.selectbox(
    "Método de Agregación",
    ["Último Paso de Tiempo", "Promedio (Mean)", "Suma (Sum)"], # Opción "None" renombrada para claridad
    key="agg_method"
)

# Aplicar agregación
# MODIFICADO: Lógica más clara
if aggregation_method == "Promedio (Mean)":
    da_agg = aggregate_time(da_selected, method="mean", time_dim="valid_time")
    agg_label = "Promedio"
elif aggregation_method == "Suma (Sum)":
    # Advertencia si la suma no tiene sentido físico para la variable
    if selected_var in ['sst', 'msl']: # Temperaturas o presiones no suelen sumarse
         st.sidebar.warning(f"La 'Suma' puede no ser físicamente significativa para {selected_label}.")
    da_agg = aggregate_time(da_selected, method="sum", time_dim="valid_time")
    agg_label = "Suma"
else: # "Último Paso de Tiempo"
    # Selecciona el último paso temporal del rango filtrado
    da_agg = da_selected.isel(valid_time=-1)
    # Intenta obtener la fecha específica para el título
    last_time = pd.to_datetime(da_agg.valid_time.values)
    agg_label = f"al {last_time.strftime('%Y-%m-%d %H:%M')}"


# --- Área Principal: Visualización ---
st.title(f"Visor de Datos Climáticos ERA5")
st.markdown(f"Mostrando: **{selected_label}**") # Indica claramente qué se está viendo

# Añadir un subtítulo dinámico
if aggregation_method == "Último Paso de Tiempo":
     st.subheader(f"Mapa para el {agg_label}")
else:
     st.subheader(f"Mapa Agregado ({agg_label}) entre {start_date_dt.strftime('%Y-%m-%d')} y {end_date_dt.strftime('%Y-%m-%d')}")


# --- Plot Map ---
try:
    # MODIFICADO: Título del gráfico más descriptivo y usa la unidad del DataArray
    plot_title = f"{selected_label} ({da.attrs.get('units', '')})"
    if aggregation_method != "Último Paso de Tiempo":
        plot_title += f" - {agg_label} ({start_date_dt.strftime('%Y-%m-%d')} a {end_date_dt.strftime('%Y-%m-%d')})"
    else:
        plot_title += f" - {agg_label}"

    fig = plot_spatial_map(
        da_agg,
        title=plot_title,
        projection="robinson", # O la proyección que prefieras
        color_scale="Spectral_r" # Ejemplo: Invertida, a menudo mejor para temperatura
    )

    # Mostrar el gráfico de Plotly
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error al generar el mapa: {e}")
    # Proporcionar más detalles si es posible, ej. si da_agg está vacío
    st.error(f"DataArray agregado para graficar (primeros valores):\n{da_agg[:5] if da_agg.size > 0 else 'Vacío'}")


# --- Métricas Clave (Opcional, pero da look de "dashboard") ---
st.divider() # Separador visual
st.subheader("Métricas Resumen del Periodo Seleccionado")

try:
    col1, col2, col3 = st.columns(3)
    # Calcula métricas sobre da_selected (antes de la agregación final para el mapa)
    mean_val = float(da_selected.mean())
    min_val = float(da_selected.min())
    max_val = float(da_selected.max())
    units = da.attrs.get('units', '')

    col1.metric(label=f"Promedio ({units})", value=f"{mean_val:.2f}")
    col2.metric(label=f"Mínimo ({units})", value=f"{min_val:.2f}")
    col3.metric(label=f"Máximo ({units})", value=f"{max_val:.2f}")
except Exception as e:
    st.warning(f"No se pudieron calcular las métricas resumen: {e}")


# --- Sección de Próximos Pasos (en un Expander) ---
st.divider()
with st.expander("Próximos Pasos y Funcionalidades Futuras"):
    st.markdown("""
    - **Selección Espacial:** Permitir hacer clic en el mapa o dibujar un área para extraer datos de puntos o regiones.
    - **Generación de Índices y Series Temporales:** Calcular y visualizar series de tiempo para las selecciones espaciales.
    - **Comparación de Series:** Graficar múltiples índices/series en el mismo gráfico interactivo.
    - **Opción de Exportación:** Botón para descargar los datos generados (índices, series) como CSV.
    - **Personalización Avanzada:** Más opciones de mapas (proyecciones, paletas de color), configuración de umbrales, etc.
    - **Manejo de Datos Más Grandes:** Estrategias para trabajar con datasets ERA5 más completos sin exceder límites de memoria/tiempo (e.g., Dask).
    """)

# --- Footer Opcional ---
st.sidebar.markdown("---")
st.sidebar.info("Aplicación desarrollada con Streamlit, Xarray y Plotly.")