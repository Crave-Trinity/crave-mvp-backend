# File: app/api/endpoints/auth_endpoints.py

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Dependencies and DB
from app.api.dependencies import (
    get_db,
    get_user_repository,
    get_current_user,
)
from app.infrastructure.database.models import UserModel

# JWT and password helpers
from app.infrastructure.auth.jwt_handler import create_access_token
from app.infrastructure.auth.password_hasher import (
    verify_password,
    hash_password
)

# -- IMPORTANT FIX: we import from app.core.entities.auth_schemas instead of app.schemas.auth_schemas
from app.core.entities.auth_schemas import (
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserDBCreate,
)

# Settings
from app.config.settings import get_settings

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
    user_repo=Depends(get_user_repository),
):
    """
    Endpoint to authenticate a user and return an access token.
    """
    # Find user by username or email
    user = user_repo.get_by_username(form_data.username)
    if not user:
        user = user_repo.get_by_email(form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = get_settings().JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": user.username or user.email},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_repo=Depends(get_user_repository),
):
    """Endpoint to register a new user (includes hashing the password)."""
    # Check for existing user by email or username
    existing_user_email = user_repo.get_by_email(user.email)
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists.",
        )
    existing_user_username = user_repo.get_by_username(user.username)
    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists.",
        )

    # Use the correct hashing function
    hashed_password = hash_password(user.password)

    db_user = UserDBCreate(
        **user.model_dump(exclude={"password"}),
        password_hash=hashed_password,
    )

    created_user = user_repo.create_user(
        email=db_user.email,
        username=db_user.username,
        password_hash=db_user.password_hash,
    )

    return created_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Get current user info from JWT credentials."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    user_repo=Depends(get_user_repository),
):
    """Update current user's info."""
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    user_repo.update_user(current_user)
    return current_user
