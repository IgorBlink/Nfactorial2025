from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import engine
from .models import Base
from .redis_client import redis_client
from .tasks.api import router as tasks_router
from .auth_api import router as auth_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    try:
        logger.info(f"Creating database tables using {settings.database_url}")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
        
        # Initialize Redis connection
        logger.info(f"Initializing Redis connection: {settings.redis_url}")
        await redis_client.connect()
        logger.info("Redis connection established")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    try:
        await redis_client.disconnect()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


app = FastAPI(
    title="Task Manager API",
    description="A simple task management API with JWT authentication, Redis caching, and Celery background tasks",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    db_type = "SQLite" if settings.use_sqlite else "PostgreSQL"
    return {
        "message": f"Welcome to {settings.name}",
        "database": db_type,
        "cache": "Redis",
        "background_tasks": "Celery",
        "docs": "/docs",
        "flower": "http://localhost:5555" if settings.redis_url else None
    }


@app.get("/health")
async def health_check():
    """Enhanced health check with Redis status"""
    health_status = {
        "status": "healthy",
        "database": settings.database_url,
        "redis": settings.redis_url
    }
    
    # Check Redis connection
    try:
        await redis_client.set("health_check", "ok", ttl=10)
        redis_status = await redis_client.get("health_check")
        health_status["redis_status"] = "connected" if redis_status == "ok" else "error"
    except Exception as e:
        health_status["redis_status"] = f"error: {str(e)}"
    
    return health_status


@app.get("/cache/status")
async def cache_status():
    """Get cache statistics"""
    try:
        # This is a simplified version - Redis INFO command would be better
        await redis_client.set("cache_test", "working", ttl=60)
        test_result = await redis_client.get("cache_test")
        
        return {
            "cache_working": test_result == "working",
            "redis_url": settings.redis_url,
            "cache_ttl": settings.cache_ttl
        }
    except Exception as e:
        return {
            "cache_working": False,
            "error": str(e)
        }


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
