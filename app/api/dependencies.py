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

# Note: We removed VoiceLogRepository from this import
#       because it's now imported from voice_logs_repository.py
from app.infrastructure.database.repository import (
    CravingRepository,
    UserRepository,
)

# CHANGED: Import VoiceLogRepository from its actual file
from app.infrastructure.database.voice_logs_repository import VoiceLogRepository

from app.infrastructure.database.models import UserModel
from app.config.settings import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def init_db() -> None:
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
    return CravingRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

# CHANGED: Now references VoiceLogRepository from voice_logs_repository.py
def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    return VoiceLogRepository(db)

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> UserModel:
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