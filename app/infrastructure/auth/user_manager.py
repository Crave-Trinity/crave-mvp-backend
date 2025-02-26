# File: app/infrastructure/auth/user_manager.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.infrastructure.database.models import UserModel

# For hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager:
    """
    Manages user retrieval and creation in the DB, along with password hashing.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> UserModel | None:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, email: str, password: str, username: str | None = None) -> UserModel:
        """
        Create a new user with hashed password, return the UserModel object.
        """
        hashed_pw = self.hash_password(password)
        new_user = UserModel(
            email=email,
            password_hash=hashed_pw,
            username=username,
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def hash_password(self, raw_password: str) -> str:
        """Hash plaintext password using passlib."""
        return pwd_context.hash(raw_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify that a plain password matches the stored hashed password."""
        return pwd_context.verify(plain_password, hashed_password)

    def deactivate_user(self, user_id: int):
        """Mark a user as inactive."""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            user.is_active = False
            self.db.commit()
            self.db.refresh(user)
        return user

    # ------------------------------------------------------------------
    # NEW METHOD FOR PARTIAL PROFILE UPDATES
    # ------------------------------------------------------------------
    def update_user_profile(self, user_id: int, updates: dict) -> UserModel | None:
        """
        Partially update a user's profile fields.

        Args:
            user_id (int): The unique ID of the user to update.
            updates (dict): Fields to update (e.g., {"username": "NewName"}).

        Returns:
            UserModel | None: The updated user object, or None if not found.
        """
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            return None

        # Whitelist only certain fields for updates:
        allowed_fields = {"username", "display_name", "avatar_url", "email"}

        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user