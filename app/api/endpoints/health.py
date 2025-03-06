"""
File: app/api/endpoints/health.py
Purpose:
  - Exposes a simple health check at GET /api/health.
  - This endpoint is used by Railway to confirm your container is healthy.
"""
# app/api/endpoints/health.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Health"])
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

@router.head("/", tags=["Health"])
def health_check_head():
    return JSONResponse(status_code=200, content=None)