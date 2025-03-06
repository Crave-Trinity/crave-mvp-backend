#!/bin/bash
# entrypoint.sh
# -------------------------------
# Exit immediately if any command exits with a non-zero status.
set -e

echo "==== RAILWAY ENV DETECT ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Env: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway environment variables detected."
fi
echo "==========================="

echo "==== DB ENV VARS ===="
# Print environment variables related to SQL/DB for debugging.
env | grep -i -E "sql|db|postgres|pg" | sort || echo "(none found)"
echo "====================="

# Provide a default DATABASE_URL if not set.
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

# Run Alembic migrations.
echo "Running Alembic migrations..."
alembic upgrade head

# Sleep a few seconds to let services (e.g. the database) settle.
echo "Sleeping 5 seconds to allow server startup..."
sleep 5

# Start the FastAPI app using Uvicorn.
# Uses $PORT from Railway (or defaults to 8000 locally) and binds to 0.0.0.0.
echo "Starting FastAPI with Uvicorn..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"