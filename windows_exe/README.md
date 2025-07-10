pyinstaller --onefile --windowed build.py \
  --add-data "main.py;." \
  --add-data "RAG.py;." \
  --add-data "secrets.env;." \
  --add-data "settings.env;." \
  --add-data "frontend;frontend" \
  --add-data "redis-server.exe;." \
  --add-data "redis.conf;." \
  --add-data "icon.ico;." \
  --add-data "chats;chats" \
  --add-data "documents;documents"



windows_exe/
├── main.py
├── RAG.py
├── secrets.env
├── settings.env
├── frontend/
│   ├── main.html
│   ├── styles/
│   ├── scripts/
│   └── images/
├── chats/              # Se crearán en instalación
├── documents/          # Se crearán en instalación
├── redis-server.exe    # Redis portable
├── redis.conf
├── build.py            # Script de arranque con pywebview
├── requirements.txt
└── icon.ico            # Ícono del programa

https://copilot.microsoft.com/chats/cQAjYqgPa6Up8eWTG9w6g