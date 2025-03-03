# ------------------------------------------------------------------------------
# Dockerfile (Baby Mode)
# Paste this into your Dockerfile and push to Railway.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    ENV PYTHONUNBUFFERED=1
    WORKDIR /app
    
    # Install dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        build-essential \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*  # Clean up in the same layer
    
    COPY requirements.txt /app/
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . /app/
    
    # VERY IMPORTANT: Fix line endings and set executable permissions within the Docker build
    RUN sed -i 's/\r$//' /app/entrypoint.sh && \
        chmod +x /app/entrypoint.sh
    
    EXPOSE 8000
    
    ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]