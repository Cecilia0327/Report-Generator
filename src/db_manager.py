# src/db_manager.py
import sqlite3
from pathlib import Path
from typing import List
import pandas as pd
from src.schemas.models import FundPosition


class DBManager:
    def __init__(self, ref_db_path: Path, fund_db_path: Path):
        self.ref_db_path = ref_db_path
        self.fund_db_path = fund_db_path
        self.connection = None
        self.fund_connection = None

    def initialize_db(self) -> None:
        """Initialize the reference database and fund database."""
        self.ref_connection = sqlite3.connect(self.ref_db_path)
        self.create_reference_db()

        self.fund_connection = sqlite3.connect(self.fund_db_path)

    def create_reference_db(self) -> None:
        """Create the reference database using the master-reference-sql file."""
        sql_file_path = Path("data/master-reference-sql.sql")
        with open(sql_file_path, "r") as file:
            sql_script = file.read()

        cursor = self.ref_connection.cursor()
        try:
            cursor.executescript(sql_script)
            self.ref_connection.commit()
            print("Reference database created successfully.")
        except Exception as e:
            print(f"Error creating reference database: {e}")
            self.ref_connection.rollback()

    def create_fund_table(self, fund_name: str, eom_date: str) -> None:
        """Create a table for fund data identified by fund name and EOM date."""
        cursor = self.fund_connection.cursor()
        table_name = f"{fund_name}_{eom_date.replace('-', '_')}"
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS "{table_name}" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                market_value REAL NOT NULL,
                realized REAL NOT NULL
            )
        ''')
        self.fund_connection.commit()

    def insert_fund_data(
        self, fund_name: str, eom_date: str, positions: List[FundPosition]
    ) -> None:
        """Insert fund data into the appropriate table."""
        self.create_fund_table(fund_name, eom_date)  # Ensure the table exists
        cursor = self.fund_connection.cursor()
        table_name = f"{fund_name}_{eom_date.replace('-', '_')}"
        for position in positions:
            cursor.execute(
                (
                    f'INSERT INTO "{table_name}" '
                    '(symbol, price, quantity, market_value, realized) '
                    'VALUES (?, ?, ?, ?, ?)'
                ),
                (
                    position.symbol,
                    position.price,
                    position.quantity,
                    position.market_value,
                    position.realized,
                ),
            )

        self.fund_connection.commit()

    def load_equity_prices(self) -> pd.DataFrame:
        """Load equity prices from the reference database."""
        return pd.read_sql("SELECT * FROM equity_prices", self.ref_connection)

    def load_bond_prices(self) -> pd.DataFrame:
        """Load bond prices from the reference database."""
        return pd.read_sql("SELECT * FROM bond_prices", self.ref_connection)

    def close_connections(self) -> None:
        """Close the database connections."""
        if self.ref_connection:
            self.ref_connection.close()
        if self.fund_connection:
            self.fund_connection.close()
