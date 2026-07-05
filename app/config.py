from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT = "change-me-generate-with-openssl-rand-hex-32"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "ResumeIQ"
    app_version: str = "1.0.0"
    debug: bool = False

    # SQLite for local dev; swap to Oracle with:
    # oracle+cx_oracle://user:pass@host:port/service_name
    database_url: str = "sqlite+aiosqlite:///./resume_screener.db"

    log_level: str = "INFO"
    max_page_size: int = 100

    # Comma-separated list of allowed CORS origins
    cors_origins: str = "http://localhost:3000"

    # JWT
    secret_key: str = _INSECURE_DEFAULT
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # short-lived
    refresh_token_expire_days: int = 7

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
