#====================================================
# File: app/api/endpoints/ai_endpoints.py (CORRECTED - with Authentication)
#====================================================
from fastapi import APIRouter, HTTPException, Depends  # Import Depends
from pydantic import BaseModel
from openai import OpenAI
from app.config.settings import get_settings
from app.infrastructure.auth.auth_service import AuthService, oauth2_scheme  # Correct import
from app.infrastructure.database.models import UserModel # Import the user model

router = APIRouter()

class ChatRequestDTO(BaseModel):
    userQuery: str

class ChatResponseDTO(BaseModel):
    message: str

# Dependency for getting the current user
def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Gets the current user from the auth service
    """
    auth_service = AuthService()  # Create an instance of AuthService
    return auth_service.get_current_user(token=token)

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_v1(payload: ChatRequestDTO, current_user: UserModel = Depends(get_current_user)):  # Add authentication
    try:
        client = OpenAI(api_key=get_settings().OPENAI_API_KEY)
        response = client.chat.completions.create(
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
        raise HTTPException(status_code=500, detail=f"Chat error: {str(exc)}")