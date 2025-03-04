#====================================================
# File: app/api/dependencies.py
#====================================================

import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.repository import (
    CravingRepository,
    UserRepository,
    VoiceLogRepository,
)
from app.config.settings import get_settings

# OAuth2 scheme for extracting the token from the Authorization header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def init_db() -> None:
    """
    Initialize and test the database connection.
    """
    engine = create_engine(
        get_settings().DATABASE_URL,
        connect_args={"sslmode": "require"} if "railway" in get_settings().DATABASE_URL else {},
    )
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            connection.commit()
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)

def get_db() -> Generator[Session, None, None]:
    """
    Create and yield a database session, ensuring it's closed afterwards.
    """
    db_settings = get_settings()
    engine = create_engine(
        db_settings.DATABASE_URL,
        connect_args={"sslmode": "require"} if "railway" in db_settings.DATABASE_URL else {},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """
    Provide an instance of the CravingRepository.
    """
    return CravingRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    Provide an instance of the UserRepository.
    """
    return UserRepository(db)

def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    """
    Provide an instance of the VoiceLogRepository.
    """
    return VoiceLogRepository(db)

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> UserModel:
    """
    Retrieve the current authenticated user from the JWT token.

    Steps:
      1. Decode the token to extract the 'sub' claim.
      2. Look up the user in the database (by username or email).
      3. Ensure the user exists and is active.

    Returns:
        UserModel: The authenticated user.

    Raises:
        HTTPException: For invalid or expired tokens, or if the user is not found/active.
    """
    settings = get_settings()
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