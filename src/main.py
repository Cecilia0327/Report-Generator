import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import logging
import pandas as pd

from src.data_loader import DataLoader
from src.db_manager import DBManager
from src.reconciliation import ReconEngine
from src.utils.reports import generate_excel_report  # Import the modified function
from src.performance import FundPerformanceAnalyzer  # Import the new class

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define paths
INPUT_DIR = Path("data/external-funds")
DB_PATH = Path("data/reference.db")
FUND_DB_PATH = Path("data/fund_data.db")  # New path for fund data
OUTPUT_DIR = Path("outputs")

# List of fund names to process
FUND_NAMES = [
    "Whitestone",
    "Wallington",
    "Catalysm",
    "Belaware",
    "Gohen",
    "Applebead",
    "Magnum",
    "Trustmind",
    "Leeder",
    "Virtous",
]


def generate_reports() -> pd.DataFrame:
    """Generate reports for each fund and return combined data."""
    all_fund_data = (
        pd.DataFrame()
    )  # Initialize an empty DataFrame to hold all funds' data
    try:
        loader = DataLoader()
        db = DBManager(DB_PATH, FUND_DB_PATH)  # Pass both DB paths
        db.initialize_db()  # Initialize both databases
        recon_engine = ReconEngine(db)  # Pass the DBManager instance

        # Process each fund individually
        for fund_name in FUND_NAMES:
            # Load fund data for the specific fund
            fund_data = loader.load_fund_data(INPUT_DIR, fund_name)
            if fund_data.empty:
                logging.warning(f"No data found for fund: {fund_name}. Skipping.")
                continue

            # Generate reconciliation data
            reconciliation_data = recon_engine.generate(fund_data)

            # Generate report for the fund
            generate_excel_report(reconciliation_data, OUTPUT_DIR, fund_name)

            # Append fund data for performance calculation
            all_fund_data = pd.concat([all_fund_data, fund_data], ignore_index=True)

    except Exception as e:
        logging.error(f"Failed to generate reports: {e}")
        raise e
    finally:
        if "db" in locals():
            db.close_connections()

    return all_fund_data  # Return the combined fund data for performance calculation


def main() -> None:
    """Main function to run the report generation."""
    # Generate reports and get all fund data
    all_fund_data = generate_reports()

    # Generate the performance report
    performance_analyzer = FundPerformanceAnalyzer(OUTPUT_DIR)
    performance_analyzer.generate_performance_report(all_fund_data)


if __name__ == "__main__":
    main()
