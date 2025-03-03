#======================
# app/api/endpoints/admin.py
#======================
from fastapi import APIRouter
from sqlalchemy import create_engine, text
import alembic.config
import alembic.command
import logging
import os

from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/stamp-db")
def stamp_db():
    """
    Stamp the DB to 'head' so Alembic won't re-create existing tables.
    """
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic.command.stamp(alembic_cfg, "head")
    return {"detail": "Database successfully stamped to 'head'."}

@router.post("/add-missing-column")
def add_missing_column():
    """
    Directly add the missing is_deleted column to cravings if needed.
    """
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.begin() as conn:
            result = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='is_deleted'"
            ))
            if result.scalar():
                return {"message": "Column is_deleted already exists"}
            conn.execute(text(
                "ALTER TABLE cravings ADD COLUMN is_deleted BOOLEAN DEFAULT false NOT NULL"
            ))
        return {"message": "Successfully added is_deleted column"}
    except Exception as e:
        return {"error": str(e)}

@router.post("/add-missing-columns")
def add_missing_columns():
    """
    Add missing columns to cravings table if needed.
    """
    engine = create_engine(settings.DATABASE_URL)
    results = {}
    try:
        with engine.begin() as conn:
            # user_id
            r = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='user_id'"
            ))
            user_id_exists = bool(r.scalar())
            if not user_id_exists:
                conn.execute(text(
                    "ALTER TABLE cravings ADD COLUMN user_id INTEGER DEFAULT 1 NOT NULL"
                ))
                results["user_id"] = "Added column"
            else:
                results["user_id"] = "Column already exists"

            # updated_at
            r = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='updated_at'"
            ))
            updated_at_exists = bool(r.scalar())
            if not updated_at_exists:
                conn.execute(text(
                    "ALTER TABLE cravings ADD COLUMN updated_at TIMESTAMP DEFAULT NOW() NOT NULL"
                ))
                conn.execute(text("""
                    CREATE OR REPLACE FUNCTION update_modified_column()
                    RETURNS TRIGGER AS $$
                    BEGIN
                        NEW.updated_at = now();
                        RETURN NEW;
                    END;
                    $$ language 'plpgsql';

                    DROP TRIGGER IF EXISTS update_cravings_updated_at ON cravings;

                    CREATE TRIGGER update_cravings_updated_at
                    BEFORE UPDATE ON cravings
                    FOR EACH ROW
                    EXECUTE FUNCTION update_modified_column();
                """))
                results["updated_at"] = "Added column and trigger"
            else:
                results["updated_at"] = "Column already exists"

        return {"success": True, "columns_added": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.post("/fix-database")
def fix_database():
    """
    Perform a comprehensive DB fix, including adding columns and stamping.
    """
    columns_result = add_missing_columns()
    stamp_result = stamp_db()
    return {
        "columns_operation": columns_result,
        "stamp_operation": stamp_result,
        "message": "Database fix operations completed"
    }

@router.get("/verify-schema")
def verify_schema():
    """
    Check if the DB schema has the required columns.
    """
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.connect() as conn:
            r = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='is_deleted'"
            ))
            is_deleted_exists = bool(r.scalar())

            r = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='user_id'"
            ))
            user_id_exists = bool(r.scalar())

            r = conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name='cravings' AND column_name='updated_at'"
            ))
            updated_at_exists = bool(r.scalar())

            return {
                "schema_status": "ok" if (is_deleted_exists and user_id_exists) else "missing_columns",
                "columns": {
                    "is_deleted": is_deleted_exists,
                    "user_id": user_id_exists,
                    "updated_at": updated_at_exists
                }
            }
    except Exception as e:
        return {"error": str(e)}