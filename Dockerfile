# ------------------------------------------------------------------------------
# Dockerfile (Corrected, Uses Separate entrypoint.sh)
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

# Copy entrypoint script and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port 8000 (your FastAPI default)
EXPOSE 8000

# Use the entrypoint script
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]