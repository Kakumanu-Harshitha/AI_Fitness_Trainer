from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models import WorkoutPlan
from ...schemas.schemas import WorkoutPlanCreate

class PlanRepository:
    async def create_plan(self, db: AsyncSession, plan: WorkoutPlanCreate, user_id: int):
        db_plan = WorkoutPlan(
            user_id=user_id,
            day_of_week=plan.day_of_week,
            exercise=plan.exercise,
            target_reps=plan.target_reps,
            target_sets=plan.target_sets
        )
        db.add(db_plan)
        await db.commit()
        await db.refresh(db_plan)
        return db_plan

    async def get_plans_by_user(self, db: AsyncSession, user_id: int):
        result = await db.execute(
            select(WorkoutPlan).filter(WorkoutPlan.user_id == user_id)
        )
        return result.scalars().all()

    async def delete_plan(self, db: AsyncSession, plan_id: int, user_id: int):
        result = await db.execute(
            select(WorkoutPlan).filter(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user_id)
        )
        db_plan = result.scalars().first()
        if db_plan:
            await db.delete(db_plan)
            await db.commit()
            return True
        return False
