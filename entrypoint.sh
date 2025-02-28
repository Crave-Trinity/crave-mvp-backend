#!/bin/bash
# File: entrypoint.sh
# Fix: Add Railway-specific environment detection and variable dumping

set -e

# Dump ALL environment variables to see what Railway provides
echo "==== RAILWAY ENVIRONMENT DETECTION ===="
if [[ -n "$RAILWAY_SERVICE_NAME" || -n "$RAILWAY_ENVIRONMENT_NAME" ]]; then
    echo "Railway detected! Service: ${RAILWAY_SERVICE_NAME:-unknown}, Environment: ${RAILWAY_ENVIRONMENT_NAME:-unknown}"
fi

echo "==== ALL DATABASE-RELATED ENVIRONMENT VARIABLES ===="
env | grep -i -E 'sql|db|postgres|pg' | sort
echo "=================================================="

# Print important variables
echo "PGUSER: ${PGUSER:-Not set}"
echo "PGHOST: ${PGHOST:-Not set}"
echo "PGDATABASE: ${PGDATABASE:-Not set}"
echo "PGPASSWORD: ${PGPASSWORD:+**********}"
echo "DATABASE_URL: ${DATABASE_URL:+**********}"

# MIGRATION_MODE environment variable decides DB migration strategy
# Default to "skip" in case database isn't ready yet
MIGRATION_MODE=${MIGRATION_MODE:-skip}

if [ "$MIGRATION_MODE" = "upgrade" ]; then
  echo "[Alembic] Running 'upgrade head'..."
  alembic upgrade head || echo "Warning: Alembic upgrade failed, continuing anyway."
elif [ "$MIGRATION_MODE" = "stamp" ]; then
  echo "[Alembic] Stamping the DB to 'head'..."
  alembic stamp head || echo "Warning: Alembic stamp failed, continuing anyway."
else
  echo "[Alembic] Skipping migrations entirely."
fi

# Add a short sleep to ensure migrations have time to complete
echo "Waiting for database to be fully ready..."
sleep 2

echo "Starting FastAPI server..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000