from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from app.controllers.profile_controller import ProfileController
from app.services.avatar_storage import AvatarStorageError
from app.services.profile_service import ProfileServiceError


def test_controller_maps_service_errors_to_http_errors() -> None:
    async def _run() -> None:
        class _Svc:
            async def get_profile(self, user_id: str):  # noqa: ARG002
                raise ProfileServiceError("User not found")

        controller = ProfileController(service=_Svc())  # type: ignore[arg-type]
        with pytest.raises(HTTPException) as exc:
            await controller.get_profile("u1")
        assert exc.value.status_code == 404

    asyncio.run(_run())


def test_controller_maps_avatar_errors_to_422() -> None:
    async def _run() -> None:
        class _Svc:
            async def update_profile_photo(self, user_id: str, file):  # noqa: ARG002
                raise AvatarStorageError("Only JPEG")

        controller = ProfileController(service=_Svc())  # type: ignore[arg-type]
        with pytest.raises(HTTPException) as exc:
            await controller.update_profile_photo("u1", file=None)  # type: ignore[arg-type]
        assert exc.value.status_code == 422

    asyncio.run(_run())
