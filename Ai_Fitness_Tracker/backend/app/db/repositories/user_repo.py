from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4
from ..models import User
from ...schemas.schemas import UserRegister, ProfileUpdate
from ...core.security import hash_password

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create(self, user_data: UserRegister) -> User:
        hashed_pw = hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password=hashed_pw
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_or_create_oauth_user(self, username: str, email: str = None) -> User:
        user = await self.get_by_username(username)
        if user:
            return user
        temp_password = f"{uuid4().hex}{uuid4().hex}"
        hashed_pw = hash_password(temp_password)
        db_user = User(
            username=username,
            email=email,
            password=hashed_pw
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def update(self, user: User, data: ProfileUpdate) -> User:
        if data.username is not None and data.username != user.username:
            # Check for existing username
            existing = await self.get_by_username(data.username)
            if existing:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = data.username
        if data.age is not None:
            user.age = data.age
        if data.height_cm is not None:
            user.height_cm = data.height_cm
        if data.weight_kg is not None:
            user.weight_kg = data.weight_kg
        if data.body_type is not None:
            user.body_type = data.body_type
        if data.diet_goal is not None:
            user.diet_goal = data.diet_goal
        if data.activity_level is not None:
            user.activity_level = data.activity_level
        if data.daily_sleep_goal is not None:
            user.daily_sleep_goal = data.daily_sleep_goal
        if data.daily_water_goal is not None:
            user.daily_water_goal = data.daily_water_goal
        if data.injuries is not None:
            user.injuries = data.injuries
        if data.dietary_preferences is not None:
            user.dietary_preferences = data.dietary_preferences
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_password(self, user: User, hashed_password: str) -> User:
        user.password = hashed_password
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_totp_secret(self, user: User, secret: str) -> User:
        user.totp_secret = secret
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def enable_totp(self, user: User, enabled: bool = True) -> User:
        user.is_totp_enabled = 1 if enabled else 0
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
