#!/usr/bin/env python3
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine

# Railway PostgreSQL connection details
RAILWAY_DB_PASSWORD = "cgODlKOGzVVipVdWghcLgbzvrLMTHmSN"

# Возможные URL для Railway PostgreSQL
possible_urls = [
    f"postgresql+asyncpg://postgres:{RAILWAY_DB_PASSWORD}@roundhouse.proxy.rlwy.net:48292/railway",
    f"postgresql+asyncpg://postgres:{RAILWAY_DB_PASSWORD}@autorack.proxy.rlwy.net:25060/railway", 
    f"postgresql+asyncpg://postgres:{RAILWAY_DB_PASSWORD}@containers-us-west-1.railway.app:5432/railway",
    f"postgresql+asyncpg://postgres:{RAILWAY_DB_PASSWORD}@junction.proxy.rlwy.net:17144/railway",
]

async def test_connection(database_url):
    print(f"🔗 Testing: {database_url[:50]}...")
    try:
        engine = create_async_engine(database_url)
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            print(f"✅ SUCCESS! Connected to Railway PostgreSQL")
            print(f"📊 Test query result: {row}")
            return database_url
    except Exception as e:
        print(f"❌ Failed: {str(e)[:100]}")
        return None
    finally:
        if 'engine' in locals():
            await engine.dispose()

async def main():
    print("🚀 Testing Railway PostgreSQL connections...")
    
    for url in possible_urls:
        result = await test_connection(url)
        if result:
            print(f"\n🎯 WORKING DATABASE_URL:")
            print(f"{result}")
            break
        print()
    else:
        print("❌ None of the URLs worked. Check Railway dashboard for correct host/port.")

if __name__ == "__main__":
    asyncio.run(main()) 