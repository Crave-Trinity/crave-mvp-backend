#====================================================
# File: app/api/endpoints/admin.py
#====================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel

router = APIRouter()

@router.post("/stamp-db")
def stamp_db():
    """
    Stamp the database to mark it as up-to-date.
    (Replace with your stamping logic if needed.)
    """
    # [Your stamping logic here]
    return {"detail": "Database stamped to 'head'"}

@router.post("/add-missing-column")
def add_missing_column():
    """
    Add a missing column to the database if it does not exist.
    This endpoint is idempotent.
    """
    # [Your column addition logic here]
    return {"detail": "Column added if missing"}

@router.post("/generate-test-token")
def generate_test_token(db: Session = Depends(get_db)):
    """
    Generate a test JWT token for development purposes.

    Steps:
      1. Attempt to retrieve the admin user (with ID=1).
      2. If not found, create a minimal admin user.
      3. Generate a JWT using AuthService.generate_token.
      4. Return the token as JSON: {"token": "<jwt_token>"}.

    Note: This endpoint should be used only in development.
    """
    # Retrieve the admin user (ID=1)
    user = db.query(UserModel).filter(UserModel.id == 1).first()

    # If the admin user doesn't exist, create one with default values.
    if not user:
        user = UserModel(
            id=1,
            email="admin@example.com",
            username="admin",
            password_hash="fakehash",  # Must match the 'password_hash' column
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate a JWT token for the admin user.
    token = AuthService().generate_token(
        user_id=user.id,
        email=user.email
    )
    return {"token": token}