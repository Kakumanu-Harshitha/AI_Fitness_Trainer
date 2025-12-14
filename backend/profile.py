from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .models import User
from .schemas import UserResponse, ProfileUpdate
from .dependencies import get_db
from .workout import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=UserResponse)
def get_profile(user: User = Depends(get_current_user)):
    return user


@router.post("", response_model=UserResponse)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if data.age is not None:
        user.age = data.age
    if data.height_cm is not None:
        user.height_cm = data.height_cm
    if data.weight_kg is not None:
        user.weight_kg = data.weight_kg

    db.commit()
    db.refresh(user)
    return user
