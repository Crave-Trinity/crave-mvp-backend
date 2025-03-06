#!/bin/bash
# entrypoint.sh
# -------------------------------
# Exit immediately if a command exits with a non-zero status.
set -e

echo "==== RAILWAY ENV DETECT ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Env: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway environment variables detected."
fi
echo "==========================="

echo "==== DB ENV VARS ===="
# Print out any environment variables related to SQL/DB to help diagnose issues.
env | grep -i -E "sql|db|postgres|pg" | sort || echo "(none found)"
echo "====================="

# Provide a default DATABASE_URL if not set (adjust if needed for your local/testing setup).
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

# Run Alembic migrations to update the database schema.
echo "Running Alembic migrations..."
alembic upgrade head

# (Optional) Sleep a few seconds if you need to wait for dependent services.
echo "Sleeping 5 seconds to allow server startup..."
sleep 5

# Start the FastAPI app with Uvicorn.
# Binds to 0.0.0.0 so that external services (like Railway) can reach it.
# Uses the $PORT environment variable (Railway sets this) or defaults to 8000 locally.
echo "Starting FastAPI with Uvicorn..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"