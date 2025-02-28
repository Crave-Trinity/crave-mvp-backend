#!/bin/bash
set -e

# ------------------------------------------------------------------------------
# Start a minimal health check responder on port 8081.
# We use 8081 to avoid conflicting with uvicorn's binding on $PORT (which may be 8080 on Railway).
# This background process ensures the container responds to basic health requests.
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
# Construct DATABASE_URL from PG* variables if available.
# ------------------------------------------------------------------------------
if [ -n "$PGHOST" ] && [ -n "$PGPASSWORD" ]; then
  export PGUSER=${PGUSER:-postgres}
  export PGDATABASE=${PGDATABASE:-railway}
  export PGPORT=${PGPORT:-5432}
  export DATABASE_URL="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE"
  echo "Constructed DATABASE_URL from PG* variables."
fi

# ------------------------------------------------------------------------------
# Set SQLALCHEMY_DATABASE_URI to DATABASE_URL if defined.
# ------------------------------------------------------------------------------
export SQLALCHEMY_DATABASE_URI=${DATABASE_URL:-$SQLALCHEMY_DATABASE_URI}
echo "Using SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI:0:25}..."

# ------------------------------------------------------------------------------
# Launch the main application using uvicorn.
# Railway provides $PORT; if not set, default to 8000.
# ------------------------------------------------------------------------------
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"

# Once uvicorn exits, clean up the health-check process.
kill $HEALTH_PID
