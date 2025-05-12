import pytest
import pandas as pd
from unittest.mock import patch
from src.performance import FundPerformanceAnalyzer


@pytest.fixture
def analyzer(tmp_path):
    """Fixture to create a FundPerformanceAnalyzer instance."""
    return FundPerformanceAnalyzer(output_dir=tmp_path)


def test_calculate_performance(analyzer):
    """Test the calculation of performance metrics."""
    # Sample fund data
    data = {
        "EOM_DATE": ["2023-10-31", "2023-10-31", "2023-09-30", "2023-09-30"],
        "FUND_NAME": ["TestFund", "TestFund", "TestFund", "TestFund"],
        "MARKET VALUE": [1500.0, 2000.0, 1000.0, 1200.0],
        "REALISED P/L": [100.0, 200.0, 50.0, 75.0],
    }
    fund_data = pd.DataFrame(data)

    # Calculate performance
    result = analyzer.calculate_performance(fund_data)

    print(result.head(10))  # For debugging purposes

    # Verify the results
    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert "Fund_MV_end" in result.columns
    assert "Realized_PL" in result.columns
    assert "Fund_MV_start" in result.columns
    assert "Rate_of_Return" in result.columns

    # Check the expected values
    assert result["Fund_MV_end"].iloc[1] == 3500.0  # Sum of MARKET VALUE for 2023-10-31
    assert result["Realized_PL"].iloc[1] == 300.0  # Sum of REALISED P/L for 2023-10-31
    assert result["Fund_MV_start"].iloc[1] == 2200.0  # Fund MV at the start of October
    assert result["Rate_of_Return"].iloc[1] == pytest.approx(
        (3500 - 2200 + 300) / 2200, rel=1e-2
    )  # Rate of Return calculation


@patch("pandas.DataFrame.to_excel")
def test_generate_performance_report(mock_to_excel, analyzer):
    """Test generating the performance report."""
    # Sample fund data
    data = {
        "EOM_DATE": ["2023-10-31", "2023-10-31", "2023-09-30", "2023-09-30"],
        "FUND_NAME": ["TestFund", "TestFund", "TestFund", "TestFund"],
        "MARKET VALUE": [1500.0, 2000.0, 1000.0, 1200.0],
        "REALISED P/L": [100.0, 200.0, 50.0, 75.0],
    }
    fund_data = pd.DataFrame(data)

    # Generate report
    analyzer.generate_performance_report(fund_data)

    # Verify that to_excel was called
    assert mock_to_excel.called
    assert mock_to_excel.call_args[1]["index"] is False
    assert mock_to_excel.call_args[1]["sheet_name"] == "Best Performing Funds"

    # Check the report path
    expected_report_path = analyzer.output_dir / "best_performing_funds.xlsx"
    assert mock_to_excel.call_args[0][0] == expected_report_path
