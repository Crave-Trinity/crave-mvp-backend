# ------------------------------------------------------------------------------
# Dockerfile (One-File, Paste-and-Run)
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    ENV PYTHONUNBUFFERED=1
    WORKDIR /app
    
    # Install dependencies (including dos2unix for line endings)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        build-essential \
        libpq-dev \
        dos2unix \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements and install
    COPY requirements.txt /app/
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy all your code
    COPY . /app/
    
    # Create entrypoint.sh with a Here-Doc to avoid Docker parser issues
    RUN cat << 'EOF' > /app/entrypoint.sh
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
    env | grep -i -E "sql|db|postgres|pg" | sort || echo "(none found)"
    echo "====================="
    
    export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:password@db:5432/crave_db}"
    echo "Using DATABASE_URL: ${DATABASE_URL:0:60}..."
    
    echo "Running Alembic migrations..."
    alembic upgrade head
    
    # Start FastAPI
    exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
    
    kill $HEALTH_PID
    EOF
    
    # Convert line endings to Unix and mark as executable
    RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh
    
    EXPOSE 8000
    ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]