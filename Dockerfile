# MirrorCore Relationship Therapist System Dockerfile
# Production-ready container for the MirrorCore Relationship Therapist System

# Use Python 3.9 as the base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for frontend dependencies
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json for frontend dependencies
COPY package.json .
RUN npm install --production

# Copy application code
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p static logs data

# Run database initialization if needed
RUN if [ -f init_db.py ]; then python init_db.py; fi

# Build any frontend assets if needed
RUN if [ -d frontend ] && [ -f frontend/package.json ]; then \
    cd frontend && npm install && npm run build; \
    fi

# Expose port for the API
EXPOSE 8000

# Set up entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1
