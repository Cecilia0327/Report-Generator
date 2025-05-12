import pytest
import pandas as pd
from unittest.mock import MagicMock
from src.reconciliation import ReconEngine


@pytest.fixture
def db_manager_mock():
    """Fixture to create a mock DBManager."""
    mock = MagicMock()
    # Sample reference equity prices
    mock.load_equity_prices.return_value = pd.DataFrame(
        {
            "DATETIME": ["2023-10-31", "2023-10-30"],
            "SYMBOL": ["AAPL", "AAPL"],
            "PRICE": [150.0, 148.0],
        }
    ).assign(DATETIME=lambda df: pd.to_datetime(df["DATETIME"]))

    # Sample reference bond prices
    mock.load_bond_prices.return_value = pd.DataFrame(
        {
            "DATETIME": ["2023-10-31", "2023-10-30"],
            "ISIN": ["US1234567890", "US1234567890"],
            "PRICE": [100.0, 99.0],
        }
    ).assign(DATETIME=lambda df: pd.to_datetime(df["DATETIME"]))

    return mock


def test_generate_reconciliation(db_manager_mock):
    """Test generating reconciliation data."""
    # Create an instance of ReconEngine with the mocked DBManager
    recon_engine = ReconEngine(db_manager=db_manager_mock)

    # Sample fund data
    fund_data = pd.DataFrame(
        {
            "FINANCIAL TYPE": ["Equities", "Government Bond", "CASH"],
            "SYMBOL": ["AAPL", "US1234567890", "CASH"],
            "PRICE": [152.0, 101.0, 0.0],
            "EOM_DATE": pd.to_datetime(["2023-10-31", "2023-10-31", "2023-10-31"]),
        }
    )

    # Generate reconciliation data
    result = recon_engine.generate(fund_data)

    # Verify the results
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert len(result) == 3  # One record for each fund position

    # Check the reconciliation for Equities
    assert result.loc[0, "FINANCIAL_TYPE"] == "Equities"
    assert result.loc[0, "SYMBOL"] == "AAPL"
    assert result.loc[0, "EOM_DATE"] == pd.Timestamp("2023-10-31")
    assert result.loc[0, "FUND_PRICE"] == 152.0
    assert result.loc[0, "REFERENCE_PRICE"] == 150.0
    assert result.loc[0, "PRICE_DIFFERENCE"] == 2.0  # 152.0 - 150.0

    # Check the reconciliation for Government Bond
    assert result.loc[1, "FINANCIAL_TYPE"] == "Government Bond"
    assert result.loc[1, "SYMBOL"] == "US1234567890"
    assert result.loc[1, "EOM_DATE"] == pd.Timestamp("2023-10-31")
    assert result.loc[1, "FUND_PRICE"] == 101.0
    assert result.loc[1, "REFERENCE_PRICE"] == 100.0
    assert result.loc[1, "PRICE_DIFFERENCE"] == 1.0  # 101.0 - 100.0

    # Check the reconciliation for CASH
    print(result.loc[2])
    assert result.loc[2, "FINANCIAL_TYPE"] == "CASH"
    assert result.loc[2, "SYMBOL"] == "CASH"
    assert result.loc[2, "EOM_DATE"] == pd.Timestamp("2023-10-31")
    assert result.loc[2, "FUND_PRICE"] == 0.0
    assert pd.isna(result.loc[2, "REFERENCE_PRICE"])  # Check for NaN
    assert pd.isna(result.loc[2, "PRICE_DIFFERENCE"])  # Check for NaN
