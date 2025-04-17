import xarray as xr
import pandas as pd
import os

def load_era5_data(file_path: str) -> xr.Dataset:
    """
    Loads ERA5 data from a netCDF file.

    Parameters:
        file_path (str): Path to the netCDF file containing ERA5 data.

    Returns:
        xr.Dataset: Loaded ERA5 dataset.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    try:
        dataset = xr.open_dataset(file_path)
        return dataset
    except Exception as e:
        raise RuntimeError(f"Error loading ERA5 data: {e}")


def load_csv_data(file_path: str) -> pd.DataFrame:
    """
    Loads time series data from a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded DataFrame with time series data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    try:
        data = pd.read_csv(file_path, parse_dates=["date"])
        return data
    except Exception as e:
        raise RuntimeError(f"Error loading CSV data: {e}")


def preprocess_era5_data(dataset: xr.Dataset, variable: str) -> xr.DataArray:
    """
    Extracts and preprocesses a specific variable from the ERA5 dataset.

    Parameters:
        dataset (xr.Dataset): ERA5 dataset.
        variable (str): Variable to extract (e.g., 't2m', 'tp').

    Returns:
        xr.DataArray: Preprocessed DataArray for the selected variable.
    """
    if variable not in dataset:
        raise ValueError(f"Variable '{variable}' not found in the dataset.")
    
    data = dataset[variable]
    data = data.squeeze()  # Remove any singleton dimensions
    return data


def preprocess_csv_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses time series data from a CSV file.

    Parameters:
        data (pd.DataFrame): DataFrame with raw time series data.

    Returns:
        pd.DataFrame: Cleaned and formatted DataFrame.
    """
    if "date" not in data.columns:
        raise ValueError("The CSV file must contain a 'date' column.")
    
    data = data.sort_values(by="date")
    data = data.set_index("date")
    return data