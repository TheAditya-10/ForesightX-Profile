from decimal import Decimal

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from shared import HTTPRequestError, get_logger

from sqlalchemy import select

from app.db.models import PortfolioPosition, User, PortfolioTransaction
from app.db.session import get_user_with_positions
from app.schemas.profile import (
    CreateProfileRequest,
    CreateProfileResponse,
    PortfolioPositionResponse,
    PortfolioResponse,
    ProfileResponse,
    RiskResponse,
    UpdateProfileRequest,
    UpdatePortfolioRequest,
)
from app.services.avatar_storage import S3AvatarStorage
from app.services.market_client import MarketDataClient
from app.utils.config import ProfileServiceSettings


class ProfileServiceError(RuntimeError):
    """Raised when profile operations fail validation or persistence checks."""


class ProfileService:
    def __init__(
        self,
        settings: ProfileServiceSettings,
        session: AsyncSession,
        market_client: MarketDataClient,
    ) -> None:
        self.settings = settings
        self.session = session
        self.market_client = market_client
        self.logger = get_logger(settings.service_name, "profile")
        self.avatar_storage = S3AvatarStorage(settings)

    async def get_portfolio(self, user_id: str) -> PortfolioResponse:
        user = await get_user_with_positions(self.session, user_id)
        if user is None:
            raise ProfileServiceError(f"User {user_id} not found")

        tickers = [position.ticker for position in user.portfolio_positions]
        prices = await self.market_client.get_prices(tickers) if tickers else {}

        holdings: list[PortfolioPositionResponse] = []
        holdings_value = Decimal("0")
        for position in user.portfolio_positions:
            current_price = Decimal(str(prices.get(position.ticker, float(position.avg_price))))
            current_value = Decimal(position.quantity) * current_price
            pnl = (current_price - position.avg_price) * Decimal(position.quantity)
            holdings_value += current_value
            holdings.append(
                PortfolioPositionResponse(
                    ticker=position.ticker,
                    quantity=position.quantity,
                    avg_price=float(position.avg_price),
                    current_price=float(current_price),
                    current_value=float(current_value),
                    unrealized_pnl=float(pnl),
                )
            )

        total_value = user.cash_balance + holdings_value
        return PortfolioResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            pan=user.pan,
            city=user.city,
            photo=self.avatar_storage.signed_url(user.photo),
            photo_key=user.photo,
            risk_level=user.risk_level,
            cash=float(user.cash_balance),
            holdings=holdings,
            total_value=float(total_value),
        )

    async def update_portfolio(self, payload: UpdatePortfolioRequest) -> PortfolioResponse:
        try:
            validated = UpdatePortfolioRequest.model_validate(payload.model_dump())
        except ValidationError as exc:
            raise ProfileServiceError(str(exc)) from exc

        user = await get_user_with_positions(self.session, validated.user_id)
        if user is None:
            raise ProfileServiceError(f"User {validated.user_id} not found")

        try:
            trade_price = Decimal(str(await self.market_client.get_price(validated.ticker)))
        except HTTPRequestError as exc:
            raise ProfileServiceError(f"Market data unavailable for {validated.ticker}") from exc
        except Exception as exc:  # pragma: no cover - defensive
            raise ProfileServiceError(f"Market data unavailable for {validated.ticker}") from exc
        if trade_price <= 0:
            raise ProfileServiceError(f"Unable to value trade for {validated.ticker}")

        position = next((item for item in user.portfolio_positions if item.ticker == validated.ticker), None)
        quantity_delta = validated.quantity
        cash_delta = trade_price * Decimal(quantity_delta)

        if quantity_delta > 0 and user.cash_balance < cash_delta:
            raise ProfileServiceError("Insufficient cash balance for requested buy")

        if quantity_delta < 0:
            if position is None or position.quantity < abs(quantity_delta):
                raise ProfileServiceError("Cannot sell more shares than currently held")

        if position is None and quantity_delta > 0:
            position = PortfolioPosition(
                user_id=user.id,
                ticker=validated.ticker,
                quantity=0,
                avg_price=Decimal("0"),
            )
            self.session.add(position)
            user.portfolio_positions.append(position)

        # Persist transaction record(s)
        if quantity_delta > 0 and position is not None:
            # BUY: update average price
            existing_cost = position.avg_price * Decimal(position.quantity)
            new_cost = trade_price * Decimal(quantity_delta)
            new_quantity = position.quantity + quantity_delta
            position.avg_price = (existing_cost + new_cost) / Decimal(new_quantity)
            position.quantity = new_quantity
            user.cash_balance -= cash_delta

            tx = PortfolioTransaction(
                user_id=user.id,
                ticker=validated.ticker,
                action="BUY",
                quantity=quantity_delta,
                price=trade_price,
                realized_pnl=None,
            )
            self.session.add(tx)
        elif quantity_delta < 0 and position is not None:
            # SELL: compute realized P&L using previous avg price
            qty_sold = abs(quantity_delta)
            prev_avg = position.avg_price
            realized = (trade_price - prev_avg) * Decimal(qty_sold)

            position.quantity = position.quantity - qty_sold
            user.cash_balance += abs(cash_delta)

            tx = PortfolioTransaction(
                user_id=user.id,
                ticker=validated.ticker,
                action="SELL",
                quantity=qty_sold,
                price=trade_price,
                realized_pnl=realized,
            )
            self.session.add(tx)

            if position.quantity == 0:
                await self.session.delete(position)

        await self.session.commit()
        return await self.get_portfolio(validated.user_id)

    async def get_portfolio_history(self, user_id: str) -> list[dict]:
        user = await get_user_with_positions(self.session, user_id)
        if user is None:
            raise ProfileServiceError(f"User {user_id} not found")

        result = await self.session.execute(
            select(PortfolioTransaction).where(PortfolioTransaction.user_id == user_id).order_by(PortfolioTransaction.created_at.desc())
        )
        rows = result.scalars().all()

        history: list[dict] = []
        for r in rows:
            history.append(
                {
                    "id": r.id,
                    "ticker": r.ticker,
                    "action": r.action,
                    "quantity": int(r.quantity),
                    "price": float(r.price),
                    "realized_pnl": float(r.realized_pnl) if r.realized_pnl is not None else None,
                    "created_at": r.created_at.isoformat() if r.created_at is not None else None,
                }
            )

        return history

    async def get_risk(self, user_id: str) -> RiskResponse:
        user = await get_user_with_positions(self.session, user_id)
        if user is None:
            raise ProfileServiceError(f"User {user_id} not found")
        return RiskResponse(user_id=user.id, risk_level=user.risk_level)

    async def get_profile(self, user_id: str) -> ProfileResponse:
        user = await get_user_with_positions(self.session, user_id)
        if user is None:
            raise ProfileServiceError(f"User {user_id} not found")
        return self._profile_response(user)

    async def update_profile(self, user_id: str, payload: UpdateProfileRequest) -> ProfileResponse:
        try:
            validated = UpdateProfileRequest.model_validate(payload.model_dump())
        except ValidationError as exc:
            raise ProfileServiceError(str(exc)) from exc

        user = await get_user_with_positions(self.session, user_id)
        if user is None:
            raise ProfileServiceError(f"User {user_id} not found")

        user.name = validated.name.strip()
        user.email = str(validated.email).lower()
        user.phone = validated.phone.strip()
        user.pan = validated.pan
        user.city = validated.city.strip()
        user.risk_level = validated.risk_level
        await self.session.commit()
        await self.session.refresh(user)
        return self._profile_response(user)

    async def create_profile(self, payload: CreateProfileRequest) -> CreateProfileResponse:
        existing = await get_user_with_positions(self.session, payload.user_id)
        if existing is not None:
            return self._create_profile_response(existing)

        display_name = (
            payload.name.strip()
            if payload.name
            else payload.email.split("@", maxsplit=1)[0].replace(".", " ").replace("_", " ").title() or "User"
        )
        user = User(
            id=payload.user_id,
            name=display_name,
            email=str(payload.email).lower(),
            phone=payload.phone.strip() if payload.phone else None,
            pan=payload.pan.strip().upper() if payload.pan else None,
            city=payload.city.strip() if payload.city else None,
            photo=payload.photo,
            risk_level=payload.risk_level or "medium",
            cash_balance=Decimal("10000.00"),
        )
        self.session.add(user)
        await self.session.commit()
        return self._create_profile_response(user)

    async def update_profile_photo(self, user_id: str, file) -> ProfileResponse:
        user = await get_user_with_positions(self.session, user_id)
        if user is None:
            raise ProfileServiceError(f"User {user_id} not found")

        object_key = await self.avatar_storage.upload_avatar(user_id=user.id, file=file)
        user.photo = object_key
        await self.session.commit()
        await self.session.refresh(user)
        return self._profile_response(user)

    def _profile_response(self, user: User) -> ProfileResponse:
        return ProfileResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            pan=user.pan,
            city=user.city,
            photo=self.avatar_storage.signed_url(user.photo),
            photo_key=user.photo,
            risk_level=user.risk_level,
        )

    def _create_profile_response(self, user: User) -> CreateProfileResponse:
        return CreateProfileResponse(
            user_id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            pan=user.pan,
            city=user.city,
            photo=self.avatar_storage.signed_url(user.photo),
            photo_key=user.photo,
            risk_level=user.risk_level,
        )
