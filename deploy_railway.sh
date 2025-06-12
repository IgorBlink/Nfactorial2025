#!/bin/bash

echo "🚄 Deploying Task Manager to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI is not installed. Please install it first:"
    echo "   npm install -g @railway/cli"
    echo "   Or visit: https://docs.railway.app/develop/cli"
    exit 1
fi

# Login to Railway (if not already logged in)
echo "🔐 Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "Please login to Railway:"
    railway login
fi

# Create new Railway project
echo "📦 Creating Railway project..."
railway login
read -p "Enter project name (default: task-manager): " project_name
project_name=${project_name:-task-manager}

# Initialize project
railway init $project_name

# Add PostgreSQL database
echo "🗄️ Adding PostgreSQL database..."
railway add postgresql

# Add Redis database  
echo "🔴 Adding Redis database..."
railway add redis

# Set environment variables
echo "⚙️ Setting environment variables..."

# Generate a secure secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set POSTGRES_HOST='${{Postgres.PGHOST}}'
railway variables set POSTGRES_USER='${{Postgres.PGUSER}}'
railway variables set POSTGRES_PASSWORD='${{Postgres.PGPASSWORD}}'
railway variables set POSTGRES_DB='${{Postgres.PGDATABASE}}'
railway variables set POSTGRES_PORT='${{Postgres.PGPORT}}'
railway variables set DATABASE_URL='${{Postgres.DATABASE_URL}}'
railway variables set REDIS_URL='${{Redis.REDIS_URL}}'

echo "✅ Environment variables set!"

# Deploy the application
echo "🚀 Deploying application..."
railway up

echo ""
echo "🎉 Deployment started!"
echo ""
echo "📝 Next steps:"
echo "1. Check deployment status: railway status"
echo "2. View logs: railway logs"
echo "3. Open application: railway open"
echo ""
echo "🌐 Your application will be available at:"
echo "   https://$project_name.railway.app"
echo ""
echo "📊 Services deployed:"
echo "   - Main API (FastAPI)"
echo "   - PostgreSQL Database"
echo "   - Redis Cache"
echo "   - Celery Worker"
echo "   - Celery Beat"
echo ""
echo "🔧 To update deployment:"
echo "   railway up"
echo ""
echo "📱 To add custom domain:"
echo "   railway domain" 