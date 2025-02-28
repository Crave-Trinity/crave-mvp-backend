#!/bin/bash
# File: entrypoint.sh
# Purpose: Application startup script for Docker
# Changes: Add debug information to track down environment variable issues

set -e

# Debug environment variables to help troubleshoot database connections
echo "==== DATABASE ENVIRONMENT VARIABLES ===="
echo "DATABASE_URL: ${DATABASE_URL:-Not set}"
echo "SQLALCHEMY_DATABASE_URI: ${SQLALCHEMY_DATABASE_URI:-Not set}"
echo "POSTGRES_URL: ${POSTGRES_URL:-Not set}"
echo "==== END DATABASE ENVIRONMENT VARIABLES ===="

# MIGRATION_MODE environment variable decides DB migration strategy
# "upgrade" runs migrations fully, "stamp" marks DB as already migrated, "skip" does nothing
MIGRATION_MODE=${MIGRATION_MODE:-stamp}

if [ "$MIGRATION_MODE" = "upgrade" ]; then
  echo "Running Alembic migration (upgrade head)..."
  alembic upgrade head || echo "Warning: Failed to run Alembic migrations."
elif [ "$MIGRATION_MODE" = "stamp" ]; then
  echo "Stamping database schema as current (head)..."
  alembic stamp head || echo "Warning: Failed to stamp database schema."
else
  echo "Skipping database migrations (MIGRATION_MODE=$MIGRATION_MODE)."
fi

echo "Starting FastAPI server..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000