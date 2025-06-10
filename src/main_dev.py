import os
os.environ["USE_SQLITE"] = "true"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine
from .models import Base
from .tasks.api import router as tasks_router
from .auth_api import router as auth_router

# Override settings for development
settings.use_sqlite = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Task Manager API (Development)",
    description="A simple task management API with JWT authentication - SQLite Version",
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
    return {"message": f"Welcome to {settings.name} (Development Mode with SQLite)"}


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router) 