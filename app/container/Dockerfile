# File: Dockerfile
# Purpose:
#   - Builds a Python 3.11 environment for FastAPI.
#   - Installs dependencies, copies code, runs your entrypoint.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY entrypoint.sh /app/entrypoint.sh
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port 8000 (default used if $PORT is not set)
EXPOSE 8000

# Rely on our custom entrypoint to run migrations & start uvicorn
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]