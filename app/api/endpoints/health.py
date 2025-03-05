#====================================================
# File: app/api/endpoints/health.py
#====================================================
from fastapi import APIRouter
from datetime import datetime
from fastapi.responses import JSONResponse

router = APIRouter()

# Only one explicit path to avoid confusion
@router.get("/")
def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "CRAVE Trinity Backend",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0"
        }
    )

# Explicit HEAD request handler
@router.head("/")
def health_check_head():
    return JSONResponse(status_code=200, content=None)