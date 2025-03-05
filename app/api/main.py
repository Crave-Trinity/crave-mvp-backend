#====================================================
# File: app/api/main.py
#====================================================
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import our endpoints
from app.api.endpoints.health import router as health_router
from app.api.endpoints.auth_endpoints import router as auth_router
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

# Configuration
from app.config.settings import settings

# Initialize FastAPI
app = FastAPI(title=settings.PROJECT_NAME, version="1.0")

# Allow CORS from anywhere (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_monitoring_router, prefix="/admin/monitoring", tags=["AdminMonitoring"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(craving_logs_router, prefix="", tags=["Cravings"])  # e.g., /cravings
app.include_router(live_updates_router, prefix="/live", tags=["LiveUpdates"])
app.include_router(search_cravings_router, prefix="/search", tags=["CravingsSearch"])
app.include_router(user_queries_router, prefix="/queries", tags=["UserQueries"])
app.include_router(voice_logs_endpoints_router, prefix="/voice-logs", tags=["VoiceLogs"])
app.include_router(voice_logs_enhancement_router, prefix="/voice-logs-enhancement", tags=["VoiceLogsEnhancement"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to CRAVE Trinity Backend. Healthy logging and analytics ahead!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)