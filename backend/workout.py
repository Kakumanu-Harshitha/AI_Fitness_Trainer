from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from .models import WorkoutLog, User
from .schemas import WorkoutCreate, WorkoutResponse
from .dependencies import get_db
from .auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/workouts", tags=["Workouts"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(401, "User not found")
        return user

    except JWTError:
        raise HTTPException(401, "Invalid token")


@router.post("/save", response_model=WorkoutResponse)
def save_workout(
    data: WorkoutCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    calories = (data.reps + data.duration) * 0.3
    posture_score = 70.0

    workout = WorkoutLog(
        user_id=user.id,
        exercise=data.exercise,
        reps=data.reps,
        duration=data.duration,
        calories=calories,
        posture_score=posture_score
    )

    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.get("/my", response_model=list[WorkoutResponse])
def my_workouts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return (
        db.query(WorkoutLog)
        .filter(WorkoutLog.user_id == user.id)
        .order_by(WorkoutLog.created_at.desc())
        .all()
    )
