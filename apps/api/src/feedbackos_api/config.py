from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from functools import lru_cache
from typing import Final, Literal, Self

from pydantic import AnyHttpUrl, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppEnvironment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "production"


LOCAL_DATABASE_URL: Final = (
    "postgresql+psycopg://feedbackos:feedbackos_local_only@127.0.0.1:5432/feedbackos"
)
LOCAL_SESSION_SECRET: Final = "feedbackos_local_only_session_secret_32_chars_minimum"
LOCAL_STORAGE_ACCESS_KEY_ID: Final = "GK0123456789abcdef0123456789abcdef"
LOCAL_STORAGE_SECRET_ACCESS_KEY: Final = (
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)

PROFILE_DEFAULTS: Final[dict[AppEnvironment, dict[str, object]]] = {
    AppEnvironment.LOCAL: {
        "debug": True,
        "database_url": LOCAL_DATABASE_URL,
        "session_secret": LOCAL_SESSION_SECRET,
        "cookie_secure": False,
        "allowed_origins": ("http://localhost:3000",),
        "storage_endpoint": "http://127.0.0.1:3900",
        "storage_region": "garage",
        "storage_bucket": "feedbackos-dev-private",
        "storage_access_key_id": LOCAL_STORAGE_ACCESS_KEY_ID,
        "storage_secret_access_key": LOCAL_STORAGE_SECRET_ACCESS_KEY,
        "storage_addressing_style": "path",
    },
    AppEnvironment.TEST: {
        "debug": False,
        "database_url": (
            "postgresql+psycopg://feedbackos:feedbackos_local_only@127.0.0.1:5432/feedbackos_test"
        ),
        "session_secret": "feedbackos_test_only_session_secret_32_chars_minimum",
        "cookie_secure": False,
        "allowed_origins": ("http://testserver",),
        "storage_endpoint": "http://127.0.0.1:3900",
        "storage_region": "garage",
        "storage_bucket": "feedbackos-test-private",
        "storage_access_key_id": LOCAL_STORAGE_ACCESS_KEY_ID,
        "storage_secret_access_key": LOCAL_STORAGE_SECRET_ACCESS_KEY,
        "storage_addressing_style": "path",
    },
    AppEnvironment.PRODUCTION: {
        "debug": False,
        "cookie_secure": True,
        "storage_addressing_style": "virtual",
    },
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FEEDBACKOS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: AppEnvironment = AppEnvironment.LOCAL
    debug: bool | None = None

    database_url: SecretStr | None = None
    session_secret: SecretStr | None = None
    cookie_secure: bool | None = None
    allowed_origins: tuple[AnyHttpUrl, ...] = ()

    storage_endpoint: AnyHttpUrl | None = None
    storage_region: str | None = None
    storage_bucket: str | None = None
    storage_access_key_id: SecretStr | None = None
    storage_secret_access_key: SecretStr | None = None
    storage_addressing_style: Literal["path", "virtual"] | None = None

    upload_max_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    preview_row_limit: int = Field(default=20, gt=0, le=100)

    @model_validator(mode="before")
    @classmethod
    def apply_environment_profile(cls, value: object) -> object:
        if not isinstance(value, Mapping):
            return value

        supplied = dict(value)
        environment = AppEnvironment(str(supplied.get("app_env", AppEnvironment.LOCAL)))
        return {**PROFILE_DEFAULTS[environment], **supplied}

    @model_validator(mode="after")
    def validate_environment_contract(self) -> Self:
        required = {
            "database_url": "FEEDBACKOS_DATABASE_URL",
            "session_secret": "FEEDBACKOS_SESSION_SECRET",
            "storage_endpoint": "FEEDBACKOS_STORAGE_ENDPOINT",
            "storage_region": "FEEDBACKOS_STORAGE_REGION",
            "storage_bucket": "FEEDBACKOS_STORAGE_BUCKET",
            "storage_access_key_id": "FEEDBACKOS_STORAGE_ACCESS_KEY_ID",
            "storage_secret_access_key": "FEEDBACKOS_STORAGE_SECRET_ACCESS_KEY",
        }
        missing = [
            environment_name
            for field, environment_name in required.items()
            if getattr(self, field) is None
        ]
        if missing:
            names = ", ".join(missing)
            raise ValueError(f"缺少必要配置: {names}")

        if self.app_env is not AppEnvironment.PRODUCTION:
            return self

        assert self.session_secret is not None
        assert self.storage_access_key_id is not None
        assert self.storage_secret_access_key is not None
        assert self.storage_endpoint is not None

        secret_values = {
            self.session_secret.get_secret_value(),
            self.storage_access_key_id.get_secret_value(),
            self.storage_secret_access_key.get_secret_value(),
        }
        local_values = {
            LOCAL_SESSION_SECRET,
            LOCAL_STORAGE_ACCESS_KEY_ID,
            LOCAL_STORAGE_SECRET_ACCESS_KEY,
        }
        if secret_values & local_values:
            raise ValueError("生产环境不得使用本地开发凭据")
        if len(self.session_secret.get_secret_value()) < 32:
            raise ValueError("FEEDBACKOS_SESSION_SECRET 在生产环境不得少于 32 个字符")
        if self.debug:
            raise ValueError("生产环境必须关闭 debug")
        if not self.cookie_secure:
            raise ValueError("生产环境必须启用 Secure Cookie")
        if self.storage_endpoint.scheme != "https":
            raise ValueError("生产对象存储 Endpoint 必须使用 HTTPS")
        if self.storage_addressing_style != "virtual":
            raise ValueError("生产 OSS 必须使用 virtual-hosted-style 寻址")
        if not self.allowed_origins or any(
            origin.scheme != "https" for origin in self.allowed_origins
        ):
            raise ValueError("生产环境必须显式配置 HTTPS Allowed Origin")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


def main() -> None:
    settings = get_settings()
    print(f"FeedbackOS configuration valid: env={settings.app_env.value}")


if __name__ == "__main__":
    main()
