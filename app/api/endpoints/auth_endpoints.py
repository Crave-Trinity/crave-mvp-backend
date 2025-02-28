# app/api/endpoints/auth_endpoints.py
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_user_repository,
    get_current_user
)
from app.infrastructure.database.models import UserModel
from app.infrastructure.auth import (
    authenticate_user,
    create_access_token,
    verify_password,
)
from app.schemas.auth_schemas import (
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserDBCreate,
)

# NO DIRECT IMPORT OF settings HERE
from app.config.settings import get_settings

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    Endpoint to authenticate a user and return an access token.

    This endpoint handles user authentication using the OAuth2 password flow.
    It takes username/password credentials, validates them, and returns a JWT
    access token upon successful authentication.

    Args:
        form_data: OAuth2PasswordRequestForm containing username and password
        db: Database session dependency

    Returns:
        Token: Contains the access token and token type

    Raises:
        HTTPException: If authentication fails
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = get_settings().JWT_ACCESS_TOKEN_EXPIRE_MINUTES  # Use get_settings()
    access_token = create_access_token(
        data={"sub": user.username or user.email},  # Use username, fallback to email
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_repo=Depends(get_user_repository),
):
    """Endpoint to register a new user.
      This includes hashing the password."""
    # Check if user already exists (by email or username)
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

    # Hash the password
    hashed_password = verify_password(user.password)

    # Create a new user in the database
    db_user = UserDBCreate(
        **user.model_dump(exclude={"password"}), password_hash=hashed_password
    )  # Use pydantic .model_dump

    created_user = user_repo.create_user(
        email=db_user.email,
        username=db_user.username,
        password_hash=db_user.password_hash,
    )

    return created_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Endpoint to get the current user's information."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    user_repo=Depends(get_user_repository)
):
    """Endpoint to update the current user's information."""

    # Update user fields only if they are provided
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    user_repo.update_user(current_user)
    return current_user