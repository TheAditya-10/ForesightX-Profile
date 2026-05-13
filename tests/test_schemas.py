from __future__ import annotations

from pydantic import ValidationError

from app.schemas.profile import UpdatePortfolioRequest, UpdateProfileRequest


def test_update_profile_pan_is_uppercase() -> None:
    payload = UpdateProfileRequest(
        name="Aditya",
        email="a@example.com",
        phone="1234567",
        pan="abcde1234f",
        city="Pune",
        risk_level="medium",
    )
    assert payload.pan == "ABCDE1234F"


def test_update_portfolio_ticker_is_uppercase() -> None:
    payload = UpdatePortfolioRequest(user_id="u1", ticker="tcs.ns", quantity=1)
    assert payload.ticker == "TCS.NS"


def test_update_portfolio_rejects_zero_quantity() -> None:
    try:
        UpdatePortfolioRequest(user_id="u1", ticker="TCS", quantity=0)
    except ValidationError as exc:
        assert "quantity" in str(exc).lower()
    else:
        raise AssertionError("Expected validation error")
