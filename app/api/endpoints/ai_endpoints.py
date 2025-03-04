# app/api/endpoints/ai_endpoints.py
# app/api/endpoints/ai_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import openai
from sqlalchemy.orm import Session

from app.config.settings import get_settings
from app.infrastructure.auth.auth_service import oauth2_scheme, AuthService
from app.infrastructure.database.models import UserModel
from app.api.dependencies import get_db

router = APIRouter()

class ChatRequestDTO(BaseModel):
    userQuery: str

class ChatResponseDTO(BaseModel):
    message: str

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    """
    Inject both the token and DB session, then use AuthService to get the current user.
    """
    return AuthService().get_current_user(token=token, db=db)

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_v1(
    payload: ChatRequestDTO, 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Receives a user query and returns an AI-generated response.

    Uses the new openai.chat.completions.create(...) function required for openai>=1.0.0.
    """
    try:
        # Use the new style of setting the API key
        openai.api_key = get_settings().OPENAI_API_KEY

        # NOTE: openai.ChatCompletion.create(...) is no longer valid in openai>=1.0.0
        # Instead, do:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # or whichever model you prefer
            messages=[
                {"role": "user", "content": payload.userQuery},
            ],
            temperature=0.7,
        )

        return {"message": response.choices[0].message.content}

    except Exception as exc:
        print("OpenAI Chat Error:", str(exc))
        raise HTTPException(
            status_code=500,
            detail="Chat error: " + str(exc)
        )