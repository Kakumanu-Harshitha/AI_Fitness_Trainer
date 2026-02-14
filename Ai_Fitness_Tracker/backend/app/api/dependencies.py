from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..db.database import get_async_db
from ..db.models import User
from ..core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Use the direct generator for dependency injection to ensure caching works correctly
from ..db.database import get_async_db as get_db

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as e:
        print(f"DEBUG: JWT decode failed: {str(e)}")
        raise credentials_exception
    
    print(f"DEBUG: Validated user: {username}")
    result = await db.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.badges))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        print(f"DEBUG: User not found in DB: {username}")
        raise credentials_exception
    return user
