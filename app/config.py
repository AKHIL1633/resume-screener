from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ResumeIQ"
    app_version: str = "1.0.0"
    debug: bool = False

    # SQLite for local dev; swap to Oracle with:
    # oracle+cx_oracle://user:pass@host:port/service_name
    database_url: str = "sqlite+aiosqlite:///./resume_screener.db"

    log_level: str = "INFO"
    max_page_size: int = 100

    # JWT — override SECRET_KEY with a long random string in production
    secret_key: str = "change-me-generate-with-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480  # 8 hours

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
