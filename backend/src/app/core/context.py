"""Request-scoped context shared by the middleware and the error envelope."""

import structlog


def current_request_id() -> str | None:
    """Return the request ID bound to the current context.

    Returns
    -------
    str or None
        The request ID, or ``None`` outside a request.
    """
    value = structlog.contextvars.get_contextvars().get("request_id")
    return str(value) if value is not None else None
