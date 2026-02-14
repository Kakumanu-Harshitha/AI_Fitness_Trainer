from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import User
from ...schemas.schemas import WorkoutCreate, WorkoutResponse
from ..dependencies import get_db, get_current_user
from ...services.workout_service import WorkoutService
from ...websockets import manager
import json

router = APIRouter(prefix="/workouts", tags=["Workouts"])

@router.post("/save", response_model=WorkoutResponse)
async def save_workout(
    data: WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    workout_service = WorkoutService(db)
    result = await workout_service.process_workout(user, data)
    
    # Broadcast real-time update
    msg = json.dumps({
        "type": "workout_completed",
        "user": user.username,
        "exercise": data.exercise,
        "reps": data.reps
    })
    await manager.broadcast(msg)
    
    return result


@router.get("/my", response_model=list[WorkoutResponse])
async def my_workouts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    workout_service = WorkoutService(db)
    return await workout_service.get_user_workouts(user.id)


@router.get("/best/{exercise}", response_model=WorkoutResponse | None)
async def best_workout(
    exercise: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    workout_service = WorkoutService(db)
    return await workout_service.get_best_workout(user.id, exercise)
