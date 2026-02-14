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

    # 4. Joint Stress & Recovery (Calculated from recent activity)
    # Joint Stress is inversely proportional to average posture score
    stress_value = 100 - int(stats_row.avg_score or 90)
    stress_level = "Low"
    if stress_value > 60:
        stress_level = "High"
    elif stress_value > 30:
        stress_level = "Moderate"
    
    # Recovery Rate decreases with total workouts in the last 24h
    recent_workouts_count = await db.execute(
        select(func.count(WorkoutLog.id)).where(
            and_(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.created_at >= now - timedelta(days=1)
            )
        )
    )
    workouts_today = recent_workouts_count.scalar() or 0
    recovery_rate = max(10, 100 - (workouts_today * 15))

    # 5. Personal Bests (Normalized exercise names)
    # We'll use a subquery to normalize names and get max reps
    # In a real app, we might want a mapping table, but for now we'll lowercase and strip trailing 's'
    all_workouts_query = select(WorkoutLog).where(WorkoutLog.user_id == current_user.id)
    all_workouts_res = await db.execute(all_workouts_query)
    all_workouts = all_workouts_res.scalars().all()

    pb_dict = {}
    for w in all_workouts:
        # Normalize: lowercase, strip 's' if it's at the end (simplistic)
        norm_name = w.exercise.lower().strip()
        if norm_name.endswith('s') and norm_name not in ['pushups', 'squats']: # Keep these as they are common
             pass # just for logic flow
        
        # Better normalization: handle known plural/singular
        if norm_name == 'squats': norm_name = 'squat'
        if norm_name == 'pushups': norm_name = 'pushup'
        if norm_name == 'lunges': norm_name = 'lunge'
        
        # Capitalize for display
        display_name = norm_name.capitalize()
        
        if display_name not in pb_dict or w.reps > pb_dict[display_name]['reps']:
            pb_dict[display_name] = {
                "exercise": display_name,
                "reps": w.reps,
                "date": w.created_at.strftime("%Y-%m-%d")
            }
    
    personal_bests = sorted(list(pb_dict.values()), key=lambda x: x['reps'], reverse=True)

    return {
        "totalWorkouts": stats_row.total_workouts or 0,
        "totalMinutes": int((stats_row.total_minutes or 0) / 60), # Convert seconds to minutes
        "avgScore": int(stats_row.avg_score or 0),
        "caloriesBurned": int(stats_row.calories_burned or 0),
        "fatigueData": fatigue_data,
        "recoveryRate": recovery_rate,
        "jointStress": stress_value,
        "jointStressLevel": stress_level,
        "weeklyWorkouts": weekly_workouts,
        "personalBests": personal_bests
    }
