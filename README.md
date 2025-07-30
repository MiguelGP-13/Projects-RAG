# Projects-RAG
Created a RAG using 3 free options:
- HuggingFace (LLM online, embeddings local) with higher limit. Recommended
- Mistral (full online), low limit
- Ollama (local)
It uses a python backend with an html/js/css frontend to interact with it.

## Frontend:
main.html: Chat where you ask questions about the documents uploaded.

files.html: Page to upload files for the RAG to use.

## API endpoints:

### Error response:
```json
{"success": false, "error_code": "Code (int)", "description": "Error description"}
```

### 1. POST /query/<queryMode> [ RAG / chat]
*Payload*: 
```json
{"prompt": "QUERY", "chat": "Chat selected"}
```
*Answer*: 

  Chat: 
  ```json
  {"success": true, "answer": "LLM answer"}
  ```
  RAG: 
  ```json
  {"success": true, "answer": "LLM answer", "references": "Id of context peices", "reference_text": "Context pieces text"}
  ```

### 2. POST /remove_doc  
*Payload*:  
```json
{"file_name": "filename", "clear_database": true}
```
*Answer*:  
```json
{
  "success": true,
  "description": "The file filename was deleted",
  "database_cleared": "n_chunks chunks deleted"
}
```

### 3. POST /update  
*Payload*:  
```json
{"pdfs_array": ["PDF NAME 1", "PDF NAME 2", "..."]}
```
*Answer*:  
```json
{
  "success": true,
  "pdfs_created": ["PDF NAME 1", "PDF NAME 2", "..."],
  "number_of_chunks": "n_chunks new chunks were created"
}
```

### 4. POST /upload  
*Payload*:  
`files[]`: Array of `.pdf` files  
*Answer*:  
```json
{
  "success": true,
  "pdfs_created": ["PDF NAME 1", "PDF NAME 2", "..."],
  "number_of_chunks": "n_chunks new chunks were created"
}
```

### 5. GET /files  
*Answer*:  
```json
{"success": true, "files": ["PDF NAME 1", "PDF NAME 2", "..."]}
```

### 6. GET /chats  
*Answer*:  
```json
{
  "success": true,
  "chats": [
    {
      "realName": "My Chat",
      "id": "hash",
      "creationDate": "timestamp"
    },
    ...
  ]
}
```

### 7. GET /chats/<id>  
*Answer*:  
```json
{
  "success": true,
  "chat": [ "Conversation saved" ]
}
```

### 8. POST /createChat/<name>  
*Answer*:  
```json
{"success": true, "id": "hash"}
```

### 9. POST /deleteChat/<name>  
*Answer*:  
```json
{"success": true, "deleted": "id.json"}
```

### 10. GET /  
*Answer*: Serves `main.html` from frontend

## Error codes:

| Code | Description |
|------|-------------|
| 0    | Unexpected error |
| 100  | A compulsory value wasn't found in the JSON provided with the POST |
| 101  | File trying to add already exists |
| 102  | The path of the file provided doesn't exist |
| 103  | Error occurred while fetching files |
| 104  | No files arrived to the backend |
| 105  | The conversation you are trying to find does not exist |
| 106  | Conversation with that name already exists |
| 107  | Conversation name can't have dots (".") |
| 108  | Conversation name can't start with a number |
| 109  | Conversation name can't be empty |
| 110  | Incorrect query mode |

##  Launch Redis DB:
docker run -d --name redis-stack -p 6379:6379 -p 8361:8001 -e REDIS_ARGS="--requirepass `password`" redis/redis-stack:latest



## Errors
Dimensionate with %, if not it is ugly in different screens

RAG doesn't sends the answer => When reloaded, it appears (loading the chat has the answer) # error with chat selection

Alignment problem with references

When selecting one choice, put ramdom number instead of 0

When chat answers, it deletes the question and appears strangely
