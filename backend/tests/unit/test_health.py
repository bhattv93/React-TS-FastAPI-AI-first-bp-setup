"""Health, readiness and the published OpenAPI contract."""

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.deps import get_session
from tests.fixtures.fakes import FakeSession


async def test_health_reports_version_and_env(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.0.0-dev", "env": "test"}


async def test_health_is_also_served_under_the_api_prefix(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


async def test_ready_ok_when_database_answers(
    app: FastAPI, client: AsyncClient
) -> None:
    session = FakeSession()
    app.dependency_overrides[get_session] = lambda: session
    response = await client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    assert len(session.executed) == 1


async def test_ready_503_when_database_is_down(
    app: FastAPI, client: AsyncClient
) -> None:
    app.dependency_overrides[get_session] = lambda: FakeSession(fail=True)
    response = await client.get("/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "not_ready"


async def test_openapi_publishes_only_the_versioned_routes(
    client: AsyncClient,
) -> None:
    paths = (await client.get("/openapi.json")).json()["paths"]
    assert "/api/v1/health" in paths
    assert "/api/v1/ready" in paths
    assert "/health" not in paths
