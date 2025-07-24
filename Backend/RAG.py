import ollama
from hashlib import md5
from pypdf import PdfReader
import numpy as np
import json
import markdown
import os
from redis.commands.search.query import Query



CHATS_FOLDER = os.getenv('CHATS_FOLDER')

def saveChat(prompt, answer, actual_chat, mode, references=None):
    try:
        with open(actual_chat, 'r') as f:
            conv = json.load(f)
            realName = conv['name']
            chat = conv['conversation']
    except FileNotFoundError:
        # chat = [] # The conversation is new
        raise FileNotFoundError # Now chats are created manually, so it should exist
    chat.append({"role":"user", "content":prompt}) # Add user prompt
    chat.append({"role":"assistant", "content":answer, "references":references, "mode": mode}) # Add assistant answer
    with open(actual_chat, 'w') as f:
        json.dump({"name":realName, "conversation":chat}, f)

    return actual_chat

def to_blob(embedding: np.array) -> bytes:
    """
    Converts embedding to blob.
    :param embedding: embedding
    :return: blob
    """
    return embedding.astype(np.float32).tobytes()

def alredy_stored(indice, hash, redis):
    '''
    indice: str = Index of the chunk in the database
    hash: str = Hash of the content of the chunk
    redis: Redis = Connection to the Redis database

    return: bool = If the content is in the database and hasn't changed

    Checks if a chunk has already been stored in the database. If it has, it checks if the content has changed.
    '''
    guardado=redis.hget(indice, "hash")
    print(guardado)
    if guardado:
        print(guardado.decode(), guardado.decode() == hash, hash, type(hash), type(guardado.decode()))
        return guardado.decode() == hash
    else:
        return False

def delete_embeddings(file_name, redis):
    '''
    file_name: str = File whose chunks are going to be deleted
    redis: Redis = Connection to the Redis database
    
    return: int = Number of chunks deleted

    Deletes all embeddings created with that file.
    '''
    file_name = file_name.split('/')[-1].split('.')[0]
    keys = redis.keys(f"documentos:{file_name}:*")
    print(f"documentos:{file_name}:*")
    print(keys)
    # Borra todas esas claves
    if keys:
        redis.delete(*keys)
    return len(keys)

def create_embeddings_pag(text, chunk_size, embedder, redis, name, page, mode):
    '''
    texts: str = Text to be encoded
    chunk_size: int = Size of each chunk to be encoded separately
    embedder: str = Model to be used for creating embeddings
    redis: Redis = Connection to the Redis database
    name: str = Name of the document
    page: int = Page number of the document
    mode: str = Mode in wich LLM is hosted

    return: int = Number of chunks obtained from the page


    Creates embeddings and saves them in the Redis vector database.
    '''
    ## We create index, hash and making sure it isn't alredy created (with the same content)
    idx = f"documentos:{name}:{page}:"
    new_chunks = []
    counter = 0
    for j in range(1, len(text), chunk_size):
        chunk = text[j:j + chunk_size]
        hash = md5(chunk.encode(), usedforsecurity= False).hexdigest()
        index = idx+str(counter)
        counter += 1
        if not alredy_stored(index, hash, redis): # If the chunk alredy exists and hasn't changed content it's not created again
            new_chunks.append((index, chunk, hash))
    
    ## API Call to create embeddigns
    print('Creating embeddigns', len(new_chunks))
    i = -1
    if len(new_chunks) > 0: # Don't call model if we don't have chunks to encode
        if mode == 'Local':
            embeddings = ollama.embed(model=embedder, input=[j[1] for j in new_chunks]).embeddings
        elif mode == 'Mistral':
            embeddings_batch_response = embedder.embeddings.create(
                model= "mistral-embed", inputs=[j[1] for j in new_chunks])
            embeddings = [k.embedding for k in embeddings_batch_response.data]
            embeddings = ollama.embed(model=embedder, input=[j[1] for j in new_chunks]).embeddings
        elif mode == 'HuggingFace':
            embeddings = embedder.encode([j[1] for j in new_chunks])
        ## We save in the redis db
        print('Saving')
        for i, embedding in enumerate(embeddings):
            redis.hset(new_chunks[i][0], mapping={"embedding":to_blob(np.array(embedding)),"hash":new_chunks[i][2], "referencia":new_chunks[i][1]})
    return i + 1

