# File: app/config/settings.py
# Fix: Add robust Railway database URL detection

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict
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
    # Handle all possible Railway PostgreSQL environment variables
    SQLALCHEMY_DATABASE_URI: str = Field(
        default=lambda: Settings._get_database_url(),
    )
    
    @staticmethod
    def _get_database_url():
        """Robust database URL detection for Railway and local development."""
        # 1. Check complete connection strings first
        if url := os.environ.get("DATABASE_URL"):
            return url
            
        if url := os.environ.get("SQLALCHEMY_DATABASE_URI"):
            return url
            
        if url := os.environ.get("POSTGRES_URL"):
            return url
        
        # 2. Check for Railway-specific PostgreSQL components
        if all(key in os.environ for key in ["PGUSER", "PGPASSWORD", "PGHOST"]):
            user = os.environ.get("PGUSER")
            password = os.environ.get("PGPASSWORD")
            host = os.environ.get("PGHOST")
            port = os.environ.get("PGPORT", 5432)  # Default PostgreSQL port
            dbname = os.environ.get("PGDATABASE", "railway")  # Default Railway DB name

            return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

        # 3. Fallback to a local development database URL if no Railway env vars found
        return "postgresql://postgres:password@localhost:5432/crave_db"

    # [Rest of your settings remain unchanged]
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_ENV: str = Field("us-east-1-aws", env="PINECONE_ENV")
    PINECONE_INDEX_NAME: str = Field("crave-embeddings", env="PINECONE_INDEX_NAME")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: str = Field(..., env="HUGGINGFACE_API_KEY")
    LLAMA2_MODEL_NAME: str = Field("meta-llama/Llama-2-13b-chat-hf", env="LLAMA2_MODEL_NAME")
    LORA_PERSONAS: Dict[str, str] = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    # -----------------------------------------
    # Pydantic Settings
    # -----------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()