# Docuchat
Created a RAG using 3 free options:
- Mistral (full online)
- HuggingFace (LLM online, embeddings local)
- Ollama (local)
It uses a python backend with an html/js/css frontend to interact with it.

# Quick start
You will need Docker for all versions.
If you don't have it, you can download it [here](https://docs.docker.com/get-started/introduction/get-docker-desktop/).
## Docker (recommended):
Open the compose folder inside the docker folder and follow the instructions

## Local:
- You need python installed. We recommend creating a venv for the app, so it doesn't have problems with interdependencies with other python you might have.
- Make sure you have all the requirements needed.
### Preparation
#### 1. Download the repository
Download it manually or using the terminal:
```bash
git clone https://github.com/MiguelGP-13/Projects-RAG.git
```
#### 2. Create .env file
> [!IMPORTANT] 
> The env file must be in the RAG folder, not elsewhere
```bash
DB_PASSWORD=<DB_PASSWORD IN .env>
API_MISTRAL=<Mistral API>
API_HUGGINGFACE=<HuggingFace API>
```
> [!NOTE] 
> The only api key needed is the one you are going to use
To get a Mistral API:
  1. Create an account or login if you alredy have one at [Mistral](https://auth.mistral.ai/ui/login).
  2. Go to the [api key](https://console.mistral.ai/api-keys) section and click on `Create a new Key`.
  3. Copy the key and put it in the .env file.

#### 3. Confirm settings.env content
Make sure it has this information if you choose `Mistral` or `HuggingFace` as MODE.
```bash
MODE=Mistral
CHUNK_SIZE=512
CONTEXT_SIZE=3
DOCUMENT_FOLDER=Backend/documents
QUESTIONNAIRES_FOLDER=Backend/questionnaires
CHATS_FOLDER=Backend/chats
```
If you want to use local LLM:
```bash
MODE=Local
MODEL=<Model you want to use (for example: mistral)> 
EMBEDDINGS=<Model you want to use (for example: jina/jina-embeddings-v2-base-en)> 
DIMENSION=<Dimension of embeddings generated (768 for jina embeddings)>
CHUNK_SIZE=512
CONTEXT_SIZE=3
DOCUMENT_FOLDER=Backend/documents
QUESTIONNAIRES_FOLDER=Backend/questionnaires
CHATS_FOLDER=Backend/chats
```
> [!IMPORTANT]
> Create the folders you are indicating in settings.env (documents, questionnaires and chats)

#### 4. Create Redis database in docker
```bash
docker run -d --name redis-stack -p 6379:6379 -p 8361:8001 -e REDIS_ARGS="--requirepass <DB_PASSWORD IN .env>" redis/redis-stack:latest
```

> [!TIP]
> If the command is not working, make sure Docker is alredy running
### Steps
#### 1. Start Redis in docker
Start the docker engine and the redis db
```bash
docker desktop start
docker start redis-stack
```

#### 2. Run main\.py file
Start the backend API
```bash
cd Backend
python main.py
```

#### 3. Open the main\.html file
Open the web so you can use the app
Linux:
```bash
cd ../Frontend
xdg-open file.htm
```
Windows:
```bash
cd ../Frontend
start file.htm
```
> [!NOTE]  
> You can also open it clicking on the file

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

### 10. POST /createQuestionnaire
*Payload*:  
```json
{"pdfs_array":["PDF NAME 1", "PDF NAME 2", "..."],
"level":2, // From 1 to 4
"number_of_questions":5}
```

*Answer*:  
```json
{"success": true, "questionnaireId": 1234}
```

### 11. POST /deleteQuestionnaire/<id>  
*Answer*:  
```json
{"success": true, "deleted": "id.json"}
```

### 12. GET /questionnaires/<id>
*Answer*:  
```json
{"success": true, 
"questions": [{"question":"",
                "options": ["..."],
                "correctOption":1}]
}
```

### 13. GET /questionnaires
*Answer*:  
```json
{"success": true, 
"questions": [{"question":"",
                "options": ["..."],
                "correctOption":1}]
}
```

### 14. POST /renameQuestionnaire/<id>
*Answer*:  
```json
{"success": true, "newName": "newName", "oldName":"oldName"}
```

### 15. GET /  
*Answer*: Serves `main.html` from frontend

### 16. /healt
*Answer*: 
```json
{"success": true}
{"success": false, "description":"What's not up running"}
```

## Error codes:

| Code | Description |
|------|-------------|
| 0    | Unexpected error |
| 100  | A compulsory value wasn't found in the JSON provided with the POST |
| 101  | File trying to add already exists |
| 102  | The path of the file provided doesn't exist |
| 103  | Error occurred while fetching files |
| 104  | No files arrived to the backend |
| 105  | The file you are trying to find does not exist |
| 106  | Conversation with that name already exists |
| 107  | Conversation name can't have dots (".") |
| 108  | Conversation name can't start with a number |
| 109  | Conversation name can't be empty |
| 110  | Incorrect query mode |
| 111  | The questionnaire you are trying to find does not exist |

