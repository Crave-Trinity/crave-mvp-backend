# File: tests/unit/test_rag_service.py

"""
Tests for the RAG pipeline and its components.
Ensures Retrieval-Augmented Generation logic handles embeddings,
search results, and LLM calls correctly.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.core.services.rag_service import RAGService, RetrievedCraving
from app.core.services.embedding_service import EmbeddingService
from app.infrastructure.vector_db.vector_repository import VectorRepository

@pytest.fixture
def mock_embedding():
    return [0.1] * 1536

@pytest.fixture
def mock_search_results():
    return {
        "matches": [
            {
                "id": "123",
                "score": 0.92,
                "metadata": {
                    "user_id": 1,
                    "description": "Strong chocolate craving after dinner",
                    "intensity": 8,
                    "created_at": datetime.utcnow().isoformat()
                }
            },
            {
                "id": "456",
                "score": 0.85,
                "metadata": {
                    "user_id": 1,
                    "description": "Mild sugar craving in afternoon",
                    "intensity": 5,
                    "created_at": (datetime.utcnow() - timedelta(days=5)).isoformat()
                }
            },
            {
                "id": "789",
                "score": 0.72,
                "metadata": {
                    "user_id": 1,
                    "description": "Intense ice cream craving at night",
                    "intensity": 9,
                    "created_at": (datetime.utcnow() - timedelta(days=60)).isoformat()
                }
            }
        ]
    }

@pytest.mark.unit
class TestRAGService:
    @patch("app.core.services.embedding_service.embedding_service.get_embedding")
    @patch("app.infrastructure.vector_db.vector_repository.VectorRepository.search_cravings")
    @patch("openai.ChatCompletion.create")
    def test_generate_personalized_insight(
        self,
        mock_chat_create,
        mock_search_cravings,
        mock_get_embedding,
        mock_embedding,
        mock_search_results
    ):
        """
        Tests the RAG pipeline end-to-end, mocking embeddings, search results, and OpenAI.
        """
        mock_get_embedding.return_value = mock_embedding
        mock_search_cravings.return_value = mock_search_results
        mock_chat_create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Mocked RAG answer"))]
        )

        service = RAGService()
        result = service.generate_personalized_insight(
            user_id=1,
            query="Why do I crave chocolate at night?",
            top_k=3
        )
        assert result == "Mocked RAG answer"
        mock_get_embedding.assert_called_once()
        mock_search_cravings.assert_called_once()
        mock_chat_create.assert_called_once()

    def test_process_search_results(self, mock_search_results):
        service = RAGService()
        processed = service._process_search_results(mock_search_results)
        assert len(processed) == 3
        assert all(isinstance(c, RetrievedCraving) for c in processed)

    def test_apply_time_weighting(self):
        service = RAGService()
        cravings = [
            RetrievedCraving(
                id=1,
                description="Recent",
                created_at=datetime.utcnow() - timedelta(days=2),
                intensity=7,
                score=0.9
            ),
            RetrievedCraving(
                id=2,
                description="Old",
                created_at=datetime.utcnow() - timedelta(days=50),
                intensity=8,
                score=0.95
            )
        ]
        weighted = service._apply_time_weighting(cravings)
        assert len(weighted) == 2

    def test_construct_prompt(self):
        service = RAGService()
        query = "Why do I crave sugary foods at night?"
        cravings = [
            RetrievedCraving(
                id=1,
                description="Chocolate craving after dinner",
                created_at=datetime.utcnow(),
                intensity=8,
                score=0.9
            )
        ]
        prompt = service._construct_prompt(user_id=1, query=query, cravings=cravings)
        assert "Chocolate craving after dinner" in prompt
        assert "Why do I crave sugary foods at night?" in prompt

@pytest.mark.unit
class TestEmbeddingService:
    def test_cache_functionality(self):
        service = EmbeddingService()
        test_text = "Test text"
        cache_key = service._get_cache_key(test_text)
        assert service._get_from_cache(cache_key) is None
        service._add_to_cache(cache_key, [0.1, 0.2])
        assert service._get_from_cache(cache_key) == [0.1, 0.2]

    @patch("app.infrastructure.external.openai_embedding.OpenAIEmbeddingService.embed_text")
    def test_get_embedding_with_cache(self, mock_embed_text):
        service = EmbeddingService()
        mock_embed_text.return_value = [0.1, 0.2, 0.3]
        text = "Cached text"

        first = service.get_embedding(text)
        second = service.get_embedding(text)
        assert mock_embed_text.call_count == 1
        assert first == second

    @patch("app.infrastructure.external.openai_embedding.OpenAIEmbeddingService.get_embeddings")
    def test_batch_embeddings(self, mock_get_embeddings):
        service = EmbeddingService()
        mock_get_embeddings.return_value = [[0.1], [0.2]]
        texts = ["Text 1", "Text 2"]
        results = service.get_batch_embeddings(texts)
        assert len(results) == 2
        assert results[0] == [0.1]
        assert results[1] == [0.2]

    @patch("app.infrastructure.external.openai_embedding.OpenAIEmbeddingService.embed_text")
    def test_error_handling(self, mock_embed_text):
        service = EmbeddingService()
        mock_embed_text.side_effect = Exception("Mock error")
        fallback = service.get_embedding("Some text")
        assert len(fallback) == 1536  # fallback embedding size