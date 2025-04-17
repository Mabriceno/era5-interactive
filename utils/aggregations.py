import xarray as xr
import pandas as pd

def aggregate_time(data: xr.DataArray, method: str = "mean", time_dim: str = "time") -> xr.DataArray:
    """
    Aggregates data over the time dimension using the specified method.

    Parameters:
        data (xr.DataArray): Input data to aggregate.
        method (str): Aggregation method ('mean', 'sum', 'max', 'min').
        time_dim (str): Name of the time dimension (default: 'time').

    Returns:
        xr.DataArray: Aggregated data.
    """
    if time_dim not in data.dims:
        raise ValueError(f"Time dimension '{time_dim}' not found in the data.")

    if method == "mean":
        return data.mean(dim=time_dim)
    elif method == "sum":
        return data.sum(dim=time_dim)
    elif method == "max":
        return data.max(dim=time_dim)
    elif method == "min":
        return data.min(dim=time_dim)
    else:
        raise ValueError(f"Unsupported aggregation method: {method}")


def aggregate_space(data: xr.DataArray, region_mask: xr.DataArray) -> xr.DataArray:
    """
    Aggregates data over a spatial region defined by a mask.

    Parameters:
        data (xr.DataArray): Input data to aggregate.
        region_mask (xr.DataArray): Boolean mask defining the region (True for included points).

    Returns:
        xr.DataArray: Aggregated data over the region.
    """
    if data.shape != region_mask.shape:
        raise ValueError("Data and region mask must have the same shape.")

    masked_data = data.where(region_mask)
    return masked_data.mean(dim=["latitude", "longitude"], skipna=True)


def aggregate_to_dataframe(data: xr.DataArray, time_dim: str = "valid_time") -> pd.DataFrame:
    """
    Converts aggregated data into a Pandas DataFrame for export or plotting.

    Parameters:
        data (xr.DataArray): Aggregated data.
        time_dim (str): Name of the time dimension (default: 'time').

    Returns:
        pd.DataFrame: DataFrame with time as index and values as columns.
    """
    if time_dim not in data.dims:
        raise ValueError(f"Time dimension '{time_dim}' not found in the data.")

    df = data.to_dataframe().reset_index()
    return df.pivot(index=time_dim, columns=data.name, values=data.name)