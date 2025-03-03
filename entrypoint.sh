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

echo "SIMPLE TEST LINE"

# echo "==== RAILWAY ENV DETECT ===="  <-- COMMENT THIS OUT FOR NOW
# ... rest of your original script ... (you can add it back later if this works)
echo "Script continues after line 14"

# Your original commands that follow "==== RAILWAY ENV DETECT ====" should go here