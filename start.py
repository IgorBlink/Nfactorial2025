#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable with validation
    port_env = os.environ.get("PORT", "8000")
    try:
        port = int(port_env)
    except (ValueError, TypeError):
        print(f"Warning: Invalid PORT value '{port_env}', using default 8000")
        port = 8000
    
    print(f"🚀 Starting server on port {port}")
    print(f"📊 Environment variables:")
    print(f"   PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"   DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
    print(f"   RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"   SECRET_KEY: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 