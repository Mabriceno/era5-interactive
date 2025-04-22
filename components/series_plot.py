import plotly.graph_objects as go
import pandas as pd



def plot_time_series(da: pd.Series, units=""):
    """
    Crea un gráfico de series temporales usando plotly.
    
    Args:
        da: xarray DataArray con dimensión temporal
        units: unidades de la variable para mostrar en el eje y
    """

    
    # Creamos la figura
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=da.index,
            y=da.values,
            mode='lines',
            name='Promedio espacial',
            line=dict(color='#1f77b4', width=2)
        )
    )
    
    # Configuramos el layout
    fig.update_layout(
        title=f"Serie temporal - Promedio espacial",
        xaxis_title="Tiempo",
        yaxis_title=f"Valor ({units})",
        showlegend=True,
        template="plotly_white",
        height=400
    )
    
    return fig