import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    name: str = "Task Manager"
    secret_key: str = os.getenv("SECRET_KEY", "fallback-secret-123")
    algorithm: str = "HS256" 
    access_token_expire_minutes: int = 30
    
    @property
    def database_url(self) -> str:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
            
        # Fix Railway postgres:// URLs
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif "postgresql://" in database_url and "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            
        return database_url


settings = Settings()
