import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import xarray as xr

def plot_spatial_map(data: xr.DataArray, title: str = "Spatial Map", color_scale: str = "Viridis"):
    """
    Generates an interactive spatial map using Plotly.

    Parameters:
        data (xr.DataArray): 2D DataArray with spatial data (latitude, longitude).
        title (str): Title of the map.
        color_scale (str): Color scale for the map (default: "Viridis").

    Returns:
        fig (plotly.graph_objects.Figure): Plotly figure object.
    """
    fig = px.imshow(
        data,
        labels={"x": "Longitude", "y": "Latitude", "color": data.name},
        color_continuous_scale=color_scale,
        title=title,
    )
    fig.update_layout(
        coloraxis_colorbar=dict(title=data.name),
        xaxis_title="Longitude",
        yaxis_title="Latitude",
    )
    return fig


def plot_time_series(data: pd.DataFrame, title: str = "Time Series", y_label: str = "Value"):
    """
    Generates an interactive time series plot using Plotly.

    Parameters:
        data (pd.DataFrame): DataFrame with time series data. Columns should include 'date' and one or more indices.
        title (str): Title of the plot.
        y_label (str): Label for the y-axis.

    Returns:
        fig (plotly.graph_objects.Figure): Plotly figure object.
    """
    fig = go.Figure()
    for column in data.columns:
        if column != "date":
            fig.add_trace(
                go.Scatter(
                    x=data["date"],
                    y=data[column],
                    mode="lines",
                    name=column,
                )
            )
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=y_label,
        legend_title="Indices",
    )
    return fig