# File: app/api/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.utils.logger import get_logger

# Import all your endpoint routers
from app.api.endpoints.health import router as health_router
from app.api.endpoints.auth_endpoints import router as auth_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.admin_monitoring import router as admin_monitoring_router
from app.api.endpoints.ai_endpoints import router as ai_router
from app.api.endpoints.analytics import router as analytics_router
from app.api.endpoints.craving_logs import router as craving_logs_router
from app.api.endpoints.search_cravings import router as search_cravings_router
from app.api.endpoints.user_queries import router as user_queries_router
from app.api.endpoints.voice_logs_endpoints import router as voice_logs_endpoints_router
from app.api.endpoints.voice_logs_enhancement import router as voice_logs_enhancement_router

logger = get_logger("main")

app = FastAPI()

# ----------------------------------------
# CORS Setup
# ----------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Include Routers
# ----------------------------------------
app.include_router(health_router)  # /api/health
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_monitoring_router, prefix="/admin/monitoring", tags=["AdminMonitoring"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(search_cravings_router, prefix="/search", tags=["CravingsSearch"])
app.include_router(user_queries_router, prefix="/queries", tags=["UserQueries"])
app.include_router(voice_logs_endpoints_router, prefix="/voice-logs", tags=["VoiceLogs"])
app.include_router(voice_logs_enhancement_router, prefix="/voice-logs-enhancement", tags=["VoiceLogsEnhancement"])
app.include_router(craving_logs_router, prefix="/cravings", tags=["Cravings"])

# ----------------------------------------
# Root Endpoint
# ----------------------------------------
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to CRAVE Trinity Backend. Healthy logging and analytics ahead!"}

# ----------------------------------------
# Request/Response Middleware
# ----------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "N/A")
    logger.info(
        "Incoming request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
        }
    )

    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.error(
            "Unhandled exception in middleware",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise

    duration = time.time() - start_time
    logger.info(
        "Completed request",
        extra={
            "request_id": request_id,
            "status_code": response.status_code,
            "duration": round(duration, 4)
        }
    )
    return response

# ----------------------------------------
# Global Exception Handler
# ----------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unhandled exceptions.
    Log the error and return a 500 response with minimal info.
    """
    request_id = request.headers.get("X-Request-ID", "N/A")
    logger.error(
        "Unhandled server error",
        exc_info=True,
        extra={"request_id": request_id, "path": str(request.url)}
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal Server Error",
            "request_id": request_id
        }
    )