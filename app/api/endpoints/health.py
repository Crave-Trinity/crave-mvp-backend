#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
Health endpoint for CRAVE Trinity Backend.
This endpoint is used by Railway to verify that the service is up.
We've explicitly added both GET and HEAD handlers and disabled
automatic trailing slash redirection so that Railway's healthcheck
receives a 200 OK response without any redirects.
"""

from fastapi import APIRouter
from datetime import datetime

# Disable automatic trailing slash redirection
router = APIRouter(redirect_slashes=False)

# Explicit GET handler for the health check.
@router.get("/", tags=["Health"])
def health_check_get():
    """
    GET health check endpoint returning JSON with status, timestamp, and version.
    Accessible via both "/api/health" and "/api/health/".
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# Explicit HEAD handler for the health check.
@router.head("/", tags=["Health"])
def health_check_head():
    """
    HEAD health check endpoint returning an empty body.
    This ensures that if Railway sends a HEAD request, it receives a 200 OK.
    """
    return {}