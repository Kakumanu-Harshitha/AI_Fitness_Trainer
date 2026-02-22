from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..dependencies import get_db, get_current_user
from ...db.models import User, Routine, RoutineStep
from ...schemas.schemas import RoutineCreate, RoutineResponse

router = APIRouter(prefix="/routines", tags=["Routines"])

@router.post("/", response_model=RoutineResponse)
async def create_routine(
    routine_data: RoutineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new workout routine with steps"""
    new_routine = Routine(
        user_id=current_user.id,
        name=routine_data.name,
        description=routine_data.description,
        complexity=routine_data.complexity,
        vision_complexity=routine_data.vision_complexity,
        type=routine_data.type
    )
    db.add(new_routine)
    await db.flush()  # Get routine ID

    for idx, step_data in enumerate(routine_data.steps):
        step = RoutineStep(
            routine_id=new_routine.id,
            exercise_name=step_data.exercise_name or step_data.exercise_id, 
            exercise_id=step_data.exercise_id,
            reps=step_data.reps,
            sets=step_data.sets,
            duration_seconds=step_data.duration_seconds,
            order=idx,
            order_index=step_data.order_index if step_data.order_index is not None else idx,
            icon=step_data.icon,
            timing_type=step_data.timing_type,
            quantity=step_data.quantity,
            vision_complexity=step_data.vision_complexity
        )
        db.add(step)
    
    await db.commit()
    
    # Fetch with steps eager loaded to avoid lazy loading issues
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Routine)
        .options(selectinload(Routine.steps))
        .filter(Routine.id == new_routine.id)
    )
    return result.scalars().first()

@router.get("/", response_model=List[RoutineResponse])
async def get_routines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all routines for current user"""
    # Eager load steps to avoid N+1 and validation errors
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Routine)
        .options(selectinload(Routine.steps))
        .filter(Routine.user_id == current_user.id)
        .order_by(Routine.created_at.desc())
    )
    return result.scalars().all()

@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(
    routine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific routine with its steps"""
    result = await db.execute(
        select(Routine).filter(
            Routine.id == routine_id, 
            Routine.user_id == current_user.id
        )
    )
    routine = result.scalars().first()
    
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    return routine

@router.delete("/{routine_id}")
async def delete_routine(
    routine_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a routine"""
    result = await db.execute(
        select(Routine).filter(
            Routine.id == routine_id, 
            Routine.user_id == current_user.id
        )
    )
    routine = result.scalars().first()
    
    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")
    
    await db.delete(routine)
    await db.commit()
    return {"status": "success"}
