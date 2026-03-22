from pydantic import BaseModel, Field, field_validator


class PortfolioPositionResponse(BaseModel):
    ticker: str
    quantity: int
    avg_price: float
    current_price: float
    current_value: float
    unrealized_pnl: float


class PortfolioResponse(BaseModel):
    user_id: str
    name: str
    risk_level: str
    cash: float = Field(..., ge=0)
    holdings: list[PortfolioPositionResponse]
    total_value: float = Field(..., ge=0)


class UpdatePortfolioRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    ticker: str = Field(..., min_length=1, max_length=20)
    quantity: int = Field(..., ne=0)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()


class RiskResponse(BaseModel):
    user_id: str
    risk_level: str
