"""The error envelope and exception mapping."""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import BaseModel, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import (
    AppError,
    ConflictError,
    DomainValidationError,
    NotFoundError,
)


class Payload(BaseModel):
    count: int


class CheckedPayload(BaseModel):
    count: int

    @field_validator("count")
    @classmethod
    def must_be_positive(cls, value: int) -> int:
        if value < 0:
            raise ValueError("count must be positive")
        return value


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

    @app.post("/boom/checked")
    async def checked(payload: CheckedPayload) -> CheckedPayload:
        return payload

    @app.get("/boom/unauthorized")
    async def unauthorized() -> None:
        raise StarletteHTTPException(
            401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )

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


@pytest.mark.usefixtures("failing_routes")
async def test_validator_errors_stay_a_422_not_a_500(client: AsyncClient) -> None:
    response = await client.post("/boom/checked", json={"count": -1})
    body = response.json()
    assert response.status_code == 422
    assert body["error"]["code"] == "request_validation_error"
    assert "count must be positive" in response.text


@pytest.mark.usefixtures("failing_routes")
async def test_http_error_headers_are_preserved(client: AsyncClient) -> None:
    response = await client.get("/boom/unauthorized")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.usefixtures("failing_routes")
async def test_unexpected_errors_still_carry_the_request_id(
    client: AsyncClient,
) -> None:
    response = await client.get("/boom/unexpected", headers={"X-Request-ID": "rid-9"})
    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == "rid-9"
    assert response.json()["error"]["request_id"] == "rid-9"


@pytest.mark.usefixtures("failing_routes")
async def test_validation_details_do_not_echo_submitted_values(
    client: AsyncClient,
) -> None:
    response = await client.post("/boom/validate", json={"count": "hunter2-secret"})
    assert response.status_code == 422
    assert "hunter2-secret" not in response.text
    assert response.json()["error"]["details"][0]["loc"] == ["body", "count"]
