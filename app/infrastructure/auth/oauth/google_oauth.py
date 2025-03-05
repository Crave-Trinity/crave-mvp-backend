#app/infrastructure/auth/oauth/google_oauth.py
from authlib.integrations.starlette_client import OAuth
from app.config.settings import settings

# Single Responsibility: Handles Google OAuth configuration
class GoogleOAuthProvider:
    def __init__(self):
        self.oauth = OAuth()
        self.oauth.register(
            name='google',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
            access_token_url='https://oauth2.googleapis.com/token',
            client_kwargs={'scope': 'openid email profile'},
        )

    def get_client(self):
        return self.oauth.google