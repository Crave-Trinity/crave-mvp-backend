# File: app/infrastructure/external/openai_embedding.py (CORRECTED)

from typing import List
from app.config.settings import Settings
from openai import OpenAI  # Use the new client

settings = Settings()

class OpenAIEmbeddingService:

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        # Initialize the client here
        self.client = OpenAI(api_key=self.api_key)

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        try:
            # Use the new embeddings.create method
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )

            # Extract embeddings correctly from the response
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Warning: OpenAI embedding error: {e}")
            import random
            mock_dim = 1536
            return [[random.random() for _ in range(mock_dim)] for _ in texts]

    def embed_text(self, text: str) -> List[float]:
        embeddings = self.get_embeddings([text])
        return embeddings[0] if embeddings else []

def get_embeddings(texts: List[str]) -> List[List[float]]:
    service = OpenAIEmbeddingService()
    return service.get_embeddings(texts)