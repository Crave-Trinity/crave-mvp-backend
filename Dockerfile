# Dockerfile
# -------------------------------
# Base image with Python 3.11 on a slim Debian-based image.
FROM python:3.11-slim

# Ensure Python outputs everything to stdout/stderr immediately.
ENV PYTHONUNBUFFERED=1s

# Set the working directory inside the container.
WORKDIR /app

# Install system-level dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    dos2unix \
 && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install Python dependencies.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire codebase into /app.
COPY . /app/

# Copy the entrypoint script, convert it to Unix format, and make it executable.
COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port 8000 (used locally) – Railway will override with its $PORT.
EXPOSE 8000

# Set the container's entrypoint to our custom script.
# Using /bin/bash ensures the shell script runs properly.
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]