from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Dict, Any

from ..dependencies import get_db, get_current_user
from ...db.models import User, WorkoutLog, WaterLog
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

    # 4. Joint Stress & Recovery (Refined calculations)
    # Windowed load (last 48h)
    last_48h = now - timedelta(hours=48)
    load_query = select(
        func.coalesce(func.sum(WorkoutLog.duration), 0).label("sum_duration_sec"),
        func.coalesce(func.max(WorkoutLog.created_at), None).label("last_time")
    ).where(
        and_(
            WorkoutLog.user_id == current_user.id,
            WorkoutLog.created_at >= last_48h
        )
    )
    load_res = await db.execute(load_query)
    load_row = load_res.one()
    total_minutes_48h = int((load_row.sum_duration_sec or 0) / 60)
    last_workout_time = load_row.last_time
    hours_since_last = 48.0
    if last_workout_time:
        hours_since_last = max(0.0, (now - last_workout_time).total_seconds() / 3600.0)

    # Water intake today and goal
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    water_query = select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(
        and_(
            WaterLog.user_id == current_user.id,
            WaterLog.created_at >= today_start
        )
    )
    water_res = await db.execute(water_query)
    water_today_ml = int(water_res.scalar() or 0)
    water_goal_ml = getattr(current_user, "daily_water_goal", None) or 2500
    hydration_ratio = min(1.0, water_today_ml / water_goal_ml) if water_goal_ml > 0 else 0.0

    # Acute load today (workouts count)
    recent_workouts_count = await db.execute(
        select(func.count(WorkoutLog.id)).where(
            and_(
                WorkoutLog.user_id == current_user.id,
                WorkoutLog.created_at >= now - timedelta(days=1)
            )
        )
    )
    workouts_today = int(recent_workouts_count.scalar() or 0)

    # Joint Stress: blend form deficit, volume, and acute load
    form_deficit = 100 - int(stats_row.avg_score or 85)
    volume_penalty = min(30.0, (total_minutes_48h / 180.0) * 30.0)
    acute_load = min(20.0, workouts_today * 10.0)
    stress_value = max(0, min(100, int(0.6 * form_deficit + 0.3 * volume_penalty + 0.1 * acute_load)))
    stress_level = "Low"
    if stress_value > 60:
        stress_level = "High"
    elif stress_value > 30:
        stress_level = "Moderate"

    # Recovery Rate: rest time base adjusted by form, load, and hydration
    recovery_base = min(100.0, (hours_since_last / 24.0) * 100.0)
    form_factor = max(0.6, min(1.1, (stats_row.avg_score or 80) / 100.0))
    fatigue_penalty = min(60.0, (total_minutes_48h / 180.0) * 60.0)
    hydration_bonus = hydration_ratio * 10.0
    recovery_rate = int(max(10.0, min(100.0, recovery_base * form_factor - fatigue_penalty + hydration_bonus)))

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
