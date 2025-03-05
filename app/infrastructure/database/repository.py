# app/infrastructure/database/repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from app.infrastructure.database.models import CravingModel, UserModel

class CravingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_craving(self, user_id: int, description: str, intensity: float) -> CravingModel:
        new_craving = CravingModel(
            user_id=user_id,
            description=description,
            intensity=intensity
        )
        self.db.add(new_craving)
        self.db.commit()
        self.db.refresh(new_craving)
        return new_craving

    def get_cravings_for_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[CravingModel]:
        return (self.db.query(CravingModel)
                .filter(CravingModel.user_id == user_id, CravingModel.is_deleted == False)
                .offset(skip)
                .limit(limit)
                .all())

    def count_cravings_for_user(self, user_id: int) -> int:
        return (self.db.query(CravingModel)
                .filter(CravingModel.user_id == user_id, CravingModel.is_deleted == False)
                .count())

    def get_craving_by_id(self, craving_id: int) -> Optional[CravingModel]:
        return (self.db.query(CravingModel)
                .filter(CravingModel.id == craving_id, CravingModel.is_deleted == False)
                .first())

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
        # Explicitly handles both traditional and OAuth user creation
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
        return user

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()