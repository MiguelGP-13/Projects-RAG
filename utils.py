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
    print(guardado, guardado == hash)
    if guardado:
        return guardado == hash
    else:
        return False


def create_embeddings_pag(texto, chunk_size, embedder, redis, nombre, pagina):
    '''
    texto: str = Text to be encoded
    chunk_size: int = Size of each chunk to be encoded separately
    modelo: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database
    nombre: str = Name of the document
    pagina: int = Page number of the document

    return: int = Number of chunks obtained from the page


    Creates embeddings and saves them in the Redis vector database.
    '''
    idx = f"documentos:{nombre}:{pagina}:"
    i = 0
    for j in range(1, len(texto), chunk_size):
        i += 1
        indice = idx+str(i)
        chunk = texto[j:j + chunk_size]
        hash = md5(chunk.encode(), usedforsecurity= False).hexdigest()
        if not alredy_stored(indice, hash, redis):
            embedding = ollama.embed(model=embedder, input=chunk).embeddings[0]
            redis.hset(indice, mapping={"embedding":to_blob(np.array(embedding)),"hash":hash, "referencia":chunk})
    return i

def create_embeddings_pdf(ruta_pdf: str, chunk_size, embedder, redis):
    '''
    ruta_pdf: str = Path to the PDF file to be encoded
    chunk_size: int = Size of each chunk to be encoded separately
    modelo: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database

    Divides the pdf into chunks and saves them in the Redis vector database
    '''
    nombre = ruta_pdf.split('.')[0].split('/')[-1]
    reader = PdfReader(ruta_pdf)
    chunks = 0
    for idx, page in enumerate(reader.pages):
        chunks += create_embeddings_pag(page.extract_text(),chunk_size, embedder, redis, nombre, idx) # Crea embeddings y devuelve numero de chunks
    print(f"¡{chunks} creados!")


def query(prompt, modelo, embedder, redis, indice, N= 3):
    '''
    prompt: str = Question about the document database
    modelo: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database

    '''
    if indice.encode() not in redis.execute_command("FT._LIST"):
        raise IndexError('El índice de la base de datos no existe. Reinicie el servicio.')
    search_embd = ollama.embed(model=embedder, input=prompt).embeddings[0]
    print(search_embd)
    query = (
        Query(f'*=>[KNN {N} @embedding $embeddings]')
        .return_fields("referencia" )  
        .dialect(2)
    )
    contexto = redis.ft(indice).search(
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
    answer = ollama.chat(model=modelo, messages=[{'role':'user', 'content':input_message}]).message
    return answer, reference_list, [doc.referencia for doc in contexto]
