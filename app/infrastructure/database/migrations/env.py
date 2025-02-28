# File: app/infrastructure/database/migrations/env.py
# Fix: Properly handle DATABASE_URL from Railway and add more robust env var handling

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.config.settings import settings  # Import settings to get DB URL

# Import your Base from models
from app.infrastructure.database.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use settings DB URL with Railway/PG fallbacks (more reliable)
db_url = settings.SQLALCHEMY_DATABASE_URI
print(f"Alembic using database URL: {db_url}")

# Override sqlalchemy.url in alembic.ini
config.set_main_option("sqlalchemy.url", db_url)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
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

def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Add SSL requirement for Railway connections
    is_railway = "railway.internal" in db_url or "rlwy.net" in db_url
    
    # Create connectable with proper configuration
    configuration = config.get_section(config.config_ini_section)
    
    # For Railway: Add SSL options to configuration
    if is_railway:
        configuration["sqlalchemy.connect_args"] = {"sslmode": "require"}
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()