from pathlib import Path
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')
    name: str = "Task Manager"
    
    # Database - Support both local and production
    postgres_user: str = os.getenv("POSTGRES_USER", "igormartynyuk")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_db: str = os.getenv("POSTGRES_DB", "postgres")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    # Production database URL (Railway/Render style)
    database_url_override: str = os.getenv("DATABASE_URL", "")
    
    # For development - use PostgreSQL by default as required
    use_sqlite: bool = os.getenv("USE_SQLITE", "false").lower() == "true"
    
    # Detect Railway environment
    railway_environment: bool = os.getenv("RAILWAY_ENVIRONMENT") is not None or os.getenv("PORT") is not None
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @property
    def database_url(self) -> str:
        # Debug information
        print(f"DEBUG: DATABASE_URL env var: {self.database_url_override[:50] if self.database_url_override else 'Not set'}")
        print(f"DEBUG: Railway environment detected: {self.railway_environment}")
        print(f"DEBUG: USE_SQLITE: {self.use_sqlite}")
        
        # Production: use DATABASE_URL if provided (Railway/Render style)
        if self.database_url_override:
            # Railway/Render provide postgres:// but we need postgresql://
            url = self.database_url_override
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            # Add asyncpg driver if not present
            if "+asyncpg" not in url and "postgresql://" in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            print(f"✅ Using production database URL: {url[:50]}...")
            return url
        
        # If we're in Railway but no DATABASE_URL, that's an error
        if self.railway_environment and not self.database_url_override:
            print("❌ WARNING: Running in Railway but DATABASE_URL not found!")
            print("❌ Please add PostgreSQL service in Railway Dashboard")
            # In Railway without DATABASE_URL, we can't connect to localhost
            # This will cause connection error, but it's better than wrong config
        
        # Development: SQLite or local PostgreSQL
        if self.use_sqlite:
            print("🔧 Using SQLite database for development")
            return "sqlite+aiosqlite:///./test.db"
        
        db_url = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        print(f"🔧 Using local PostgreSQL: {self.postgres_host}:{self.postgres_port}")
        return db_url


settings = Settings()
