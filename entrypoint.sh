#!/bin/bash
set -e

# Health check responder
(
  echo "Setting up emergency health endpoint..."
  while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}" | nc -l -p 8000 -q 1 || true
  done
) &
HEALTH_PID=$!

# Database detection
echo "==== RAILWAY ENVIRONMENT DETECTION ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
    echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Environment: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
fi

echo "==== DATABASE VARIABLES ===="
env | grep -i -E 'sql|db|postgres|pg' | sort
echo "==========================="

# Improve PostgreSQL URL detection
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

# Skip migrations initially
# alembic upgrade head

# Start the web server
uvicorn app.api.main:app --host 0.0.0.0 --port 8000

# Kill healthcheck process
kill $HEALTH_PID