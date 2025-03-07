"""
File: app/api/endpoints/craving_logs.py
Description: Defines the API endpoints for handling cravings,
including creation, listing, and retrieval, matching the front-end CravingEntity.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from uuid import UUID as pyUUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.infrastructure.database.repository import CravingRepository
from app.infrastructure.database.models import CravingModel

router = APIRouter()

# -------------------------------------------------------------------------
# REQUEST/RESPONSE MODELS
# -------------------------------------------------------------------------

class CreateCravingRequest(BaseModel):
    """
    Matches front-end's CravingEntity:
    - id (UUID)
    - cravingDescription (String)
    - cravingStrength (Double)
    - confidenceToResist (Double)
    - emotions ([String])
    - timestamp (DateTime, ideally ISO8601)
    - isArchived (Bool)
    user_id is also needed.
    """
    id: Optional[pyUUID] = Field(None, description="UUID from front end if available")
    user_id: int = Field(..., description="User ID logging the craving")
    cravingDescription: str
    cravingStrength: float
    confidenceToResist: float
    emotions: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    isArchived: bool = False

class CravingResponse(BaseModel):
    """
    Response model that maps exactly to front-end's CravingEntity.
    """
    id: pyUUID
    user_id: int
    cravingDescription: str
    cravingStrength: float
    confidenceToResist: float
    emotions: List[str]
    timestamp: datetime
    isArchived: bool

class CravingListResponse(BaseModel):
    """
    Response model for listing cravings.
    """
    cravings: List[CravingResponse]
    count: int

# -------------------------------------------------------------------------
# ENDPOINTS (Corrected Routes)
# -------------------------------------------------------------------------

@router.post("/", response_model=CravingResponse, tags=["Cravings"])
async def create_craving(
    request: CreateCravingRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new craving entry that aligns with the front end's CravingEntity.
    """
    try:
        repo = CravingRepository(db)
        # Use a valid UUID if not provided
        craving_uuid = request.id or uuid.uuid4()
        new_craving = CravingModel(
            craving_uuid=craving_uuid,
            user_id=request.user_id,
            description=request.cravingDescription,
            intensity=request.cravingStrength,
            confidence_to_resist=request.confidenceToResist,
            emotions=request.emotions,
            timestamp=request.timestamp,
            is_archived=request.isArchived,
            is_deleted=False
        )
        db.add(new_craving)
        db.commit()
        db.refresh(new_craving)
        return CravingResponse(
            id=new_craving.craving_uuid,
            user_id=new_craving.user_id,
            cravingDescription=new_craving.description,
            cravingStrength=new_craving.intensity,
            confidenceToResist=new_craving.confidence_to_resist or 0.0,
            emotions=new_craving.emotions or [],
            timestamp=new_craving.timestamp,
            isArchived=new_craving.is_archived
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create craving: {str(e)}")

@router.get("/{craving_uuid}", response_model=CravingResponse, tags=["Cravings"])
async def get_craving(
    craving_uuid: pyUUID = Path(..., description="The UUID of the craving to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a single craving by its UUID.
    """
    try:
        repo = CravingRepository(db)
        craving = db.query(CravingModel).filter(
            CravingModel.craving_uuid == craving_uuid,
            CravingModel.is_deleted == False
        ).first()
        if not craving:
            raise HTTPException(status_code=404, detail=f"Craving with UUID {craving_uuid} not found")
        return CravingResponse(
            id=craving.craving_uuid,
            user_id=craving.user_id,
            cravingDescription=craving.description,
            cravingStrength=craving.intensity,
            confidenceToResist=craving.confidence_to_resist or 0.0,
            emotions=craving.emotions or [],
            timestamp=craving.timestamp,
            isArchived=craving.is_archived
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=CravingListResponse, tags=["Cravings"])
async def list_cravings(
    user_id: int = Query(..., description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db)
):
    """
    Paginated list of cravings for the specified user.
    """
    try:
        repo = CravingRepository(db)
        query = db.query(CravingModel).filter(
            CravingModel.user_id == user_id,
            CravingModel.is_deleted == False
        )
        cravings = query.offset(skip).limit(limit).all()
        count = query.count()
        craving_responses = [
            CravingResponse(
                id=c.craving_uuid,
                user_id=c.user_id,
                cravingDescription=c.description,
                cravingStrength=c.intensity,
                confidenceToResist=c.confidence_to_resist or 0.0,
                emotions=c.emotions or [],
                timestamp=c.timestamp,
                isArchived=c.is_archived
            )
            for c in cravings
        ]
        return CravingListResponse(cravings=craving_responses, count=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list cravings: {str(e)}")