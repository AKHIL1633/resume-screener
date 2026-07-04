from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings

_INSECURE_DEFAULT = "change-me-generate-with-openssl-rand-hex-32"


class Settings(BaseSettings):
    app_name: str = "ResumeIQ"
    app_version: str = "1.0.0"
    debug: bool = False

    # SQLite for local dev; swap to Oracle with:
    # oracle+cx_oracle://user:pass@host:port/service_name
    database_url: str = "sqlite+aiosqlite:///./resume_screener.db"

    log_level: str = "INFO"
    max_page_size: int = 100

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

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
