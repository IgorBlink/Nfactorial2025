from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# Engine will be created lazily
engine = None
async_session_maker = None

def get_engine():
    global engine, async_session_maker
    if engine is None:
        from .config import settings
        print("🔗 Creating SQLite database engine...")
        engine = create_async_engine(
            settings.database_url, 
            echo=True,
            connect_args={"check_same_thread": False}  # SQLite specific
        )
        async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    return engine

class Base(DeclarativeBase):
    pass

# Dependency to get database session
async def get_db():
    get_engine()  # Ensure engine is created
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


