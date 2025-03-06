# File: app/api/endpoints/auth_endpoints.py
# PURPOSE: Provides authentication endpoints for both email/password and native Google OAuth.
#          For Google OAuth, it verifies the ID token and creates an OAuth user with an empty password hash.
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Google libraries for ID token verification
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.api.dependencies import get_db
from app.config.settings import get_settings
from app.infrastructure/database/repository import UserRepository
from app.infrastructure.auth.auth_service import AuthService

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Email/Password login endpoint.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(payload.email)
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = AuthService().generate_token(user_id=user.id, email=user.email)
    return {"access_token": token, "token_type": "bearer"}

class GoogleVerifyRequest(BaseModel):
    id_token: str

@router.post("/verify-google-id-token")
def verify_google_id_token(payload: GoogleVerifyRequest, db: Session = Depends(get_db)):
    """
    Receives an ID token from the iOS Google Sign-In SDK, verifies it using the iOS client ID,
    and returns a local JWT upon success. For OAuth users, creates a user with an empty password hash.
    """
    settings = get_settings()
    ios_client_id = settings.GOOGLE_IOS_CLIENT_ID  # The correct audience

    try:
        # Verify the ID token with google.oauth2
        claims = id_token.verify_oauth2_token(payload.id_token, google_requests.Request(), ios_client_id)
        if claims["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Invalid issuer.")
        user_email = claims.get("email")
        if not user_email:
            raise ValueError("Email not found in token.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    # Upsert user based on email
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(user_email)
    if not user:
        # Create new OAuth user; note password_hash is set to an empty string.
        user = user_repo.create_user(
            email=user_email,
            password_hash="",  # No password needed for OAuth users.
            username=None,
            display_name=claims.get("name"),
            avatar_url=claims.get("picture"),
            oauth_provider="google"
        )

    # Generate JWT for the user.
    token = AuthService().generate_token(user_id=user.id, email=user.email)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}