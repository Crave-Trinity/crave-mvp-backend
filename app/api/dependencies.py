# File: app/api/dependencies.py
"""
Centralized FastAPI dependencies for database sessions, repositories, and authentication.

This module promotes reusability and testability by providing consistent ways to access
database connections, data repositories, and authenticated user information.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, exc, text  # text() is used for SQLAlchemy 2.0+ compatibility
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.infrastructure.database.repository import (
    CravingRepository,
    UserRepository,
    VoiceLogRepository,
)
from app.infrastructure.database.models import UserModel
from app.config.settings import settings  # Global settings configuration

# Retrieve the database URL, with a fallback for local development.
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@db:5432/crave_db"
)

# Create the SQLAlchemy engine.
engine = create_engine(DATABASE_URL)

# Create a configured session class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database connection.
    
    This function tests the database connection using a simple SQL query (using text() for compatibility).
    It can be extended for migrations or seeding.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()  # Commit is required for SQLAlchemy 2.0+ when using execute()
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a new SQLAlchemy session for each request.
    
    Ensures that the session is closed after the request is completed.
    
    Yields:
        Session: A new SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """
    FastAPI dependency that provides a CravingRepository instance using the current session.
    
    Args:
        db: The current SQLAlchemy session.
        
    Returns:
        CravingRepository: An instance to perform craving-related database operations.
    """
    return CravingRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    FastAPI dependency that provides a UserRepository instance using the current session.
    
    Args:
        db: The current SQLAlchemy session.
        
    Returns:
        UserRepository: An instance to perform user-related database operations.
    """
    return UserRepository(db)


def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    """
    FastAPI dependency that provides a VoiceLogRepository instance using the current session.
    
    Args:
        db: The current SQLAlchemy session.
        
    Returns:
        VoiceLogRepository: An instance to perform voice log operations.
    """
    return VoiceLogRepository(db)


# --- Authentication Dependencies ---

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token"
)  # This is the URL used for obtaining a token.


async def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    FastAPI dependency that retrieves the current authenticated user from the JWT token.
    
    The function decodes the token using settings.JWT_SECRET and settings.JWT_ALGORITHM.
    It attempts to find the user first by username (extracted from the "sub" claim) and,
    if not found, by email. It raises an HTTPException if the token is invalid or the user
    is not found or inactive.
    
    Args:
        request: The incoming HTTP request.
        db: The current SQLAlchemy session.
        token: The JWT token from the Authorization header.
        
    Returns:
        UserModel: The authenticated user.
        
    Raises:
        HTTPException: For invalid tokens, not found users, or inactive users.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
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