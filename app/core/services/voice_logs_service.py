#====================================================
# File: app/core/services/voice_logs_service.py
#====================================================
# This file contains the service layer for managing voice logs.
# It handles file storage, record creation, and transcription steps.
# The key fix here is the correct import of VoiceLogRepository (singular)
# from the proper file, ensuring that our dependency injection works correctly.

import os
from datetime import datetime
from uuid import uuid4
from typing import Optional

# Import the VoiceLog domain entity.
from app.core.entities.voice_log import VoiceLog

# FIXED: Import the correct repository (singular) instead of an incorrect name.
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository

# Define a persistent uploads directory.
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the uploads directory exists.

class VoiceLogsService:
    """
    Encapsulates voice log business logic:
      - Storing the audio file on disk.
      - Creating and persisting a VoiceLog record in the database.
      - Orchestrating transcription steps (triggering and completing).
    """

    def __init__(self, repo: VoiceLogRepository):
        # Inject the repository dependency for database operations.
        self.repo = repo

    def upload_new_voice_log(self, user_id: int, audio_bytes: bytes) -> VoiceLog:
        """
        1. Generate a unique file path in the uploads directory.
        2. Write the uploaded audio bytes to disk.
        3. Create and persist a VoiceLog record with status 'PENDING'.
        """
        file_name = f"voice_{user_id}_{uuid4()}.wav"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # Write the audio file to persistent storage.
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Create the VoiceLog domain entity.
        voice_log = VoiceLog(
            user_id=user_id,
            file_path=file_path,
            created_at=datetime.utcnow(),
            transcription_status="PENDING"
        )
        # Persist the voice log record via the repository.
        return self.repo.create_voice_log(voice_log)

    def trigger_transcription(self, voice_log_id: int) -> Optional[VoiceLog]:
        """
        Mark the voice log as 'IN_PROGRESS' to initiate transcription.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcription_status = "IN_PROGRESS"
            return self.repo.update(record)
        return None

    def complete_transcription(self, voice_log_id: int, text: str) -> Optional[VoiceLog]:
        """
        Finalize the transcription by saving the transcribed text
        and marking the record as 'COMPLETED'.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcribed_text = text
            record.transcription_status = "COMPLETED"
            return self.repo.update(record)
        return None

    def get_voice_log(self, voice_log_id: int) -> Optional[VoiceLog]:
        """
        Retrieve a voice log record by its ID.
        """
        return self.repo.get_by_id(voice_log_id)

    def process_transcription(self, voice_log_id: int) -> None:
        """
        Placeholder method for background transcription processing.
        Implement asynchronous transcription logic here.
        """
        # TODO: Implement asynchronous processing (e.g., using Celery or RQ).
        pass