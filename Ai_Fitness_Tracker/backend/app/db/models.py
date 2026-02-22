from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    points = Column(Integer, default=0)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak = Column(Integer, default=0)
    bio = Column(String, nullable=True)
    profile_image = Column(String, nullable=True, default=None)

    age = Column(Integer, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Lifestyle & Goals
    body_type = Column(String, nullable=True) # Ectomorph, Mesomorph, Endomorph
    diet_goal = Column(String, nullable=True) # Lose Weight, Build Muscle, Maintain
    activity_level = Column(String, nullable=True) # Sedentary, Light, Moderate, Active, Very Active
    daily_sleep_goal = Column(Float, default=8.0)
    daily_water_goal = Column(Integer, default=2000)
    
    # Extended Assessment
    injuries = Column(String, nullable=True) # Comma-separated list or JSON string
    dietary_preferences = Column(String, nullable=True) # Vegan, Keto, Paleo, etc.

    # TOTP / MFA
    totp_secret = Column(String, nullable=True)
    is_totp_enabled = Column(Integer, default=0) # Using Integer as Boolean (0=False, 1=True) for SQLite compatibility if needed, or just Boolean

    created_at = Column(DateTime, default=datetime.utcnow)

    workouts = relationship("WorkoutLog", back_populates="user", cascade="all, delete")
    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete")
    routines = relationship("Routine", back_populates="user", cascade="all, delete")
    sent_friend_requests = relationship("Friendship", foreign_keys="Friendship.sender_id", back_populates="sender", cascade="all, delete")
    received_friend_requests = relationship("Friendship", foreign_keys="Friendship.receiver_id", back_populates="receiver", cascade="all, delete")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete")
    activities = relationship("FriendActivity", back_populates="user", cascade="all, delete")
    water_logs = relationship("WaterLog", back_populates="user", cascade="all, delete")

class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    icon = Column(String, nullable=False)  # Lucide icon name or image path
    criteria_type = Column(String, nullable=False)  # reps, streak, posture, etc.
    criteria_value = Column(Integer, nullable=False)

    users = relationship("UserBadge", back_populates="badge")

class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"))
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge", back_populates="users")

class Routine(Base):
    __tablename__ = "routines"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    complexity = Column(String, default="BALANCED") # LITE, BALANCED, HEAVY
    vision_complexity = Column(String, default="NORMAL") # BASIC, NORMAL, ADVANCED
    type = Column(String, default="fitness") # fitness, mindfulness
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="routines")
    steps = relationship("RoutineStep", back_populates="routine", cascade="all, delete")

class RoutineStep(Base):
    __tablename__ = "routine_steps"

    id = Column(Integer, primary_key=True, index=True)
    routine_id = Column(Integer, ForeignKey("routines.id", ondelete="CASCADE"))
    exercise_name = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    timing_type = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    order_index = Column(Integer, nullable=True)
    exercise_id = Column(String, nullable=True)
    reps = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    order = Column(Integer, nullable=True)
    vision_complexity = Column(String, default="NORMAL") # BASIC, NORMAL, ADVANCED

    routine = relationship("Routine", back_populates="steps")

class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_friend_requests")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_friend_requests")


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    day_of_week = Column(String, nullable=False)
    exercise = Column(String, nullable=False)
    target_reps = Column(Integer, default=10)
    target_sets = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")


class WorkoutLog(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    name = Column(String, nullable=False)
    exercise = Column(String, nullable=False)
    reps = Column(Integer)
    duration = Column(Integer)
    calories = Column(Float)
    posture_score = Column(Float)
    replay_data = Column(String, nullable=True) # JSON string of timestamped performance

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="workouts")

class FriendActivity(Base):
    __tablename__ = "friend_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    activity_type = Column(String, nullable=False)  # workout_completed, badge_unlocked, streak_milestone
    details = Column(String, nullable=True) # JSON string or simple text
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(String, nullable=False)
    is_read = Column(Integer, default=0) # 0 for false, 1 for true
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount_ml = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="water_logs")
