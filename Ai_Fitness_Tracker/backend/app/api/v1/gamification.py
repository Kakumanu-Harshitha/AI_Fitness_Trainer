from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from datetime import datetime, timedelta
from ...db.models import User, WorkoutLog, Badge, UserBadge
from ...schemas.schemas import WorkoutCreate

def calculate_points(workout_data: WorkoutCreate, posture_score: float) -> int:
    """
    Calculate points based on workout performance.
    Formula: (Reps * 10) + (Duration_Seconds * 0.5) * (Avg_Posture_Score / 100)
    """
    reps_points = workout_data.reps * 10
    duration_points = workout_data.duration * 0.5
    posture_multiplier = posture_score / 100.0
    
    total_points = int(reps_points + (duration_points * posture_multiplier))
    return max(0, total_points)

async def update_user_streak(db: AsyncSession, user: User):
    """
    Update the user's daily workout streak.
    """
    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)
    
    # Get the last workout date
    result = await db.execute(
        select(WorkoutLog)
        .filter(WorkoutLog.user_id == user.id)
        .order_by(WorkoutLog.created_at.desc())
    )
    last_workout = result.scalars().first()
    
    if not last_workout:
        user.streak = 1
        return

    last_workout_date = last_workout.created_at.date()
    
    if last_workout_date == today:
        # Already worked out today, streak remains same
        return
    elif last_workout_date == yesterday:
        # Worked out yesterday, increment streak
        user.streak += 1
    else:
        # Missed a day, reset streak
        user.streak = 1
    
    # We remove the explicit commit here as this is typically called 
    # within WorkoutService which handles its own commit.
    await db.flush()

async def check_and_unlock_badges(db: AsyncSession, user: User):
    """
    Check if the user qualifies for any new badges and unlock them.
    """
    # Get all badges the user hasn't unlocked yet
    unlocked_badge_ids = [ub.badge_id for ub in user.badges]
    result = await db.execute(
        select(Badge).filter(~Badge.id.in_(unlocked_badge_ids))
    )
    available_badges = result.scalars().all()
    
    new_badges = []
    
    for badge in available_badges:
        is_unlocked = False
        
        if badge.criteria_type == "reps":
            reps_result = await db.execute(
                select(func.sum(WorkoutLog.reps))
                .filter(WorkoutLog.user_id == user.id)
            )
            total_reps = reps_result.scalar() or 0
            if total_reps >= badge.criteria_value:
                is_unlocked = True
                
        elif badge.criteria_type == "streak":
            if user.streak >= badge.criteria_value:
                is_unlocked = True
                
        elif badge.criteria_type == "posture":
            # Average posture score of last 5 workouts
            posture_result = await db.execute(
                select(WorkoutLog)
                .filter(WorkoutLog.user_id == user.id)
                .order_by(WorkoutLog.created_at.desc())
                .limit(5)
            )
            recent_workouts = posture_result.scalars().all()
            
            if len(recent_workouts) >= 5:
                avg_posture = sum(w.posture_score for w in recent_workouts) / len(recent_workouts)
                if avg_posture >= badge.criteria_value:
                    is_unlocked = True

        if is_unlocked:
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            new_badges.append(badge)
            
    if new_badges:
        # We remove the explicit commit here as this is typically called 
        # within WorkoutService which handles its own commit.
        await db.flush()
    
    return new_badges
