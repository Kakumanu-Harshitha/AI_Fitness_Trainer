from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from ...db.models import User
from ..dependencies import get_current_user
from ...core_ai.coach.lifestyle_bot import ask_lifestyle_bot

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(
    request: ChatRequest,
    user: User = Depends(get_current_user)
):
    # Construct user context from profile
    user_context = {
        "username": user.username,
        "age": user.age,
        "height_cm": user.height_cm,
        "weight_kg": user.weight_kg,
        "body_type": user.body_type,
        "activity_level": user.activity_level,
        "diet_goal": user.diet_goal,
        "daily_sleep_goal": user.daily_sleep_goal,
        "daily_water_goal": user.daily_water_goal,
        "injuries": user.injuries,
        "dietary_preferences": user.dietary_preferences
    }

    # Get response from AI
    bot_response = await ask_lifestyle_bot(user_context, request.message)
    
    return {"response": bot_response}
