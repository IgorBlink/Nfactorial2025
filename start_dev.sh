#!/bin/bash

echo "🚀 Starting Task Manager with Redis & Celery..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start services with Docker Compose
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."

# Check main app
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Main app is running: http://localhost:8000"
else
    echo "❌ Main app is not responding"
fi

# Check Flower
if curl -f http://localhost:5555 > /dev/null 2>&1; then
    echo "✅ Flower is running: http://localhost:5555"
else
    echo "❌ Flower is not responding"
fi

# Check Redis
if redis-cli -h localhost -p 6379 ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not responding"
fi

echo ""
echo "🎉 Services started successfully!"
echo ""
echo "📝 Available URLs:"
echo "   - API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Frontend: ./frontend/index.html"
echo "   - Flower (Celery): http://localhost:5555"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Cache Status: http://localhost:8000/cache/status"
echo ""
echo "📊 New API endpoints:"
echo "   - GET /tasks/statistics - Task statistics"
echo "   - POST /tasks/export - Export tasks"
echo "   - POST /tasks/bulk-update - Bulk update tasks"
echo ""
echo "To stop all services: docker-compose down"
echo "To view logs: docker-compose logs -f" 