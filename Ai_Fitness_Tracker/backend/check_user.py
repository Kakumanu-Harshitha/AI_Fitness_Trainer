
import asyncio
from app.db.database import AsyncSessionLocal
from app.db.repositories.user_repo import UserRepository
from sqlalchemy import select
from app.db.models import User
from app.core.security import verify_password, hash_password

async def check_user():
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        email = "varshini@gmail.com"
        user = await repo.get_by_email(email)
        
        if user:
            print(f"User found: {user.username}, Email: {user.email}")
            # Verify password
            is_valid = verify_password("Varshini@123", user.password)
            print(f"Password 'Varshini@123' valid: {is_valid}")
            
            # Reset password if invalid
            if not is_valid:
                print("Resetting password to 'Varshini@123'...")
                user.password = get_password_hash("Varshini@123")
                await session.commit()
                print("Password reset complete.")
        else:
            print(f"User with email {email} not found.")
            
            # Check if username exists
            result = await session.execute(select(User).filter(User.username == "Varshini"))
            user_by_name = result.scalars().first()
            if user_by_name:
                print(f"Found user by username 'Varshini': {user_by_name.email}")
                
                # Check password for username user
                is_valid = verify_password("Varshini@123", user_by_name.password)
                print(f"Password 'Varshini@123' valid for user 'Varshini': {is_valid}")
                
                if not is_valid:
                    print("Resetting password for 'Varshini' to 'Varshini@123'...")
                    user_by_name.password = get_password_hash("Varshini@123")
                    await session.commit()
                    print("Password reset complete.")

if __name__ == "__main__":
    asyncio.run(check_user())
