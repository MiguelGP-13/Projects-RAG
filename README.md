# Projects-RAG
Discovering RAG, implementated with Ollama and Mistral API

### Launch Redis DB:
docker run -d --name redis-stack -p 6379:6379 -p 8361:8001 -e REDIS_ARGS="--requirepass `password`" redis/redis-stack:latest


### Error codes:

0: Unexpected error

100: A compulsary value wasn't found in the json provided with the POST
101 : File trying to add alredy exists
102 : The path of the file provided doesn't exists
