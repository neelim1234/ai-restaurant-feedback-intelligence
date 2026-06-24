"""
alembic/env.py - Alembic migration environment.

Key behaviors:
  - DATABASE_URL is loaded from .env via config.py (single source of truth).
  - All models are imported via models/__init__.py so autogenerate detects them.
  - Supports both online (--sql) and offline modes.
"""

from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Add backend/ to sys.path so we can import application modules
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# ---------------------------------------------------------------------------
# Load app settings and override the alembic.ini URL
# ---------------------------------------------------------------------------
from config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

# Override the sqlalchemy.url with the real DATABASE_URL from .env
alembic_config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# ---------------------------------------------------------------------------
# Import all models so autogenerate can detect them
# ---------------------------------------------------------------------------
import models  # noqa: F401 — side effect: registers all models with Base.metadata
from database import Base

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Migration functions
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    Configures the context with just a URL and not an Engine.
    Calls to context.execute() here emit the given string to the script output.
    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    Creates an Engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,      # Detect column type changes
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
