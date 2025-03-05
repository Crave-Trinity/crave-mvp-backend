# crave_trinity_backend/app/api/endpoints/health.py (CORRECTED)
"""
Health endpoint for CRAVE Trinity Backend.
This endpoint is used by Railway and other systems to verify the service is up.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

# With the router mounted at /api/health, this endpoint becomes:
# GET /api/health/
@router.get("/", tags=["Health"])
def health_check():
    """
    Simple health check endpoint returning service status, timestamp, and version.
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }