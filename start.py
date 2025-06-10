#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    print("🚀 Task Manager Starting...")
    print(f"📡 Port: {port}")
    print(f"🔑 SECRET_KEY: {'✅ Set' if os.environ.get('SECRET_KEY') else '❌ Not set'}")
    print(f"🗄️  DATABASE_URL: {'✅ Set' if os.environ.get('DATABASE_URL') else '❌ Not set'}")
    
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        raise 