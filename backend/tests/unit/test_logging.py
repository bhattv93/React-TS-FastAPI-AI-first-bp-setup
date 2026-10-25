"""Structured logging and redaction."""

import json

import pytest
import structlog

from app.core.logging import configure_logging, redact_sensitive


def test_redact_sensitive_masks_known_keys() -> None:
    event = {"event": "login", "password": "hunter2", "Authorization": "Bearer x"}
    result = redact_sensitive(None, "info", event)
    assert result["password"] == "***"
    assert result["Authorization"] == "***"
    assert result["event"] == "login"


def test_json_logs_include_context_and_redaction(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO", json_logs=True)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id="abc123")
    structlog.get_logger("test").info("hello", token="top-secret")
    line = capsys.readouterr().out.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["event"] == "hello"
    assert payload["request_id"] == "abc123"
    assert payload["token"] == "***"
    assert payload["level"] == "info"
    structlog.contextvars.clear_contextvars()


def test_console_logs_are_not_json(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging("INFO", json_logs=False)
    structlog.get_logger("test").info("plain message")
    out = capsys.readouterr().out
    assert "plain message" in out
    assert not out.lstrip().startswith("{")
    configure_logging("INFO", json_logs=True)


def test_json_logs_render_exception_tracebacks(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("INFO", json_logs=True)
    try:
        raise ValueError("kaboom")
    except ValueError as exc:
        structlog.get_logger("test").error("failed", exc_info=exc)
    payload = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert "Traceback" in payload["exception"]
    assert "ValueError: kaboom" in payload["exception"]


def test_redaction_reaches_nested_values_and_key_variants() -> None:
    event = {
        "event": "call",
        "payload": {"user": {"Password": "x"}, "items": [{"api_key": "y"}]},
        "headers": {"Set-Cookie": "sid=1", "X-Request-ID": "keep"},
        "access_token": "z",
    }
    result = redact_sensitive(None, "info", event)
    assert result["payload"]["user"]["Password"] == "***"
    assert result["payload"]["items"][0]["api_key"] == "***"
    assert result["headers"]["Set-Cookie"] == "***"
    assert result["headers"]["X-Request-ID"] == "keep"
    assert result["access_token"] == "***"
    assert result["event"] == "call"
