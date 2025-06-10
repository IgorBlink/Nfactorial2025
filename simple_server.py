#!/usr/bin/env python3

import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    print("Starting simple server...")
    uvicorn.run(app, host="127.0.0.1", port=8003) 