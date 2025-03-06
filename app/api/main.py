"""
File: app/api/main.py
Purpose:
    - Defines the main FastAPI app.
    - Registers routers for health, authentication, OAuth, admin, etc.
    - Does not hard-code port settings; entrypoint.sh handles that.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router modules.
from app.api.endpoints.health import router as health_router
from app.api.endpoints.auth_endpoints import router as auth_router
from app.api.endpoints.oauth_endpoints import router as oauth_router
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.admin_monitoring import router as admin_monitoring_router
from app.api.endpoints.ai_endpoints import router as ai_router
from app.api.endpoints.analytics import router as analytics_router
from app.api.endpoints.craving_logs import router as craving_logs_router
from app.api.endpoints.live_updates import router as live_updates_router
from app.api.endpoints.search_cravings import router as search_cravings_router
from app.api.endpoints.user_queries import router as user_queries_router
from app.api.endpoints.voice_logs_endpoints import router as voice_logs_endpoints_router
from app.api.endpoints.voice_logs_enhancement import router as voice_logs_enhancement_router

from app.config.settings import settings

# Create the FastAPI instance.
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0",
    description="CRAVE Trinity Backend..."
)

# Configure CORS to allow requests from any origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Register API routers with appropriate prefixes.
# -------------------------------

# Register the health router.
# Mounting with prefix "/api/health" makes the final endpoint exactly /api/health.
app.include_router(health_router, prefix="/api/health", tags=["Health"])

# Authentication routes.
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])

# Google OAuth endpoints.
app.include_router(oauth_router, prefix="/auth/oauth", tags=["OAuth"])

# Admin endpoints.
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_monitoring_router, prefix="/admin/monitoring", tags=["AdminMonitoring"])

# AI endpoints.
app.include_router(ai_router, prefix="/ai", tags=["AI"])

# Analytics endpoints.
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

# Cravings-related endpoints.
app.include_router(craving_logs_router, prefix="", tags=["Cravings"])
app.include_router(live_updates_router, prefix="/live", tags=["LiveUpdates"])
app.include_router(search_cravings_router, prefix="/search", tags=["CravingsSearch"])
app.include_router(user_queries_router, prefix="/queries", tags=["UserQueries"])

# Voice logs endpoints.
app.include_router(voice_logs_endpoints_router, prefix="/voice-logs", tags=["VoiceLogs"])
app.include_router(voice_logs_enhancement_router, prefix="/voice-logs-enhancement", tags=["VoiceLogsEnhancement"])

# Root endpoint.
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to CRAVE Trinity Backend. Healthy logging and analytics ahead!"}

# Note: No duplicate or fallback /api/health endpoint is defined here.