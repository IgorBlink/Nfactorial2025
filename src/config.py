import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    name: str = "Task Manager"
    secret_key: str = os.getenv("SECRET_KEY", "local-dev-secret-key-123456789")
    algorithm: str = "HS256" 
    access_token_expire_minutes: int = 30
    
    @property
    def database_url(self) -> str:
        # Use SQLite database
        # In production (Railway), use /tmp directory which is writable
        # Locally, store in current directory
        default_db = "sqlite+aiosqlite:///./tasks.db"
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
            # Railway deployment detected - use /tmp for writable storage
            default_db = "sqlite+aiosqlite:////tmp/tasks.db"
            
        database_url = os.getenv("DATABASE_URL", default_db)
        return database_url


settings = Settings()
