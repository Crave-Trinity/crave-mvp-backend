# ------------------------------------------------------------------------------
# Dockerfile (One-File, Paste-and-Run)
# ------------------------------------------------------------------------------

# Base Python image
FROM python:3.11-slim

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . /app/

# Create entrypoint.sh inline
# (If you prefer a separate entrypoint.sh file in your repo, you can delete
#  this RUN command and just do a COPY + dos2unix + chmod instead.)
RUN echo '#!/bin/bash
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
env | grep -i -E "sql|db|postgres|pg" | sort || echo "(none found)"
echo "====================="

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."

echo "Running Alembic migrations..."
alembic upgrade head

exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
kill $HEALTH_PID
' > /app/entrypoint.sh

# Convert line endings and mark entrypoint as executable
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port 8000 (your FastAPI default)
EXPOSE 8000

# Use the newly created entrypoint
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]