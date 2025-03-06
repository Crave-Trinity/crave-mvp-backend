"""
File: app/api/endpoints/health.py
Purpose:
  - Exposes a simple health check at GET /api/health.
  - This endpoint is used by Railway to confirm your container is healthy.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

# Define a single GET endpoint on the empty string.
# When mounted with a prefix, this becomes exactly /api/health.
@router.get("", tags=["Health"])
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "CRAVE Trinity Backend",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    )

# Also define the HEAD method for completeness.
@router.head("", tags=["Health"])
def health_check_head():
    return JSONResponse(status_code=200, content=None)