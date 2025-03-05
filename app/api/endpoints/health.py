#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
Health endpoint for CRAVE Trinity Backend.
This endpoint is used by Railway to verify that the service is up.
We explicitly handle both the empty path ("") and the "/" path within the mounted router,
so that both "/api/health" and "/api/health/" return 200 OK.
Additionally, HEAD requests are supported for both paths.
"""

from fastapi import APIRouter
from datetime import datetime

# Disable automatic trailing slash redirection to control routing explicitly.
router = APIRouter(redirect_slashes=False)

# GET handler for requests to "/api/health" (empty path after mounting).
@router.get("", tags=["Health"])
def health_check_empty_get():
    """
    GET health check for empty path.
    This handles requests made to "/api/health" (without a trailing slash).
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# GET handler for requests to "/api/health/".
@router.get("/", tags=["Health"])
def health_check_slash_get():
    """
    GET health check for slash path.
    This handles requests made to "/api/health/" (with a trailing slash).
    """
    return {
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

# HEAD handler for requests to "/api/health" (empty path).
@router.head("")
def health_check_empty_head():
    """
    HEAD health check for empty path.
    Ensures that a HEAD request to "/api/health" returns 200 OK.
    """
    return {}

# HEAD handler for requests to "/api/health/".
@router.head("/")
def health_check_slash_head():
    """
    HEAD health check for slash path.
    Ensures that a HEAD request to "/api/health/" returns 200 OK.
    """
    return {}