# File: app/infrastructure/database/session.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.config.settings import get_settings  # Import get_settings

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


def get_engine():
    # Get database URL from settings using get_settings()
    settings = get_settings()
    DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
    print(f"[SESSION] Using database URL: {DATABASE_URL}")

    # Detect Railway from URL
    is_railway = (
        "railway.app" in DATABASE_URL 
        or ".railway.internal" in DATABASE_URL 
        or "railway." in DATABASE_URL
    )

    try:
        # Configure engine with correct parameters
        engine_args = {
            "pool_pre_ping": True,   # Enable connection health checks
            "pool_recycle": 300,     # Recycle connections every 5 minutes
        }

        # Add SSL for Railway connections - THIS IS CRUCIAL
        if is_railway:
            engine_args["connect_args"] = {"sslmode": "require"}

        # Create engine with all parameters
        engine = create_engine(DATABASE_URL, **engine_args)
        return engine

    except Exception as e:
        error_msg = f"Database connection failed: {str(e)}"
        print(f"[SESSION] ERROR: {error_msg}")
        print(f"[SESSION] Connection string: {DATABASE_URL}")
        # Raise the exception to halt startup
        raise

engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def get_db():
    """
    FastAPI dependency that creates a new database session for a request,
    and ensures it is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
