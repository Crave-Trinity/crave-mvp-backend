#!/bin/bash
set -e

# MIGRATION_MODE environment variable decides DB migration strategy
# "upgrade" runs migrations fully, "stamp" marks DB as already migrated
if [ "$MIGRATION_MODE" = "upgrade" ]; then
  echo "Running Alembic migration (upgrade head)..."
  alembic upgrade head
else
  echo "Stamping database schema as current (head)..."
  alembic stamp head
fi

echo "Starting FastAPI server..."
exec uvicorn app.api.main:app --host 0.0.0.0 --port 8000