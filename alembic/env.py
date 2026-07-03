"""Alembic env.py — uses sync SQLAlchemy engine for migrations."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import Base so all models are registered before metadata is read
from app.database import Base  # noqa: F401
import app.models  # noqa: F401 — registers all ORM classes

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_sync_url() -> str:
    """Return a sync DB URL — strip async driver prefixes."""
    from app.config import get_settings
    url = get_settings().database_url
    return (
        url.replace("sqlite+aiosqlite", "sqlite")
           .replace("+asyncpg", "")
           .replace("+aiohttp", "")
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = _get_sync_url()
    connectable = engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
