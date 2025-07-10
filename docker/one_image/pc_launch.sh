#!/bin/bash

# Env files
ENV1="/home/miguel/Escritorio/RAG/docker/one_image/settings.env"
ENV2="/home/miguel/Escritorio/RAG/secrets.env"

# Docker Image
IMAGE_NAME="miguelgp13/rag-complete:1.0"

# Check if Docker is active
if ! systemctl is-active --quiet docker; then
    echo "🔧 Docker is not active. Attempting to start it..."
    sudo systemctl start docker
    sleep 2
    echo "Docker started."
else
    echo "Docker is already running."
fi

# Run the container
echo "Launching the container with environment files..."

docker run --env-file "$ENV1" --env-file "$ENV2" -it "$IMAGE_NAME"
