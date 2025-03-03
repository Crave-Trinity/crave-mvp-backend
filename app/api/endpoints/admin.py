#====================================================
# File: app/api/endpoints/admin.py
#====================================================

# Import FastAPI's APIRouter and other needed modules
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel

# Initialize the router instance at the top
router = APIRouter()

# -------------------------------
# Existing Admin Endpoints
# -------------------------------
@router.post("/stamp-db")
def stamp_db():
    # ... your existing code for stamping the DB ...
    return {"detail": "Database stamped to 'head'"}

@router.post("/add-missing-column")
def add_missing_column():
    # ... your existing code for adding a column ...
    return {"detail": "Column added if missing"}

# -------------------------------
# New Endpoint: Generate Test Token
# -------------------------------
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
            hashed_password="fakehash",  # Use an appropriate placeholder
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