from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Dict, Any

from ..dependencies import get_db, get_current_user
from ...db.models import User, WorkoutLog
from ...schemas.schemas import UserResponse

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("")
async def get_user_stats(
    time_range: str = Query("week", enum=["week", "month", "year"], alias="range"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user workout statistics for a given time range.
    """
    now = datetime.utcnow()
    if time_range == "week":
        start_date = now - timedelta(days=7)
        days_count = 7
    elif time_range == "month":
        start_date = now - timedelta(days=30)
        days_count = 30
    else: # year
        start_date = now - timedelta(days=365)
        days_count = 365

    # 1. Total statistics in range
    stats_query = select(
        func.count(WorkoutLog.id).label("total_workouts"),
        func.sum(WorkoutLog.duration).label("total_minutes"),
        func.avg(WorkoutLog.posture_score).label("avg_score"),
        func.sum(WorkoutLog.calories).label("calories_burned")
    ).where(
        and_(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.created_at >= start_date
        )
    )
    
    stats_result = await db.execute(stats_query)
    stats_row = stats_result.one()

    # 2. Fatigue Data (Simplified as posture scores over time)
    # We'll group by day for the last 7 days regardless of range for the chart
    fatigue_data = []
    for i in range(7):
        d = (now - timedelta(days=6-i)).date()
        day_query = select(func.avg(WorkoutLog.posture_score)).where(
            and_(
                WorkoutLog.user_id == current_user.id,
                func.date(WorkoutLog.created_at) == d
            )
        )
        day_res = await db.execute(day_query)
        score = day_res.scalar() or 0
        fatigue_data.append(float(score))

    # 3. Weekly Workouts (Count per day for last 7 days)
    weekly_workouts = []
    for i in range(7):
        d = (now - timedelta(days=6-i)).date()
        day_query = select(func.count(WorkoutLog.id)).where(
            and_(
                WorkoutLog.user_id == current_user.id,
                func.date(WorkoutLog.created_at) == d
            )
        )
        day_res = await db.execute(day_query)
        count = day_res.scalar() or 0
        weekly_workouts.append(int(count))

    # 4. Joint Stress (Mocked for now as it needs more complex vision data)
    joint_stress = [45, 32, 28, 38, 25]

    # 5. Personal Bests
    pb_query = select(
        WorkoutLog.exercise,
        func.max(WorkoutLog.reps).label("max_reps"),
        func.max(WorkoutLog.created_at).label("latest_date")
    ).where(
        WorkoutLog.user_id == current_user.id
    ).group_by(WorkoutLog.exercise)
    
    pb_result = await db.execute(pb_query)
    personal_bests = []
    for row in pb_result:
        personal_bests.append({
            "exercise": row.exercise,
            "reps": row.max_reps,
            "date": row.latest_date.strftime("%Y-%m-%d")
        })

    return {
        "totalWorkouts": stats_row.total_workouts or 0,
        "totalMinutes": int((stats_row.total_minutes or 0) / 60), # Convert seconds to minutes
        "avgScore": int(stats_row.avg_score or 0),
        "caloriesBurned": int(stats_row.calories_burned or 0),
        "fatigueData": fatigue_data,
        "jointStress": joint_stress,
        "weeklyWorkouts": weekly_workouts,
        "personalBests": personal_bests
    }
