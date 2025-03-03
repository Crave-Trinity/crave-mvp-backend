# File: app/core/services/embedding_service.py
"""
Embedding Service for CRAVE Trinity Backend.

This service centralizes access to text embedding functionality, 
providing a clean interface between application logic and the 
embedding provider (OpenAI).

It implements:
1. Caching for performance optimization
2. Error handling and fallback strategies
3. Consistent embedding dimensionality
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
    
    This service provides a high-level interface for converting text
    to vector embeddings, with caching and error handling.
    """
    
    def __init__(self):
        """Initialize the embedding service with OpenAI integration and caching."""
        self.openai_service = OpenAIEmbeddingService()
        # In-memory cache for embeddings - in production, consider Redis
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache embeddings for 24 hours
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for a single text string, with caching.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
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
        except Exception as e:
            logger.error(f"Error getting embedding: {str(e)}")
            # Generate a deterministic fallback embedding based on text hash
            # This ensures consistency even when API fails
            return self._generate_fallback_embedding(text)
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts, maximizing throughput.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        # Check cache for all texts
        cache_keys = [self._get_cache_key(text) for text in texts]
        cache_results = [self._get_from_cache(key) for key in cache_keys]
        
        # Identify which texts need embedding
        missing_indices = [i for i, result in enumerate(cache_results) if result is None]
        
        if not missing_indices:
            logger.debug("All embeddings found in cache")
            return cache_results
            
        # Embed missing texts
        texts_to_embed = [texts[i] for i in missing_indices]
        try:
            new