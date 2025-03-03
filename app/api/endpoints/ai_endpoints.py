# ==============================================================
#  ai_endpoints.py
#  FastAPI endpoints for AI-related features
#  Uncle Bob + GoF + Clean Architecture
# ==============================================================

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

from app.core.use_cases.generate_craving_insights import generate_insights
from app.core.services.analytics_service import analyze_patterns, list_personas
from app.core.services.rag_service import rag_service
from app.api.dependencies import get_current_user
from app.infrastructure.database.models import UserModel

router = APIRouter()

# ----------------------------------------------------------------
# Existing Models for other AI endpoints
# ----------------------------------------------------------------
class InsightResponse(BaseModel):
    insights: str
    model_config = ConfigDict(from_attributes=True)

class PatternsResponse(BaseModel):
    patterns: dict
    model_config = ConfigDict(from_attributes=True)

class PersonasResponse(BaseModel):
    personas: List[str]
    model_config = ConfigDict(from_attributes=True)

class RAGRequest(BaseModel):
    query: str
    persona: Optional[str] = None
    top_k: Optional[int] = 5
    time_weighted: Optional[bool] = True

class RAGResponse(BaseModel):
    answer: str
    model_config = ConfigDict(from_attributes=True)


@router.post("/ai/insights", tags=["AI"], response_model=InsightResponse)
async def ai_insights(user_id: int, query: Optional[str] = None):
    """
    Generate AI insights based on a user's craving history.
    Final URL: POST /api/ai/insights
    """
    try:
        insights = generate_insights(user_id, query)
        return {"insights": insights}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI insights error: {exc}")


@router.get("/ai/patterns", tags=["AI"], response_model=PatternsResponse)
async def ai_patterns(user_id: int):
    """
    Retrieve pattern analysis of the user's cravings.
    Final URL: GET /api/ai/patterns
    """
    try:
        patterns = analyze_patterns(user_id)
        return {"patterns": patterns}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pattern analysis error: {exc}")


@router.get("/ai/personas", tags=["AI"], response_model=PersonasResponse)
async def ai_personas():
    """
    List available craving personas.
    Final URL: GET /api/ai/personas
    """
    try:
        personas = list_personas()
        return {"personas": personas}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Personas retrieval error: {exc}")


@router.post("/ai/rag/insights", tags=["AI"], response_model=RAGResponse)
async def rag_insights(
    request: RAGRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Generate personalized insights using RAG (Retrieval-Augmented Generation).
    Final URL: POST /api/ai/rag/insights
    """
    try:
        answer = rag_service.generate_personalized_insight(
            user_id=current_user.id,
            query=request.query,
            persona=request.persona,
            top_k=request.top_k,
            time_weighted=request.time_weighted
        )
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"RAG generation failed: {str(exc)}"
        )


@router.post("/ai/query", tags=["AI"], response_model=RAGResponse)
async def ai_query(
    query: str,
    persona: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Legacy endpoint for querying the AI about cravings.
    Final URL: POST /api/ai/query
    """
    try:
        answer = rag_service.generate_personalized_insight(
            user_id=current_user.id,
            query=query,
            persona=persona
        )
        return {"answer": answer}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"AI query failed: {str(exc)}"
        )


# ----------------------------------------------------------------
# NEW: v1/chat endpoint matching the iOS frontend’s POST /api/v1/chat
# ----------------------------------------------------------------
class ChatRequestDTO(BaseModel):
    userQuery: str

class ChatResponseDTO(BaseModel):
    message: str

@router.post("/v1/chat", tags=["Chat"], response_model=ChatResponseDTO)
async def chat_v1(
    payload: ChatRequestDTO,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Handles the chat-based AI request from the iOS app’s POST /api/v1/chat.
    Returns JSON in { "message": "<AI response>" } format.
    """
    try:
        answer = rag_service.generate_personalized_insight(
            user_id=current_user.id,
            query=payload.userQuery
        )
        return {"message": answer}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(exc)}"
        )