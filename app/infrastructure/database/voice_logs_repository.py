#====================================================
# File: app/infrastructure/database/voice_logs_repository.py
#====================================================

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.models import VoiceLogModel

class VoiceLogRepository:
    """
    Manages CRUD operations for VoiceLog in the DB.
    (Renamed to 'VoiceLogRepository' to match all imports consistently.)
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

    def get_by_id(self, voice_log_id: int) -> Optional[VoiceLog]:
        db_item = self.db_session.query(VoiceLogModel).filter(
            VoiceLogModel.id == voice_log_id,
            VoiceLogModel.is_deleted == False
        ).first()
        if db_item:
            return VoiceLog(
                id=db_item.id,
                user_id=db_item.user_id,
                file_path=db_item.file_path,
                created_at=db_item.created_at,
                transcribed_text=db_item.transcribed_text,
                transcription_status=db_item.transcription_status,
                is_deleted=db_item.is_deleted
            )
        return None

    def list_by_user(self, user_id: int) -> List[VoiceLog]:
        query = self.db_session.query(VoiceLogModel).filter(
            VoiceLogModel.user_id == user_id,
            VoiceLogModel.is_deleted == False
        ).order_by(VoiceLogModel.created_at.desc())
        return [
            VoiceLog(
                id=item.id,
                user_id=item.user_id,
                file_path=item.file_path,
                created_at=item.created_at,
                transcribed_text=item.transcribed_text,
                transcription_status=item.transcription_status,
                is_deleted=item.is_deleted
            ) for item in query.all()
        ]

    def update(self, voice_log: VoiceLog) -> Optional[VoiceLog]:
        db_item = self.db_session.query(VoiceLogModel).filter(
            VoiceLogModel.id == voice_log.id,
            VoiceLogModel.is_deleted == False
        ).first()
        if not db_item:
            return None
        db_item.transcribed_text = voice_log.transcribed_text
        db_item.transcription_status = voice_log.transcription_status
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

    def soft_delete(self, voice_log_id: int) -> bool:
        db_item = self.db_session.query(VoiceLogModel).filter(
            VoiceLogModel.id == voice_log_id
        ).first()
        if not db_item:
            return False
        db_item.is_deleted = True
        self.db_session.commit()
        return True