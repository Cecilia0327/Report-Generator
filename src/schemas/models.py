from pydantic import BaseModel


class FundPosition(BaseModel):
    symbol: str
    price: float
    quantity: float
    market_value: float
    realized: float


class ReconciliationData(BaseModel):
    symbol: str
    fund_price: float
    reference_price: float
    price_difference: float
