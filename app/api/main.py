"""
app/api/main.py

Defines the FastAPI instance and includes routers for all endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your routers. Adjust these imports to match your project structure.
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

# Create the FastAPI application instance
app = FastAPI(
    title="CRAVE Trinity Backend",
    description="A modular, AI-powered backend for craving analytics",
    version="0.1.0",
)

# Configure CORS middleware (lock this down for production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from various endpoints
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

# Root endpoint (for quick info)
@app.get("/")
async def root():
    return {
        "service": "CRAVE Trinity Backend",
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint for Railway and other monitoring
@app.get("/health")
async def health():
    return {"status": "ok", "service": "CRAVE Trinity Backend"}