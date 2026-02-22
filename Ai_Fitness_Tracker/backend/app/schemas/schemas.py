from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# -------- USER SCHEMAS --------

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ChangePasswordRequest(BaseModel):
    new_password: str
    totp_code: Optional[str] = None

class TOTPSetupResponse(BaseModel):
    secret: str
    qr_code: str

class TOTPVerifyRequest(BaseModel):
    otp: str

class UserRegister(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    streak: int = 0
    xp: int = 0
    points: int = 0
    level: int = 1
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_image: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_type: Optional[str] = None
    diet_goal: Optional[str] = None
    activity_level: Optional[str] = None
    daily_sleep_goal: Optional[float] = None
    daily_water_goal: Optional[int] = None
    injuries: Optional[str] = None
    dietary_preferences: Optional[str] = None
    created_at: Optional[datetime] = None
    # Stats fields for profile
    total_workouts: Optional[int] = 0
    total_duration: Optional[int] = 0
    total_calories: Optional[float] = 0.0
    avg_score: Optional[float] = 0.0
    total_reps: Optional[int] = 0
    # Social field
    friendship_status: Optional[str] = None
    is_totp_enabled: Optional[bool] = False

    model_config = {
        "from_attributes": True
    }

class ProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_type: Optional[str] = None
    diet_goal: Optional[str] = None
    activity_level: Optional[str] = None
    daily_sleep_goal: Optional[float] = None
    daily_water_goal: Optional[int] = None
    injuries: Optional[str] = None
    dietary_preferences: Optional[str] = None
    bio: Optional[str] = None

class ProfileResponse(BaseModel):
    user: UserResponse
    access_token: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class BadgeResponse(BaseModel):
    id: int
    name: str
    description: str
    icon_url: str
    xp_reward: int

    model_config = {
        "from_attributes": True
    }

class UserBadgeResponse(BaseModel):
    badge: BadgeResponse
    unlocked_at: datetime

    model_config = {
        "from_attributes": True
    }

class RoutineStepCreate(BaseModel):
    exercise_name: str
    exercise_id: Optional[str] = None
    reps: Optional[int] = None
    sets: Optional[int] = None
    duration_seconds: Optional[int] = None
    order_index: Optional[int] = None
    icon: Optional[str] = None
    timing_type: Optional[str] = None
    quantity: Optional[int] = None
    vision_complexity: Optional[str] = "NORMAL"

class RoutineStepResponse(BaseModel):
    id: int
    exercise_name: str
    exercise_id: Optional[str]
    reps: Optional[int]
    sets: Optional[int]
    duration_seconds: Optional[int]
    order_index: Optional[int]
    icon: Optional[str]
    timing_type: Optional[str]
    quantity: Optional[int]
    vision_complexity: Optional[str]

    model_config = {
        "from_attributes": True
    }

class RoutineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    complexity: Optional[str] = "BALANCED"
    vision_complexity: Optional[str] = "NORMAL"
    type: Optional[str] = "fitness"
    steps: List[RoutineStepCreate]

class RoutineResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    complexity: Optional[str]
    vision_complexity: Optional[str]
    type: Optional[str]
    steps: List[RoutineStepResponse]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# -------- WORKOUT SCHEMAS --------

class WorkoutCreate(BaseModel):
    exercise: str = Field(..., min_length=2, max_length=50)
    reps: int = Field(..., ge=0, le=1000)
    duration: int = Field(..., ge=0, le=36000) # Max 10 hours
    avg_angle: float = Field(0.0, ge=0, le=360)
    calories: Optional[float] = Field(None, ge=0)
    posture_score: Optional[float] = Field(None, ge=0, le=100)
    replay_data: Optional[str] = None

class WorkoutResponse(BaseModel):
    id: int
    exercise: str
    reps: int
    duration: int
    calories: float
    posture_score: float
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class WorkoutLogCreate(BaseModel):
    exercise_name: str
    reps: int
    sets: int
    duration_seconds: Optional[int] = None
    calories_burned: Optional[float] = None

class WorkoutLogResponse(BaseModel):
    id: int
    exercise_name: str
    reps: int
    sets: int
    duration_seconds: Optional[int]
    calories_burned: Optional[float]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# -------- WATER SCHEMAS --------

class WaterLogCreate(BaseModel):
    amount_ml: int = Field(..., ge=-5000, le=5000)

class WaterLogResponse(BaseModel):
    id: int
    amount_ml: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class DailyWaterResponse(BaseModel):
    current: int
    goal: int

class AIPulseResponse(BaseModel):
    title: str
    exercises: List[str]
    duration: int
    calories: int

class DietPlanResponse(BaseModel):
    pre_workout: str
    post_workout: str
    analysis: str
    management_suggestion: str

class DashboardResponse(BaseModel):
    greeting: str
    streak: int
    weekly_progress: List[bool]
    ai_pulse: AIPulseResponse
    stats_summary: Dict[str, Any]
    water_intake: Dict[str, Any]
    diet_plan: Optional[DietPlanResponse] = None

# -------- SOCIAL SCHEMAS --------

class LeaderboardUser(BaseModel):
    rank: int
    id: int
    username: str
    points: int = 0
    streak: int = 0
    level: int = 1
    profile_image: Optional[str] = None
    friendship_status: Optional[str] = "none"

class UserLeaderboardResponse(BaseModel):
    users: List[LeaderboardUser]

class ActivityFeedItem(BaseModel):
    id: int
    user_id: int
    username: str
    profile_image: Optional[str] = None
    type: str
    details: str
    created_at: datetime

class FriendResponse(BaseModel):
    id: int
    username: str
    points: int = 0
    profile_image: Optional[str] = None
    status: str = "offline"
    streak: int = 0

class ChatMessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }

class FriendActivityResponse(BaseModel):
    id: int
    user_id: int
    username: str
    type: str
    details: str
    timestamp: datetime

class WorkoutPlanCreate(BaseModel):
    day_of_week: str
    exercise: str
    target_reps: int = 10
    target_sets: int = 3

class WorkoutPlanResponse(BaseModel):
    id: int
    day_of_week: str
    exercise: str
    target_reps: int
    target_sets: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
