# File: app/infrastructure/auth/user_manager.py
# PURPOSE: Manages user creation and retrieval.
#          For OAuth users, if no password is provided, an empty string is stored.
from typing import Optional, Dict
from app.infrastructure/database.repository import UserRepository
from app.infrastructure.database.models import UserModel

class UserManager:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.repository.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        return self.repository.get_by_username(username)

    def create_user(
        self, email: str, username: Optional[str], password: Optional[str],
        display_name: Optional[str] = None, avatar_url: Optional[str] = None,
        oauth_provider: Optional[str] = None
    ) -> UserModel:
        # For OAuth users, if password is None, set password_hash to empty string.
        hashed_password = ""
        if password:
            # If email/password login is used, insert hashing here.
            # For now, we simply use the plain password (or you can call your hashing function).
            hashed_password = password  
        return self.repository.create_user(
            email=email,
            username=username,
            password_hash=hashed_password,
            display_name=display_name,
            avatar_url=avatar_url,
            oauth_provider=oauth_provider
        )

    async def get_or_create_oauth_user(
        self, provider: str, email: str,
        name: Optional[str] = None, picture: Optional[str] = None
    ) -> UserModel:
        user = self.repository.get_by_email(email)
        if user:
            return user
        user = self.create_user(
            email=email,
            username=None,
            password=None,  # No password for OAuth users.
            display_name=name,
            avatar_url=picture,
            oauth_provider=provider
        )
        return user

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