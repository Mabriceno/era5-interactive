import xarray as xr
import pandas as pd
import os
import json
from pathlib import Path
from utils.aggregations import get_layer, get_series
from database.db_utils import get_path

def get_file_name(request: dict) -> str:
    """Generate a str with any keys from the request dictionary."""
    # Sort dictionary keys to ensure consistent naming
    sorted_items = sorted(request.items())
    # Create a string joining key-value pairs
    return "_".join([f"{k}-{v}" for k, v in sorted_items])

def load_dataset(path: str) -> xr.Dataset:
    """Load a dataset from a given path. Get all nc file names in path, sort by date in name and concatenate with xarray"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path {path} does not exist")
    
    # Get all .nc files in the directory
    nc_files = [f for f in os.listdir(path) if f.endswith('.nc')]
    print(f"Found {len(nc_files)} .nc files in {path}")

    if not nc_files:
        raise FileNotFoundError(f"No .nc files found in {path}")
    
    # Sort files by date in filename
    nc_files.sort()
    # Create full paths
    full_paths = [os.path.join(path, f) for f in nc_files]
    
    # Open and concatenate all datasets
    datasets = [xr.open_dataset(f) for f in full_paths]
    return xr.concat(datasets, dim='time')


def load_dataset_lazy(path, chunks={"time": -1}):
    """
    Carga perezosa usando Dask para no saturar RAM.
    - Agrupa todos los .nc en la carpeta.
    - Renombra/ajusta coordenadas en un preprocess.
    """
    pattern = os.path.join(path, "*.nc")

    def _preprocess(ds):
        #rename valid_time to time
        if 'valid_time' in ds.coords:
            ds = ds.rename({"valid_time": "time"})

        return ds

    return xr.open_mfdataset(
        pattern,
        combine="by_coords",   # concat + merge automático
        parallel=True,         # usa threads/processes de Dask
        chunks=chunks,         # activa loading perezoso
        preprocess=_preprocess
    )

def check_cache(path: str) -> bool:
    """Check if the dataset is already cached. If it is, return True."""
    return os.path.exists(path)

def request_dataset(request: dict) -> xr.Dataset:
    """Request a dataset from the database. First check if dataset is cached. if it is, load it from cache. 
    If not, load it from the database and save on cache/datasets/ with the name of the request. Then return the dataset."""
    # Get database path for the dataset
    db_path = get_path(request['source_id'], request['var_id'])
    if not db_path:
        raise ValueError("Dataset not found in database")
    
    # Generate cache filename
    cache_dir = "cache/datasets"
    os.makedirs(cache_dir, exist_ok=True)
    cache_filename = get_file_name(request) + ".nc"
    print(f"Cache filename: {cache_filename}")
    cache_path = os.path.join(cache_dir, cache_filename)
    
    # Check cache
    if check_cache(cache_path):
        return xr.open_dataset(cache_path)
    
    print(f"Loading dataset from {db_path}...")
    # Load dataset from source
    ds = load_dataset_lazy(db_path)
    print(f"Loaded dataset with {len(ds.time)} time steps")
    # Save to cache
    ds.to_netcdf(cache_path)
    
    return ds

def request_layer(ds: xr.Dataset, request: dict) -> xr.Dataset:
    """Request a specific layer from the dataset. First check if layer is cached. if it is, load it from cache. 
    If not, get from aggregations.get_layer and save on cache/layers/ with the name of the request. Then return the layer."""
    # Generate cache filename
    cache_dir = "cache/layers"
    os.makedirs(cache_dir, exist_ok=True)
    cache_filename = get_file_name(request) + ".nc"
    cache_path = os.path.join(cache_dir, cache_filename)
    
    # Check cache
    if check_cache(cache_path):
        return xr.open_dataset(cache_path)
    
    # Get layer from dataset
    layer = get_layer(
        ds,
        start_date=request['start_date'],
        end_date=request['end_date'],
        aggregation=request.get('aggregation', 'mean')
    )
    
    # Save to cache
    layer.to_netcdf(cache_path)
    
    return layer

def request_series(ds: xr.Dataset, request: dict) -> pd.Series:
    """Request a specific series from the dataset. First check if series is cached. if it is, load it from cache. 
    If not, get from aggregations.get_series and save on cache/series/ with the name of the request. Then return the series."""
    # Generate cache filename
    cache_dir = "cache/series"
    os.makedirs(cache_dir, exist_ok=True)
    cache_filename = get_file_name(request) + ".csv"
    cache_path = os.path.join(cache_dir, cache_filename)
    
    # Check cache
    if check_cache(cache_path):
        return pd.read_csv(cache_path, index_col='time', parse_dates=True)['value']
    
    # Get series from dataset
    series = get_series(
        ds,
        start_date=request['start_date'],
        end_date=request['end_date'],
    )
    
    return series