# File: app/core/services/embedding_service.py
"""
Embedding Service for CRAVE Trinity Backend.

Generates and manages text embeddings, including caching,
and logs critical steps plus any exceptions.
"""

from typing import List, Dict, Optional, Any
import hashlib
import random
from datetime import datetime, timedelta
import logging

from app.infrastructure.external.openai_embedding import OpenAIEmbeddingService

logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating and managing text embeddings.
    """

    def __init__(self):
        self.openai_service = OpenAIEmbeddingService()
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=24)

    def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for a single text string, with caching.
        """
        cache_key = self._get_cache_key(text)
        cached = self._get_from_cache(cache_key)
        if cached:
            logger.debug("Cache hit for embedding", extra={"cache_key": cache_key[:8]})
            return cached

        try:
            embedding = self.openai_service.embed_text(text)
            self._add_to_cache(cache_key, embedding)
            return embedding
        except Exception as e:
            logger.error("Error getting embedding", exc_info=True, extra={"text": text})
            return self._generate_fallback_embedding(text)

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts, with caching.
        """
        cache_keys = [self._get_cache_key(t) for t in texts]
        cache_results = [self._get_from_cache(k) for k in cache_keys]
        missing_indices = [i for i, r in enumerate(cache_results) if r is None]

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
        except Exception:
            logger.error("Error getting batch embeddings", exc_info=True)
            for i in missing_indices:
                cache_results[i] = self._generate_fallback_embedding(texts[i])
            return cache_results

    def _get_cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _get_from_cache(self, key: str) -> Optional[List[float]]:
        if key in self._cache:
            entry = self._cache[key]
            if datetime.utcnow() - entry['timestamp'] < self.cache_ttl:
                return entry['embedding']
            else:
                del self._cache[key]
        return None

    def _add_to_cache(self, key: str, embedding: List[float]) -> None:
        self._cache[key] = {
            'embedding': embedding,
            'timestamp': datetime.utcnow()
        }

    def _generate_fallback_embedding(self, text: str) -> List[float]:
        """
        Generate a fallback embedding for error cases.
        """
        text_hash = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
        random.seed(text_hash)
        return [random.uniform(-1, 1) for _ in range(1536)]


embedding_service = EmbeddingService()