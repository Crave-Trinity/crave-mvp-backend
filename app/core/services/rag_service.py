# File: app/core/services/rag_service.py

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import logging
from dataclasses import dataclass

import openai  # We'll call OpenAI directly for text generation

from app.core.services.embedding_service import embedding_service
from app.infrastructure.vector_db.vector_repository import VectorRepository
from app.config.settings import Settings

settings = Settings()
logger = logging.getLogger(__name__)

@dataclass
class RetrievedCraving:
    """Represents a retrieved craving from the vector database."""
    id: int
    description: str
    created_at: datetime
    intensity: int
    score: float  # Similarity score from vector search
    time_score: float = 1.0  # Time-weighted adjustment (1.0 = no adjustment)

    @property
    def final_score(self) -> float:
        """Calculate the final score with time weighting applied."""
        return self.score * self.time_score

class RAGService:
    """
    Implements a CPU-friendly Retrieval-Augmented Generation pipeline using OpenAI's API.
    
    This service handles:
    - Query embedding
    - Context retrieval with time weighting
    - Prompt construction
    - OpenAI GPT text generation
    """
    
    def __init__(self):
        """Initialize the RAG service with dependencies."""
        self.vector_repo = VectorRepository()
        
    def generate_personalized_insight(
        self, 
        user_id: int, 
        query: str, 
        persona: Optional[str] = None,
        top_k: int = 5,
        time_weighted: bool = True,
        recency_boost_days: int = 30
    ) -> str:
        """
        Generate a personalized craving insight for the user's query using OpenAI.
        
        Args:
            user_id: The user's ID
            query: The user's question or query text
            persona: (Optional) You can still treat "persona" as a special style or tone
            top_k: Number of relevant cravings to retrieve
            time_weighted: Whether to apply time-weighted retrieval
            recency_boost_days: Days for which to apply maximum recency boost
            
        Returns:
            A personalized response based on the user's cravings history
        """
        try:
            # 1. Embed the query for vector search
            query_embedding = embedding_service.get_embedding(query)
            
            # 2. Retrieve relevant cravings
            search_results = self.vector_repo.search_cravings(
                embedding=query_embedding, 
                top_k=top_k * 2  # retrieve more for time-weight weighting
            )
            
            # 3. Convert to domain objects
            retrieved_cravings = self._process_search_results(search_results)
            
            # 4. Optionally apply time weighting
            if time_weighted and retrieved_cravings:
                retrieved_cravings = self._apply_time_weighting(
                    retrieved_cravings, 
                    recency_boost_days=recency_boost_days
                )
            
            # 5. Truncate to top_k
            retrieved_cravings = retrieved_cravings[:top_k]
            
            # 6. Build the prompt
            prompt = self._construct_prompt(user_id, query, retrieved_cravings, persona)
            
            # 7. Generate text using OpenAI ChatCompletion (gpt-3.5 or gpt-4)
            openai.api_key = settings.OPENAI_API_KEY
            
            completion = openai.ChatCompletion.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are CRAVE AI, a specialized assistant..."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            answer = completion.choices[0].message["content"].strip()
            return answer
        
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}", exc_info=True)
            # Provide a fallback response
            return (
                "I'm having trouble accessing your craving history right now. "
                "Please try again in a moment or rephrase your question."
            )
    
    def _process_search_results(self, search_results: Dict[str, Any]) -> List[RetrievedCraving]:
        """Convert Pinecone-like search results into domain objects."""
        retrieved_cravings = []
        
        for match in search_results.get("matches", []):
            try:
                metadata = match.get("metadata", {})
                created_at_str = metadata.get("created_at", "")
                
                if created_at_str:
                    dt = datetime.fromisoformat(created_at_str)
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(timezone.utc)
                    dt = dt.replace(tzinfo=None)
                    created_at = dt
                else:
                    created_at = datetime.utcnow()
                
                try:
                    craving_id = int(match.get("id", "0"))
                except ValueError:
                    craving_id = 0
                
                craving = RetrievedCraving(
                    id=craving_id,
                    description=metadata.get("description", "Unknown craving"),
                    created_at=created_at,
                    intensity=metadata.get("intensity", 0),
                    score=match.get("score", 0.0)
                )
                retrieved_cravings.append(craving)
                
            except Exception as e:
                logger.warning(f"Error processing search result: {str(e)}")
                continue
                
        return retrieved_cravings
    
    def _apply_time_weighting(
        self, 
        cravings: List[RetrievedCraving], 
        recency_boost_days: int = 30
    ) -> List[RetrievedCraving]:
        """Apply a time decay for older cravings, boosting recent items."""
        now = datetime.utcnow()
        recency_threshold = timedelta(days=recency_boost_days)
        
        for craving in cravings:
            age = now - craving.created_at
            if age <= recency_threshold:
                craving.time_score = 1.0
            else:
                days_old = age.total_seconds() / 86400  # seconds in a day
                # Exponential decay, never below 0.2
                craving.time_score = max(0.2, (0.95 ** (days_old - recency_boost_days)))
        
        # Re-sort by final_score
        return sorted(cravings, key=lambda c: c.final_score, reverse=True)
    
    def _construct_prompt(
        self, 
        user_id: int, 
        query: str, 
        retrieved_cravings: List[RetrievedCraving],
        persona: Optional[str] = None
    ) -> str:
        """
        Construct an optimized text snippet that includes the user's craving history
        and query. If persona is provided, you can incorporate that style in the prompt.
        """
        # If persona is relevant, you could add special instructions to your prompt here
        persona_instruction = ""
        if persona:
            persona_instruction = f"(Persona: {persona})\n"
        
        if not retrieved_cravings:
            context_text = "No relevant craving data found in your history."
        else:
            context_lines = []
            for i, craving in enumerate(retrieved_cravings, 1):
                date_str = craving.created_at.strftime("%b %d, %Y at %I:%M %p")
                context_lines.append(
                    f"{i}. {craving.description} (Intensity: {craving.intensity}/10, {date_str})"
                )
            context_text = "\n".join(context_lines)

        prompt = (
            f"{persona_instruction}"
            f"USER PROFILE:\n- User ID: {user_id}\n\n"
            f"RELEVANT CRAVING HISTORY:\n{context_text}\n\n"
            f"USER QUERY:\n{query}\n\n"
            "GUIDELINES:\n"
            "1. Provide an empathetic, insightful response based on the user's craving patterns.\n"
            "2. Ground your response in their actual history, NOT generic advice.\n"
            "3. Identify patterns or triggers if apparent.\n"
            "4. Be supportive and non-judgmental.\n"
            "5. Focus on patterns rather than medical advice.\n"
            "6. If there's not enough data, acknowledge that limitation.\n\n"
            "YOUR RESPONSE:"
        )

        return prompt

# Singleton instance
rag_service = RAGService()

def generate_personalized_insight(
    user_id: int, 
    query: str, 
    persona: str = None, 
    top_k: int = 5
) -> str:
    """
    Backwards-compatible function interface for the RAG service.
    """
    return rag_service.generate_personalized_insight(
        user_id=user_id,
        query=query,
        persona=persona,
        top_k=top_k
    )
