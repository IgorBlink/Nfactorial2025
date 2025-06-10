#!/bin/bash

# Set default port if not provided and ensure it's a valid integer
if [ -z "$PORT" ] || ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    export PORT=8000
fi

echo "Starting server on port $PORT"

# Start the application using Python script for better error handling
exec python start.py 