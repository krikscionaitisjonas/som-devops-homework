import os
from functools import lru_cache

from pydantic import BaseModel, Field, field_validator


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = Field(default="TMF641 Service Ordering Demo")
    app_version: str = Field(default="0.1.0")
    app_description: str = Field(
        default="Demo implementation skeleton for TMF641 Service Ordering API."
    )
    environment: str = Field(default="dev")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8080, ge=1, le=65535)
    reload: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.lower()
        allowed = {"dev", "test", "prod"}
        if normalized not in allowed:
            raise ValueError(f"environment must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.upper()
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        if normalized not in allowed:
            raise ValueError(f"log_level must be one of: {', '.join(sorted(allowed))}")
        return normalized


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "TMF641 Service Ordering Demo"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        app_description=os.getenv(
            "APP_DESCRIPTION",
            "Demo implementation skeleton for TMF641 Service Ordering API.",
        ),
        environment=os.getenv("APP_ENV", "dev"),
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8080")),
        reload=_to_bool(os.getenv("APP_RELOAD"), True),
        log_level=os.getenv("APP_LOG_LEVEL", "INFO"),
    )

