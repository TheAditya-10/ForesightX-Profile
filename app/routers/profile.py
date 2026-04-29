from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.profile_controller import ProfileController
from app.schemas.profile import (
    CreateProfileRequest,
    CreateProfileResponse,
    PortfolioResponse,
    ProfileResponse,
    RiskResponse,
    UpdateProfileRequest,
    UpdatePortfolioRequest,
)
from app.services.market_client import MarketDataClient
from app.services.profile_service import ProfileService


router = APIRouter(tags=["profile"])


async def get_session(request: Request) -> AsyncSession:
    async with request.app.state.session_factory() as session:
        yield session


def get_controller(request: Request, session: AsyncSession = Depends(get_session)) -> ProfileController:
    market_client = MarketDataClient(
        base_url=request.app.state.settings.data_service_url,
        http_client=request.app.state.http_client,
        service_name=request.app.state.settings.service_name,
        max_retries=request.app.state.settings.max_retries,
    )
    service = ProfileService(
        settings=request.app.state.settings,
        session=session,
        market_client=market_client,
    )
    return ProfileController(service=service)


@router.get("/portfolio/{user_id}", response_model=PortfolioResponse)
async def get_portfolio(
    user_id: str,
    controller: ProfileController = Depends(get_controller),
) -> PortfolioResponse:
    return await controller.get_portfolio(user_id=user_id)


@router.post("/portfolio/update", response_model=PortfolioResponse)
async def update_portfolio(
    payload: UpdatePortfolioRequest,
    controller: ProfileController = Depends(get_controller),
) -> PortfolioResponse:
    return await controller.update_portfolio(payload=payload)


@router.get("/risk/{user_id}", response_model=RiskResponse)
async def get_risk(
    user_id: str,
    controller: ProfileController = Depends(get_controller),
) -> RiskResponse:
    return await controller.get_risk(user_id=user_id)


@router.get("/profiles/{user_id}", response_model=ProfileResponse)
async def get_profile(
    user_id: str,
    controller: ProfileController = Depends(get_controller),
) -> ProfileResponse:
    return await controller.get_profile(user_id=user_id)


@router.patch("/profiles/{user_id}", response_model=ProfileResponse)
async def update_profile(
    user_id: str,
    payload: UpdateProfileRequest,
    controller: ProfileController = Depends(get_controller),
) -> ProfileResponse:
    return await controller.update_profile(user_id=user_id, payload=payload)


@router.post("/profiles", response_model=CreateProfileResponse, status_code=201)
async def create_profile(
    payload: CreateProfileRequest,
    controller: ProfileController = Depends(get_controller),
) -> CreateProfileResponse:
    return await controller.create_profile(payload)


@router.post("/api/v1/profile/create", response_model=CreateProfileResponse, status_code=201, include_in_schema=False)
async def create_profile_legacy(
    payload: CreateProfileRequest,
    controller: ProfileController = Depends(get_controller),
) -> CreateProfileResponse:
    return await create_profile(payload, controller)
