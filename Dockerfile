# ------------------------------------------------------------------------------
# Use a slim Python 3.11 base image.
# ------------------------------------------------------------------------------
    FROM python:3.11-slim

    # ------------------------------------------------------------------------------
    # Set the working directory inside the container.
    # ------------------------------------------------------------------------------
    WORKDIR /app
    
    # ------------------------------------------------------------------------------
    # Install system dependencies:
    #   - netcat-openbsd: Provides `nc` for health checks.
    #   - build-essential, libpq-dev: Required for compiling some Python dependencies.
    # ------------------------------------------------------------------------------
    RUN apt-get update && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        build-essential \
        libpq-dev && \
        rm -rf /var/lib/apt/lists/*
    
    # ------------------------------------------------------------------------------
    # Copy requirements file and install dependencies.
    # ------------------------------------------------------------------------------
    COPY requirements.txt /app/requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt
    
    # ------------------------------------------------------------------------------
    # Copy the rest of the application code.
    # ------------------------------------------------------------------------------
    COPY . /app
    
    # ------------------------------------------------------------------------------
    # Ensure `entrypoint.sh` is executable.
    # ------------------------------------------------------------------------------
    RUN chmod +x /app/entrypoint.sh
    
    # ------------------------------------------------------------------------------
    # Expose port 8000 (for local use), but Railway will provide its own PORT.
    # ------------------------------------------------------------------------------
    EXPOSE 8000
    
    # ------------------------------------------------------------------------------
    # Use `entrypoint.sh` to launch the container.
    # ------------------------------------------------------------------------------
    ENTRYPOINT ["/app/entrypoint.sh"]
    