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
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Cache settings
    cache_ttl: int = 300  # 5 minutes
    
    @property
    def database_url(self) -> str:
        # Production: use DATABASE_URL if provided
        if self.database_url_override:
            # Railway/Render provide postgres:// but we need postgresql://
            url = self.database_url_override
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            # Add asyncpg driver if not present
            if "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        
        # Development: SQLite or local PostgreSQL
        if self.use_sqlite:
            return "sqlite+aiosqlite:///./test.db"
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
