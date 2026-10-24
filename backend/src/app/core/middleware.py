"""HTTP middleware: request ID propagation and access logging."""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"

logger = structlog.get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to logs and the response, and log each request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Process one request.

        Parameters
        ----------
        request : Request
            The incoming request.
        call_next : Callable[[Request], Awaitable[Response]]
            The next ASGI handler in the chain.

        Returns
        -------
        Response
            The downstream response with an ``X-Request-ID`` header.
        """
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id, method=request.method, path=request.url.path
        )
        started = time.perf_counter()
        response = await call_next(request)
        logger.info(
            "request_completed",
            status=response.status_code,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def current_request_id() -> str | None:
    """Return the request ID bound to the current context.

    Returns
    -------
    str or None
        The request ID, or ``None`` outside a request.
    """
    value = structlog.contextvars.get_contextvars().get("request_id")
    return str(value) if value is not None else None
