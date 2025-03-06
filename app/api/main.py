################################################################################
#                                                                              
#  "I understand there's a guy inside me who wants to lay in bed,              
#   smoke weed 🍃 all day, and watch cartoons and old movies.                     
#   My whole life is a series of stratagems to avoid, and outwit, that guy."  
#                                                                              
#   - Anthony Bourdain                                                                                                                         
#                                                                              
################################################################################
#
#
#
#

# File: app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import endpoints (ensure these modules exist and have __init__.py files)
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

app = FastAPI()

# Setup CORS middleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers.
app.include_router(health_router)  # Health endpoint: /api/health/
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(admin_monitoring_router, prefix="/admin/monitoring", tags=["AdminMonitoring"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(search_cravings_router, prefix="/search", tags=["CravingsSearch"])
app.include_router(user_queries_router, prefix="/queries", tags=["UserQueries"])
app.include_router(voice_logs_endpoints_router, prefix="/voice-logs", tags=["VoiceLogs"])
app.include_router(voice_logs_enhancement_router, prefix="/voice-logs-enhancement", tags=["VoiceLogsEnhancement"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to CRAVE Trinity Backend. Healthy logging and analytics ahead!"}