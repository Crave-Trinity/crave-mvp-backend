# File: app/infrastructure/database/voice_logs_repository.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.models import VoiceLogModel

class VoiceLogRepository:  # <-- RENAMED
    """
    Manages CRUD operations for VoiceLogs in the DB.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_voice_log(self, voice_log: VoiceLog) -> VoiceLog:
        db_item = VoiceLogModel(
            user_id=voice_log.user_id,
            file_path=voice_log.file_path,
            created_at=voice_log.created_at,
            transcribed_text=voice_log.transcribed_text,
            transcription_status=voice_log.transcription_status,
            is_deleted=voice_log.is_deleted
        )
        self.db_session.add(db_item)
        self.db_session.commit()
        self.db_session.refresh(db_item)
        return VoiceLog(
            id=db_item.id,
            user_id=db_item.user_id,
            file_path=db_item.file_path,
            created_at=db_item.created_at,
            transcribed_text=db_item.transcribed_text,
            transcription_status=db_item.transcription_status,
            is_deleted=db_item.is_deleted
        )

    # ... (same CRUD methods, just referencing VoiceLogRepository)