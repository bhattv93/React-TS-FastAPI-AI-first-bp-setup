"""Settings behaviour and the .env.example contract."""

from pathlib import Path

import pytest

from app.core.config import Settings, get_settings


def test_pool_size_is_small_on_lambda(settings: Settings) -> None:
    lambda_settings = settings.model_copy(update={"runtime": "lambda"})
    assert lambda_settings.db_pool_size == 1
    assert settings.db_pool_size == 5


def test_get_settings_reads_prefixed_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_DATABASE_URL", "postgresql+asyncpg://u:p@db:5432/x")
    monkeypatch.setenv("APP_SECRET_KEY", "s3cret")
    monkeypatch.setenv("APP_ENV", "dev")
    get_settings.cache_clear()
    try:
        loaded = get_settings()
        assert loaded.env == "dev"
        assert loaded.secret_key.get_secret_value() == "s3cret"
        assert "s3cret" not in repr(loaded)
        assert get_settings() is loaded
    finally:
        get_settings.cache_clear()


def test_missing_required_settings_fail_fast(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)
    with pytest.raises(ValueError):
        Settings(_env_file=None)  # type: ignore[call-arg]


def test_env_example_lists_every_setting() -> None:
    example = Path(__file__).parents[2] / ".env.example"
    keys = {
        line.split("=", 1)[0]
        for line in example.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    }
    expected = {f"APP_{name.upper()}" for name in Settings.model_fields}
    assert keys == expected
