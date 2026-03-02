from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional

from ...db.models import User
from ..dependencies import get_current_user
from ...core_ai.coach.lifestyle_bot import ask_lifestyle_bot, ask_coach_formatted
from ...core_ai.personalization_model import predict

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

    t = (request.message or "").strip().lower()
    triggers = ["what should i do", "give me a plan", "how can i improve"]
    if any(k in t for k in triggers):
        gender = "male"
        if user.body_type and "female" in (user.body_type or "").lower():
            gender = "female"
        data = {
            "age": int(user.age or 25),
            "gender": gender,
            "height_cm": float(user.height_cm or 170),
            "weight_kg": float(user.weight_kg or 70),
            "workout_type": "general",
            "experience_level": "Beginner",
            "workout_frequency": 3,
            "session_duration": 30.0
        }
        preds = predict(data)
        bot_response = await ask_coach_formatted(user_context, preds, request.message)
    else:
        bot_response = await ask_lifestyle_bot(user_context, request.message)
    
    return {"response": bot_response}
