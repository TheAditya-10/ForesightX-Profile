from fastapi import HTTPException, status

from app.schemas.profile import (
    CreateProfileRequest,
    CreateProfileResponse,
    PortfolioResponse,
    ProfileResponse,
    RiskResponse,
    UpdateProfileRequest,
    UpdatePortfolioRequest,
)
from app.services.profile_service import ProfileService, ProfileServiceError


class ProfileController:
    def __init__(self, service: ProfileService) -> None:
        self.service = service

    async def get_portfolio(self, user_id: str) -> PortfolioResponse:
        try:
            return await self.service.get_portfolio(user_id=user_id)
        except ProfileServiceError as exc:
            code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_422_UNPROCESSABLE_ENTITY
            raise HTTPException(status_code=code, detail=str(exc)) from exc

    async def update_portfolio(self, payload: UpdatePortfolioRequest) -> PortfolioResponse:
        try:
            return await self.service.update_portfolio(payload)
        except ProfileServiceError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    async def get_risk(self, user_id: str) -> RiskResponse:
        try:
            return await self.service.get_risk(user_id=user_id)
        except ProfileServiceError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def get_profile(self, user_id: str) -> ProfileResponse:
        try:
            return await self.service.get_profile(user_id=user_id)
        except ProfileServiceError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    async def update_profile(self, user_id: str, payload: UpdateProfileRequest) -> ProfileResponse:
        try:
            return await self.service.update_profile(user_id=user_id, payload=payload)
        except ProfileServiceError as exc:
            code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_422_UNPROCESSABLE_ENTITY
            raise HTTPException(status_code=code, detail=str(exc)) from exc

    async def create_profile(self, payload: CreateProfileRequest) -> CreateProfileResponse:
        try:
            return await self.service.create_profile(payload)
        except ProfileServiceError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
