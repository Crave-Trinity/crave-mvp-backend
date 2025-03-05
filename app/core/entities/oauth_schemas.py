# app/core/entities/oauth_schemas.py
from pydantic import BaseModel, EmailStr

class OAuthUser(BaseModel):
    email: EmailStr
    name: str | None = None
    picture: str | None = None

class OAuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"