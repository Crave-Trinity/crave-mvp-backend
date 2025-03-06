#!/bin/bash
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
echo "====================="

# Provide a default if DATABASE_URL isn't set
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Sleeping 5 seconds to allow server startup..."
sleep 5

# Finally, start uvicorn on $PORT or default 8000
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"