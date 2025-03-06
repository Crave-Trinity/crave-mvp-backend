#!/bin/bash
# File: entrypoint.sh
# ------------------------------------------------------------------------------
# Purpose: Run Alembic migrations and start the FastAPI application.
# ------------------------------------------------------------------------------
set -e

echo "==== RAILWAY ENV DETECT ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Env: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway environment variables detected."
fi
echo "==========================="

echo "==== DB ENV VARS ===="
env | grep -i -E "sql|db|postgres|pg" | sort || echo "(none found)"
echo "==========================="

# Provide a default DATABASE_URL if not set.
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

# Run Alembic migrations to update the database schema.
echo "Running Alembic migrations..."
alembic upgrade head

# Sleep briefly to allow services to settle.
echo "Sleeping 5 seconds to allow server startup..."
sleep 5

# Start FastAPI using Uvicorn.
echo "Starting FastAPI with Uvicorn..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"