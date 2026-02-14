from sqlalchemy.ext.asyncio import AsyncSession
from ..db.repositories.plan_repo import PlanRepository
from ..schemas.schemas import WorkoutPlanCreate

class PlanService:
    def __init__(self):
        self.plan_repo = PlanRepository()

    async def create_user_plan(self, db: AsyncSession, plan: WorkoutPlanCreate, user_id: int):
        return await self.plan_repo.create_plan(db, plan, user_id)

    async def get_user_plans(self, db: AsyncSession, user_id: int):
        return await self.plan_repo.get_plans_by_user(db, user_id)
        
    async def delete_user_plan(self, db: AsyncSession, plan_id: int, user_id: int):
        return await self.plan_repo.delete_plan(db, plan_id, user_id)
