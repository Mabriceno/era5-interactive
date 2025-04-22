import xarray as xr
import pandas as pd

def get_aggregation_time(ds: xr.Dataset, type: str) -> xr.Dataset:
    """
    Get the aggregation time from the dataset. 
    If type is 'mean', return the mean of the dataset. 
    If type is 'sum', return the sum of the dataset.
    """
    if type == 'mean':
        return ds.mean(dim='time')
    elif type == 'sum':
        return ds.sum(dim='time')
    else:
        raise ValueError("Invalid aggregation type. Use 'mean' or 'sum'.")

def select_dates(ds: xr.Dataset, start_date: str, end_date: str) -> xr.Dataset:
    """
    Select a date range from the dataset. 
    The date range is defined by the start and end dates.
    """
    ds = ds.sel(time=slice(start_date, end_date))
    return ds

def select_region(ds: xr.Dataset, lat_range: tuple, lon_range: tuple) -> xr.Dataset:
    """
    Select a region from the dataset. 
    The region is defined by the latitude and longitude ranges.
    """
    ds = ds.sel(lat=slice(lat_range[0], lat_range[1]), lon=slice(lon_range[0], lon_range[1]))
    return ds

def get_series(ds: xr.Dataset, lat: float, lon: float) -> pd.Series:
    """
    Get a specific series from the dataset. 
    The series is defined by the latitude and longitude coordinates.
    """
    layer = ds.sel(lat=lat, lon=lon, method='nearest').squeeze()
    series = layer.to_dataframe().reset_index()
    series.set_index('time', inplace=True)
    return series['tp']  # Assuming 'tp' is the variable name in the dataset

def get_layer(ds: xr.Dataset, 
              start_date : str,
                end_date : str,
                aggregation : str = 'mean',) -> xr.Dataset:
    

    """
    Get a specific layer from the dataset. 
    """
    ds = select_dates(ds, start_date, end_date)
    layer = get_aggregation_time(ds, aggregation)
    return layer

def get_series(ds: xr.Dataset, 
               start_date : str,
                end_date : str) -> pd.Series:
    
    """
    Get a specific series from the dataset.
    """
    ds = select_dates(ds, start_date, end_date)
    series = ds.mean(dim=['latitude', 'longitude'])

    #series to pandas series
    series = series.to_dataframe().reset_index()
    series.set_index('time', inplace=True)
    return series





