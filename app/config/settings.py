#======================
# app/config/settings.py
#======================
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Central configuration for CRAVE Trinity Backend.
    """

    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # Database
    DATABASE_URL: str = Field(default_factory=lambda: Settings._get_database_url())

    @staticmethod
    def _get_database_url() -> str:
        """
        Single source of truth for the database URL.
        Falls back to a local PostgreSQL if not set.
        """
        url: Optional[str] = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
        if url:
            return url
        if all(key in os.environ for key in ["PGUSER", "PGPASSWORD", "PGHOST"]):
            user = os.environ["PGUSER"]
            password = os.environ["PGPASSWORD"]
            host = os.environ["PGHOST"]
            port = os.environ.get("PGPORT", "5432")
            dbname = os.environ.get("PGDATABASE", "railway")
            return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return "postgresql://postgres:password@localhost:5432/crave_db"

    # API Keys (no defaults)
    PINECONE_API_KEY: str = Field(...)
    PINECONE_ENV: str = Field(default="us-east-1-aws")
    PINECONE_INDEX_NAME: str = Field(default="crave-embeddings")
    OPENAI_API_KEY: str = Field(...)

    # Auth & Misc
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    MIGRATION_MODE: str = Field(default="auto")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


_settings = None

def get_settings():
    """
    Return singleton settings instance.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

settings = get_settings()