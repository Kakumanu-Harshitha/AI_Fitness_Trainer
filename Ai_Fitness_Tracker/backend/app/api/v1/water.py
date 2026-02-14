from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime
from typing import List

from ..dependencies import get_db, get_current_user
from ...db.models import User, WaterLog
from ...schemas.schemas import WaterLogCreate, WaterLogResponse, DailyWaterResponse

router = APIRouter(prefix="/water", tags=["Water Tracking"])

@router.post("/log", response_model=WaterLogResponse)
async def log_water(
    water_in: WaterLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log water intake in ml.
    """
    new_log = WaterLog(
        user_id=current_user.id,
        amount_ml=water_in.amount_ml
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)
    return new_log

@router.get("/today", response_model=DailyWaterResponse)
async def get_today_water(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's total water intake.
    """
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    query = select(func.sum(WaterLog.amount_ml)).where(
        and_(
            WaterLog.user_id == current_user.id,
            WaterLog.created_at >= today_start
        )
    )
    result = await db.execute(query)
    total = result.scalar() or 0
    total = max(0, total)
    
    # Default goal is 2500ml, could be user-specific in the future
    return DailyWaterResponse(current=total, goal=2500)

@router.get("/history", response_model=List[WaterLogResponse])
async def get_water_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent water logs.
    """
    query = select(WaterLog).where(
        WaterLog.user_id == current_user.id
    ).order_by(WaterLog.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()
