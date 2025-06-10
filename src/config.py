import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    name: str = "Task Manager"
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "fallback-secret-key-123456789")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @property
    def database_url(self) -> str:
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            # Fallback for development/testing
            database_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"
            print(f"⚠️  WARNING: Using fallback database URL")
        
        # Railway provides postgres:// but we need postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        # Add asyncpg driver
        if "+asyncpg" not in database_url:
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        print(f"🔗 Database URL: {database_url[:50]}...")
        return database_url


settings = Settings()
