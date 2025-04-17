import numpy as np
import xarray as xr


def get_point_index(lat_array, lon_array, selected_lat, selected_lon):
    """
    Encuentra el índice más cercano para una coordenada lat/lon.
    """
    lat_idx = np.abs(lat_array - selected_lat).argmin()
    lon_idx = np.abs(lon_array - selected_lon).argmin()
    return lat_idx, lon_idx


def extract_point_timeseries(dataset: xr.DataArray, lat: float, lon: float) -> xr.DataArray:
    """
    Extrae una serie temporal para un punto dado (lat, lon).
    """
    lat_idx, lon_idx = get_point_index(dataset.lat.values, dataset.lon.values, lat, lon)
    return dataset.isel(lat=lat_idx, lon=lon_idx)


def extract_region_timeseries(dataset: xr.DataArray, lat_min: float, lat_max: float,
                               lon_min: float, lon_max: float, method: str = "mean") -> xr.DataArray:
    """
    Extrae una serie temporal para una región definida por un rectángulo.
    Aplica el método de agregación especificado ("mean", "sum", etc).
    """
    ds_region = dataset.sel(
        lat=slice(lat_max, lat_min),  # invertir si latitudes decrecen
        lon=slice(lon_min, lon_max)
    )

    if method == "mean":
        return ds_region.mean(dim=["lat", "lon"])
    elif method == "sum":
        return ds_region.sum(dim=["lat", "lon"])
    else:
        raise ValueError(f"Unsupported aggregation method: {method}")
