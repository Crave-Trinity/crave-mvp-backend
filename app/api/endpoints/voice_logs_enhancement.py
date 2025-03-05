#====================================================
# File: app/api/endpoints/voice_logs_enhancement.py
#====================================================

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import ConfigDict

from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel

# CHANGED: Import the renamed VoiceLogRepository (singular)
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository

from app.core.services.voice_logs_service import VoiceLogsService
from app.infrastructure.external.transcription_service import TranscriptionService
from app.core.entities.voice_log_schemas import VoiceLogCreate, VoiceLogOut
from app.core.entities.voice_log import VoiceLog

router = APIRouter()

def get_voice_logs_service(db: Session = Depends(get_db)) -> VoiceLogsService:
    # CHANGED: Use VoiceLogRepository (singular) when creating the service
    repo = VoiceLogRepository(db)
    return VoiceLogsService(repo)

@router.post("/{voice_log_id}/retry-transcription", response_model=VoiceLogOut)
async def retry_transcription(
    voice_log_id: int,
    background_tasks: BackgroundTasks,
    service: VoiceLogsService = Depends(get_voice_logs_service),
    current_user: UserModel = Depends(AuthService().get_current_user)
):
    voice_log = service.get_voice_log(voice_log_id)
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice log not found or inaccessible"
        )
    if voice_log.transcription_status == "COMPLETED" and voice_log.transcribed_text:
        return VoiceLogOut(**voice_log.dict())

    updated_log = service.trigger_transcription(voice_log_id)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update voice log status"
        )

    background_tasks.add_task(
        service.process_transcription,
        voice_log_id
    )
    return VoiceLogOut(**updated_log.dict())

@router.get("/{voice_log_id}/status", response_model=Dict[str, Any])
async def get_transcription_status(
    voice_log_id: int,
    service: VoiceLogsService = Depends(get_voice_logs_service),
    current_user: UserModel = Depends(AuthService().get_current_user)
):
    voice_log = service.get_voice_log(voice_log_id)
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice log not found or inaccessible"
        )
    return {
        "id": voice_log.id,
        "created_at": voice_log.created_at.isoformat(),
        "transcription_status": voice_log.transcription_status,
        "has_transcript": bool(voice_log.transcribed_text),
        "transcript_length": len(voice_log.transcribed_text) if voice_log.transcribed_text else 0,
        "last_updated": voice_log.updated_at.isoformat() if hasattr(voice_log, "updated_at") and voice_log.updated_at else None
    }

@router.post("/{voice_log_id}/analyze", response_model=Dict[str, Any])
async def analyze_voice_log(
    voice_log_id: int,
    service: VoiceLogsService = Depends(get_voice_logs_service),
    current_user: UserModel = Depends(AuthService().get_current_user)
):
    voice_log = service.get_voice_log(voice_log_id)
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice log not found or inaccessible"
        )
    if voice_log.transcription_status != "COMPLETED" or not voice_log.transcribed_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice log has not been transcribed yet"
        )
    text = voice_log.transcribed_text.lower()
    positive_words = ["good", "great", "happy", "positive", "excited", "love", "enjoy"]
    negative_words = ["bad", "sad", "angry", "upset", "hate", "dislike", "struggle"]
    pos_count = sum(1 for word in positive_words if word in text.split())
    neg_count = sum(1 for word in negative_words if word in text.split())
    sentiment = "neutral"
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    topics = []
    potential_topics = ["food", "exercise", "sleep", "work", "stress", "family", "health"]
    for topic in potential_topics:
        if topic in text:
            topics.append(topic)
    word_count = len(text.split())
    return {
        "voice_log_id": voice_log.id,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "sentiment": sentiment,
        "topics": topics,
        "word_count": word_count,
        "positive_words": pos_count,
        "negative_words": neg_count
    }