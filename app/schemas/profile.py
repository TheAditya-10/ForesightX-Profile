from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateProfileRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    email: EmailStr
    name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: str | None = Field(default=None, max_length=32)
    pan: str | None = Field(default=None, max_length=16)
    city: str | None = Field(default=None, max_length=120)
    photo: str | None = Field(default=None, max_length=4096)
    risk_level: str | None = Field(default=None, pattern="^(low|medium|high)$")


class CreateProfileResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    pan: str | None = None
    city: str | None = None
    photo: str | None = None
    photo_key: str | None = None
    risk_level: str


class ProfileResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    pan: str | None = None
    city: str | None = None
    photo: str | None = None
    photo_key: str | None = None
    risk_level: str


class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=32)
    pan: str = Field(..., min_length=10, max_length=16)
    city: str = Field(..., min_length=2, max_length=120)
    photo: str | None = Field(default=None, max_length=4096)
    risk_level: str = Field(..., pattern="^(low|medium|high)$")

    @field_validator("pan")
    @classmethod
    def normalize_pan(cls, value: str) -> str:
        return value.strip().upper()


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
    email: EmailStr | None = None
    phone: str | None = None
    pan: str | None = None
    city: str | None = None
    photo: str | None = None
    photo_key: str | None = None
    risk_level: str
    cash: float = Field(..., ge=0)
    holdings: list[PortfolioPositionResponse]
    total_value: float = Field(..., ge=0)


class PortfolioTransactionResponse(BaseModel):
    id: int
    ticker: str
    action: str
    quantity: int
    price: float
    realized_pnl: float | None = None
    created_at: str


class UpdatePortfolioRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    ticker: str = Field(..., min_length=1, max_length=20)
    quantity: int = Field(...)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("quantity")
    @classmethod
    def validate_quantity_non_zero(cls, value: int) -> int:
        if value == 0:
            raise ValueError("quantity must be non-zero")
        return value


class RiskResponse(BaseModel):
    user_id: str
    risk_level: str
