# File: app/core/services/rag_service.py
"""
Service for Retrieval-Augmented Generation (RAG) in CRAVE Trinity.

Uses embeddings and vector DB to retrieve relevant cravings, then calls an LLM.
Logs all key steps and handles unexpected errors.
"""

import logging
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

from app.core.services.embedding_service import embedding_service
from app.infrastructure.vector_db.vector_repository import VectorRepository
from app.config.settings import settings
import openai

logger = logging.getLogger(__name__)

@dataclass
class RetrievedCraving:
    """
    Represents a craving retrieved from the vector database.
    """
    id: int
    description: str
    created_at: datetime
    intensity: int
    score: float
    time_score: float = 1.0

class RAGService:
    """
    Service for Retrieval-Augmented Generation for cravings.
    """

    def __init__(self):
        self.vector_repository = VectorRepository()
        openai.api_key = settings.OPENAI_API_KEY

    def generate_personalized_insight(
        self,
        user_id: int,
        query: str,
        persona: Optional[str] = None,
        top_k: int = 5,
        time_weighted: bool = True
    ) -> str:
        logger.info("Starting RAG pipeline", extra={"user_id": user_id, "query": query})
        try:
            query_embedding = embedding_service.get_embedding(query)
            raw_results = self.vector_repository.search_cravings(
                user_id=user_id,
                query_vector=query_embedding,
                limit=top_k * 2
            )
            retrieved_cravings = self._process_search_results(raw_results)
            if time_weighted:
                retrieved_cravings = self._apply_time_weighting(retrieved_cravings)

            # Sort by final score
            sorted_cravings = sorted(
                retrieved_cravings,
                key=lambda x: x.time_score,
                reverse=True
            )[:top_k]

            prompt = self._construct_prompt(user_id, query, sorted_cravings)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for craving analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            answer = response.choices[0].message.content
            logger.info("RAG pipeline succeeded", extra={"user_id": user_id})
            return answer
        except Exception:
            logger.error("Error in RAG pipeline", exc_info=True, extra={"user_id": user_id})
            return (
                "An error occurred during retrieval-augmented generation. "
                "Please try again later."
            )

    def _process_search_results(self, search_results) -> List[RetrievedCraving]:
        """
        Convert raw search results from DB to RetrievedCraving objects.
        """
        cravings_list = []
        matches = search_results.get("matches", [])
        for m in matches:
            try:
                metadata = m["metadata"]
                cravings_list.append(
                    RetrievedCraving(
                        id=int(m["id"]),
                        description=metadata["description"],
                        created_at=datetime.fromisoformat(metadata["created_at"]),
                        intensity=int(metadata["intensity"]),
                        score=float(m["score"])
                    )
                )
            except (KeyError, ValueError, TypeError) as e:
                logger.warning("Skipping invalid craving record", extra={"error": str(e)})
        return cravings_list

    def _apply_time_weighting(self, cravings: List[RetrievedCraving]) -> List[RetrievedCraving]:
        """
        Example time-based weighting to highlight newer cravings.
        """
        now = datetime.utcnow()
        recency_boost_days = 30
        for c in cravings:
            days_ago = (now - c.created_at).total_seconds() / (60 * 60 * 24)
            if days_ago <= recency_boost_days:
                # Weighted more if it's fresh
                c.time_score = 1.0 - (days_ago / recency_boost_days) * 0.5
            else:
                # Slowly decays over time
                c.time_score = 0.5 * (1.0 - min(days_ago / 365, 1.0))
        return cravings

    def _construct_prompt(self, user_id: int, query: str, cravings: List[RetrievedCraving]) -> str:
        """
        Build a prompt for the LLM based on query and retrieved cravings.
        """
        prompt = f"USER QUERY: {query}\n\n"
        prompt += "RELEVANT CRAVINGS:\n"
        if cravings:
            for c in cravings:
                prompt += (
                    f"- ID: {c.id}\n"
                    f"  Description: {c.description}\n"
                    f"  Created at: {c.created_at}\n"
                    f"  Intensity: {c.intensity}\n"
                    f"  Score: {round(c.score, 3)}\n"
                    f"  Time-Score: {round(c.time_score, 3)}\n\n"
                )
        else:
            prompt += "No relevant cravings found.\n\n"
        prompt += (
            "Please generate a personalized insight for the user, "
            "considering these cravings and the user query."
        )
        return prompt

rag_service = RAGService()