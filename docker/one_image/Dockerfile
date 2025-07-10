FROM redis/redis-stack-server:latest

ENV REDIS_ARGS="--requirepass REDIS_PASSWORD_2025"

# Instala Python y utilidades
RUN apt update && apt install -y python3 python3-pip curl

# Create folders for documents and chats
RUN mkdir -p /app/Backend/chats /app/Backend/documents

# Copy backend y frontend
COPY Backend /app/Backend
COPY Frontend /app/Frontend

WORKDIR /app/Backend

# Install dependencies
COPY docker/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


# Copy start.sh
COPY docker/one_image/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port for web connection
EXPOSE 13001

ENTRYPOINT ["bash", "-c", "/app/start.sh"]

