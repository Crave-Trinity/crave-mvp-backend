# app/infrastructure/auth/user_manager.py
from typing import Optional, Dict
from app.infrastructure.database.repository import UserRepository
from app.infrastructure.auth.password_hasher import hash_password, verify_password
from app.infrastructure.database.models import UserModel

# Manages all user-related operations, clearly delegating DB access to UserRepository
class UserManager:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    # Retrieve a user by email address
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.repository.get_by_email(email)

    # Retrieve a user by username
    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        return self.repository.get_by_username(username)

    # Create traditional user with email/password authentication
    def create_user(
        self, email: str, username: Optional[str], password: str,
        display_name: Optional[str] = None, avatar_url: Optional[str] = None
    ) -> UserModel:
        hashed_password = hash_password(password)
        return self.repository.create_user(
            email=email,
            username=username,
            password_hash=hashed_password,
            display_name=display_name,
            avatar_url=avatar_url
        )

    # Create or retrieve an OAuth-authenticated user (no password needed)
    async def get_or_create_oauth_user(
        self, provider: str, email: str,
        name: Optional[str] = None, picture: Optional[str] = None
    ) -> UserModel:
        user = self.repository.get_by_email(email)
        if user:
            return user

        # New OAuth user creation clearly handled here
        user = self.repository.create_user(
            email=email,
            username=None,
            password_hash=None,
            display_name=name,
            avatar_url=picture,
            oauth_provider=provider
        )
        return user

    # Verify provided password against stored hashed password
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    # Update user's profile data clearly based on allowed fields only
    def update_user_profile(self, user_id: int, updates: Dict) -> Optional[UserModel]:
        user = self.repository.get_by_id(user_id)
        if user:
            allowed_fields = ["display_name", "avatar_url", "username"]
            for field, value in updates.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)
            self.repository.db.commit()
            self.repository.db.refresh(user)
        return user