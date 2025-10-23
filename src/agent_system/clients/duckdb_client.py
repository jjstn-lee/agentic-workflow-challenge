import sys
import duckdb
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data/campaign_performance.csv"

class DuckDBClient:
    """
    Lightweight SQL interface using DuckDB.
    Automatically loads the campaign_performance.csv dataset at initialization.
    """

    def __init__(self, db_path=":memory:"):
        """
        Initialize the DuckDB connection and load the campaign performance data.

        Args:
            db_path (str): Path to the DuckDB database file.
                           Use ':memory:' for an in-memory instance.
        """
        self.conn = duckdb.connect(database=db_path)
        self._registered_tables = set()
        self._load_default_csv()

    def _load_default_csv(self):
        """Register the default campaign_performance.csv file."""
        if not DATA_PATH.exists():
            print(f"Error: CSV file not found: {DATA_PATH}")
            sys.exit(1)
        table_name = DATA_PATH.stem
        self.conn.execute(
            f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_csv_auto('{DATA_PATH}')"
        )
        self._registered_tables.add(table_name)

    def query(self, sql: str, params=None) -> pd.DataFrame:
        """Run a SQL query and return a pandas DataFrame."""
        if params:
            return self.conn.execute(sql, params).fetchdf()
        return self.conn.execute(sql).fetchdf()

    def list_tables(self):
        """List all tables currently registered in the DuckDB connection."""
        return self.query("SHOW TABLES;")

    def close(self):
        """Close the DuckDB connection."""
        self.conn.close()