# File: app/infrastructure/database/session.py
# Fix: Add better error handling and SSL support for Railway

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import sys
from pydantic import Field  # Import Field
from pydantic_settings import BaseSettings, SettingsConfigDict # Import BaseSettings
from typing import Optional

class SessionSettings(BaseSettings): # Create a class for settings
    SQLALCHEMY_DATABASE_URI: str = Field(default_factory=lambda: SessionSettings._get_database_url())
    @staticmethod
    def _get_database_url() -> str:
        """Robust database URL detection for Railway and local development."""
        url: Optional[str] = os.environ.get("DATABASE_URL") or \
               os.environ.get("SQLALCHEMY_DATABASE_URI") or \
               os.environ.get("POSTGRES_URL")
        if url:
            return url

        if all(key in os.environ for key in ["PGUSER", "PGPASSWORD", "PGHOST"]):
            user = os.environ["PGUSER"]
            password = os.environ["PGPASSWORD"]
            host = os.environ["PGHOST"]
            port = os.environ.get("PGPORT", "5432")
            dbname = os.environ.get("PGDATABASE", "railway")
            return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        return "postgresql://postgres:password@localhost:5432/crave_db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = SessionSettings() # Create an instance of settings.

# Debug: Print all database-related environment variables
print("=== DATABASE ENV VARS ===")
for key in sorted(os.environ.keys()):
    if any(db_term in key.lower() for db_term in ["postgres", "pg", "sql", "db"]):
        # Mask passwords
        value = os.environ[key]
        if "password" in key.lower():
            value = "********"
        print(f"  {key}: {value}")
print("========================")

# Get database URL from settings
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
print(f"[SESSION] Using database URL: {DATABASE_URL}")

# Detect Railway from URL
is_railway = any(domain in DATABASE_URL for domain in
                ["railway.internal", "rlwy.net", ".railway.app"])
print(f"[SESSION] Railway environment detected: {is_railway}")

try:
    # Configure engine with correct parameters
    engine_args = {
        "pool_pre_ping": True,
        "pool_recycle": 300,  # Recycle connections every 5 minutes
    }

    # Add SSL for Railway connections
    if is_railway:
        engine_args["connect_args"] = {"sslmode": "require"}

    # Create engine with all parameters
    engine = create_engine(DATABASE_URL, **engine_args)

    # Test connection immediately
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print(f"[SESSION] Database connection test result: {result}")

except Exception as e:
    error_msg = f"Database connection failed: {str(e)}"
    print(f"[SESSION] ERROR: {error_msg}")
    print(f"[SESSION] Connection string: {DATABASE_URL}")

    # Continue execution to allow application to start with proper error messages

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()