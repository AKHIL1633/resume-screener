"""Alembic env.py — supports async SQLAlchemy engine (aiosqlite / cx_Oracle)."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

# Import Base so all models are registered before metadata is read
from app.database import Base  # noqa: F401
import app.models  # noqa: F401 — registers all ORM classes

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Prefer DATABASE_URL env var; fall back to alembic.ini value."""
    from app.config import get_settings
    url = get_settings().database_url
    # Alembic needs a sync driver — strip the async prefix
    return url.replace("sqlite+aiosqlite", "sqlite").replace("+asyncpg", "").replace("+aiohttp", "")


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # Use the async engine but hand a sync connection to Alembic via run_sync
    connectable = create_async_engine(_get_url(), poolclass=pool.NullPool)
    async with connectable.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
