# app/infrastructure/auth/jwt_handler.py

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt, JWTError
from app.config.settings import get_settings

def create_access_token(data: Dict, expires_delta: Optional[int] = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "jti": jti, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise