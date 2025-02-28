"""
app/api/main.py

Defines the FastAPI instance and includes routers for all endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import get_settings
from app.api.endpoints import (
    health,
    auth_endpoints,
    craving_logs,
    search_cravings,
    ai_endpoints,
    analytics,
    admin,
    admin_monitoring,
    user_queries,
    voice_logs_endpoints,
    voice_logs_enhancement,
)

app = FastAPI(
    title="CRAVE Trinity Backend",
    description="A modular, AI-powered backend for craving analytics",
    version="0.1.0",
)

# Add CORS middleware (be sure to lock this down in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initialize settings on startup (read environment variables, etc.).
    """
    get_settings()  # calling get_settings() ensures env variables are loaded


# Include routers from all endpoints
app.include_router(health.router, prefix="/api/health")
app.include_router(auth_endpoints.router, prefix="/api/auth")
app.include_router(craving_logs.router, prefix="/api/cravings")
app.include_router(search_cravings.router, prefix="/api/cravings")
app.include_router(ai_endpoints.router, prefix="/api/ai")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(admin_monitoring.router, prefix="/api/admin")
app.include_router(user_queries.router, prefix="/api/cravings/user")
app.include_router(voice_logs_endpoints.router, prefix="/api/voice-logs")
app.include_router(voice_logs_enhancement.router, prefix="/api/voice-logs")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "CRAVE Trinity Backend",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def railway_health():
    """
    Health check endpoint (Railway expects /health by default).
    """
    return {"status": "ok", "service": "CRAVE Trinity Backend"}
