"""The error envelope and exception mapping."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel

from app.core.errors import (
    AppError,
    ConflictError,
    DomainValidationError,
    NotFoundError,
)


class Payload(BaseModel):
    count: int


@pytest.fixture
def failing_routes(app: FastAPI) -> FastAPI:
    @app.get("/boom/not-found")
    async def not_found() -> None:
        raise NotFoundError("Item 7 not found", details={"id": 7})

    @app.get("/boom/conflict")
    async def conflict() -> None:
        raise ConflictError("Already exists")

    @app.get("/boom/domain")
    async def domain() -> None:
        raise DomainValidationError("Bad state")

    @app.get("/boom/base")
    async def base() -> None:
        raise AppError("Generic")

    @app.get("/boom/unexpected")
    async def unexpected() -> None:
        raise RuntimeError("secret internals")

    @app.post("/boom/validate")
    async def validate(payload: Payload) -> Payload:
        return payload

    return app


@pytest.mark.usefixtures("failing_routes")
@pytest.mark.parametrize(
    ("path", "status", "code"),
    [
        ("/boom/not-found", 404, "not_found"),
        ("/boom/conflict", 409, "conflict"),
        ("/boom/domain", 422, "validation_error"),
        ("/boom/base", 400, "app_error"),
    ],
)
async def test_domain_errors_use_the_envelope(
    client: AsyncClient, path: str, status: int, code: str
) -> None:
    response = await client.get(path, headers={"X-Request-ID": "rid-1"})
    body = response.json()
    assert response.status_code == status
    assert body["error"]["code"] == code
    assert body["error"]["request_id"] == "rid-1"


@pytest.mark.usefixtures("failing_routes")
async def test_error_details_are_included(client: AsyncClient) -> None:
    response = await client.get("/boom/not-found")
    assert response.json()["error"]["details"] == {"id": 7}


@pytest.mark.usefixtures("failing_routes")
async def test_request_validation_error_is_enveloped(client: AsyncClient) -> None:
    response = await client.post("/boom/validate", json={"count": "not-a-number"})
    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "request_validation_error"
    assert body["error"]["details"]


async def test_unknown_route_is_enveloped(client: AsyncClient) -> None:
    response = await client.get("/does-not-exist")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"


@pytest.mark.usefixtures("failing_routes")
async def test_unexpected_errors_do_not_leak_internals(client: AsyncClient) -> None:
    response = await client.get("/boom/unexpected")
    assert response.status_code == 500
    assert response.json()["error"]["message"] == "Internal server error"
    assert "secret internals" not in response.text
