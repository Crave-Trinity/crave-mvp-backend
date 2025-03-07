# app/api/endpoints/health.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

# Note: The router is mounted with the prefix "/api/health" so we remove the slash from the route.
router = APIRouter(prefix="/api/health", tags=["Health"])

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

@router.head("", tags=["Health"])
def health_check_head():
    return JSONResponse(status_code=200, content=None)