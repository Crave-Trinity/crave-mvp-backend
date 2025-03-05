#====================================================
# File: app/api/main.py
#====================================================
"""
Main application entrypoint file for CRAVE Trinity Backend.
Clearly initializes FastAPI, configures CORS, and explicitly includes all endpoint routers.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Explicit imports for all endpoint routers
from app.api.endpoints.health import router as health_router
from app.api.endpoints.auth_endpoints import router as auth_router
from app.api.endpoints.oauth_endpoints import router as oauth_router  # OAuth explicitly imported
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

# Explicit import of project-wide settings
from app.config.settings import settings

# Initialize FastAPI application explicitly with metadata
app = FastAPI(title=settings.PROJECT_NAME, version="1.0")

# Explicit CORS configuration allowing requests from any origin (adjust explicitly for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint routers explicitly integrated with clear prefixes and tags
app.include_router(health_router, prefix="/api/health", tags=["Health"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(oauth_router, prefix="/auth/oauth", tags=["OAuth"])  # OAuth explicitly integrated here
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_monitoring_router, prefix="/admin/monitoring", tags=["AdminMonitoring"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(craving_logs_router, prefix="", tags=["Cravings"])
app.include_router(live_updates_router, prefix="/live", tags=["LiveUpdates"])
app.include_router(search_cr