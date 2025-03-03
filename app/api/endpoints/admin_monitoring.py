#====================================================
# File: app/api/endpoints/admin_monitoring.py
#====================================================
import os
import logging
import psutil
import time
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, text, inspect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json

# Import your DB, models, and AuthService:
from app.infrastructure.database.session import get_db, engine
from app.infrastructure.database.models import UserModel, CravingModel, VoiceLogModel, Base
from app.infrastructure.auth.auth_service import AuthService
from app.config.settings import Settings

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the router
router = APIRouter()


# -----------------------------------------------------
# Helper function to check if user is admin
# -----------------------------------------------------
def is_admin(user: UserModel) -> bool:
    """
    Check if the user has admin privileges.
    
    In a production system, you would use a proper role-based access
    control system. For this MVP, we're simply checking if user ID = 1.
    """
    return user.id == 1


# -----------------------------------------------------
# Admin-only dependency
# -----------------------------------------------------
def admin_only(current_user: UserModel = Depends(AuthService().get_current_user)):
    """
    Dependency to ensure only admins can access the endpoint.
    Raises 403 if the user is not an admin.
    """
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required."
        )
    return current_user


# -----------------------------------------------------
# GET /api/admin/logs
# -----------------------------------------------------
@router.get("/logs", tags=["Admin"])
async def get_application_logs(
    lines: int = Query(100, ge=1, le=10000, description="Number of log lines to return"),
    admin_user: UserModel = Depends(admin_only)
):
    """
    Retrieve recent application logs (requires admin privileges).
    """
    try:
        settings = Settings()
        log_file_path = getattr(settings, "LOG_FILE_PATH", "app.log")
        
        if not os.path.exists(log_file_path):
            return {
                "status": "warning",
                "message": f"Log file not found at {log_file_path}",
                "logs": []
            }
        
        with open(log_file_path, 'r') as file:
            all_lines = file.readlines()
            log_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "log_file": log_file_path,
            "lines_requested": lines,
            "lines_returned": len(log_lines),
            "logs": log_lines
        }
    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve logs: {str(e)}"
        )


# -----------------------------------------------------
# GET /api/admin/metrics
# -----------------------------------------------------
@router.get("/metrics", tags=["Admin"])
async def get_system_metrics(
    admin_user: UserModel = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """
    Get system and application metrics (CPU, memory, user counts, etc.).
    Requires admin privileges.
    """
    try:
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - psutil.boot_time()
        }
        
        db_metrics = {}
        inspector = inspect(engine)
        
        # Count users
        try:
            user_count = db.query(func.count(UserModel.id)).scalar()
            db_metrics["total_users"] = user_count
            
            # Count active users in last 30 days
            if "last_login_at" in [col["name"] for col in inspector.get_columns("users")]:
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                active_users = db.query(func.count(UserModel.id)).filter(
                    UserModel.last_login_at >= thirty_days_ago
                ).scalar()
                db_metrics["active_users_30d"] = active_users or 0
        except Exception as e:
            db_metrics["users_error"] = str(e)
        
        # Count cravings
        try:
            craving_count = db.query(func.count(CravingModel.id)).scalar()
            db_metrics["total_cravings"] = craving_count
            
            day_ago = datetime.utcnow() - timedelta(days=1)
            recent_cravings = db.query(func.count(CravingModel.id)).filter(
                CravingModel.created_at >= day_ago
            ).scalar()
            db_metrics["cravings_24h"] = recent_cravings or 0
            
            # Average intensity
            avg_intensity = db.query(func.avg(CravingModel.intensity)).scalar()
            db_metrics["avg_intensity"] = round(float(avg_intensity), 2) if avg_intensity else 0
        except Exception as e:
            db_metrics["cravings_error"] = str(e)
        
        # Voice logs
        try:
            voice_log_count = db.query(func.count(VoiceLogModel.id)).scalar()
            db_metrics["total_voice_logs"] = voice_log_count
            transcribed_count = db.query(func.count(VoiceLogModel.id)).filter(
                VoiceLogModel.transcription_status == "COMPLETED"
            ).scalar()
            db_metrics["transcribed_voice_logs"] = transcribed_count or 0
        except Exception as e:
            db_metrics["voice_logs_error"] = str(e)
        
        app_metrics = {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "version": "0.1.0",
            "api_requests_total": 0,
            "api_errors_total": 0
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_metrics,
            "database": db_metrics,
            "application": app_metrics
        }
        
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


# -----------------------------------------------------
# GET /api/admin/health-detailed
# -----------------------------------------------------
@router.get("/health-detailed", tags=["Admin"])
async def detailed_health_check(
    db: Session = Depends(get_db),
    admin_user: UserModel = Depends(admin_only)
):
    """
    Perform a detailed health check of the system (DB, filesystem, memory).
    Requires admin privileges.
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = {
            "status": "ok",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "error"
        health_status["components"]["database"] = {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }
    
    # Check file system
    try:
        temp_file_path = "/tmp/health_check_test.txt"
        with open(temp_file_path, "w") as f:
            f.write("test")
        os.remove(temp_file_path)
        health_status["components"]["filesystem"] = {
            "status": "ok",
            "message": "File system is writable"
        }
    except Exception as e:
        health_status["status"] = "warning"
        health_status["components"]["filesystem"] = {
            "status": "warning",
            "message": f"File system check failed: {str(e)}"
        }
    
    # Memory usage check
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health_status["status"] = "warning"
            health_status["components"]["memory"] = {
                "status": "warning",
                "message": f"High memory usage: {memory.percent}%",
                "details": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                }
            }
        else:
            health_status["components"]["memory"] = {
                "status": "ok",
                "message": f"Memory usage: {memory.percent}%",
                "details": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                }
            }
    except Exception as e:
        health_status["components"]["memory"] = {
            "status": "unknown",
            "message": f"Memory check failed: {str(e)}"
        }
    
    # Schema verification
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = ["users", "cravings", "voice_logs"]
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            health_status["status"] = "warning"
            health_status["components"]["schema"] = {
                "status": "warning",
                "message": f"Missing tables: {', '.join(missing_tables)}",
                "details": {
                    "existing_tables": tables,
                    "missing_tables": missing_tables
                }
            }
        else:
            health_status["components"]["schema"] = {
                "status": "ok",
                "message": "All required tables exist",
                "details": {
                    "tables": tables
                }
            }
    except Exception as e:
        health_status["components"]["schema"] = {
            "status": "unknown",
            "message": f"Schema check failed: {str(e)}"
        }
    
    return health_status


# -----------------------------------------------------
# POST /api/admin/generate-test-token (NO AUTH REQUIRED)
# -----------------------------------------------------
@router.post("/generate-test-token")
def generate_test_token(
    db: Session = Depends(get_db)
):
    """
    Creates a "test" JWT for development without requiring a real user login flow.
    1. Fetch or create user #1
    2. Return {"token": "<JWT>"}
    """
    # 1) Check if user #1 exists
    user = db.query(UserModel).filter(UserModel.id == 1).first()
    if not user:
        user = UserModel(
            id=1,
            email="admin@example.com",
            username="admin",
            hashed_password="fakehash",  # or empty string if your model allows it
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 2) Generate a JWT
    token = AuthService().generate_token(
        user_id=user.id,
        email=user.email
    )
    return {"token": token}