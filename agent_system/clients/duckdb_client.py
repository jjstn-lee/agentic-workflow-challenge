import duckdb
from pathlib import Path
import pandas as pd

from state.global_state import GLOBAL_STATE

class DuckDBClient:
    """
    Lightweight SQL interface using DuckDB.
    Works directly with CSV files for prototyping or analytics workloads.
    """
    def __init__(self, db_path=":memory:"):
        """
        Initialize the DuckDB connection.

        Args:
            db_path (str): Path to the DuckDB database file. 
                           Use ':memory:' for an in-memory instance.
        """
        self.conn = duckdb.connect(database=db_path)
        self._registered_tables = set()

    def query(self, sql: str, params=None) -> pd.DataFrame:
        """
        Run a SQL query and return a pandas DataFrame.

        Args:
            sql (str): SQL query string.
            params (tuple, optional): Query parameters (if needed).

        Returns:
            pd.DataFrame: Query result.
        """
        if params:
            result = self.conn.execute(sql, params).fetchdf()
        else:
            result = self.conn.execute(sql).fetchdf()
        return result

    def register_csv(self, name: str, csv_path: str):
        """
        Register a CSV file as a virtual table in DuckDB.

        Args:
            name (str): Name of the table to register.
            csv_path (str): Path to the CSV file.
        """
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
        self.conn.execute(f"CREATE VIEW {name} AS SELECT * FROM read_csv_auto('{csv_path}')")
        self._registered_tables.add(name)
        
    def list_tables(self):
        """List all tables currently registered in the DuckDB connection."""
        return self.query("SHOW TABLES;")

    def close(self):
        """Close the DuckDB connection."""
        self.conn.close()