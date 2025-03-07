#======================
# app/infrastructure/database/session.py
#======================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.config.settings import get_settings

print("=== DATABASE ENV VARS ===")
for key in sorted(os.environ.keys()):
    if any(db_term in key.lower() for db_term in ["postgres", "pg", "sql", "db"]):
        value = os.environ[key]
        if "password" in key.lower():
            value = "********"
        print(f"  {key}: {value}")
print("========================")

def get_engine():
    """
    Build and return the SQLAlchemy engine using the single DATABASE_URL.
    Enable sslmode=require for Railway if needed.
    """
    settings = get_settings()
    db_url = settings.DATABASE_URL
    print(f"[SESSION] Using database URL: {db_url}")

    is_railway = "railway" in db_url
    engine_args = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    if is_railway:
        engine_args["connect_args"] = {"sslmode": "require"}

    try:
        return create_engine(db_url, **engine_args)
    except Exception as e:
        error_msg = f"Database connection failed: {str(e)}"
        print(f"[SESSION] ERROR: {error_msg}")
        print(f"[SESSION] Connection string: {db_url}")
        raise

engine = get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    """
    Provide a scoped session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()