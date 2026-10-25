"""HTTP middleware: request ID, access logging and unexpected-error handling."""

import re
import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.errors import error_response

REQUEST_ID_HEADER = "X-Request-ID"
# Client-supplied IDs end up in every log line and in the error envelope, so only a
# short, plain alphabet is accepted; anything else is replaced by a generated ID.
_SAFE_REQUEST_ID = re.compile(r"[A-Za-z0-9._-]{1,64}")

logger = structlog.get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to logs and the response, and log each request.

    Unexpected exceptions become the 500 error envelope here (not in a framework
    handler) so the response still passes through the CORS middleware, carries the
    request ID and is access-logged like any other request.
    """

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
        supplied = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = (
            supplied if _SAFE_REQUEST_ID.fullmatch(supplied) else uuid.uuid4().hex
        )
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id, method=request.method, path=request.url.path
        )
        started = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:  # pylint: disable=broad-exception-caught
                logger.exception("unhandled_exception")
                response = error_response(
                    500, "internal_error", "Internal server error"
                )
            logger.info(
                "request_completed",
                status=response.status_code,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            structlog.contextvars.clear_contextvars()
