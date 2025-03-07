# File: app/api/dependencies.py
"""
Centralized FastAPI dependencies for database sessions, repositories, and authentication.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.infrastructure.database.repository import (
    CravingRepository,
    UserRepository,
)
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository
from app.infrastructure.database.models import UserModel
from app.config.settings import settings  # Global settings configuration

# -- Instead of reading from an env var with a fallback:
# DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@db:5432/crave_db")
# -- Use the one from your settings (which logs show is correct on Railway):
DATABASE_URL = settings.DATABASE_URL

# Create the SQLAlchemy engine.
engine = create_engine(DATABASE_URL)

# Create a configured session class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Check DB connectivity with a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)


def get_db() -> Generator[Session, None, None]:
    """Provide a new SQLAlchemy session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    return CravingRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    return VoiceLogRepository(db)

# --- Authentication Dependencies ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        subject: str = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(subject) or user_repo.get_by_email(subject)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user