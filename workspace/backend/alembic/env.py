from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401 — ensure all models are registered in Base.metadata
from alembic import context
from app.core.config import settings
from app.core.database import Base

# Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _get_sync_url(url: str) -> str:
    """Convert an async database URL to a sync one for Alembic migrations.

    Replaces the ``+asyncpg`` driver with ``+psycopg2`` so that Alembic
    can run migrations using a synchronous connection.  If the URL does
    not contain ``+asyncpg``, it is returned unchanged.
    """
    return url.replace("+asyncpg", "+psycopg2")


config.set_main_option("sqlalchemy.url", _get_sync_url(settings.DATABASE_URL))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
