#!/bin/bash

echo "→ Starting Redis..."
redis-server $REDIS_ARGS &

# Waiting for Redis (puerto 6379)
echo "→ Waiting for Redis..."
until redis-cli -a "REDIS_PASSWORD_2025" ping | grep -q PONG; do
  sleep 2
done
echo "✔ Redis up."

# Show current ACL configuration
echo "→ Current ACL users and permissions:"
redis-cli -a "REDIS_PASSWORD_2025" ACL LIST

echo "new"

echo "→ Starting backend Python..."
python3 main.py
