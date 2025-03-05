# app/core/entities/craving.py
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Craving(BaseModel):
    id: Optional[int] = None
    user_id: int
    description: str
    intensity: float
    created_at: datetime

    class Config:
        from_attributes = True