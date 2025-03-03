#======================================================================
# File: app/api/endpoints/ai_endpoints.py
# Directory: your_project/app/api/endpoints
# Purpose:
#    FastAPI endpoint that returns a "message" key matching the frontend.
#    Demonstrates SOLID, testable design, minimal but clear commentary.
#======================================================================

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
    # We deliberately use "message" to match the frontend's DTO
    message: str

# Dependency for extracting current user from token
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Extracts the current user from JWT token via AuthService.
    Ensures only authenticated requests access the chat endpoint.
    """
    return AuthService().get_current_user(token=token)

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_v1(
    payload: ChatRequestDTO, 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Receives a user query and returns an AI-generated response (ChatGPT).
    The 'message' key is essential for aligning with the Swift client's decoding.
    """
    try:
        # Use your actual OpenAI API key here
        openai.api_key = get_settings().OPENAI_API_KEY

        # Example: GPT-3.5-turbo chat completion
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": payload.userQuery}
            ],
            temperature=0.7
        )
        # Return exactly "message" in JSON
        return {"message": response.choices[0].message.content}

    except Exception as exc:
        print("OpenAI Chat Error:", str(exc))
        raise HTTPException(status_code=500, detail="Chat error: " + str(exc))