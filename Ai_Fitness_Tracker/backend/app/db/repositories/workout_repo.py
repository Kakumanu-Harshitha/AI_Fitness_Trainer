from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import WorkoutLog, User
from ...schemas.schemas import WorkoutCreate

class WorkoutRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user: User, data: WorkoutCreate) -> WorkoutLog:
        workout = WorkoutLog(
            user_id=user.id,
            name=data.exercise,
            exercise=data.exercise,
            reps=data.reps,
            duration=data.duration,
            calories=data.calories, 
            posture_score=data.posture_score,
            replay_data=data.replay_data
        )
        self.db.add(workout)
        await self.db.flush()
        await self.db.refresh(workout)
        return workout

    async def get_by_user(self, user_id: int) -> list[WorkoutLog]:
        result = await self.db.execute(
            select(WorkoutLog)
            .filter(WorkoutLog.user_id == user_id)
            .order_by(WorkoutLog.created_at.desc())
        )
        return result.scalars().all()

    async def get_best_by_exercise(self, user_id: int, exercise: str) -> WorkoutLog | None:
        # Best defined as max reps, tie-break by posture_score
        result = await self.db.execute(
            select(WorkoutLog)
            .filter(WorkoutLog.user_id == user_id, WorkoutLog.exercise == exercise)
            .order_by(WorkoutLog.reps.desc(), WorkoutLog.posture_score.desc())
            .limit(1)
        )
        return result.scalars().first()
