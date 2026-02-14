from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import List

from ..dependencies import get_db, get_current_user
from ...db.models import User, WorkoutLog, WaterLog
from ...schemas.schemas import DashboardResponse, AIPulseResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/home", response_model=DashboardResponse)
async def get_dashboard_home(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated dashboard data for the home screen.
    Includes:
    - User streak and greeting
    - Weekly progress (last 7 days)
    - AI Pulse recommendation
    - Daily stats summary
    """
    now = datetime.utcnow()
    
    # 1. Weekly Progress (Last 7 days)
    # Return list of booleans indicating if a workout was done that day
    weekly_progress = []
    for i in range(7):
        # 0 = today, 1 = yesterday, ...
        # But for display we might want Mon-Sun or last 7 days.
        # Let's do last 7 days ending today.
        d = (now - timedelta(days=6-i)).date()
        
        query = select(func.count(WorkoutLog.id)).where(
            and_(
                WorkoutLog.user_id == current_user.id,
                func.date(WorkoutLog.created_at) == d
            )
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        weekly_progress.append(count > 0)

    # 2. Daily Stats Summary
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    stats_query = select(
        func.sum(WorkoutLog.duration).label("total_minutes"),
        func.count(WorkoutLog.id).label("exercises_count"),
        func.sum(WorkoutLog.calories).label("calories_burned")
    ).where(
        and_(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.created_at >= today_start
        )
    )
    stats_res = await db.execute(stats_query)
    stats_row = stats_res.one()
    
    stats_summary = {
        "minutes": int((stats_row.total_minutes or 0) / 60),
        "exercises": stats_row.exercises_count or 0,
        "calories": int(stats_row.calories_burned or 0),
        "calories_goal": 500,
        "avg_posture_score": 0,
        "posture_trend": 0
    }

    # 3. AI Pulse Recommendation (Mock logic for now, could be LLM based)
    # Simple logic: If morning -> Cardio, Evening -> Strength
    hour = now.hour
    if 5 <= hour < 12:
        ai_pulse = AIPulseResponse(
            title="Morning Energizer",
            exercises=["Jumping Jacks", "High Knees", "Squats"],
            duration=15,
            calories=150
        )
    elif 12 <= hour < 18:
        ai_pulse = AIPulseResponse(
            title="Lunch Break Power",
            exercises=["Pushups", "Lunges", "Plank"],
            duration=20,
            calories=180
        )
    else:
        ai_pulse = AIPulseResponse(
            title="Evening Decompress",
            exercises=["Yoga Stretch", "Child's Pose", "Deep Breathing"],
            duration=10,
            calories=50
        )

    # 4. Water Intake Summary
    water_query = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == current_user.id,
            WaterLog.created_at >= today_start
        )
    )
    water_res = await db.execute(water_query)
    water_total = water_res.scalar() or 0
    water_total = max(0, water_total)
    
    water_intake = {
        "current": water_total,
        "goal": 2500 # Default goal
    }

    return DashboardResponse(
        greeting=f"Hello, {current_user.username}!",
        streak=current_user.streak,
        weekly_progress=weekly_progress,
        ai_pulse=ai_pulse,
        stats_summary=stats_summary,
        water_intake=water_intake
    )
