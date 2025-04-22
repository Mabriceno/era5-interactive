import sqlite3
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Dataset:
    source_id: int
    source_name: str
    variable_id: int
    variable_name: str
    variable_key: str
    long_name: str
    unit: str
    path: str

def get_db_connection():
    """Create a database connection"""
    return sqlite3.connect('database/climate_studio.db')

def get_available_datasets() -> List[Dataset]:
    """
    Fetch all available datasets from the database.
    Returns a list of Dataset objects with source and variable information.
    """
    query = """
    SELECT 
        s.id as source_id,
        s.name as source_name,
        v.id as variable_id,
        v.name as variable_name,
        d.variable_key,
        v.long_name,
        v.unit,
        d.path
    FROM datasets d
    JOIN sources s ON d.source_id = s.id
    JOIN variables v ON d.variable_id = v.id
    WHERE d.available = 1
    ORDER BY s.name, v.name
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        return [Dataset(
            source_id=row[0],
            source_name=row[1],
            variable_id=row[2],
            variable_name=row[3],
            variable_key=row[4],
            long_name=row[5],
            unit=row[6],
            path=row[7]
        ) for row in rows]

def get_available_dates(source_id: int, variable_id: int) -> Tuple[datetime, datetime]:
    """
    Get the available date range for a specific dataset.
    Returns a tuple of (start_date, end_date).
    """
    query = """
    SELECT MIN(date_start), MAX(date_end)
    FROM requests
    WHERE source_id = ? AND variable_id = ?
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (source_id, variable_id))
        start_date, end_date = cursor.fetchone()
        return datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')
    

def get_path(source_id: int, variable_id: int) -> str:
    """
    Get the path of a specific dataset.
    Returns the path as a string.
    """
    query = """
    SELECT path
    FROM datasets
    WHERE source_id = ? AND variable_id = ?
    """
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (source_id, variable_id))
        path = cursor.fetchone()[0]
        return path if path else None