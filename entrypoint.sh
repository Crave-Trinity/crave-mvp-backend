#!/bin/bash
set -e

(
  echo "Starting minimal health check responder on port 8081..."
  while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n{\"status\":\"ok\"}" \
      | nc -l -p 8081 -q 1 || true
  done
) &
HEALTH_PID=$!

echo "==== RAILWAY ENV DETECT ===="
...