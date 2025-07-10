#!/bin/bash

echo "→ Starting Redis..."
redis-server /app/redis.conf &

# Esperar a que Redis esté listo (puerto 6379)
echo "→ Waiting for Redis..."
until redis-cli -a "$DB_PASSWORD" ping | grep -q PONG; do
  sleep 0.5
done
echo "✔ Redis up."

echo "→ Starting backend Python..."
python3 main.py
