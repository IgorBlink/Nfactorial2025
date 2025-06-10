from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

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
        print("🔄 Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        print("⚠️  App will continue but database operations may fail")
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
    return {"message": f"Welcome to {settings.name}", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Serve static files and frontend
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/frontend")
    async def serve_frontend():
        """Serve the frontend HTML file"""
        frontend_path = os.path.join(static_dir, "index.html")
        return FileResponse(frontend_path)


# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)
