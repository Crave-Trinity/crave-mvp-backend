# File: tests/unit/test_ingest_craving.py

import pytest
from datetime import datetime
from app.core.entities.craving import Craving
from app.core.use_cases.ingest_craving import (
    IngestCravingInput,
    ingest_craving,
)
from app.infrastructure.database.repository import CravingRepository

class MockCravingRepository:
    def create_craving(self, user_id: int, description: str, intensity: float) -> Craving:
        # Return a pretend DB result
        return Craving(
            id=123,
            user_id=user_id,
            description=description,
            intensity=intensity,
            created_at=datetime.utcnow()
        )

@pytest.mark.unit
def test_ingest_craving_use_case():
    """
    Tests the ingest_craving use case with a mock repository.
    """
    repo = MockCravingRepository()
    input_dto = IngestCravingInput(
        user_id=1,
        description="Test craving",
        intensity=5
    )
    result = ingest_craving(input_dto, repo)
    assert result.id == 123
    assert result.user_id == 1
    assert result.description == "Test craving"
    assert result.intensity == 5