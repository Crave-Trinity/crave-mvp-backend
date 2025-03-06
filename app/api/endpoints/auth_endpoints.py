"""
File: auth_endpoints.py
Purpose:
  - Exposes Authentication endpoints for email/password login, user registration if desired.
  - The router is included in main.py with prefix="/api/v1/auth".
  => This yields final paths: 
     POST /api/v1/auth/login
     GET /api/v1/auth/me
     etc.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.infrastructure.database.session import get_db
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.database.repository import UserRepository
from app.core.entities.auth_schemas import LoginRequest, AuthResponseDTO  # Adjust import paths as needed

router = APIRouter()

@router.post("/login")
async def login_user(
    credentials: LoginRequest, 
    db: Session = Depends(get_db)
) -> AuthResponseDTO:
    """
    Email/password login endpoint.
    Final route => POST /api/v1/auth/login
    """
    user_manager = UserManager(UserRepository(db))
    user = await user_manager.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Example: you might create a JWT or session
    access_token = user_manager.create_access_token_for_user(user)
    return AuthResponseDTO(accessToken=access_token)

@router.get("/me")
async def read_users_me(db: Session = Depends(get_db)):
    """
    Example for retrieving current user data 
    (Requires some auth, e.g. a Bearer token).
    => GET /api/v1/auth/me
    """
    return {"message": "Current user info placeholder."}