# ------------------------------------------------------------------------------
# entrypoint.sh (Baby Mode)
# Paste this in your project at /app/entrypoint.sh
# Make sure it has LF line endings (dos2unix).
# ------------------------------------------------------------------------------
#!/bin/bash
set -e

(
  echo "Starting minimal health check responder on port 8081..."
  while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}" \
      | nc -l -p 8081 -q 1 || true
  done
) &
HEALTH_PID=$!

echo "==== RAILWAY ENV DETECT ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Env: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway env variables detected."
fi
echo "==========================="

echo "==== DB ENV VARS ===="
env | grep -i -E 'sql|db|postgres|pg' | sort || echo "(none found)"
echo "====================="

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

echo "Running Alembic migrations..."
alembic upgrade head

exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
kill $HEALTH_PID