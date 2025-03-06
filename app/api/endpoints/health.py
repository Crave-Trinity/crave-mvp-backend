#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
File: health.py
Purpose:
  - Exposes a simple health check at GET /api/health
  - This is used by Railway to confirm your container is healthy.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Health"])
def health_check():
    """
    GET /api/health -> returns 200 OK if healthy
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "CRAVE Trinity Backend",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    )

@router.head("/", tags=["Health"])
def health_check_head():
    """
    HEAD /api/health -> returns 200, no body
    Some platforms do HEAD for health checks
    """
    return JSONResponse(status_code=200, content=None)