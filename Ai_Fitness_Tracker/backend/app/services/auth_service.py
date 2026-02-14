from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from ..db.repositories.user_repo import UserRepository
from ..core.security import verify_password, create_access_token
from ..schemas.schemas import UserRegister, TokenResponse

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register_user(self, user_data: UserRegister) -> TokenResponse:
        if await self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        if user_data.email and await self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user = await self.user_repo.create(user_data)
        access_token = create_access_token(data={"sub": user.username})
        response = {"access_token": access_token, "token_type": "bearer", "user": user}
        print(f"DEBUG: register_user returning: {response.keys()}")
        return response

    async def authenticate_user(self, username: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_username(username)
        if not user:
            # Try to find by email if username lookup failed
            user = await self.user_repo.get_by_email(username)

        if not user:
            print(f"Auth failed: User '{username}' not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not verify_password(password, user.password):
            print(f"Auth failed: Password mismatch for user '{username}'. Provided len: {len(password)}, Hash len: {len(user.password)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer", "user": user}
