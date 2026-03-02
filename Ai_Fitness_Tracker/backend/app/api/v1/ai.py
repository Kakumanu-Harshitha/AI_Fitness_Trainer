from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from ...db.models import User
from ..dependencies import get_current_user
from ...core_ai.personalization_model import predict

router = APIRouter(prefix="/ai", tags=["AI Personalization"])

class PersonalizeRequest(BaseModel):
    age: int = Field(..., ge=10, le=100)
    gender: str
    height_cm: float = Field(..., gt=0)
    weight_kg: float = Field(..., gt=0)
    workout_type: str = "general"
    experience_level: str = "Beginner"
    workout_frequency: int = 3
    session_duration: float = 30.0

class PersonalizeResponse(BaseModel):
    calories: float
    water: float
    intensity: int

@router.post("/personalize", response_model=PersonalizeResponse)
async def personalize(req: PersonalizeRequest, user: User = Depends(get_current_user)):
    data: Dict[str, Any] = req.model_dump()
    res = predict(data)
    return res
