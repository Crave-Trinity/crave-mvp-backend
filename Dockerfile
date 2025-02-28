# Dockerfile

# Use Python 3.11-slim as the base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies in a single RUN to keep layers small
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Now copy the entire project
COPY . /app

# Make sure our entry script is executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script, which will start our server + health check
ENTRYPOINT ["/app/entrypoint.sh"]
