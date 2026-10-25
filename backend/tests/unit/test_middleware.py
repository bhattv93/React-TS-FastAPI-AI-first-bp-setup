"""Request ID propagation."""

import json

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.context import current_request_id
from app.core.logging import configure_logging
from app.core.middleware import REQUEST_ID_HEADER
from app.main import create_app


def test_no_request_id_outside_a_request() -> None:
    assert current_request_id() is None


async def test_generates_request_id_when_absent(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert len(response.headers[REQUEST_ID_HEADER]) == 32


async def test_echoes_incoming_request_id(client: AsyncClient) -> None:
    response = await client.get("/health", headers={REQUEST_ID_HEADER: "trace-42"})
    assert response.headers[REQUEST_ID_HEADER] == "trace-42"


@pytest.mark.parametrize(
    "unsafe", ["line\nbreak", "x" * 200, "with space", "a/b", "<script>"]
)
async def test_unsafe_incoming_request_ids_are_replaced(
    client: AsyncClient, unsafe: str
) -> None:
    response = await client.get("/health", headers={REQUEST_ID_HEADER: unsafe})
    assert len(response.headers[REQUEST_ID_HEADER]) == 32


async def test_request_context_does_not_outlive_the_request(
    client: AsyncClient,
) -> None:
    await client.get("/health", headers={REQUEST_ID_HEADER: "trace-1"})
    assert current_request_id() is None


async def test_failed_requests_are_access_logged_with_a_traceback(
    capsys: pytest.CaptureFixture[str], app: FastAPI
) -> None:
    configure_logging("INFO", json_logs=True)  # bind the handler to the captured stdout

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secret internals")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        await http.get("/boom", headers={REQUEST_ID_HEADER: "rid-77"})
    lines = [
        json.loads(line)
        for line in capsys.readouterr().out.splitlines()
        if line.startswith("{")
    ]
    failure = next(entry for entry in lines if entry["event"] == "unhandled_exception")
    assert failure["request_id"] == "rid-77"
    assert "Traceback" in failure["exception"]
    completed = next(entry for entry in lines if entry["event"] == "request_completed")
    assert completed["status"] == 500
    assert completed["request_id"] == "rid-77"


async def test_server_errors_still_get_cors_headers(settings: Settings) -> None:
    cors_settings = settings.model_copy(
        update={"cors_origins": ["http://localhost:5173"]}
    )
    application = create_app(cors_settings)

    @application.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secret internals")

    async with application.router.lifespan_context(application):
        transport = ASGITransport(app=application, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as http:
            response = await http.get(
                "/boom", headers={"Origin": "http://localhost:5173"}
            )
    assert response.status_code == 500
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert REQUEST_ID_HEADER in response.headers["access-control-expose-headers"]
