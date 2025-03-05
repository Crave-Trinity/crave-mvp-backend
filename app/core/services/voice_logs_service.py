#====================================================
# File: app/core/services/voice_logs_service.py
#====================================================

import os
from datetime import datetime
from uuid import uuid4
from typing import Optional

# Import the VoiceLog domain entity
from app.core.entities.voice_log import VoiceLog

# CHANGED: Import the correct VoiceLogRepository (singular) from its file,
# instead of the incorrect VoiceLogsRepository.
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository

# Define a persistent uploads directory.
UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
    "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

class VoiceLogsService:
    """
    Encapsulates voice log business logic:
      - Storing the audio file
      - Creating a VoiceLog record
      - Orchestrating transcription steps
    """

    def __init__(self, repo: VoiceLogRepository):
        # Dependency injection of the repository for database operations.
        self.repo = repo

    def upload_new_voice_log(self, user_id: int, audio_bytes: bytes) -> VoiceLog:
        """
        1. Generate a unique file path in a persistent uploads directory.
        2. Write the uploaded audio bytes to persistent storage.
        3. Create and persist a VoiceLog domain entity with 'PENDING' status.
        """
        file_name = f"voice_{user_id}_{uuid4()}.wav"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # Write the audio file to disk.
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
        Mark the voice log as 'IN_PROGRESS' and trigger transcription.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcription_status = "IN_PROGRESS"
            return self.repo.update(record)
        return None

    def complete_transcription(self, voice_log_id: int, text: str) -> Optional[VoiceLog]:
        """
        Finalize transcription by setting status to 'COMPLETED' and saving the transcribed text.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcribed_text = text
            record.transcription_status = "COMPLETED"
            return self.repo.update(record)
        return None

    def get_voice_log(self, voice_log_id: int) -> Optional[VoiceLog]:
        """
        Retrieve a voice log by its ID.
        """
        return self.repo.get_by_id(voice_log_id)

    def process_transcription(self, voice_log_id: int) -> None:
        """
        Placeholder for background transcription processing logic.
        """
        # Implement your asynchronous transcription processing here.
        pass