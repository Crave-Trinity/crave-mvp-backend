# Dockerfile - Build instructions for CRAVE Trinity Backend.

# Use a lightweight Python 3.11 image.
FROM python:3.11-slim

# Ensure Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container.
WORKDIR /app

# Install system dependencies: networking, build tools, PostgreSQL client libraries, dos2unix.
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container.
COPY . /app/

# Copy the entrypoint script into the container and ensure it's Unix-formatted and executable.
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose the port that uvicorn will run on.
EXPOSE 8000

# Set the entrypoint to the shell script.
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]