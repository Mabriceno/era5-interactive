import sqlite3
import os

def initialize_database(db_path="database"):
    """
    Initializes the SQLite database with the required schema.

    Args:
        db_path (str): The path to the SQLite database file.
                       If it exists, tables will be dropped and recreated.
    """
    print(f"Initializing database at: {db_path}")

    # Asegura que el directorio para el archivo DB exista
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"Created directory: {db_dir}")

    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- Habilitar claves foráneas (importante por conexión) ---
        cursor.execute("PRAGMA foreign_keys = ON;")

        # --- Eliminar tablas si existen (orden inverso por dependencias FK) ---
        print("Dropping existing tables (if any)...")
        cursor.execute("DROP TABLE IF EXISTS layers;")
        cursor.execute("DROP TABLE IF EXISTS indices;")
        cursor.execute("DROP TABLE IF EXISTS request_executions;")
        cursor.execute("DROP TABLE IF EXISTS request_months;")
        cursor.execute("DROP TABLE IF EXISTS requests;")
        cursor.execute("DROP TABLE IF EXISTS datasets;")
        cursor.execute("DROP TABLE IF EXISTS variables;")
        cursor.execute("DROP TABLE IF EXISTS sources;")

        # --- Crear tablas ---
        print("Creating table: sources")
        cursor.execute("""
        CREATE TABLE sources (
            id INTEGER PRIMARY KEY,                     -- Identificador único
            name TEXT NOT NULL UNIQUE,                  -- Nombre corto único (e.g., 'era5_hourly_sl')
            source_type TEXT,                           -- 'reanalysis', 'simulation', etc.
            data_name TEXT,                             -- Identificador interno o patrón (e.g., 'era5')
            description TEXT,                           -- Descripción detallada
            lat_key TEXT DEFAULT 'latitude',            -- Nombre coord latitud en archivo
            lon_key TEXT DEFAULT 'longitude',           -- Nombre coord longitud en archivo
            time_key TEXT DEFAULT 'time',               -- Nombre coord tiempo en archivo
            lvl_key TEXT NULL,                          -- Nombre coord nivel (si aplica)
            x_key TEXT NULL,                            -- Nombre coord X proyectada (si aplica)
            y_key TEXT NULL                             -- Nombre coord Y proyectada (si aplica)
        );
        """)

        print("Creating table: variables")
        cursor.execute("""
        CREATE TABLE variables (
            id INTEGER PRIMARY KEY,                     -- Identificador único
            name TEXT NOT NULL UNIQUE,                  -- Nombre corto ('t2m', 'tp')
            long_name TEXT,                             -- Nombre descriptivo
            unit TEXT                                   -- Unidades ('K', 'm')
        );
        """)

        print("Creating table: datasets")
        cursor.execute("""
        CREATE TABLE datasets (
            id INTEGER PRIMARY KEY,                     -- ID único del dataset
            source_id INTEGER NOT NULL,                 -- FK a sources
            variable_id INTEGER NOT NULL,               -- FK a variables
            variable_key TEXT NOT NULL,                 -- Nombre de la variable DENTRO del archivo fuente
            available INTEGER DEFAULT 1,                -- 0=False, 1=True
            path TEXT NULL,                             -- Ruta al archivo fuente (opcional)

            FOREIGN KEY (source_id) REFERENCES sources (id)
                ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (variable_id) REFERENCES variables (id)
                ON DELETE RESTRICT ON UPDATE CASCADE,
            UNIQUE (source_id, variable_id, variable_key) -- Clave única compuesta
        );
        """)

        print("Creating table: requests")
        cursor.execute("""
        CREATE TABLE requests (
            id INTEGER PRIMARY KEY,                     -- ID único de la definición de petición
            source_id INTEGER NOT NULL,                 -- FK a sources
            variable_id INTEGER NOT NULL,               -- FK a variables
            type_request TEXT NOT NULL CHECK (type_request IN ('layer', 'series')), -- 'layer' o 'series'
            aggregations TEXT NULL,                     -- Agregaciones aplicadas ('mean', 'sum')
            date_start TEXT NOT NULL,                   -- Fecha inicio (ISO8601 string 'YYYY-MM-DD')
            date_end TEXT NOT NULL,                     -- Fecha fin (ISO8601 string 'YYYY-MM-DD')
            lat_start REAL NULL,                        -- Latitud inicial BBox
            lat_end REAL NULL,                          -- Latitud final BBox
            lon_start REAL NULL,                        -- Longitud inicial BBox
            lon_end REAL NULL,                          -- Longitud final BBox
            n_request INTEGER DEFAULT 1,                -- Contador de cuántas veces se solicitaron estos parámetros
            valid_request INTEGER DEFAULT 0,            -- 0=False (no cacheado/inválido), 1=True (cacheado y válido)

            FOREIGN KEY (source_id) REFERENCES sources (id)
                ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (variable_id) REFERENCES variables (id)
                ON DELETE RESTRICT ON UPDATE CASCADE,

            -- Restricción de unicidad sobre los parámetros que definen la petición
            UNIQUE (source_id, variable_id, type_request, aggregations,
                    date_start, date_end, lat_start, lat_end, lon_start, lon_end)
        );
        """)
        # Nota: El UNIQUE anterior asume que no habrá peticiones idénticas
        # excepto por los meses filtrados, ya que estos van a otra tabla.

        print("Creating table: request_months")
        cursor.execute("""
        CREATE TABLE request_months (
            request_id INTEGER NOT NULL,                -- FK a requests
            month_number INTEGER NOT NULL CHECK (month_number >= 1 AND month_number <= 12), -- Mes (1-12)

            PRIMARY KEY (request_id, month_number),     -- Clave primaria compuesta
            FOREIGN KEY (request_id) REFERENCES requests (id)
                ON DELETE CASCADE ON UPDATE CASCADE     -- Si se borra el request, borrar sus meses
        );
        """)

        print("Creating table: request_executions")
        cursor.execute("""
        CREATE TABLE request_executions (
            id INTEGER PRIMARY KEY,                     -- ID único de esta ejecución específica
            request_id INTEGER NOT NULL,                -- FK a la definición de la petición en 'requests'
            execution_time TEXT NOT NULL,               -- Timestamp (ISO8601 'YYYY-MM-DD HH:MM:SS.SSS') de CUANDO se ejecutó

            FOREIGN KEY (request_id) REFERENCES requests (id)
                ON DELETE CASCADE ON UPDATE CASCADE     -- Si se borra la definición del request, borrar su historial
        );
        """)

        print("Creating table: indices") # Para caché de series temporales
        cursor.execute("""
        CREATE TABLE indices (
            request_id INTEGER PRIMARY KEY,             -- FK a requests (relación 1 a 1 con request cacheado)
            name TEXT NULL,                             -- Nombre descriptivo opcional
            path TEXT NOT NULL UNIQUE,                  -- Ruta al archivo cacheado (CSV, Parquet, etc.)
            created_at TEXT NOT NULL,                   -- Timestamp (ISO8601) de creación del archivo caché

            FOREIGN KEY (request_id) REFERENCES requests (id)
                ON DELETE CASCADE ON UPDATE CASCADE     -- Si se borra el request, borrar su caché
        );
        """)

        print("Creating table: layers") # Para caché de mapas espaciales
        cursor.execute("""
        CREATE TABLE layers (
            request_id INTEGER PRIMARY KEY,             -- FK a requests (relación 1 a 1 con request cacheado)
            name TEXT NULL,                             -- Nombre descriptivo opcional
            path TEXT NOT NULL UNIQUE,                  -- Ruta al archivo cacheado (GeoTIFF, NetCDF subset, etc.)
            created_at TEXT NOT NULL,                   -- Timestamp (ISO8601) de creación del archivo caché

            FOREIGN KEY (request_id) REFERENCES requests (id)
                ON DELETE CASCADE ON UPDATE CASCADE     -- Si se borra el request, borrar su caché
        );
        """)

        # --- Crear Índices para optimización ---
        print("Creating indexes...")
        # Datasets
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_source_id ON datasets (source_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_datasets_variable_id ON datasets (variable_id);")
        # Requests
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_source_variable ON requests (source_id, variable_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_dates ON requests (date_start, date_end);")
        # cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_coords ON requests (lat_start, lat_end, lon_start, lon_end);") # Index on NULLable columns might be less effective depending on query
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_requests_valid_cache ON requests (valid_request) WHERE valid_request = 1;") # SQLite supports partial indexes
        # Request Executions
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_executions_request_id ON request_executions (request_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_executions_time ON request_executions (execution_time);")
        # Request Months
        # PK ya indexa (request_id, month_number). Un índice solo en request_id puede ser útil.
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_months_request_id ON request_months (request_id);")


        # --- Confirmar cambios ---
        conn.commit()
        print("Database initialized successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            print("Rolling back changes.")
            conn.rollback() # Deshacer cambios en caso de error
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# --- Ejemplo de uso ---
if __name__ == "__main__":
    # Define la ruta donde quieres crear el archivo de base de datos
    database_file = "database/climate_studio.db"

    # Llama a la función para inicializar (o reiniciar) la base de datos
    initialize_database(database_file)

    # Puedes añadir aquí código para verificar la creación de tablas o insertar datos iniciales
    # Ejemplo: Conectar y listar tablas
    try:
        conn_check = sqlite3.connect(database_file)
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor_check.fetchall()
        print("\nTables created:")
        for table in tables:
            print(f"- {table[0]}")
        conn_check.close()
    except sqlite3.Error as e:
        print(f"\nCould not verify tables: {e}")