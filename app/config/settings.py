# File: app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, Optional
import os


class Settings(BaseSettings):
    """Central configuration for CRAVE Trinity Backend."""

    # -----------------------------------------
    # Project / Environment
    # -----------------------------------------
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # -----------------------------------------
    # Database - Railway Support
    # -----------------------------------------
    SQLALCHEMY_DATABASE_URI: str = Field(default_factory=lambda: Settings._get_database_url())

    @staticmethod
    def _get_database_url() -> str:
        """Robust database URL detection for Railway and local development."""
        url: Optional[str] = os.environ.get("DATABASE_URL") or \
            os.environ.get("SQLALCHEMY_DATABASE_URI") or \
            os.environ.get("POSTGRES_URL")
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

    # API Keys - NO DEFAULTS
    PINECONE_API_KEY: str = Field(...)
    PINECONE_ENV: str = Field(default="us-east-1-aws")
    PINECONE_INDEX_NAME: str = Field(default="crave-embeddings")
    OPENAI_API_KEY: str = Field(...)
    HUGGINGFACE_API_KEY: str = Field(...)

    # Other Settings
    LLAMA2_MODEL_NAME: str = Field(default="meta-llama/Llama-2-13b-chat-hf")
    LORA_PERSONAS: Dict[str, str] = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }
    JWT_SECRET: str = Field(...)
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    MIGRATION_MODE: str = Field(default="auto")

    # -----------------------------------------
    # Pydantic Settings
    # -----------------------------------------
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


_settings = None  # Global variable to hold the settings instance


def get_settings():
    """
    Get the settings instance. Creates it if it doesn't exist yet.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# Create a global instance for convenience.
settings = get_settings()
