
import plotly.graph_objects as go
import pandas as pd



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