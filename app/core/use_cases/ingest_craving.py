# app/core/use_cases/ingest_craving.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from pydantic import BaseModel
from app.core.entities.craving import Craving
from app.infrastructure.database.repository import CravingRepository
from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService
from app.infrastructure.vector_db.vector_repository import VectorRepository

@dataclass
class IngestCravingInput:
    """DTO for ingesting a craving log."""
    user_id: int
    description: str
    intensity: float  # was int, but okay to store as float

class IngestCravingOutput(BaseModel):
    """DTO for returning a successfully saved craving."""
    id: int
    user_id: int
    description: str
    intensity: float
    created_at: datetime

def ingest_craving(input_dto: IngestCravingInput, repo: CravingRepository) -> IngestCravingOutput:
    """
    Ingest a new craving into the system.
    Steps:
      1) Convert input DTO to domain entity
      2) Persist via repository
      3) Optionally embed & store in Pinecone
      4) Return output DTO
    """
    domain_craving = Craving(
        id=None,  # DB auto
        user_id=input_dto.user_id,
        description=input_dto.description,
        intensity=input_dto.intensity,
        created_at=datetime.utcnow(),
    )
    saved_craving = repo.create_craving(
        user_id=domain_craving.user_id,
        description=domain_craving.description,
        intensity=domain_craving.intensity
    )

    # optionally generate embeddings
    try:
        embed_service = OpenAIEmbeddingService()
        embedding = embed_service.embed_text(saved_craving.description)

        vector_repo = VectorRepository()
        metadata = {
            "user_id": saved_craving.user_id,
            "created_at": str(saved_craving.created_at)
        }
        vector_repo.upsert_craving_embedding(saved_craving.id, embedding, metadata)
    except Exception as e:
        print(f"Embedding error: {e}")

    return IngestCravingOutput(
        id=saved_craving.id,
        user_id=saved_craving.user_id,
        description=saved_craving.description,
        intensity=saved_craving.intensity,
        created_at=saved_craving.created_at
    )