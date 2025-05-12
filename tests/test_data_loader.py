from unittest.mock import patch
import pytest
import pandas as pd
from src.data_loader import DataLoader


@pytest.fixture
def data_loader(tmp_path):
    """Fixture to create a DataLoader instance."""
    return DataLoader()


def test_load_fund_data(data_loader, tmp_path):
    """Test loading fund data from CSV files."""
    # Create a sample CSV file
    fund_name = "TestFund"
    csv_content = (
    "symbol,price,quantity,market_value,realized\n"
    "AAPL,150.0,10,1500.0,0.0\n"
    "GOOGL,2800.0,5,14000.0,0.0"
    )
    csv_file = tmp_path / f"2023-10-31_{fund_name}.csv"
    csv_file.write_text(csv_content)

    # Load the fund data
    result_df = data_loader.load_fund_data(tmp_path, fund_name)

    # Verify the loaded data
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    assert len(result_df) == 2  # Two rows in the CSV
    assert "FUND_NAME" in result_df.columns
    assert "EOM_DATE" in result_df.columns
    assert result_df["FUND_NAME"].iloc[0] == fund_name


def test_extract_date_from_filename(data_loader):
    """Test extracting date from various filename formats."""
    filenames = {
        "31-10-2023_TestFund.csv": pd.Timestamp("2023-10-31"),
        "31_10_2023_TestFund.csv": pd.Timestamp("2023-10-31"),
        "10-31-2023_TestFund.csv": pd.Timestamp("2023-10-31"),
        "20231031_TestFund.csv": pd.Timestamp("2023-10-31"),
        "invalid_date_TestFund.csv": None,
    }

    for filename, expected_date in filenames.items():
        extracted_date = data_loader.extract_date_from_filename(filename)
        print(filename)
        assert extracted_date == expected_date


@patch("pandas.read_sql")
def test_load_reference_prices(mock_read_sql, data_loader):
    """Test loading reference prices from the database."""
    # Create mock data
    mock_data = pd.DataFrame({"symbol": ["AAPL", "GOOGL"], "price": [150.0, 2800.0]})
    mock_read_sql.return_value = mock_data

    # Mock database connection
    mock_db_connection = object()  # Just a placeholder; it won't be used

    result_df = data_loader.load_reference_prices(mock_db_connection)

    # Verify the loaded data
    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty
    assert len(result_df) == 2  # Two rows in the mock data
    assert "symbol" in result_df.columns
    assert "price" in result_df.columns
