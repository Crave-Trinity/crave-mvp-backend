#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
Health endpoint for CRAVE Trinity Backend.
This endpoint is used by Railway and other systems to verify the service is up.
To avoid issues with trailing slash redirects (which Railway’s healthchecks might not follow),
this endpoint now responds to both "/api/health" and "/api/health/".
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

# Multiple decorators to catch both the trailing and non-trailing slash cases.
@router.get("", tags=["Health"])
@router.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint returning service status, timestamp, and version.
    Accessible via both "/api/health" and "/api/health/" to satisfy Railway healthcheck requirements.
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }