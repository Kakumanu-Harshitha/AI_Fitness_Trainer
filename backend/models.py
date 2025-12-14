from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    workouts = relationship("WorkoutLog", back_populates="user", cascade="all, delete")


class WorkoutLog(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    exercise = Column(String, nullable=False)
    reps = Column(Integer)
    duration = Column(Integer)
    calories = Column(Float)
    posture_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workouts")
