# File: app/infrastructure/database/voice_logs_repository.py
"""
VoiceLogRepository: Manages CRUD operations for voice logs.
Logs each DB operation for auditing and debugging.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.models import VoiceLogModel

logger = logging.getLogger(__name__)

class VoiceLogRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_voice_log(self, voice_log: VoiceLog) -> VoiceLog:
        logger.info("Creating new voice log DB entry", extra={"user_id": voice_log.user_id})
        try:
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
            logger.info("Voice log DB entry created", extra={"voice_log_id": db_item.id})
            return VoiceLog(
                id=db_item.id,
                user_id=db_item.user_id,
                file_path=db_item.file_path,
                created_at=db_item.created_at,
                transcribed_text=db_item.transcribed_text,
                transcription_status=db_item.transcription_status,
                is_deleted=db_item.is_deleted
            )
        except Exception:
            logger.error(
                "Error creating voice log DB entry",
                exc_info=True,
                extra={"user_id": voice_log.user_id}
            )
            self.db_session.rollback()
            raise

    def get_by_id(self, voice_log_id: int) -> Optional[VoiceLog]:
        logger.debug("Fetching voice log by ID", extra={"voice_log_id": voice_log_id})
        try:
            db_item = self.db_session.query(VoiceLogModel).filter(
                VoiceLogModel.id == voice_log_id,
                VoiceLogModel.is_deleted == False
            ).first()
            if not db_item:
                return None
            return VoiceLog(
                id=db_item.id,
                user_id=db_item.user_id,
                file_path=db_item.file_path,
                created_at=db_item.created_at,
                transcribed_text=db_item.transcribed_text,
                transcription_status=db_item.transcription_status,
                is_deleted=db_item.is_deleted
            )
        except Exception:
            logger.error("Error fetching voice log by ID", exc_info=True, extra={"voice_log_id": voice_log_id})
            raise

    def list_by_user(self, user_id: int) -> List[VoiceLog]:
        logger.debug("Listing voice logs by user", extra={"user_id": user_id})
        try:
            records = self.db_session.query(VoiceLogModel).filter(
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
                )
                for item in records.all()
            ]
        except Exception:
            logger.error("Error listing voice logs by user", exc_info=True, extra={"user_id": user_id})
            raise

    def update(self, voice_log: VoiceLog) -> Optional[VoiceLog]:
        logger.info("Updating voice log", extra={"voice_log_id": voice_log.id})
        try:
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
            logger.info("Voice log updated", extra={"voice_log_id": db_item.id})
            return VoiceLog(
                id=db_item.id,
                user_id=db_item.user_id,
                file_path=db_item.file_path,
                created_at=db_item.created_at,
                transcribed_text=db_item.transcribed_text,
                transcription_status=db_item.transcription_status,
                is_deleted=db_item.is_deleted
            )
        except Exception:
            logger.error("Error updating voice log", exc_info=True, extra={"voice_log_id": voice_log.id})
            self.db_session.rollback()
            raise

    def soft_delete(self, voice_log_id: int) -> bool:
        logger.info("Soft deleting voice log", extra={"voice_log_id": voice_log_id})
        try:
            db_item = self.db_session.query(VoiceLogModel).filter(
                VoiceLogModel.id == voice_log_id
            ).first()
            if not db_item:
                return False
            db_item.is_deleted = True
            self.db_session.commit()
            logger.info("Voice log soft-deleted", extra={"voice_log_id": voice_log_id})
            return True
        except Exception:
            logger.error("Error soft-deleting voice log", exc_info=True, extra={"voice_log_id": voice_log_id})
            self.db_session.rollback()
            raise