#app/api/endpoints/oauth_endpoints.py
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from app.infrastructure.auth.oauth.google_oauth import GoogleOAuthProvider
from app.infrastructure.database.session import get_db
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth/oauth", tags=["OAuth"])

google_oauth_provider = GoogleOAuthProvider()

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await google_oauth_provider.get_client().authorize_redirect(request, redirect_uri)

@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await google_oauth_provider.get_client().authorize_access_token(request)
    user_info = await google_oauth_provider.get_client().parse_id_token(request, token)

    user_manager = UserManager(db)
    user = await user_manager.get_or_create_oauth_user(
        provider="google",
        email=user_info["email"],
        name=user_info.get("name"),
        picture=user_info.get("picture")
    )

    jwt_token = create_access_token({"sub": user.email})
    frontend_redirect = f"https://your-frontend.com/auth/success?token={jwt_token}"

    return RedirectResponse(url=redirect_frontend)