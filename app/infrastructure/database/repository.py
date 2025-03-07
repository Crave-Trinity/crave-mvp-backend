# File: app/infrastructure/database/repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
import logging

from app.infrastructure.database.models import CravingModel, UserModel

logger = logging.getLogger(__name__)

class CravingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_craving(self, user_id: int, description: str, intensity: float) -> CravingModel:
        logger.info("Creating new craving", extra={"user_id": user_id})
        try:
            new_craving = CravingModel(
                user_id=user_id,
                description=description,
                intensity=intensity
            )
            self.db.add(new_craving)
            self.db.commit()
            self.db.refresh(new_craving)
            logger.info("Craving created successfully", extra={"craving_id": new_craving.id})
            return new_craving
        except Exception:
            logger.error("Error creating craving", exc_info=True, extra={"user_id": user_id})
            self.db.rollback()
            raise

    def get_cravings_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[CravingModel]:
        logger.debug("Fetching cravings for user", extra={"user_id": user_id, "skip": skip, "limit": limit})
        try:
            return (
                self.db.query(CravingModel)
                .filter(CravingModel.user_id == user_id, CravingModel.is_deleted == False)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception:
            logger.error("Error fetching cravings", exc_info=True, extra={"user_id": user_id})
            raise

    def count_cravings_for_user(self, user_id: int) -> int:
        logger.debug("Counting cravings for user", extra={"user_id": user_id})
        try:
            return (
                self.db.query(CravingModel)
                .filter(CravingModel.user_id == user_id, CravingModel.is_deleted == False)
                .count()
            )
        except Exception:
            logger.error("Error counting cravings", exc_info=True, extra={"user_id": user_id})
            raise

    def get_craving_by_id(self, craving_id: int) -> Optional[CravingModel]:
        logger.debug("Getting craving by ID", extra={"craving_id": craving_id})
        try:
            return (
                self.db.query(CravingModel)
                .filter(CravingModel.id == craving_id, CravingModel.is_deleted == False)
                .first()
            )
        except Exception:
            logger.error("Error getting craving by ID", exc_info=True, extra={"craving_id": craving_id})
            raise


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self,
        email: str,
        password_hash: Optional[str] = None,
        username: Optional[str] = None,
        display_name: Optional[str] = None,
        avatar_url: Optional[str] = None,
        oauth_provider: Optional[str] = None
    ) -> UserModel:
        logger.info("Creating new user", extra={"email": email})
        try:
            user = UserModel(
                email=email,
                password_hash=password_hash,
                username=username,
                display_name=display_name,
                avatar_url=avatar_url,
                oauth_provider=oauth_provider
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info("User created successfully", extra={"user_id": user.id})
            return user
        except Exception:
            logger.error("Error creating user", exc_info=True, extra={"email": email})
            self.db.rollback()
            raise

    def get_by_email(self, email: str) -> Optional[UserModel]:
        logger.debug("Getting user by email", extra={"email": email})
        try:
            return self.db.query(UserModel).filter(UserModel.email == email).first()
        except Exception:
            logger.error("Error getting user by email", exc_info=True, extra={"email": email})
            raise

    def get_by_username(self, username: str) -> Optional[UserModel]:
        logger.debug("Getting user by username", extra={"username": username})
        try:
            return self.db.query(UserModel).filter(UserModel.username == username).first()
        except Exception:
            logger.error("Error getting user by username", exc_info=True, extra={"username": username})
            raise

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        logger.debug("Getting user by ID", extra={"user_id": user_id})
        try:
            return self.db.query(UserModel).filter(UserModel.id == user_id).first()
        except Exception:
            logger.error("Error getting user by ID", exc_info=True, extra={"user_id": user_id})
            raise