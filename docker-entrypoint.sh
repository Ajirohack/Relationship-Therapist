#!/bin/bash
# Docker entrypoint script for Core Engine Relationship Therapist System
set -e

# Function to wait for a service to be ready
wait_for_service() {
  local host="$1"
  local port="$2"
  local service_name="$3"
  local timeout="${4:-30}"
  
  echo "Waiting for $service_name to be ready..."
  for i in $(seq 1 $timeout); do
    if nc -z "$host" "$port"; then
      echo "$service_name is ready!"
      return 0
    fi
    echo "Waiting for $service_name... $i/$timeout"
    sleep 1
  done
  echo "Timeout reached waiting for $service_name"
  return 1
}

# Wait for dependent services if they're defined
if [ -n "$DATABASE_HOST" ] && [ -n "$DATABASE_PORT" ]; then
  wait_for_service "$DATABASE_HOST" "$DATABASE_PORT" "database" 60
fi

# Set the correct server to run based on environment
if [ "$ENVIRONMENT" = "production" ]; then
  echo "Starting server in production mode..."
  SERVER_FILE="main.py"
else
  echo "Starting server in development mode..."
  SERVER_FILE="main_simple.py"
fi

# Check if the server file exists
if [ ! -f "$SERVER_FILE" ]; then
  echo "Server file $SERVER_FILE does not exist. Falling back to main_simple.py"
  SERVER_FILE="main_simple.py"
  
  # If that doesn't exist either, use any Python file with 'main' in the name
  if [ ! -f "$SERVER_FILE" ]; then
    SERVER_FILE=$(find . -maxdepth 1 -name "*main*.py" | head -n 1)
    if [ -z "$SERVER_FILE" ]; then
      echo "No server file found. Exiting."
      exit 1
    fi
    SERVER_FILE="${SERVER_FILE#./}"
    echo "Found server file: $SERVER_FILE"
  fi
fi

# Get the app variable name from the server file
APP_VARIABLE="app"
if grep -q "app = FastAPI" "$SERVER_FILE"; then
  APP_VARIABLE="app"
elif grep -q "application = FastAPI" "$SERVER_FILE"; then
  APP_VARIABLE="application"
fi

# Extract the module name without the .py extension
MODULE_NAME="${SERVER_FILE%.py}"

# Run database migrations if a migrations script exists
if [ -f "run_migrations.py" ]; then
  echo "Running database migrations..."
  python run_migrations.py
fi

# Execute the command provided to the entrypoint
echo "Executing: $@"
if [ "$1" = "uvicorn" ]; then
  shift
  exec uvicorn "$MODULE_NAME:$APP_VARIABLE" "$@"
else
  exec "$@"
fi
