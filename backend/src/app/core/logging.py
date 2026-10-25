"""Structured JSON logging with request-scoped context and secret redaction."""

import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

MASK = "***"
# A key is sensitive when its lower-cased name (dashes as underscores) holds one of
# these fragments.
REDACTED_KEY_PARTS = (
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "cookie",
    "api_key",
    "apikey",
    "email",
)


def _is_sensitive(key: object) -> bool:
    """Return whether a mapping key names a sensitive value.

    Parameters
    ----------
    key : object
        The mapping key.

    Returns
    -------
    bool
        ``True`` when the key contains one of ``REDACTED_KEY_PARTS``.
    """
    name = str(key).lower().replace("-", "_")
    return any(part in name for part in REDACTED_KEY_PARTS)


def _redact(value: Any) -> Any:
    """Return a copy of ``value`` with sensitive mapping values masked.

    Parameters
    ----------
    value : Any
        A logged value; mappings and lists are searched, anything else is kept.

    Returns
    -------
    Any
        The redacted copy.
    """
    if isinstance(value, dict):
        return {
            key: MASK if _is_sensitive(key) else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


def redact_sensitive(
    _logger: WrappedLogger, _method: str, event_dict: EventDict
) -> EventDict:
    """Mask the value of any sensitive key, at any depth.

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
    redacted: EventDict = _redact(event_dict)
    return redacted


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
    if json_logs:
        # JSON has no pretty exceptions: turn ``exc_info`` into a traceback string.
        shared.append(structlog.processors.format_exc_info)
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
