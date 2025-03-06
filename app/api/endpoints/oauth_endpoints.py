"""
File: oauth_endpoints.py
Purpose:
  - Defines Google OAuth endpoints for initiating OAuth and handling callbacks.
  - The router is included in main.py with prefix="/auth/oauth".
  => Final routes:
     GET /auth/oauth/google/login
     GET /auth/oauth/google/callback
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.infrastructure.auth.oauth.google_oauth import GoogleOAuthProvider
from app.infrastructure.database.session import get_db
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.auth.jwt_handler import create_access_token
from app.infrastructure.database.repository import UserRepository

router = APIRouter()

google_oauth_provider = GoogleOAuthProvider()

@router.get("/google/login")
async def google_login(request: Request):
    """
    Final route => GET /auth/oauth/google/login
    Initiates the Google OAuth flow 
    by redirecting to Google with your client_id, scope, etc.
    """
    redirect_uri = request.url_for('google_callback')  # => /auth/oauth/google/callback
    return await google_oauth_provider.get_client().authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Final route => GET /auth/oauth/google/callback
    Google redirects here after user grants permission.
    We exchange authorization code for tokens and parse user info.
    """
    token = await google_oauth_provider.get_client().authorize_access_token(request)
    user_info = await google_oauth_provider.get_client().parse_id_token(request, token)

    # Example user creation/fetch
    user_manager = UserManager(UserRepository(db))
    user = await user_manager.get_or_create_oauth_user(
        provider="google",
        email=user_info["email"],
        name=user_info.get("name"),
        picture=user_info.get("picture")
    )

    # Generate an internal JWT to authenticate user in your system
    jwt_token = create_access_token({"sub": user.email})
    
    # For final redirect, pass the token to the frontend
    # Example placeholder URL:
    frontend_redirect = f"https://your-frontend.com/auth/success?token={jwt_token}"
    return RedirectResponse(url=frontend_redirect)