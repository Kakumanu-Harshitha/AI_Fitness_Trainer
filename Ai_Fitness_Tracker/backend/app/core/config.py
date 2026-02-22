from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Fitness Tracker"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for easier development
    DATABASE_URL: Optional[str] = None
    USE_POSTGRES: bool = False
    DATABASE_HOSTNAME: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_PASSWORD: str = "password"
    DATABASE_NAME: str = "fitness_tracker"
    DATABASE_USERNAME: str = "postgres"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    GROQ_API_KEY: Optional[str] = None
    WEB_BASE_URL: str = "http://localhost:3000"
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None
    APPLE_CLIENT_ID: Optional[str] = None
    APPLE_TEAM_ID: Optional[str] = None
    APPLE_KEY_ID: Optional[str] = None
    APPLE_PRIVATE_KEY: Optional[str] = None
    APPLE_REDIRECT_URI: Optional[str] = None

    # Email Settings
    GMAIL_SENDER_EMAIL: Optional[str] = "honey2006597@gmail.com"
    GMAIL_APP_PASSWORD: Optional[str] = "jdnsrqietzdmthiu"
    RESET_PASSWORD_TOKEN_EXPIRE_HOURS: int = 1

    def get_database_url(self, is_async: bool = False) -> str:
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if is_async:
                if url.startswith("postgresql://"):
                    return url.replace("postgresql://", "postgresql+asyncpg://")
                if url.startswith("sqlite:///"):
                    return url.replace("sqlite:///", "sqlite+aiosqlite:///")
            return url
        
        if self.USE_POSTGRES and self.DATABASE_NAME and self.DATABASE_USERNAME and self.DATABASE_PASSWORD and self.DATABASE_HOSTNAME:
            driver = "postgresql+asyncpg" if is_async else "postgresql"
            return (
                f"{driver}://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOSTNAME}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )
        
        driver = "sqlite+aiosqlite" if is_async else "sqlite"
        return f"{driver}:///./fitness_v3.db"

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env")
        extra = "ignore"

settings = Settings()
