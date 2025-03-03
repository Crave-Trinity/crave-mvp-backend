# app/core/services/rag_service.py (CORRECTED - ModuleNotFoundError Fix)
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from app.core.services.embedding_service import embedding_service
from app.infrastructure.vector_db.vector_repository import VectorRepository
# REMOVE: from app.infrastructure.llm.llama2_adapter import Llama2Adapter  # This module doesn't exist
from app.config.settings import settings
from openai import OpenAI

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
    time_score: float = 1.0  # Default time score

class RAGService:
    """
    Service for Retrieval-Augmented Generation (RAG) for craving insights.
    """

    def __init__(self):
        """
        Initialize the RAGService.
        """
        self.vector_repository = VectorRepository()
        # REMOVE: self.llm_adapter = Llama2Adapter()  # No longer needed
        self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_personalized_insight(
        self,
        user_id: int,
        query: str,
        persona: Optional[str] = None,  # Persona is not used with OpenAI directly
        top_k: int = 5,
        time_weighted: bool = True
    ) -> str:
        """
        Generate a personalized insight.
        """
        try:
            query_embedding = embedding_service.get_embedding(query)
            search_results = self.vector_repository.search_cravings(
                user_id=user_id,
                query_vector=query_embedding,
                limit=top_k * 2
            )
            retrieved_cravings = self._process_search_results(search_results)

            if time_weighted:
                retrieved_cravings = self._apply_time_weighting(
                    retrieved_cravings,
                    recency_boost_days=30
                )

            retrieved_cravings = sorted(
                retrieved_cravings,
                key=lambda x: x.time_score,
                reverse=True
            )[:top_k]

            prompt = self._construct_prompt(user_id, query, retrieved_cravings)

            # --- Use OpenAI for generation ---
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Or your preferred OpenAI model
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant specializing in craving analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
            )
            answer = response.choices[0].message.content
            return answer

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
            return (
                "I'm sorry, I'm having trouble generating a personalized insight right now. "
                "Please try again later."
            )
    def _process_search_results(self, search_results) -> List[RetrievedCraving]:
        """Convert raw search results from DB to RetrievedCraving objects."""
        processed_cravings = []
        for result in search_results.get("matches", []):
            try:
                metadata = result['metadata']
                craving = RetrievedCraving(
                    id=int(result['id']),  # Ensure ID is int
                    description=metadata['description'],
                    created_at=datetime.fromisoformat(metadata['created_at']),
                    intensity=int(metadata['intensity']),
                    score=float(result['score'])
                )
                processed_cravings.append(craving)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid craving result: {result}. Error: {e}")
                continue  # Skip this result and move to the next
        return processed_cravings

    def _apply_time_weighting(
        self,
        cravings: List[RetrievedCraving],
        recency_boost_days: int = 30
    ) -> List[RetrievedCraving]:
        """
        Apply time-based weighting to craving scores.
        """
        now = datetime.utcnow()
        for craving in cravings:
            days_ago = (now - craving.created_at).total_seconds() / (60 * 60 * 24)
            if days_ago <= recency_boost_days:
                craving.time_score = 1.0 - (days_ago / recency_boost_days) * 0.5
            else:
                craving.time_score = 0.5 * (1.0 - min(days_ago / 365, 1.0))
        return cravings


    def _construct_prompt(
        self,
        user_id: int,
        query: str,
        retrieved_cravings: List[RetrievedCraving]
    ) -> str:
        """Construct the prompt for the LLM."""

        prompt = "USER PROFILE:\n"
        prompt += f"User ID: {user_id}\n\n"
        prompt += "USER QUERY:\n"
        prompt += f"{query}\n\n"
        prompt += "RELEVANT CRAVINGS:\n"
        if retrieved_cravings:
            for craving in retrieved_cravings:
                prompt += f"- ID: {craving.id}\n"
                prompt += f"  Description: {craving.description}\n"
                prompt += f"  Created at: {craving.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
                prompt += f"  Intensity: {craving.intensity}/10\n"
                prompt += f"  Original Score: {craving.score:.3f}\n"
                prompt += f"  Time-weighted Score: {craving.time_score:.3f}\n"
                prompt += "\n"
        else:
            prompt += "No relevant craving data found for this user.\n\n"
        prompt += (
            "Based on the provided user profile and craving history, "
            "please generate a personalized insight to address the user's query. "
            "Consider patterns, triggers, and intensity of cravings. "
            "If no relevant data is available, acknowledge the limitation."
        )
        return prompt

rag_service = RAGService()