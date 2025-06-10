#!/usr/bin/env python3
import asyncio
from src.config import settings
from src.database import get_engine

async def test():
    print(f'🔗 Testing Railway connection...')
    print(f'Database URL: {settings.database_url[:60]}...')
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            result = await conn.execute('SELECT version();')
            version = result.fetchone()[0]
            print(f'✅ SUCCESS! PostgreSQL version: {version[:50]}...')
            
            # Test creating tables
            from src.models import Base
            await conn.run_sync(Base.metadata.create_all)
            print('✅ Tables created successfully!')
            
        await engine.dispose()
    except Exception as e:
        print(f'❌ Connection failed: {e}')

if __name__ == "__main__":
    asyncio.run(test()) 