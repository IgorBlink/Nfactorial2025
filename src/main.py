from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import engine
from .models import Base
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
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
    yield


app = FastAPI(
    title="Task Manager API",
    description="A simple task management API with JWT authentication",
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
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "database": settings.database_url}


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
