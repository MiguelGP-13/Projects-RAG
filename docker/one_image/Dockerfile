FROM redis/redis-stack-server:latest

# Instala Python y utilidades
RUN apt update && apt install -y python3 python3-pip curl

# Create folders for documents and chats
RUN mkdir -p /app/Backend/chats /app/Backend/documents

# Copy backend y frontend
COPY ../../Backend /app/Backend
COPY ../../Frontend /app/Frontend

WORKDIR /app/Backend

# Install dependencies
COPY ../requirements.txt .
RUN pip3 install -r requirements.txt


# Copy redis.conf
COPY ../../Backend/redis.conf /app/Backend/redis.conf

# Copy start.sh
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port for web connection
EXPOSE 13001

CMD ["/app/start.sh"]
