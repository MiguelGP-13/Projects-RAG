#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker desktop start

# Run Docker Compose
echo "Starting Docker Compose..."
cd "$SCRIPT_DIR"
docker compose up -d
sleep 2

# Open browser to target URL
URL="http://localhost:1380/main.html"
echo "Opening $URL"
if command -v xdg-open > /dev/null; then
    xdg-open "$URL"             # Linux
elif command -v open > /dev/null; then
    open "$URL"                 # macOS
else
    echo "Please open $URL manually"
fi
