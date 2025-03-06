#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
File: health.py
Purpose:
  - Defines a simple health check endpoint, crucial for container readiness on Railway.
  - Yields final path => GET /api/health or HEAD /api/health
    (due to main.py prefix="/api/health").
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Health"])
def health_check():
    """
    GET /api/health -> returns JSON status code 200, used by Railway's health check.
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
    HEAD /api/health -> also returns 200, but no body.
    Some platforms do HEAD requests for health checks.
    """
    return JSONResponse(status_code=200, content=None)