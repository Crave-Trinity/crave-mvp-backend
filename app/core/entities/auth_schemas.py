"""
auth_schemas.py

Pydantic models (schemas) for Auth flows (registration, token, user profiles, etc.).
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# Example token model
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# For user creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    username: Optional[str] = None


# For storing user creation in DB (with hashed password)
class UserDBCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password_hash: str


# For updating user info
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    # Additional fields
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    # etc...


# For user retrieval
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    created_at: str
