# File: app/core/services/voice_logs_service.py
"""
Service layer for managing voice logs:
 - File storage
 - Creating DB records
 - Handling transcription steps

Logs both success and error conditions.
"""

import os
import logging
from datetime import datetime
from typing import Optional

from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository
from app.infrastructure.external.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)

# Define a persistent uploads directory
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

class VoiceLogsService:
    """
    Encapsulates voice log business logic:
      - Storing audio file on disk
      - Creating & updating VoiceLog DB records
      - Orchestrating transcription steps
    """

    def __init__(self, repo: VoiceLogRepository):
        self.repo = repo

    def upload_new_voice_log(self, user_id: int, audio_bytes: bytes) -> VoiceLog:
        logger.info("Uploading new voice log", extra={"user_id": user_id})
        try:
            file_name = f"voice_{user_id}_{datetime.utcnow().timestamp()}.wav"
            file_path = os.path.join(UPLOAD_DIR, file_name)

            with open(file_path, "wb") as f:
                f.write(audio_bytes)

            voice_log = VoiceLog(
                user_id=user_id,
                file_path=file_path,
                created_at=datetime.utcnow(),
                transcription_status="PENDING"
            )
            saved = self.repo.create_voice_log(voice_log)
            logger.info("Voice log created successfully", extra={"voice_log_id": saved.id})
            return saved

        except Exception:
            logger.error("Error creating voice log", exc_info=True, extra={"user_id": user_id})
            raise

    def trigger_transcription(self, voice_log_id: int) -> Optional[VoiceLog]:
        """
        Mark the voice log as IN_PROGRESS to start transcription.
        """
        logger.info("Triggering transcription", extra={"voice_log_id": voice_log_id})
        try:
            record = self.repo.get_by_id(voice_log_id)
            if record and not record.is_deleted:
                record.transcription_status = "IN_PROGRESS"
                updated = self.repo.update(record)
                logger.info("Voice log transcription status updated", extra={"voice_log_id": voice_log_id})
                return updated
            return None
        except Exception:
            logger.error("Error triggering transcription", exc_info=True, extra={"voice_log_id": voice_log_id})
            raise

    def complete_transcription(self, voice_log_id: int, text: str) -> Optional[VoiceLog]:
        """
        Finalize the transcription by saving the text and marking as COMPLETED.
        """
        logger.info("Completing transcription", extra={"voice_log_id": voice_log_id})
        try:
            record = self.repo.get_by_id(voice_log_id)
            if record and not record.is_deleted:
                record.transcribed_text = text
                record.transcription_status = "COMPLETED"
                updated = self.repo.update(record)
                logger.info("Transcription completed successfully", extra={"voice_log_id": voice_log_id})
                return updated
            return None
        except Exception:
            logger.error("Error completing transcription", exc_info=True, extra={"voice_log_id": voice_log_id})
            raise

    def get_voice_log(self, voice_log_id: int) -> Optional[VoiceLog]:
        try:
            return self.repo.get_by_id(voice_log_id)
        except Exception:
            logger.error("Error retrieving voice log", exc_info=True, extra={"voice_log_id": voice_log_id})
            raise

    def process_transcription(self, voice_log_id: int) -> None:
        """
        Placeholder background method for transcription.
        Could integrate Celery, RQ, or another job queue.
        """
        logger.info("Processing transcription in background", extra={"voice_log_id": voice_log_id})
        # Implement async logic if needed
        pass