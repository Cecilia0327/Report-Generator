import pandas as pd
from pathlib import Path


def generate_excel_report(
    recon_data: pd.DataFrame, output_dir: Path, fund_name: str
) -> None:
    """
    Generate an Excel report from the reconciliation data for a specific fund.
    """
    report_path = output_dir / f"{fund_name}_reconciliation_report.xlsx"

    with pd.ExcelWriter(report_path) as writer:
        recon_data.to_excel(writer, sheet_name="Reconciliation Data", index=False)

    print(f"Report generated successfully for {fund_name} at {report_path}")
