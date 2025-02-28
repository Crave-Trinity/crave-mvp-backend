# Use slim Python 3.11 image optimized for CPU-only
FROM python:3.11-slim

# Set working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        netcat-openbsd && \  # Install netcat-openbsd specifically
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better Docker caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all project files to the container
COPY . /app

# Set entrypoint permissions and run the entrypoint script
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]