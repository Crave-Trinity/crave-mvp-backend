#!/bin/bash
# entrypoint.sh - Entry script for Docker container startup.
# This script detects Railway environment variables,
# runs database migrations, and finally starts the uvicorn server.

set -e  # Exit immediately if a command exits with a non-zero status

echo "==== RAILWAY ENV DETECT ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Env: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway env variables detected."
fi
echo "==========================="

echo "==== DB ENV VARS ===="
env | grep -i -E "sql|db|postgres|pg" | sort || echo "(none found)"
echo "====================="

# Set DATABASE_URL if not already set
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

echo "Running Alembic migrations..."
alembic upgrade head

# Optional: Pause briefly to ensure the server is ready before Railway healthchecks start.
echo "Sleeping 5 seconds to allow server startup..."
sleep 5

# Launch uvicorn with host and port provided by Railway (or default 8000)
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"