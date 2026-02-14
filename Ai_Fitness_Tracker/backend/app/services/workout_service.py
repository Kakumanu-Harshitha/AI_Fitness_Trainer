from sqlalchemy.ext.asyncio import AsyncSession
from ..db.repositories.workout_repo import WorkoutRepository
from ..db.models import User
from ..schemas.schemas import WorkoutCreate
from ..api.v1.gamification import calculate_points, update_user_streak, check_and_unlock_badges
from .activity_service import ActivityService

class WorkoutService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workout_repo = WorkoutRepository(db)
        self.activity_service = ActivityService(db)

    async def process_workout(self, user: User, data: WorkoutCreate):
        # Business Logic: Calculate calories if not provided
        if data.calories is None:
            data.calories = (data.reps + data.duration) * 0.3
        
        # Determine posture score
        if data.posture_score is None:
            data.posture_score = 85.0
        
        # Calculate points
        points_earned = calculate_points(data, data.posture_score)
        user.points += points_earned
        
        # Save workout log
        workout = await self.workout_repo.create(user, data)
        
        # Update streak
        await update_user_streak(self.db, user)
        
        # Check for badges
        new_badges = await check_and_unlock_badges(self.db, user)

        # Log Activity
        await self.activity_service.log_activity(
            user.id, 
            "workout_completed", 
            f"Completed {data.exercise} ({int(data.calories)} kcal)"
        )
        
        for badge in new_badges:
             await self.activity_service.log_activity(
                user.id,
                "badge_unlocked",
                f"Unlocked badge: {badge.name}"
            )
        
        await self.db.commit()
        
        return workout

    async def get_user_workouts(self, user_id: int):
        return await self.workout_repo.get_by_user(user_id)

    async def get_best_workout(self, user_id: int, exercise: str):
        # Find the workout with the highest score (points or posture * reps)
        # For simplicity, let's pick the one with max reps * posture_score
        # But we need to use repository for this.
        return await self.workout_repo.get_best_by_exercise(user_id, exercise)
