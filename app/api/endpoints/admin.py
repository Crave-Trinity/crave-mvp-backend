# ======================================================
# File: app/api/endpoints/admin.py  (or admin_monitoring.py)
# Add this at the BOTTOM of the file.
# ======================================================
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel

@router.post("/generate-test-token")
def generate_test_token(db: Session = Depends(get_db)):
    """
    Creates a "test" JWT for development without requiring a real user login flow.
    
    1. Fetches or creates a user with ID=1 (our 'admin' user).
    2. Generates a JWT using AuthService.generate_token.
    3. Returns JSON: {"token": "<the_jwt_string>"}
    """
    # Try to find user #1 in the database
    user = db.query(UserModel).filter(UserModel.id == 1).first()
    
    # If it doesn't exist, create a minimal user #1 
    if not user:
        user = UserModel(
            id=1,
            email="admin@example.com",
            username="admin",
            hashed_password="",  # or "fakehash" if your model requires it
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate a token for that user
    token = AuthService().generate_token(
        user_id=user.id,
        email=user.email
    )
    return {"token": token}