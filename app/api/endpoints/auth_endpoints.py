"""
File: app/api/endpoints/auth_endpoints.py

Purpose:
- Provides authentication endpoints:
  1) Email/Password login
  2) Google OAuth ID token verification -> local JWT issuance

Logging:
- Uses get_logger(__name__) from app.utils.logger for structured, JSON-based logs.
- Includes info logs on success, warning logs on client errors, and error logs on unexpected exceptions.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Google OAuth libs for ID token verification
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.utils.logger import get_logger
from app.api.dependencies import get_db
from app.config.settings import get_settings
from app.infrastructure.database.repository import UserRepository
from app.infrastructure.auth.auth_service import AuthService

# Create FastAPI router and logger instance
router = APIRouter()
logger = get_logger(__name__)

# -----------------------------------------------------
# Email/Password Login
# -----------------------------------------------------
class LoginRequest(BaseModel):
    """Request payload for standard email/password login."""
    email: str
    password: str


@router.post("/login")
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    1) Fetch user by email
    2) Validate password_hash existence
    3) If valid, generate JWT
    4) Log success or invalid credentials
    """
    logger.info("Login attempt received", extra={"email": payload.email})
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(payload.email)

        if not user or not user.password_hash:
            logger.warning("Invalid login credentials", extra={"email": payload.email})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials."
            )

        # Generate JWT token upon success
        token = AuthService().generate_token(user_id=user.id, email=user.email)
        logger.info("User logged in successfully", extra={"user_id": user.id})

        return {"access_token": token, "token_type": "bearer"}

    except HTTPException as http_exc:
        logger.warning(
            "HTTP exception during login",
            extra={"detail": str(http_exc.detail), "email": payload.email}
        )
        raise

    except Exception:
        logger.error("Unexpected error during login", exc_info=True, extra={"email": payload.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# -----------------------------------------------------
# Google ID Token Verification
# -----------------------------------------------------
class GoogleVerifyRequest(BaseModel):
    """Request payload containing the Google ID token."""
    id_token: str


@router.post("/verify-google-id-token")
def verify_google_id_token(payload: GoogleVerifyRequest, db: Session = Depends(get_db)):
    """
    1) Verifies Google ID token using the iOS client ID
    2) Upserts an OAuth user with empty password hash
    3) Returns a local JWT upon success
    """
    logger.info("Verifying Google ID token", extra={"route": "/verify-google-id-token"})
    try:
        settings = get_settings()
        ios_client_id = settings.GOOGLE_IOS_CLIENT_ID

        # Validate the Google ID token
        claims = id_token.verify_oauth2_token(
            payload.id_token,
            google_requests.Request(),
            ios_client_id
        )
        if claims["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            logger.warning("Invalid token issuer", extra={"issuer": claims.get("iss")})
            raise ValueError("Invalid issuer.")

        user_email = claims.get("email")
        if not user_email:
            logger.warning("No email in Google token claims", extra={"claims": claims})
            raise ValueError("Email not found in token.")

        # Upsert the user in DB
        user_repo = UserRepository(db)
        user = user_repo.get_by_email(user_email)
        if not user:
            logger.info("Creating new OAuth user", extra={"email": user_email})
            user = user_repo.create_user(
                email=user_email,
                password_hash="",  # No password for OAuth
                username=None,
                display_name=claims.get("name"),
                avatar_url=claims.get("picture"),
                oauth_provider="google"
            )

        # Generate local JWT token
        token = AuthService().generate_token(user_id=user.id, email=user.email)
        logger.info("Google verification succeeded", extra={"user_id": user.id})

        return {"access_token": token, "token_type": "bearer", "user_id": user.id}

    except ValueError as e:
        logger.error("Google ID token validation failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception:
        logger.error("Unexpected error in Google ID token verification", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )