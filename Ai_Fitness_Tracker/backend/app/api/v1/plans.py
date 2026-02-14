from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..dependencies import get_db, get_current_user
from ...schemas.schemas import WorkoutPlanCreate, WorkoutPlanResponse
from ...services.plan_service import PlanService
from ...db.models import User

router = APIRouter(prefix="/plans", tags=["plans"])
plan_service = PlanService()

@router.post("/", response_model=WorkoutPlanResponse)
async def create_plan(
    plan: WorkoutPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await plan_service.create_user_plan(db, plan, current_user.id)

@router.get("/", response_model=List[WorkoutPlanResponse])
async def get_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await plan_service.get_user_plans(db, current_user.id)

@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = await plan_service.delete_user_plan(db, plan_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"status": "success"}
