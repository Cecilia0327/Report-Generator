import re
import pandas as pd
from pathlib import Path


class DataLoader:
    def load_fund_data(self, input_dir: Path, fund_name: str) -> pd.DataFrame:
        """
        Load fund data for a specific fund from CSV files in the specified directory.
        """
        all_positions = []
        for csv_file in input_dir.glob(f"*{fund_name}*.csv"):
            try:
                df = pd.read_csv(csv_file)
                df["FUND_NAME"] = fund_name

                # Extract EOM date from filename
                eom_date = self.extract_date_from_filename(csv_file.stem)
                if eom_date is not None:
                    df["EOM_DATE"] = eom_date
                    all_positions.append(df)
                else:
                    print(f"Could not extract date from {csv_file.name}")
            except Exception as e:
                print(f"Error loading {csv_file}: {e}")

        return (
            pd.concat(all_positions, ignore_index=True)
            if all_positions
            else pd.DataFrame()
        )

    def extract_date_from_filename(self, filename: str) -> pd.Timestamp:
        """
        Extract the date from the filename using various formats.
        """
        # Define regex patterns for different date formats
        date_patterns = [
            r"(\d{2})-(\d{2})-(\d{4})",  # DD-MM-YYYY
            r"(\d{2})_(\d{2})_(\d{4})",  # DD_MM_YYYY
            r"(\d{2})_(\d{2})_(\d{2})",  # MM_DD_YYYY
            r"(\d{2})-(\d{2})-(\d{2})",  # MM-DD-YYYY
            r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
            r"(\d{8})",  # YYYYMMDD
        ]

        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(0)
                date_str = date_str.replace("_", "-")  # Normalize underscores to dashes
                # Attempt to convert based on the identified format
                if len(date_str) == 10:
                    if "-" or "_" in date_str:
                        if (
                            "-" not in date_str[0:4] and "_" not in date_str[0:4]
                        ):  # YYYY-MM-DD
                            return pd.to_datetime(date_str, format="%Y-%m-%d")
                        elif int(date_str[0:2]) > 12:  # DD-MM-YYYY
                            return pd.to_datetime(
                                date_str, format="%d-%m-%Y", dayfirst=True
                            )
                        elif int(date_str[3:5]) > 12:  # MM-DD-YYYY
                            return pd.to_datetime(date_str, format="%m-%d-%Y")

                elif len(date_str) == 8:
                    return pd.to_datetime(date_str, format="%Y%m%d", errors="coerce")

        return None

    def load_reference_prices(self, db_connection) -> pd.DataFrame:
        """
        Load equity prices from the reference database.
        """
        return pd.read_sql("SELECT * FROM equity_prices", db_connection)
