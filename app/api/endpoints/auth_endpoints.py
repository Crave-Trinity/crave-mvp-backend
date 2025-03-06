# File: app/api/endpoints/auth_endpoints.py

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Google libraries to verify the ID token
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.api.dependencies import get_db
from app.config.settings import get_settings
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.repository import UserRepository
from app.infrastructure.auth.auth_service import AuthService

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Existing method for normal email/password login (if you keep it).
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(payload.email)
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    # TODO: verify password...
    token = AuthService().generate_token(user_id=user.id, email=user.email)
    return {"access_token": token, "token_type": "bearer"}

class GoogleVerifyRequest(BaseModel):
    id_token: str

@router.post("/verify-google-id-token")
def verify_google_id_token(
    payload: GoogleVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Receives an ID token from the iOS Google Sign-In SDK,
    verifies it against our iOS client ID, 
    and returns a local JWT upon success.
    """
    settings = get_settings()
    ios_client_id = settings.GOOGLE_IOS_CLIENT_ID  # The valid "aud" expected

    try:
        # Verify token with google.oauth2
        claims = id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            ios_client_id
        )
        # Optionally double-check issuer
        if claims["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Invalid issuer.")

        # The unique user ID from Google
        google_sub = claims["sub"]
        user_email = claims.get("email")
        if not user_email:
            # Typically always present, but just in case
            raise ValueError("Email not found in token.")

    except ValueError as e:
        # If any verification step fails
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    # Upsert user in DB based on email or google_sub
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(user_email)
    if not user:
        # Create user if doesn't exist
        user = user_repo.create_user(
            email=user_email,
            password_hash=None,  # No password needed, it's Google-based
            username=None,
            display_name=claims.get("name"),
            avatar_url=claims.get("picture"),
            oauth_provider="google"
        )

    # Generate your local JWT
    token = AuthService().generate_token(user_id=user.id, email=user.email)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}