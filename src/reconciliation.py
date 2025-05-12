# src/reconciliation.py
import pandas as pd
from src.db_manager import DBManager  # Ensure this import matches your actual structure


class ReconEngine:
    def __init__(self, db_manager: DBManager):
        self.db_manager = db_manager

    def generate(self, fund_data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate reconciliation data by comparing fund prices with reference prices.
        """
        # Load reference prices from the database
        equity_prices = self.db_manager.load_equity_prices()
        bond_prices = self.db_manager.load_bond_prices()

        # Ensure the reference prices DataFrame has a DatetimeIndex
        equity_prices["DATETIME"] = pd.to_datetime(equity_prices["DATETIME"])
        equity_prices.set_index("DATETIME", inplace=True)

        bond_prices["DATETIME"] = pd.to_datetime(bond_prices["DATETIME"])
        bond_prices.set_index("DATETIME", inplace=True)

        reconciliation_records = []
        # Iterate through each fund position to reconcile
        for _, position in fund_data.iterrows():
            financial_type = position["FINANCIAL TYPE"]
            symbol = position["SYMBOL"]
            fund_price = position["PRICE"]
            eom_date = position["EOM_DATE"]

            if financial_type == "Equities":
                ref_prices = equity_prices[equity_prices["SYMBOL"] == symbol]
                ref_price_row = ref_prices.loc[ref_prices.index == eom_date]

                if not ref_price_row.empty:
                    reference_price = ref_price_row["PRICE"].values[0]
                else:
                    last_available_row = ref_prices[ref_prices.index < eom_date]
                    reference_price = (
                        last_available_row.last("1D")["PRICE"].values[0]
                        if not last_available_row.empty
                        else None
                    )

            elif financial_type == "Government Bond":
                ref_prices = bond_prices[bond_prices["ISIN"] == symbol]
                ref_price_row = ref_prices.loc[ref_prices.index == eom_date]

                if not ref_price_row.empty:
                    reference_price = ref_price_row["PRICE"].values[0]
                else:
                    last_available_row = ref_prices[ref_prices.index < eom_date]
                    reference_price = (
                        last_available_row.last("1D")["PRICE"].values[0]
                        if not last_available_row.empty
                        else None
                    )

            elif financial_type == "CASH":
                reference_price = None  # No comparison needed for cash

            # Calculate price difference
            price_difference = (
                fund_price - reference_price if reference_price is not None else None
            )

            reconciliation_records.append(
                {
                    "FINANCIAL_TYPE": financial_type,
                    "SYMBOL": symbol,
                    "EOM_DATE": eom_date,
                    "FUND_PRICE": fund_price,
                    "REFERENCE_PRICE": reference_price,
                    "PRICE_DIFFERENCE": price_difference,
                }
            )

        # Convert to DataFrame for output
        return pd.DataFrame(reconciliation_records)
