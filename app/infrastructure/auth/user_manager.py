# app/infrastructure/auth/user_manager.py
from typing import Optional, Dict
from app.infrastructure.database.repository import UserRepository
from app.infrastructure.auth.password_hasher import hash_password, verify_password
from app.infrastructure.database.models import UserModel

class UserManager:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.repository.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        return self.repository.get_by_username(username)

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

    async def get_or_create_oauth_user(
        self, provider: str, email: str,
        name: Optional[str] = None, picture: Optional[str] = None
    ) -> UserModel:
        user = self.repository.get_by_email(email)
        if user:
            return user
        # Clearly handles creation of new OAuth-authenticated user
        user = self.repository.create_user(
            email=email,
            username=None,
            password_hash=None,
            display_name=name,
            avatar_url=picture,
            oauth_provider=provider
        )
        return user

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

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