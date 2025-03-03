#====================================================
# File: app/api/endpoints/ai_endpoints.py
#====================================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import openai
from app.config.settings import get_settings

router = APIRouter()

class ChatRequestDTO(BaseModel):
    userQuery: str

class ChatResponseDTO(BaseModel):
    message: str

@router.post("/chat", response_model=ChatResponseDTO)
async def chat_v1(payload: ChatRequestDTO):
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
        return {"message": response["choices"][0]["message"]["content"]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(exc)}")