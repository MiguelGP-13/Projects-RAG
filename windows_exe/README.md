# Direct Implementation on Windows
Unable to create it, because to use redis FT and KNN, you have to use linux or docker

## Without terminal
pyinstaller --windowed build.py --contents-directory "." --add-data "main.py;." --add-data "RAG.py;." --add-data "../secrets.env;." --add-data "../settings.env;." --add-data "../Frontend;frontend" --add-data "redis-server.exe;." --add-data "redis.conf.template;." --add-data "chats;chats" --add-data "documents;documents"

## With terminal
pyinstaller --onedir build.py --contents-directory "." --add-data "main.py;." --add-data "RAG.py;." --add-data "../secrets.env;." --add-data "../settings.env;." --add-data "../Frontend;frontend" --add-data "redis-server.exe;." --add-data "redis.conf.template;." --add-data "chats;chats" --add-data "documents;documents" --console


# Project Structure Overview
MAIN
├── secrets.env
├── settings.env
├── frontend/
│   ├── main.html
│   ├── styles/
│   ├── scripts/
│   └── images/
├── windows_exe/
│   ├── main.py
│   ├── RAG.py
│   ├── chats/              # Will be created upon installation
│   ├── documents/          # Will be created upon installation
│   ├── redis-server.exe    # Portable Redis (Not available for FT and KNN) => You need wsl + redis-stack or redis-stack in docker.
│   ├── redis.conf          # Redis configuration template
│   ├── build.py            # Startup script using pywebview
│   ├── requirements.txt
│   └── icon.ico            # Application icon
