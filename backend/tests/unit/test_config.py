import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings

REQUIRED_ENV_VARS = (
    "DATABASE_URL",
    "REDIS_URL",
    "MINIO_ENDPOINT",
    "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY",
    "MINIO_BUCKET",
)


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def test_settings_requires_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in REQUIRED_ENV_VARS:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_cors_origins_parses_json_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:5173"]')
    settings = Settings(_env_file=None)
    assert settings.cors_origins == ["http://localhost:5173"]
