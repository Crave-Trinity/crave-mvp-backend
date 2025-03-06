"""
File: app/core/entities/auth_schemas.py

Pydantic models (schemas) for Auth flows (registration, tokens, user profiles, etc.).
Includes:
  - LoginRequest and AuthResponseDTO (for email/password login)
  - Token (example model)
  - UserCreate, UserDBCreate, UserUpdate, UserResponse (for user CRUD)
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# =======================
# For Email/Password Login
# =======================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponseDTO(BaseModel):
    # Matches 'accessToken' usage in the Auth code.
    accessToken: str

# =======================
# Token Model
# =======================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# =======================
# For user creation
# =======================
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    username: Optional[str] = None

class UserDBCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password_hash: str

# =======================
# For updating user info
# =======================
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    # etc...

# =======================
# For user retrieval
# =======================
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    created_at: str