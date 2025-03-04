# app/api/endpoints/ai_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import openai
from sqlalchemy.orm import Session
from app.config.settings import get_settings
from app.infrastructure.auth.auth_service import oauth2_scheme, AuthService
from app.infrastructure.database.models import UserModel
from app.api.dependencies import get_db  # Import the DB dependency

router = APIRouter()

class ChatRequestDTO(BaseModel):
    userQuery: str

class ChatResponseDTO(BaseModel):
    # The key "message" matches the expected JSON structure on the frontend.
    message: str

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)  # Now we also inject the DB session
) -> UserModel:
    """
    Extracts the current user using AuthService.
    This revised function passes both the token and the actual DB session,
    avoiding the error 'Depends object has no attribute "query"'.
    """
    return AuthService().get_current_user(token=token, db=db)

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_v1(
    payload: ChatRequestDTO, 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Receives a user query and returns an AI-generated response.
    Returns a JSON object with the key "message" to align with the frontend.
    """
    try:
        # Set the OpenAI API key from your settings.
        openai.api_key = get_settings().OPENAI_API_KEY

        # Generate a chat completion using GPT-3.5-turbo.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": payload.userQuery}
            ],
            temperature=0.7
        )
        # Return the generated message.
        return {"message": response.choices[0].message.content}

    except Exception as exc:
        print("OpenAI Chat Error:", str(exc))
        raise HTTPException(status_code=500, detail="Chat error: " + str(exc))