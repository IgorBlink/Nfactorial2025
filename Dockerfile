FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy and make entrypoint executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app && chown appuser /entrypoint.sh
USER appuser

# Set environment variable with default
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check  
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Use Python start script as default, can be overridden by Railway
CMD ["python", "start.py"]
