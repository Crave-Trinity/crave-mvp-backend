#!/bin/bash
set -e

# ------------------------------------------------------------------------------
# Background "emergency" health endpoint for hosting platforms, so
# they see that "something" is alive even if the app hasn't fully started.
#
# We run netcat (nc) on a different port (8080) to avoid conflicts with Uvicorn.
# ------------------------------------------------------------------------------
(
  echo "Starting minimal health check responder on port 8080..."
  while true; do
    # We send a valid HTTP/1.1 response with "OK" status.
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}" \
      | nc -l -p 8080 -q 1 || true
  done
) &
HEALTH_PID=$!

# ------------------------------------------------------------------------------
# If we detect a Railway environment, just print that out for clarity.
# ------------------------------------------------------------------------------
echo "==== RAILWAY ENVIRONMENT DETECTION ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected!"
  echo "Service: ${RAILWAY_SERVICE_NAME:-unknown}, Environment: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
else
  echo "No Railway environment variables found."
fi
echo "========================================"

# ------------------------------------------------------------------------------
# Print out DB-related environment variables (useful for debugging).
# ------------------------------------------------------------------------------
echo "==== DATABASE VARIABLES ===="
env | grep -i -E 'sql|db|postgres|pg' | sort || echo "(none found)"
echo "==========================="

# ------------------------------------------------------------------------------
# If PGHOST/PGPASSWORD are set, construct a DATABASE_URL for convenience.
# ------------------------------------------------------------------------------
if [ -n "$PGHOST" ] && [ -n "$PGPASSWORD" ]; then
  export PGUSER=${PGUSER:-postgres}
  export PGDATABASE=${PGDATABASE:-railway}
  export PGPORT=${PGPORT:-5432}
  export DATABASE_URL="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE"
  echo "Constructed DATABASE_URL from PG* variables."
fi

# ------------------------------------------------------------------------------
# The app expects SQLALCHEMY_DATABASE_URI, so we fall back to DATABASE_URL if
# that’s defined, or use an existing SQLALCHEMY_DATABASE_URI if you have it.
# ------------------------------------------------------------------------------
export SQLALCHEMY_DATABASE_URI=${DATABASE_URL:-$SQLALCHEMY_DATABASE_URI}
echo "Using SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI:0:25}..."

# ------------------------------------------------------------------------------
# Finally, launch Uvicorn on 0.0.0.0:$PORT. Railway supplies $PORT automatically.
# If $PORT is empty (local dev?), default to 8000.
# ------------------------------------------------------------------------------
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"

# Once uvicorn stops, kill the background health check.
kill $HEALTH_PID
