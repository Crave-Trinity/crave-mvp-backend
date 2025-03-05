# app/api/endpoints/analytics.py
"""
Analytics endpoints for CRAVE Trinity Backend.

Provides endpoints for analyzing craving patterns, including
a /basic route that returns BasicAnalyticsResult matching the front-end.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from pydantic import BaseModel
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import CravingModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------------------------------------------------
# BASIC ANALYTICS MATCHING THE FRONT-END
# -------------------------------------------------------------------------
class BasicAnalyticsResponse(BaseModel):
    """
    Matches front-end's BasicAnalyticsResult:
    - totalCravings
    - totalResisted
    - averageIntensity
    - averageResistance
    - successRate
    - cravingsByDate (date-string -> int)
    """
    user_id: int
    period: str
    totalCravings: int
    totalResisted: int
    averageIntensity: float
    averageResistance: float
    successRate: float
    cravingsByDate: Dict[str, int]


@router.get("/user/{user_id}/basic", response_model=BasicAnalyticsResponse, tags=["Analytics"])
async def get_basic_craving_analytics(
    user_id: int,
    days: Optional[int] = Query(30, description="Analyze the last N days"),
    db: Session = Depends(get_db)
):
    """
    Computes a 'BasicAnalyticsResult' for the specified user, from [now - days] to now.
    1) totalCravings
    2) totalResisted (confidence_to_resist > 7)
    3) averageIntensity
    4) averageResistance
    5) successRate (resisted / total * 100)
    6) cravingsByDate
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    query = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.timestamp >= start_date,
        CravingModel.timestamp <= end_date
    )

    # If your 'cravings' table does have user_id, filter:
    query = query.filter(CravingModel.user_id == user_id)

    cravings = query.all()
    if not cravings:
        return BasicAnalyticsResponse(
            user_id=user_id,
            period=f"Last {days} days",
            totalCravings=0,
            totalResisted=0,
            averageIntensity=0.0,
            averageResistance=0.0,
            successRate=0.0,
            cravingsByDate={}
        )

    total = len(cravings)
    total_resisted = sum([
        1 for c in cravings if (c.confidence_to_resist or 0.0) > 7.0
    ])

    intensities = [c.intensity for c in cravings]
    resistances = [c.confidence_to_resist for c in cravings if c.confidence_to_resist is not None]

    avg_intensity = sum(intensities) / len(intensities) if intensities else 0.0
    avg_resistance = sum(resistances) / len(resistances) if resistances else 0.0
    success_rate = (total_resisted / total * 100.0) if total > 0 else 0.0

    # group by date string
    cravings_by_date = defaultdict(int)
    for c in cravings:
        day_str = c.timestamp.strftime("%Y-%m-%d")
        cravings_by_date[day_str] += 1

    return BasicAnalyticsResponse(
        user_id=user_id,
        period=f"Last {days} days",
        totalCravings=total,
        totalResisted=total_resisted,
        averageIntensity=avg_intensity,
        averageResistance=avg_resistance,
        successRate=success_rate,
        cravingsByDate=dict(cravings_by_date)
    )


# -------------------------------------------------------------------------
# OTHER ANALYTICS ENDPOINTS (unchanged)
# -------------------------------------------------------------------------
class AnalyticsResponse(BaseModel):
    user_id: int
    period: str
    total_cravings: Optional[int] = 0
    average_intensity: Optional[float] = 0
    max_intensity: Optional[float] = 0
    min_intensity: Optional[float] = 0
    std_deviation: Optional[float] = 0
    message: Optional[str] = None

@router.get("/user/{user_id}/summary", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_user_craving_summary(
   user_id: int,
   days: Optional[int] = Query(30),
   db: Session = Depends(get_db)
) -> AnalyticsResponse:
    # old logic remains
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    cravings = db.query(CravingModel).filter(
        CravingModel.is_deleted == False,
        CravingModel.timestamp >= start_date,
        CravingModel.timestamp <= end_date,
        CravingModel.user_id == user_id
    ).all()

    if not cravings:
        return AnalyticsResponse(
            user_id=user_id,
            period=f"Last {days} days",
            message="No cravings recorded in this period."
        )

    intensities = [c.intensity for c in cravings]
    avg_int = sum(intensities) / len(intensities) if intensities else 0
    return AnalyticsResponse(
        user_id=user_id,
        period=f"Last {days} days",
        total_cravings=len(cravings),
        average_intensity=round(avg_int, 1),
        max_intensity=max(intensities),
        min_intensity=min(intensities),
        std_deviation=round(statistics.stdev(intensities), 2) if len(intensities) > 1 else 0
    )