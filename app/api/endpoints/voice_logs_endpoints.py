#====================================================
# File: app/api/endpoints/voice_logs_endpoints.py
#====================================================

import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ConfigDict

# CHANGED: Import the renamed VoiceLogRepository (singular)
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository

from app.core.services.voice_logs_service import VoiceLogsService
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import SessionLocal
from app.core.entities.voice_log_schemas import VoiceLogCreate, VoiceLogOut
from app.infrastructure.database.models import UserModel
from app.infrastructure.external.transcription_service import TranscriptionService

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_voice_logs_service(db: Session = Depends(get_db)) -> VoiceLogsService:
    # CHANGED: Create the repo with VoiceLogRepository (no "s")
    repo = VoiceLogRepository(db)
    return VoiceLogsService(repo)

@router.post("/", response_model=VoiceLogOut, status_code=status.HTTP_201_CREATED)
async def create_voice_log(
    file: UploadFile = File(...),
    payload: VoiceLogCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file or unable to read file bytes."
        )
    repo = VoiceLogRepository(db)
    service = VoiceLogsService(repo)
    voice_log = service.upload_new_voice_log(
        user_id=current_user.id,
        audio_bytes=audio_bytes
    )
    return VoiceLogOut(model_config=ConfigDict(from_attributes=True), **voice_log.dict())

@router.post("/{voice_log_id}/transcribe", response_model=VoiceLogOut)
def transcribe_voice_log(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    repo = VoiceLogRepository(db)
    service = VoiceLogsService(repo)
    voice_log = repo.get_by_id(voice_log_id)
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(status_code=404, detail="Voice log not found or inaccessible.")

    transcription_service = TranscriptionService()
    updated_in_progress = service.trigger_transcription(voice_log_id)
    if not updated_in_progress:
        raise HTTPException(status_code=404, detail="Voice log not found or already deleted.")

    transcription_text = transcription_service.transcribe_audio(updated_in_progress)
    completed_log = service.complete_transcription(voice_log_id, transcription_text)
    return VoiceLogOut(model_config=ConfigDict(from_attributes=True), **completed_log.dict()) if completed_log else None

@router.get("/{voice_log_id}/transcript")
def get_transcript(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    repo = VoiceLogRepository(db)
    voice_log = repo.get_by_id(voice_log_id)
    if not voice_log or voice_log.is_deleted or voice_log.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Voice log not found or inaccessible.")

    return {
        "voice_log_id": voice_log.id,
        "transcribed_text": voice_log.transcribed_text,
        "transcription_status": voice_log.transcription_status
    }

@router.get("/", response_model=list[VoiceLogOut])
def list_voice_logs(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    repo = VoiceLogRepository(db)
    logs = repo.list_by_user(current_user.id)
    return [VoiceLogOut(model_config=ConfigDict(from_attributes=True), **log.dict()) for log in logs]

@router.delete("/{voice_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_voice_log(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    repo = VoiceLogRepository(db)
    voice_log = repo.get_by_id(voice_log_id)
    if not voice_log or voice_log.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Voice log not found or inaccessible.")

    success = repo.soft_delete(voice_log_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete voice log.")
    return