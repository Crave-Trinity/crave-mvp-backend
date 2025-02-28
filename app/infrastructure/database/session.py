# File: app/infrastructure/database/session.py
# Purpose: Configure SQLAlchemy database connection
# Changes: Add support for Railway's SSL requirements and better error handling

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
import sys

# Debug: Print the database connection string when starting the app
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
print(f"Connecting to database: {DATABASE_URL}")

# Check if we're connecting to Railway
is_railway = "railway.internal" in DATABASE_URL or "rlwy.net" in DATABASE_URL
print(f"Railway environment detected: {is_railway}")

try:
    # Configure the SQLAlchemy engine with appropriate settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        # Add SSL requirement for Railway PostgreSQL connections
        connect_args={"sslmode": "require"} if is_railway else {}
    )
    
    # Test the connection immediately to catch issues early
    with engine.connect() as conn:
        conn.execute("SELECT 1")
        print("Database connection successful!")
        
except Exception as e:
    print(f"ERROR - Database connection failed: {str(e)}")
    print(f"Using connection string: {DATABASE_URL}")
    print(f"Environment variables:")
    print(f"  DATABASE_URL: {sys.environ.get('DATABASE_URL', 'Not set')}")
    print(f"  SQLALCHEMY_DATABASE_URI: {sys.environ.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    # Don't raise here, let the application start and show proper error messages

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Creates a new SQLAlchemy SessionLocal that will be used in a single request,
    and then closes it once the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()