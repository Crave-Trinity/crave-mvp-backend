#====================================================
# File: app/api/endpoints/auth_endpoints.py
#====================================================
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_user_repository, get_current_user
from app.infrastructure.database.models import UserModel
from app.infrastructure.auth.jwt_handler import create_access_token
from app.infrastructure.auth.password_hasher import (
    verify_password,
    hash_password
)
from app.core.entities.auth_schemas import (
    Token,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserDBCreate,
)
from app.config.settings import get_settings

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
    user_repo=Depends(get_user_repository),
):
    """
    Authenticates the user via username/email + password.
    Returns a JWT whose 'sub' contains the user's integer ID.
    """
    user = (
        user_repo.get_by_username(form_data.username) or
        user_repo.get_by_email(form_data.username)
    )
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fixed: Store the integer user.id in 'sub', so you can cast to int later
    access_token_expires = get_settings().JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    access_token = create_access_token(
        data={"sub": str(user.id)},  # ID is always int; cast to string for JWT
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    user_repo=Depends(get_user_repository),
):
    """
    Creates a new user. Checks for existing email or username.
    """
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
    """
    Returns the current user's info (based on the JWT).
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    user_repo=Depends(get_user_repository),
):
    """
    Updates the currently logged-in user's profile fields.
    """
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    user_repo.update_user(current_user)
    return current_user