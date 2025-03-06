# File: Dockerfile
# ------------------------------------------------------------------------------
# This Dockerfile sets up the Python 3.11-slim environment,
# installs dependencies, copies the code, and uses an entrypoint script.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    # Ensure unbuffered Python output.
    ENV PYTHONUNBUFFERED=1
    
    # Set working directory to /app.
    WORKDIR /app
    
    # Install system dependencies.
    RUN apt-get update && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        build-essential \
        libpq-dev \
        dos2unix \
     && rm -rf /var/lib/apt/lists/*
    
    # Copy the requirements file and install dependencies.
    COPY requirements.txt /app/
    RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
    
    # Copy the entire codebase into the container.
    COPY . /app/
    
    # Copy the entrypoint script, fix line endings, and make it executable.
    COPY entrypoint.sh /app/entrypoint.sh
    RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh
    
    # Expose port 8000 (Railway will override $PORT if provided).
    EXPOSE 8000
    
    # Set the entrypoint to run our startup script.
    ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]