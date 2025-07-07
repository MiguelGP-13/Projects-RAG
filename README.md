# Projects-RAG
Created a RAG using 2 options:
- Mistral (online)
- Ollama (local)
It uses a python backend with an html/js/css frontend to interact with it.

## Frontend:
main.html: Chat where you ask questions about the documents uploaded.

files.html: Page to upload files for the RAG to use.

## API endpoints:
### 1. POST /query 
*Payload*: {"prompt":`QUERY`}
*Answer*: 

### 2. POST /update 
*Payload*: {"pdfs": [`PDF NAME 1`, `PDF NAME 2`,...], "force":true, "rename":}
*Answer*: 

### 3. POST /add_doc 
*Payload*: {}
*Answer*: 
 
## Error codes:

0. Unexpected error

100. A compulsary value wasn't found in the json provided with the POST

101. File trying to add alredy exists

102. The path of the file provided doesn't exists

103. Error ocurred while fetching files

104. No files arrived the backend

##  Launch Redis DB:
docker run -d --name redis-stack -p 6379:6379 -p 8361:8001 -e REDIS_ARGS="--requirepass `password`" redis/redis-stack:latest



