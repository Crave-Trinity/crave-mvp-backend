# File: app/container/Dockerfile
# ------------------------------------------------------------------
# Use a lightweight Python 3.11-slim base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements first for Docker layer caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . /app

# Expose port 8000 (Railway will supply the actual PORT via env var)
EXPOSE 8000

# Use a custom entrypoint script to run migrations and start Uvicorn
ENTRYPOINT ["./entrypoint.sh"]
