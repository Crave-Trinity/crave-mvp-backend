FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# 1) Install all needed packages, including dos2unix
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# 2) Install requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 3) Copy everything else
COPY . /app/

# 4) *Definitely* fix line endings and chmod
RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 5) Expose and run
EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]