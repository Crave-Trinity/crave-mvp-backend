#====================================================
# File: app/api/main.py
#====================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth_endpoints.router, prefix="/api/auth")
app.include_router(craving_logs.router, prefix="/api/cravings")
app.include_router(search_cravings.router, prefix="/api/cravings")
app.include_router(ai_endpoints.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(admin.router, prefix="/api/admin")
app.include_router(admin_monitoring.router, prefix="/api/admin")
app.include_router(user_queries.router, prefix="/api/cravings/user")
app.include_router(voice_logs_endpoints.router, prefix="/api/voice-logs")
app.include_router(voice_logs_enhancement.router, prefix="/api/voice-logs")


@app.get("/")
async def root():
    return {
        "service": "CRAVE Trinity Backend",
        "status": "running",
        "docs": "/docs"
    }