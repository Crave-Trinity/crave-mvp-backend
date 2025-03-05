#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
Health endpoint for CRAVE Trinity Backend.
This endpoint is used by Railway and other systems to verify that the service is up.
We've added support for both GET and HEAD requests (with and without trailing slashes)
to ensure Railway's healthcheck, which may use HEAD, receives a 200 OK response.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

# Support GET on both "/api/health" and "/api/health/"
@router.get("", tags=["Health"])
@router.get("/", tags=["Health"])
def health_check_get():
    """
    GET health check endpoint returning JSON with status information.
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# Support HEAD on both "/api/health" and "/api/health/"
@router.head("", tags=["Health"])
@router.head("/", tags=["Health"])
def health_check_head():
    """
    HEAD health check endpoint returning an empty body.
    FastAPI will automatically set the status to 200 OK.
    """
    return {}