from typing import Optional
from sqlalchemy.orm import Session
from app.infrastructure.database.models import CravingLogModel, UserModel, VoiceLogModel
from app.infrastructure.auth.jwt_handler import verify_password

class CravingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, craving_log_data: dict) -> CravingLogModel:
        db_craving_log = CravingLogModel(**craving_log_data)
        self.db.add(db_craving_log)
        self.db.commit()
        self.db.refresh(db_craving_log)
        return db_craving_log

    def get_by_id(self, craving_log_id: int) -> Optional[CravingLogModel]:
        return (
            self.db.query(CravingLogModel)
            .filter(CravingLogModel.id == craving_log_id)
            .first()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> list[CravingLogModel]:
        return self.db.query(CravingLogModel).offset(skip).limit(limit).all()

    def get_by_user_id(self, user_id: int) -> list[CravingLogModel]:
         return self.db.query(CravingLogModel).filter(CravingLogModel.user_id == user_id).all()

    # Add other CRUD methods as needed (update, delete, etc.)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, username: Optional[str], password_hash: str) -> UserModel:
        db_user = UserModel(email=email, username=username, password_hash=password_hash)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def update_user(self, user: UserModel) -> None:
        self.db.commit()
        self.db.refresh(user)

    def authenticate_user(self, username: str, password: str) -> Optional[UserModel]:
        """Authenticates a user by username/email and password."""
        user = self.get_by_username(username)
        if not user:
          user = self.get_by_email(username)
          if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user


class VoiceLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, voice_log_data: dict) -> VoiceLogModel:
        db_voice_log = VoiceLogModel(**voice_log_data)
        self.db.add(db_voice_log)
        self.db.commit()
        self.db.refresh(db_voice_log)
        return db_voice_log

    def get_by_id(self, voice_log_id: int) -> Optional[VoiceLogModel]:
        return (
            self.db.query(VoiceLogModel)
            .filter(VoiceLogModel.id == voice_log_id)
            .first()
        )
    def get_all(self, skip: int = 0, limit: int = 100) -> list[VoiceLogModel]:
        return self.db.query(VoiceLogModel).offset(skip).limit(limit).all()

    def get_by_user_id(self, user_id: int) -> list[VoiceLogModel]:
         return self.db.query(VoiceLogModel).filter(VoiceLogModel.user_id == user_id).all()

    # Add other CRUD methods as needed (update, delete, etc.)