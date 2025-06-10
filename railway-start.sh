#!/bin/bash

# Railway startup script
echo "Railway deployment starting..."

# Debug: Show environment variables
echo "Environment variables:"
echo "PORT: $PORT"
echo "DATABASE_URL: $DATABASE_URL"

# Validate PORT
if [ -z "$PORT" ]; then
    echo "PORT not set, using default 8000"
    export PORT=8000
elif ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Invalid PORT value: $PORT, using default 8000"
    export PORT=8000
fi

echo "Final PORT: $PORT"

# Start the application
exec python start.py 