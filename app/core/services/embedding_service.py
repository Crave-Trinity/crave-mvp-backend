# File: app/core/services/embedding_service.py (CORRECTED - Syntax Error Fix)
"""
Embedding Service for CRAVE Trinity Backend.
"""

from typing import List, Dict, Optional, Union, Any
import hashlib
import json
from datetime import datetime, timedelta
import logging

from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService

# Setup logging
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    """

    def __init__(self):
        """Initialize the embedding service."""
        self.openai_service = OpenAIEmbeddingService()
        # In-memory cache for embeddings
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache for 24 hours

    def get_embedding(self, text: str) -> List[float]:
        """Get an embedding for a single text string, with caching."""
        cache_key = self._get_cache_key(text)
        cached = self._get_from_cache(cache_key)

        if cached:
            logger.debug(f"Cache hit for embedding: {cache_key[:8]}...")
            return cached

        # Get embedding from OpenAI
        try:
            embedding = self.openai_service.embed_text(text)
            self._add_to_cache(cache_key, embedding)
            return embedding
        except Exception as e:  # <--- THIS WAS MISSING!
            logger.error(f"Error getting embedding: {str(e)}")
            return self._generate_fallback_embedding(text)

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        cache_keys = [self._get_cache_key(text) for text in texts]
        cache_results = [self._get_from_cache(key) for key in cache_keys]
        missing_indices = [i for i, result in enumerate(cache_results) if result is None]

        if not missing_indices:
            logger.debug("All embeddings found in cache")
            return cache_results

        texts_to_embed = [texts[i] for i in missing_indices]
        try:
            new_embeddings = self.openai_service.get_embeddings(texts_to_embed)
            for i, embedding in zip(missing_indices, new_embeddings):
                self._add_to_cache(cache_keys[i], embedding)
                cache_results[i] = embedding
            return cache_results
        except Exception as e:  # <--- AND THIS!
            logger.error(f"Error getting batch embeddings: {str(e)}")
            for i in missing_indices:
                cache_results[i] = self._generate_fallback_embedding(texts[i])
            return cache_results

    def _get_cache_key(self, text: str) -> str:
        """Generate a deterministic cache key."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[List[float]]:
        """Retrieve an embedding from cache."""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() - entry['timestamp'] < self.cache_ttl:
                return entry['embedding']
            else:
                del self._cache[key]
        return None

    def _add_to_cache(self, key: str, embedding: List[float]) -> None:
        """Add an embedding to the cache."""
        self._cache[key] = {
            'embedding': embedding,
            'timestamp': datetime.utcnow()
        }

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """Generate a fallback embedding."""
        import random
        text_hash = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        random.seed(text_hash)
        return [random.uniform(-1, 1) for _ in range(1536)]

embedding_service = EmbeddingService()