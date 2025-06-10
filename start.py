#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    # Railway передает PORT как строку, нужно проверить
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except:
        port = 8000
    
    print(f"🚀 Starting on port: {port}")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    ) 