"""Request ID propagation."""

from httpx import AsyncClient

from app.core.middleware import REQUEST_ID_HEADER, current_request_id


def test_no_request_id_outside_a_request() -> None:
    assert current_request_id() is None


async def test_generates_request_id_when_absent(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert len(response.headers[REQUEST_ID_HEADER]) == 32


async def test_echoes_incoming_request_id(client: AsyncClient) -> None:
    response = await client.get("/health", headers={REQUEST_ID_HEADER: "trace-42"})
    assert response.headers[REQUEST_ID_HEADER] == "trace-42"
