import ollama
from hashlib import md5
from pypdf import PdfReader
import numpy as np
import re
import random
import json
import markdown
import os
from redis.commands.search.query import Query

def saveChat(prompt, answer, actual_chat, mode, references=None):
    try:
        with open(actual_chat, 'r') as f:
            conv = json.load(f)
            realName = conv['name']
            chat = conv['conversation']
            creationDate = conv['creationDate']
    except FileNotFoundError:
        # chat = [] # The conversation is new
        raise FileNotFoundError # Now chats are created manually, so it should exist
    chat.append({"role":"user", "content":prompt}) # Add user prompt
    chat.append({"role":"assistant", "content":answer, "references":references, "mode": mode}) # Add assistant answer
    with open(actual_chat, 'w') as f:
        json.dump({"name": realName, "conversation": chat, "creationDate": creationDate}, f)

    return actual_chat

def to_blob(embedding: np.array) -> bytes:
    """
    embedding: np.array = embedding

    return: bytes = blob

    Converts embedding to blob.
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
        print('Embedding')
        if mode == 'Local':
            embeddings = ollama.embed(model=embedder, input=[j[1] for j in new_chunks]).embeddings
        elif mode == 'Mistral':
            embeddings_batch_response = embedder.embeddings.create(
                model= "mistral-embed", inputs=[j[1] for j in new_chunks])
            embeddings = [k.embedding for k in embeddings_batch_response.data]
        elif mode == 'HuggingFace':
            embeddings = embedder.encode([j[1] for j in new_chunks])
        ## We save in the redis db
        print('Saving', len(embeddings), embeddings[0][0])
        for i, embedding in enumerate(embeddings):
            redis.hset(new_chunks[i][0], mapping={"embedding":to_blob(np.array(embedding)),"hash":new_chunks[i][2], "reference":new_chunks[i][1]})
    print(i)
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

def cleanReferences(references):
    """
    references: list = List with used references

    return: str = Text to show in frontend with the references used

    Cleans how references are shown, to make it more concise and more understandable
    """
    cleanReferences = {}
    for reference in references:
        if "documentos:" in reference:
            reference = reference.replace("documentos:",'') # We remove the prefix 'documentos:' from each reference
        document, page, chunk = reference.split(':') # We split into [document, page, chunk]
        if document in cleanReferences:
            cleanReferences[document] += f', {page}:{chunk}'
        else:
            cleanReferences[document] = f'[{page}:{chunk}'
    result = ''
    for doc in [f"{document} : {cleanReferences[document]}]" for document in cleanReferences.keys()]:
        result += doc + ', '
    return '[' + result[:-2] + ']'

def query(prompt, model, embedder, redis, search_index, N, mode, actual_chat):
    '''
    prompt: str = Question about the document database
    model: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database
    search_index: str = Name of the index created in redis
    N: int = Number of similar chunks
    mode: str = Local, Mistral of HuggingFace
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
        .return_fields("reference")  
        .dialect(2)
    )
    context = redis.ft(search_index).search(
        query,
        {
          'embeddings': to_blob(np.array(search_embd)) # Replaces $embeddings
        }
    ).docs
    print(context)
    reference_list = cleanReferences([doc.id for doc in context])

    ## Create the prompt
    input_message = "Using only and exclusively this context, answer the next question in the same language as the context. Context:\n" + \
    f"\n-----\n".join([doc.reference.encode('utf-8').decode('utf-8') for doc in context]) + \
    f"\nQuestion: {prompt}."
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
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
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

    return answer, str(reference_list)[1:-1], [doc.reference.encode('utf-8').decode('utf-8') for doc in context], actual_chat

def LLMChat(prompt, model, mode, actual_chat):
    '''
    prompt: str = Question about the document database
    model: str = Model to be used for encoding
    mode: str = Local,  Mistral of HuggingFace
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
        answer = model.chat.completions.create(model="meta-llama/Meta-Llama-3.1-8B-Instruct", messages= chat).choices[0].message
    print(answer)
    
    ## Convert markdown to html
    answer = markdown.markdown(answer.content)

    ## Save chat
    actual_chat = saveChat(prompt, answer, actual_chat, 'chat')

    return answer, actual_chat

def checkQuestions(answer):
    """
    answer: str = The answer given by the LLM. It should be a list of questions.

    return: list = The parsed json with the questions.

    Cleans the LLM answer to avoid errors.
    """
    if answer[0] != '[' or answer[-1] != ']': # We make sure it has no initial or ending extra text
        try:
            answer = '[' + re.search(r"\[(.*)\]", answer, re.DOTALL).group() + ']'
        except AttributeError:
            print(answer)
            print("¡¡AttributeError!!")
            return []
    # if checkBrackets(answer): Maybe we could check brackets match
    questions = json.loads(answer)
    if len(questions) == 1:
        questions = questions[0]
    return questions

def createQuestionnaireHTML(pdfs, level, nQuestions, model, redis, mode, maxChunks):
    """
    pdfs: list = Names of pdfs to use for the questionnaire
    level: int = Level of the questionnaire from 1 to 4
    nQuestions: int = Number of questions to return
    model: str = Model to be used for encoding
    redis: Redis = Connection to the Redis database
    mode: str = Local, Mistral of HuggingFace
    maxChunks: int = Max of chunks to use. To avoid consuming too much credits
    """
    keys = []
    for file in pdfs:
        file_name = file.split('/')[-1].split('.')[0]
        keys += redis.keys(f"documentos:{file_name}:*")
    print(keys)
    nChunks = min(len(keys), nQuestions) # We query if possible, one chunk per question (After we will filter)
    questions = [] # We will store here the questions
    for _ in range(min(nChunks,maxChunks)): # We create questions about nChunks
        chosen = random.choice(keys)
        keys.remove(chosen)
        print(chosen)
        context = redis.hget(chosen,"reference").decode('utf-8')
        prompt = f'''
                Create {max(5,nQuestions//nChunks)} test questions with 4 possible answers of this information (in the same language as the infromation). 
                Using exclusively this information:
                {context}

                The level of the questions should be {level}, being 1 the easiest and 4 the most difficult. Make all options plausible, making it more difficult and realistic (all answers can seem the correct one if you don't know about the aspects inquired), specially in the hardests level.
                Your answer should be a list of json objects and only the json, without any text like the example (correct option is the index in the options array of the solution, from 0 to 3):
                [{{
                "question":"What size are the ninja turtles?"
                "options":["5 meters", "All options are correct", "1.2 cm", "2 meters"]
                "correctOption": 0
                }},
                ...]
                '''
        # print(prompt)
        ## Generate the questions and answers with the LLM aid
        if mode == 'Local':
            answer = ollama.chat(model=model, messages=[{"role":"user", "content":prompt}]).message
        elif mode == 'Mistral':
            answer = model.chat.complete(model= "mistral-small-latest", messages = [{"role":"user", "content":prompt}]).choices[0].message
        elif mode == 'HuggingFace':
            answer = model.chat.completions.create(model="meta-llama/Meta-Llama-3.1-8B-Instruct", messages= [{"role":"user", "content":prompt}]).choices[0].message
        # print(answer)
        print(checkQuestions(answer.content))
        questions += checkQuestions(answer.content) # Check the format is correct
        # print(checkQuestions(answer.content))
    print('All questions:')
    print(questions)
    ## Choose the best nQuestions
    prompt = f'''
             Choose the best {nQuestions} (exactly {nQuestions}, no one more, no one less) adjusted to the level {level}, being 1 the easiest and 4 the most difficult.
             Choose based on relevance. Choose wisely according to the level and making sure they cover various topics.Discard the ones that might have been errors, or if they are repetitive. 
             Answer only with the number before the question. Don't explain anything. Answer only and just with the answers id. NOTHING ELSE PLEASE
             Example answer: "1, 2, 7, 9"
             Questions to evaluate:

             '''
    print(prompt)
    for i, question in enumerate(questions):
        prompt += "\n" + str(i+1) + ":" + question['question']
        for n, option in enumerate(question['options']):
            prompt += f"\n\t {chr(ord('a') + n)}: {option}"
    if mode == 'Local':
        answer = ollama.chat(model=model, messages=[{"role":"user", "content":prompt}]).message
    elif mode == 'Mistral':
        answer = model.chat.complete(model= "mistral-small-latest", messages = [{"role":"user", "content":prompt}]).choices[0].message
    elif mode == 'HuggingFace':
        answer = model.chat.completions.create(model="meta-llama/Meta-Llama-3.1-8B-Instruct", messages= [{"role":"user", "content":prompt}]).choices[0].message
    number = ''
    print(answer)
    answer = re.search(r"([\d,\s]+)", answer.content, re.DOTALL).group()
    finalQuestions = []
    for char in answer: # Detect numbers in answer
        if char in [str(i) for i in range(10)]:
            number += char
        else:
            if number != '':
                finalQuestions.append(questions[int(number) - 1])
                print(number, end= ', ')
            number = ''
    if number.isdigit(): # For the last one
                finalQuestions.append(questions[int(number) - 1])
                print(number)
    print()
    print(finalQuestions)
    return finalQuestions
