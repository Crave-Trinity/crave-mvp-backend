#====================================================
# File: app/api/endpoints/health.py
#====================================================
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint for Railway and monitoring.
    This explicitly responds at '/api/health/'.
    """
    return JSONResponse(status_code=200, content={
        "status": "ok",
        "service": "CRAVE Trinity Backend",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@router.head("/", tags=["Health"])
def health_check_head():
    """
    Head method health check endpoint, explicitly returns 200.
    """
    return JSONResponse(status_code=200, content=None)