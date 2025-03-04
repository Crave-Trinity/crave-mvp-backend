# app/api/endpoints/ai_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import openai
from app.config.settings import get_settings
from app.infrastructure.auth.auth_service import oauth2_scheme, AuthService
from app.infrastructure.database.models import UserModel

router = APIRouter()

class ChatRequestDTO(BaseModel):
    userQuery: str

class ChatResponseDTO(BaseModel):
    message: str

# Revert to the original dependency (only token injection)
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Extracts the current user using AuthService. This function now
    calls AuthService().get_current_user with only the token, so that the
    internal dependency resolution in AuthService (for the database session)
    is used.
    """
    return AuthService().get_current_user(token=token)

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_v1(
    payload: ChatRequestDTO, 
    current_user: UserModel = Depends(get_current_user)
):
    try:
        openai.api_key = get_settings().OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": payload.userQuery}
            ],
            temperature=0.7
        )
        return {"message": response.choices[0].message.content}
    except Exception as exc:
        print("OpenAI Chat Error:", str(exc))
        raise HTTPException(status_code=500, detail="Chat error: " + str(exc))