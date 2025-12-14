from pydantic import BaseModel
from typing import Optional
# -------- USER SCHEMAS --------

class UserRegister(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    age: Optional[int]
    height_cm: Optional[float]
    weight_kg: Optional[float]

    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    token: str
    user: UserResponse


# -------- WORKOUT SCHEMAS --------

class WorkoutCreate(BaseModel):
    exercise: str
    reps: int
    duration: int
    avg_angle: float


class WorkoutResponse(BaseModel):
    id: int
    user_id: int
    exercise: str
    reps: int
    duration: int
    calories: float
    posture_score: float

    model_config = {
        "from_attributes": True
    }
class ProfileUpdate(BaseModel):
    age: Optional[int] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