def create_embeddings_pdf(pdf_path: str, chunk_size: int, embedder, redis, mode):
    '''
    pdf_path: str = Path to the PDF file to be encoded
    chunk_size: int = Size of each chunk to be encoded separately
    modelo: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database

    Divides the pdf into chunks and saves them in the Redis vector database
    '''
    nombre = pdf_path.split('.')[0].split('/')[-1]
    reader = PdfReader(pdf_path)
    chunks = 0
    for idx, page in enumerate(reader.pages):
        chunks += create_embeddings_pag(page.extract_text(),chunk_size, embedder, redis, nombre, idx, mode) # Crea embeddings y devuelve numero de chunks
    print(f"¡{chunks} creados!")
    return chunks


def query(prompt, model, embedder, redis, search_index, N, mode, actual_chat):
    '''
    prompt: str = Question about the document database
    model: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database
    search_index: str = Name of the index created in redis
    N: int = Number of similar chunks
    mode: str = Local or Mistral
    actual_chat: chat where conversation is saved

    Embedds the query, searchs for the most similar chunks and LLM writes the answer
    '''
    ## Compute the embeddings
    if search_index.encode() not in redis.execute_command("FT._LIST"):
        raise IndexError('The Redis database index does not exist. Please restart the app.')
    if mode == 'Local':
        search_embd = ollama.embed(model=embedder, input=prompt).embeddings[0]
    elif mode == 'Mistral':
            search_embd = embedder.embeddings.create(
                model= "mistral-embed", inputs=prompt).data[0].embedding
    elif mode == 'HuggingFace':
            search_embd = embedder.encode(prompt)
    print(search_embd)

    ## Find the N most similar chunks
    query = (
        Query(f'*=>[KNN {N} @embedding $embeddings]')
        .return_fields("referencia")  
        .dialect(2)
    )
    context = redis.ft(search_index).search(
        query,
        {
          'embeddings': to_blob(np.array(search_embd)) # Replaces $embeddings
        }
    ).docs
    print(context)
    reference_list = [doc.id for doc in context]

    ## Create the prompt
    input_message = "Utilizando solo y unicamente este contexto, responde a la pregunta del final. Contexto:\n" + \
    f"\n-----\n".join([doc.referencia for doc in context]) + \
    f"\nPregunta: {prompt}."
    print(input_message)

    ## Generate the answer with the LLM aid
    if mode == 'Local':
        answer = ollama.chat(model=model, messages=[{'role':'user', 'content':input_message}]).message
    elif mode == 'Mistral':
        answer = model.chat.complete(model= "mistral-small-latest", messages = [
                {
                    "role": "user",
                    "content": input_message,
                },
            ]
        ).choices[0].message
    elif mode == 'HuggingFace':
        answer = model.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            messages=[
                {
                    "role": "user",
                    "content": input_message
                }
            ],
        ).choices[0].message
    print(answer)
    
    ## Convert markdown to html
    answer = markdown.markdown(answer.content)

    ## Save chat
    actual_chat = saveChat(prompt, answer, actual_chat, 'RAG', str(reference_list))

    return answer, reference_list, [doc.referencia for doc in context], actual_chat

def LLMChat(prompt, model, mode, actual_chat):
    '''
    prompt: str = Question about the document database
    model: str = Model to be used for encoding
    mode: str = Local or Mistral
    actual_chat: chat where conversation is saved

    Sends all the conversation to the LLM
    '''
    # try: 
    with open(actual_chat, 'r') as f:
        chat = json.load(f)['conversation']
    # except FileNotFoundError:
        # chat = []
        # print('Chat anterior no encontrado')
    chat.append({'role':'user', 'content':prompt})
    
    ## Generate the answer with the LLM aid
    if mode == 'Local':
        answer = ollama.chat(model=model, messages=chat).message
    elif mode == 'Mistral':
        answer = model.chat.complete(model= "mistral-small-latest", messages = chat).choices[0].message
    elif mode == 'HuggingFace':
        answer = model.chat.completions.create(model="mistralai/Mistral-7B-Instruct-v0.3", messages= chat).choices[0].message
    print(answer)
    
    ## Convert markdown to html
    answer = markdown.markdown(answer.content)

    ## Save chat
    actual_chat = saveChat(prompt, answer, actual_chat, 'chat')

    return answer, actual_chat