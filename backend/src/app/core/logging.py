"""Structured JSON logging with request-scoped context and secret redaction."""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

REDACTED_KEYS = frozenset(
    {"password", "token", "authorization", "email", "secret", "secret_key"}
)


def redact_sensitive(
    _logger: WrappedLogger, _method: str, event_dict: EventDict
) -> EventDict:
    """Mask the value of any known sensitive key.

    The first two arguments are required by the structlog processor API and are
    unused.

    Parameters
    ----------
    event_dict : EventDict
        The event being logged.

    Returns
    -------
    EventDict
        The event with sensitive values replaced by ``"***"``.
    """
    for key in event_dict:
        if key.lower() in REDACTED_KEYS:
            event_dict[key] = "***"
    return event_dict


def configure_logging(level: str = "INFO", *, json_logs: bool = True) -> None:
    """Configure structlog and the standard library to emit one log format.

    Parameters
    ----------
    level : str, default "INFO"
        Minimum log level name.
    json_logs : bool, default True
        Emit JSON lines when true, a human-readable console format otherwise.
    """
    shared: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        redact_sensitive,
    ]
    renderer: Any = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            *shared,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                renderer,
            ],
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
