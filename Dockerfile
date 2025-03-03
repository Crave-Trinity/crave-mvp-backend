# ------------------------------------------------------------------------------
# Dockerfile (Baby Mode)
# Paste this into your Dockerfile and push to Railway.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    ENV PYTHONUNBUFFERED=1
    WORKDIR /app
    
    # Install dependencies in a single layer for caching efficiency
    RUN apt-get update && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        build-essential \
        libpq-dev \
        dos2unix && \
        rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt /app/
    RUN pip install --no-cache-dir -r requirements.txt
    
    COPY . /app/
    
    # Convert line endings and make executable in one step
    RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh
    
    EXPOSE 8000
    
    # Explicitly use bash
    ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]