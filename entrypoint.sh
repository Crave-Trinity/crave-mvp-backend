#======================
# entrypoint.sh
#======================
#!/bin/bash
set -e

# ------------------------------------------------------------------------------
# Start a minimal health check responder on port 8081.
# ------------------------------------------------------------------------------
(
  echo "Starting minimal health check responder on port 8081..."
  while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}" \
      | nc -l -p 8081 -q 1 || true
  done
) &
HEALTH_PID=$!

# ------------------------------------------------------------------------------
# Railway Environment Detection
# ------------------------------------------------------------------------------
echo "==== RAILWAY ENVIRONMENT DETECTION ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Environment: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway environment variables detected."
fi
echo "========================================"

# ------------------------------------------------------------------------------
# Display Database Environment Variables (for debugging)
# ------------------------------------------------------------------------------
echo "==== DATABASE VARIABLES ===="
env | grep -i -E 'sql|db|postgres|pg' | sort || echo "(none found)"
echo "==========================="

# ------------------------------------------------------------------------------
# Ensure DATABASE_URL is set or default (for local dev).
# ------------------------------------------------------------------------------
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

# ------------------------------------------------------------------------------
# Run Alembic migrations to ensure the database schema is up-to-date.
# ------------------------------------------------------------------------------
echo "Running Alembic migrations..."
alembic upgrade head

# ------------------------------------------------------------------------------
# Launch the main application using uvicorn.
# Railway provides $PORT; if not set, default to 8000.
# ------------------------------------------------------------------------------
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"

# Once uvicorn exits, clean up the health-check process.
kill $HEALTH_PID