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
