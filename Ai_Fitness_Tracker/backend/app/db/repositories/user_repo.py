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
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
