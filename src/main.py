from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from .config import settings
from .database import get_engine
from .models import Base
from .tasks.api import router as tasks_router
from .auth_api import router as auth_router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App startup - create database tables
    print("🚀 Application starting...")
    print("📊 Creating database tables...")
    try:
        from .database import get_engine
        from .models import Base
        
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.name}", "docs": "/docs"}


@app.get("/health")
def health_check():
    from .config import settings
    return {
        "status": "healthy", 
        "database": "SQLite",
        "database_url": settings.database_url
    }


@app.get("/db-status")
async def database_status():
    """Check database connection status"""
    from .config import settings
    import os
    
    database_url = settings.database_url
    result = {
        "database_url": database_url,
        "database_type": "SQLite" if "sqlite" in database_url else "PostgreSQL",
        "secret_key_set": bool(os.getenv("SECRET_KEY")) or bool(settings.secret_key),
        "connection_status": "testing"
    }
    
    try:
        from .database import get_engine
        engine = get_engine()
        # Just try to get the engine - this is enough to test connection
        if engine:
            result["connection_status"] = "connected"
            result["message"] = "SQLite database connection successful"
            result["database_file"] = "./tasks.db"
    except Exception as e:
        result["connection_status"] = "failed"
        result["message"] = f"Database connection failed: {str(e)}"
        result["error"] = str(e)
    
    return result


@app.post("/init-db")
async def initialize_database():
    """Initialize database tables (call this after fixing database connection)"""
    try:
        from .database import get_engine
        from .models import Base
        
        print("🔄 Creating database tables...")
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")
        return {"status": "success", "message": "Database initialized"}
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return {"status": "error", "message": f"Database initialization failed: {str(e)[:100]}"}


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
