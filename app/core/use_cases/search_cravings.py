"""
File: app/api/endpoints/search_cravings.py
This module implements the search endpoint for the CRAVE Trinity Backend.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from datetime import datetime
from app.api.dependencies import get_db
from app.infrastructure.database.repository import CravingRepository

# Define a Pydantic model for outputting a craving record.
class CravingOut(BaseModel):
    id: int = Field(..., description="Unique identifier for the craving")
    user_id: int = Field(..., description="User ID associated with the craving")
    description: str = Field(..., description="Text description of the craving")
    intensity: int = Field(..., description="Intensity rating of the craving")
    created_at: datetime = Field(..., description="Timestamp when the craving was logged")
    model_config = ConfigDict(from_attributes=True)

# Define the response model for a search request.
class SearchResponse(BaseModel):
    cravings: List[CravingOut] = Field(..., description="List of cravings matching the search query")
    count: int = Field(..., description="Total number of matching cravings")
    model_config = ConfigDict(from_attributes=True)

router = APIRouter()

@router.get("", response_model=SearchResponse, tags=["Cravings"])
def search_cravings_endpoint(
    user_id: int = Query(..., description="User ID for search context"),
    query: str = Query(..., description="Search query text"),
    db = Depends(get_db)
):
    """
    Search for cravings that contain the provided query text in their description.
    """
    try:
        repo = CravingRepository(db)
        results = repo.search_cravings(user_id, query)
        cravings_out = [CravingOut.model_validate(craving) for craving in results]
        return SearchResponse(cravings=cravings_out, count=len(cravings_out))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cravings: {str(e)}")