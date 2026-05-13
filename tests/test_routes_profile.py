from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.profile import get_controller
from app.routers.profile import router as profile_router


class _ControllerStub:
    async def get_profile(self, user_id: str):  # noqa: ARG002
        return {"user_id": "u1", "name": "User", "email": "u1@example.com", "risk_level": "medium"}

    async def get_risk(self, user_id: str):  # noqa: ARG002
        return {"user_id": "u1", "risk_level": "medium"}

    async def get_portfolio(self, user_id: str):  # noqa: ARG002
        return {
            "user_id": "u1",
            "name": "User",
            "email": "u1@example.com",
            "risk_level": "medium",
            "cash": 100.0,
            "holdings": [],
            "total_value": 100.0,
        }


def test_profile_routes_return_expected_shapes() -> None:
    app = FastAPI()
    app.include_router(profile_router)
    app.dependency_overrides[get_controller] = lambda: _ControllerStub()
    client = TestClient(app)

    response = client.get("/profiles/u1")
    assert response.status_code == 200
    assert response.json()["user_id"] == "u1"

    response = client.get("/risk/u1")
    assert response.status_code == 200
    assert response.json()["risk_level"] == "medium"

    response = client.get("/portfolio/u1")
    assert response.status_code == 200
    assert response.json()["total_value"] == 100.0
