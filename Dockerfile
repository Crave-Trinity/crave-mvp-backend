# ------------------------------------------------------------------------------
# Use a slim Python 3.11 base image. We'll add dependencies ourselves.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    # ------------------------------------------------------------------------------
    # Set the working directory to /app inside the container.
    # ------------------------------------------------------------------------------
    WORKDIR /app
    
    # ------------------------------------------------------------------------------
    # Install system dependencies:
    #   - netcat: so `nc` is available for our health check script.
    #   - build-essential + libpq-dev: if needed for psycopg2/binary builds, etc.
    # ------------------------------------------------------------------------------
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        netcat \
        build-essential \
        libpq-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # ------------------------------------------------------------------------------
    # Copy requirements file first, so we can cache pip install layer.
    # ------------------------------------------------------------------------------
    COPY requirements.txt /app/requirements.txt
    
    # ------------------------------------------------------------------------------
    # Install Python dependencies without caching packages.
    # ------------------------------------------------------------------------------
    RUN pip install --no-cache-dir -r requirements.txt
    
    # ------------------------------------------------------------------------------
    # Copy the rest of the code into /app
    # ------------------------------------------------------------------------------
    COPY . /app
    
    # ------------------------------------------------------------------------------
    # Make sure our entrypoint script is executable.
    # ------------------------------------------------------------------------------
    RUN chmod +x /app/entrypoint.sh
    
    # ------------------------------------------------------------------------------
    # Expose port 8000 (common default), but remember Railway sets $PORT dynamically.
    # This is mostly for local `docker run -p 8000:8000`.
    # ------------------------------------------------------------------------------
    EXPOSE 8000
    
    # ------------------------------------------------------------------------------
    # Use our entrypoint script to launch the container. That script starts
    # the health-check background process and eventually launches uvicorn.
    # ------------------------------------------------------------------------------
    ENTRYPOINT ["/app/entrypoint.sh"]
    