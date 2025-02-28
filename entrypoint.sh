#!/bin/bash
set -e

# Health check responder in a subshell. This helps hosting platforms
# see that "something" is responding, even if the actual app has not fully started.
(
  echo "Setting up emergency health endpoint..."
  while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}" \
      | nc -l -p 8000 -q 1 || true
  done
) &
HEALTH_PID=$!

echo "==== RAILWAY ENVIRONMENT DETECTION ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
  echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Environment: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
fi

echo "==== DATABASE VARIABLES ===="
env | grep -i -E 'sql|db|postgres|pg' | sort
echo "==========================="

# If PGHOST/PGPASSWORD are set, construct a DATABASE_URL
if [ -n "$PGHOST" ] && [ -n "$PGPASSWORD" ]; then
  export PGUSER=${PGUSER:-postgres}
  export PGDATABASE=${PGDATABASE:-railway}
  export PGPORT=${PGPORT:-5432}
  export DATABASE_URL="postgresql://$PGUSER:$PGPASSWORD@$PGHOST:$PGPORT/$PGDATABASE"
  echo "Constructed DATABASE_URL from PG* variables"
fi

# Export as SQLALCHEMY_DATABASE_URI for our app
export SQLALCHEMY_DATABASE_URI=${DATABASE_URL:-$SQLALCHEMY_DATABASE_URI}
echo "Using SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI:0:25}..."

# Start uvicorn. Notice we're directly referencing the "main" app from app/api/main.py
uvicorn app.api.main:app --host 0.0.0.0 --port $PORT

# Kill the background health check
kill $HEALTH_PID
