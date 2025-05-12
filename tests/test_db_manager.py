import pandas as pd
import pytest
import sqlite3
from src.db_manager import DBManager
from src.schemas.models import FundPosition


@pytest.fixture
def db_manager(tmp_path):
    """Fixture to create a DBManager instance with temporary database paths."""
    ref_db_path = tmp_path / "ref_db.sqlite"
    fund_db_path = tmp_path / "fund_db.sqlite"
    manager = DBManager(ref_db_path, fund_db_path)
    manager.initialize_db()
    yield manager
    manager.close_connections()


def test_create_reference_db(db_manager):
    """Test if the reference database is created successfully."""
    # Check if the reference database file exists
    assert db_manager.ref_db_path.exists()

    # Check if the expected tables exist
    ref_connection = sqlite3.connect(db_manager.ref_db_path)
    cursor = ref_connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    assert len(tables) > 0  # Ensure at least one table exists


def test_create_fund_table(db_manager):
    """Test if a fund table is created successfully."""
    fund_name = "TestFund"
    eom_date = "2023-10-31"
    db_manager.create_fund_table(fund_name, eom_date)

    # Check if the table exists
    table_name = f"{fund_name}_{eom_date.replace('-', '_')}"
    fund_connection = sqlite3.connect(db_manager.fund_db_path)
    cursor = fund_connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    )
    table_exists = cursor.fetchone()

    assert table_exists is not None


def test_insert_fund_data(db_manager):
    """Test if fund data is inserted correctly."""
    fund_name = "TestFund"
    eom_date = "2023-10-31"
    positions = [
        FundPosition(
            symbol="AAPL", price=150.0, quantity=10, market_value=1500.0, realized=0.0
        ),
        FundPosition(
            symbol="GOOGL", price=2800.0, quantity=5, market_value=14000.0, realized=0.0
        ),
    ]

    db_manager.insert_fund_data(fund_name, eom_date, positions)

    # Verify the data was inserted
    table_name = f"{fund_name}_{eom_date.replace('-', '_')}"
    fund_connection = sqlite3.connect(db_manager.fund_db_path)
    cursor = fund_connection.cursor()
    cursor.execute(f'SELECT * FROM "{table_name}"')
    rows = cursor.fetchall()

    assert len(rows) == len(positions)  # Ensure the number of inserted rows matches
    assert rows[0][1] == "AAPL"  # Check the first symbol
    assert rows[1][1] == "GOOGL"  # Check the second symbol


def test_load_equity_prices(db_manager):
    """Test loading equity prices from the reference database."""
    equity_prices = db_manager.load_equity_prices()
    assert isinstance(equity_prices, pd.DataFrame)  # Ensure the result is a DataFrame
    assert not equity_prices.empty  # Ensure the DataFrame is not empty


def test_load_bond_prices(db_manager):
    """Test loading bond prices from the reference database."""
    bond_prices = db_manager.load_bond_prices()
    assert isinstance(bond_prices, pd.DataFrame)  # Ensure the result is a DataFrame
    assert not bond_prices.empty  # Ensure the DataFrame is not empty
