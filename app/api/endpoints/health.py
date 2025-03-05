#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
Health endpoint for CRAVE Trinity Backend.
This endpoint is used by Railway to verify that the service is up.
We disable automatic trailing slash redirection to ensure Railway’s healthcheck
receives a 200 OK response without triggering a redirect.
"""

from fastapi import APIRouter
from datetime import datetime

# Disable redirect_slashes to avoid automatic 307 redirects when the trailing slash is missing.
router = APIRouter(redirect_slashes=False)

@router.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint returning JSON with status, timestamp, and version.
    With redirect_slashes disabled, both "/api/health" and "/api/health/" will match this endpoint.
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }