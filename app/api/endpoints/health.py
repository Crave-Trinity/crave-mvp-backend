#====================================================
# File: app/api/endpoints/health.py
#====================================================
"""
File: health.py
Purpose:
  - Defines a simple health check endpoint, crucial for container readiness on Railway.
  - Final path => GET /api/health or HEAD /api/health (due to prefix in main.py).
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get(\"/\", tags=[\"Health\"])
def health_check():
    \"\"\"GET /api/health -> returns 200 for Railway's health check.\"\"\"
    return JSONResponse(
        status_code=200,
        content={
            \"status\": \"ok\",
            \"service\": \"CRAVE Trinity Backend\",
            \"timestamp\": datetime.utcnow().isoformat(),
            \"version\": \"1.0.0\"
        }
    )

@router.head(\"/\", tags=[\"Health\"])
def health_check_head():
    \"\"\"HEAD /api/health -> also returns 200, no body. Some environments do HEAD checks.\"\"\"
    return JSONResponse(status_code=200, content=None)