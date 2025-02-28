# File: app/infrastructure/database/session.py
# Fix: Correctly use the main settings object, add connect_args for Railway

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from app.config.settings import settings  # Import the main settings object

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

# Get database URL from settings - CORRECTLY, using the main settings
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
print(f"[SESSION] Using database URL: {DATABASE_URL}")

# Detect Railway from URL
is_railway = "railway.app" in DATABASE_URL or ".railway.internal" in DATABASE_URL or "railway." in DATABASE_URL

try:
    # Configure engine with correct parameters
    engine_args = {
        "pool_pre_ping": True,  # Enable connection health checks
        "pool_recycle": 300,  # Recycle connections every 5 minutes
    }

    # Add SSL for Railway connections - THIS IS CRUCIAL
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
    # Instead of continuing, raise the exception to halt startup
    raise  # Re-raise the exception

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()