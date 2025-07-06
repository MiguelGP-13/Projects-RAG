import ollama
from hashlib import md5
from pypdf import PdfReader
import numpy as np

from redis.commands.search.query import Query

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
    file_name = file_name.split('.')[0].split('/')[-1]
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
    if mode == 'Local':
        if len(new_chunks) > 0: # Don't call model if we don't have chunks to encode
            embeddings = ollama.embed(model=embedder, input=[j[1] for j in new_chunks]).embeddings
    elif mode == 'Mistral':
        if len(new_chunks) > 0: # Don't call model if we don't have chunks to encode
            embeddings_batch_response = embedder.embeddings.create(
                model= "mistral-embed", inputs=[j[1] for j in new_chunks])
            embeddings = [k.embedding for k in embeddings_batch_response.data]
    # elif mode == 'HuggingFace':

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


def query(prompt, model, embedder, redis, search_index, N, mode):
    '''
    prompt: str = Question about the document database
    model: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database
    search_index: str = Name of the index created in redis
    N: int = Number of similar chunks
    mode: str = Local or Mistral

    Embedds the query, searchs more similar chunks and LLM writes the answer
    '''
    if search_index.encode() not in redis.execute_command("FT._LIST"):
        raise IndexError('El índice de la base de datos no existe. Reinicie el servicio.')
    if mode == 'Local':
        search_embd = ollama.embed(model=embedder, input=prompt).embeddings[0]
    elif mode == 'Mistral':
            search_embd = embedder.embeddings.create(
                model= "mistral-embed", inputs=prompt).data[0].embedding
    print(search_embd)
    query = (
        Query(f'*=>[KNN {N} @embedding $embeddings]')
        .return_fields("referencia")  
        .dialect(2)
    )
    contexto = redis.ft(search_index).search(
        query,
        {
          'embeddings': to_blob(np.array(search_embd)) # Replaces $embeddings
        }
    ).docs
    print(contexto)
    reference_list = [doc.id for doc in contexto]
    input_message = "Utilizando solo y unicamente este contexto, responde a la pregunta del final. Contexto:\n" + \
    f"\n-----\n".join([doc.referencia for doc in contexto]) + \
    f"\nPregunta: {prompt}."
    print(input_message)
    if mode == 'Local':
        answer = ollama.chat(model=model, messages=[{'role':'user', 'content':input_message}]).message
    elif mode == 'Mistral':
        answer = model.chat.complete(model= "mistral-medium-2505", messages = [
                {
                    "role": "user",
                    "content": input_message,
                },
            ]
        ).choices[0].message
    # elif mode == 'HuggingFace':
    #     answer = model.chat.completions.create(
    #         model="mistralai/Mistral-7B-Instruct-v0.3",
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": input_message
    #             }
    #         ],
    #     ).choices[0].message
    print(answer)
    return answer, reference_list, [doc.referencia for doc in contexto]
