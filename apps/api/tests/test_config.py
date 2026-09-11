from pathlib import Path

import pytest
from feedbackos_api.config import (
    LOCAL_DATABASE_URL,
    AppEnvironment,
    Settings,
)
from pydantic import ValidationError


def build_settings(**overrides: object) -> Settings:
    return Settings(_env_file=None, **overrides)  # type: ignore[call-arg]


def production_values() -> dict[str, object]:
    return {
        "app_env": "production",
        "database_url": "postgresql+psycopg://app:secret@db.internal/feedbackos",
        "session_secret": "production-session-secret-from-secret-manager",
        "allowed_origins": ("https://app.feedbackos.example",),
        "storage_endpoint": "https://feedbackos.oss-cn-hangzhou.aliyuncs.com",
        "storage_region": "oss-cn-hangzhou",
        "storage_bucket": "feedbackos-production-private",
        "storage_access_key_id": "production-access-key-from-secret-manager",
        "storage_secret_access_key": "production-storage-secret-from-secret-manager",
    }


def test_local_profile_has_working_local_defaults() -> None:
    settings = build_settings()

    assert settings.app_env is AppEnvironment.LOCAL
    assert settings.database_url is not None
    assert settings.database_url.get_secret_value() == LOCAL_DATABASE_URL
    assert settings.cookie_secure is False
    assert settings.storage_addressing_style == "path"


def test_test_profile_is_isolated_from_local_database_and_bucket() -> None:
    settings = build_settings(app_env="test")

    assert settings.database_url is not None
    assert settings.database_url.get_secret_value().endswith("/feedbackos_test")
    assert settings.storage_bucket == "feedbackos-test-private"
    assert settings.debug is False


def test_production_rejects_missing_secrets() -> None:
    with pytest.raises(ValidationError, match="FEEDBACKOS_DATABASE_URL"):
        build_settings(app_env="production")


def test_production_rejects_local_credentials() -> None:
    values = production_values()
    local_secret = "feedbackos_local_only_session_secret_32_chars_minimum"
    values["session_secret"] = local_secret

    with pytest.raises(ValidationError, match="本地开发凭据") as error:
        build_settings(**values)

    assert local_secret not in str(error.value)
    assert "synthetic-password" not in str(error.value)
    assert "production-storage-secret-from-secret-manager" not in str(error.value)


def test_production_accepts_complete_secure_configuration() -> None:
    settings = build_settings(**production_values())

    assert settings.app_env is AppEnvironment.PRODUCTION
    assert settings.debug is False
    assert settings.cookie_secure is True
    assert settings.storage_addressing_style == "virtual"


def test_secret_values_are_redacted_from_settings_repr() -> None:
    settings = build_settings(**production_values())

    assert "production-session-secret-from-secret-manager" not in repr(settings)
    assert "production-storage-secret-from-secret-manager" not in repr(settings)


def test_env_example_contains_only_known_local_credentials() -> None:
    repository_root = Path(__file__).parents[3]
    example = (repository_root / ".env.example").read_text(encoding="utf-8")

    assert "feedbackos_local_only" in example
    assert "BEGIN PRIVATE KEY" not in example
    assert "LTAI" not in example
    assert "aliyuncs.com" not in example
