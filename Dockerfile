# Dockerfile
FROM python:3.11-slim

# Ensure unbuffered Python output.
ENV PYTHONUNBUFFERED=1

# Set working directory.
WORKDIR /app

# Install system dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    dos2unix \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies without hash verification.
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy entire codebase.
COPY . /app/

# Copy the entrypoint script; convert to Unix line endings and make executable.
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port 8000 (Railway will override with its $PORT).
EXPOSE 8000

# Set the entrypoint to our custom script.
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]