# File: app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # Database URL
    DATABASE_URL: str = Field(default_factory=lambda: Settings._get_database_url())

    @staticmethod
    def _get_database_url() -> str:
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

    # REMOVED: GOOGLE_CLIENT_SECRET or other web-flow variables
    # Keeping only the iOS client ID:
    GOOGLE_IOS_CLIENT_ID: str = Field(
        default="YOUR_IOS_CLIENT_ID_HERE", 
        description="Google iOS client ID for token verification"
    )

    JWT_SECRET: str = Field("CHANGE_ME")
    JWT_ALGORITHM: str = Field("HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60)

    PINECONE_API_KEY: str = Field("YOUR_PINECONE_API_KEY")
    PINECONE_ENV: str = Field("us-east-1-aws")
    PINECONE_INDEX_NAME: str = Field("crave-embeddings")
    OPENAI_API_KEY: str = Field("YOUR_OPENAI_API_KEY")

    MIGRATION_MODE: str = Field("auto")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

settings = get_settings()