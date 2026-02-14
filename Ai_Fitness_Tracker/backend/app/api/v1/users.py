from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.models import User
from ...schemas.schemas import UserResponse, ProfileUpdate, ProfileResponse
from ..dependencies import get_db, get_current_user
from ...db.repositories.user_repo import UserRepository
from ...core.security import create_access_token

router = APIRouter(prefix="/profile", tags=["Profile"])


from sqlalchemy import select, func

@router.get("", response_model=UserResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    print(f"DEBUG: get_profile starting for user {user.username}")
    try:
        # Fetch additional stats for the profile
        from ...db.models import WorkoutLog
        
        stats_query = select(
            func.count(WorkoutLog.id).label("total_workouts"),
            func.sum(WorkoutLog.duration).label("total_duration"),
            func.sum(WorkoutLog.calories).label("total_calories"),
            func.avg(WorkoutLog.posture_score).label("avg_score"),
            func.sum(WorkoutLog.reps).label("total_reps")
        ).where(WorkoutLog.user_id == user.id)
        
        result = await db.execute(stats_query)
        stats = result.one()
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "age": user.age,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "points": user.points,
            "streak": user.streak,
            "profile_image": user.profile_image,
            "total_workouts": stats.total_workouts or 0,
            "total_duration": stats.total_duration or 0,
            "total_calories": stats.total_calories or 0.0,
            "avg_score": stats.avg_score or 0.0,
            "total_reps": stats.total_reps or 0,
            "created_at": user.created_at
        }
        print(f"DEBUG: get_profile returning data for {user.username}")
        return user_dict
    except Exception as e:
        print(f"ERROR in get_profile: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e


@router.post("", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    user_repo = UserRepository(db)
    old_username = user.username
    updated_user = await user_repo.update(user, data)
    
    response = {"user": updated_user}
    
    # If username changed, issue a new token
    if updated_user.username != old_username:
        access_token = create_access_token(data={"sub": updated_user.username})
        response["access_token"] = access_token
        
    return response
