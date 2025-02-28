# File: app/config/settings.py
# Purpose: Application configuration using Pydantic
# Changes: Add support for both Railway's DATABASE_URL and SQLALCHEMY_DATABASE_URI

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict
import os

class Settings(BaseSettings):
    """
    Central configuration for CRAVE Trinity Backend.
    
    Reads environment variables using Pydantic's BaseSettings. By default,
    it also loads values from a `.env` file if present.
    """

    # -----------------------------------------
    # Project / Environment
    # -----------------------------------------
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # -----------------------------------------
    # Database
    # -----------------------------------------
    # Support both SQLALCHEMY_DATABASE_URI and DATABASE_URL for Railway compatibility
    SQLALCHEMY_DATABASE_URI: str = Field(
        # First check DATABASE_URL (Railway standard), then SQLALCHEMY_DATABASE_URI, then default
        default=os.environ.get("DATABASE_URL", 
                os.environ.get("SQLALCHEMY_DATABASE_URI", 
                    "postgresql://postgres:password@localhost:5432/crave_db")),
    )

    # [Rest of the settings remain unchanged]
    # ...

    # -----------------------------------------
    # Pydantic Settings
    # -----------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

# Create the singleton settings instance
settings = Settings()

# Debug: Print the database URL for troubleshooting
print(f"Using database URL: {settings.SQLALCHEMY_DATABASE_URI}")