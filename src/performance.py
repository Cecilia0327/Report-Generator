# src/fund_performance_analyzer.py
import pandas as pd
from pathlib import Path


class FundPerformanceAnalyzer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def calculate_performance(self, fund_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the performance metrics for each fund and return a DataFrame with
        results.
        """
        # Ensure EOM_DATE is a datetime
        fund_data["EOM_DATE"] = pd.to_datetime(fund_data["EOM_DATE"])

        # Group by EOM_DATE and FUND NAME
        monthly_performance = (
            fund_data.groupby(["EOM_DATE", "FUND_NAME"])
            .agg(
                Fund_MV_end=("MARKET VALUE", "sum"), Realized_PL=("REALISED P/L", "sum")
            )
            .reset_index()
        )

        # Calculate Fund Market Value at the start of the month
        monthly_performance["Fund_MV_start"] = monthly_performance.groupby("FUND_NAME")[
            "Fund_MV_end"
        ].shift(1)

        # Calculate Rate of Return
        monthly_performance["Rate_of_Return"] = (
            monthly_performance["Fund_MV_end"]
            - monthly_performance["Fund_MV_start"]
            + monthly_performance["Realized_PL"]
        ) / monthly_performance["Fund_MV_start"]

        return monthly_performance

    def generate_performance_report(self, fund_data: pd.DataFrame) -> None:
        """
        Generate an Excel report for the best performing fund for each month.
        """
        performance_data = self.calculate_performance(fund_data)

        performance_data = performance_data.dropna(subset=["Rate_of_Return"])

        # Find the best performing fund for each month
        best_performing_funds = performance_data.loc[
            performance_data.groupby("EOM_DATE")["Rate_of_Return"].idxmax()
        ]

        # Save to Excel
        report_path = self.output_dir / "best_performing_funds.xlsx"
        best_performing_funds.to_excel(
            report_path, index=False, sheet_name="Best Performing Funds"
        )

        print(f"Best performing funds report generated at: {report_path}")
