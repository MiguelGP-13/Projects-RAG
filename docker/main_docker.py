import redis
import os
import warnings
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from mistralai import Mistral
# from huggingface_hub import InferenceClient
from RAG import *

import json

## Load enviroment variables
MODE = os.getenv('MODE')
DB_PASS = os.getenv('DB_PASSWORD')
MODEL_EMBEDDING = os.getenv('EMBEDDINGS')
MODEL = os.getenv('MODEL')
DIMENSION = os.getenv('DIMENSION')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
CONTEXT_SIZE = os.getenv('CONTEXT_SIZE')
DOCUMENT_FOLDER = os.getenv('DOCUMENT_FOLDER')
CHATS_FOLDER = os.getenv('CHATS_FOLDER')
actual_chat = None

if MODE == 'Mistral':
    MODEL = Mistral(api_key=os.getenv('API_MISTRAL'))
    MODEL_EMBEDDING = MODEL
    DIMENSION = 1024
# if MODE == 'HuggingFace':
#     MODEL = InferenceClient(api_key=os.getenv('API_HUGGING_FACE'))
#     MODEL_EMBEDDING = MODEL
#     DIMENSION = 1024
elif MODE != 'Local':
    raise Exception('MODE enviroment variable supported types are: [LOCAL, MISTRAL]')


## Create conexion to db and create index to search embeddings
REDIS_DB = redis.Redis(host='redis', port=6379, password=DB_PASS)
INDICE_REDIS = 'knn'
if INDICE_REDIS.encode() not in REDIS_DB.execute_command("FT._LIST"):
    REDIS_DB.execute_command(
    f"""
    FT.CREATE {INDICE_REDIS}
    ON HASH PREFIX 1 documentos:
    SCHEMA embedding VECTOR
        FLAT 6
        TYPE FLOAT32 
        DIM {DIMENSION}
        DISTANCE_METRIC COSINE
    """
    )
else:
    print('Ya existe')


#### CREATE API backend ####
def embedd_pdf(pdfs):
    print(pdfs)
    n_chunks = 0
    for pdf in pdfs:
        n_chunks += create_embeddings_pdf(pdf, CHUNK_SIZE, MODEL_EMBEDDING, REDIS_DB, MODE)
    
    return jsonify({'success':True, "pdfs_created":pdfs, "number_of_chunks": f"{n_chunks} new chunks were created"})

app = Flask(__name__)
CORS(app) 

# Load all documents embedded to the database
@app.route("/update", methods=['POST'])
def update_redis(): # list with pdf paths
    message = request.json 
    if "pdfs_array" in message.keys():
        pdfs = message["pdfs_array"]
    else:
        print(os.listdir(DOCUMENT_FOLDER))
        pdfs  = [os.path.join(DOCUMENT_FOLDER, doc) for doc in os.listdir(DOCUMENT_FOLDER) if doc.endswith('.pdf')]

    try:
        return embedd_pdf(pdfs) 
    except Exception as e:
        return jsonify({'success':False, "error_code":0, 'description':f"Unexpected error ocurred while embeddign pdfs: {e}"})

@app.route("/query/<queryMode>", methods=['POST'])
def query_database(queryMode):
    message = request.json
    if 'prompt' not in message.keys():
        return jsonify({'success':False,"error_code":100, 'description':f"The compulsary value \"prompt\" was not found in the json."})
    if 'chat' not in message.keys():
        return jsonify({'success':False,"error_code":100, 'description':f"The compulsary value \"chat\" was not found in the json."})
    prompt = message['prompt']
    actual_chat = CHATS_FOLDER + '/' + message['chat'].replace(' ','%20') + '.json'
    try:
        if queryMode == "RAG":
            answer, context, context_text, actual_chat = query(prompt, MODEL, MODEL_EMBEDDING, REDIS_DB, INDICE_REDIS, CONTEXT_SIZE, MODE, actual_chat)
            return jsonify({'answer':answer, 'references':context, 'reference_text':context_text, 'success':True})
        elif queryMode == "chat":
            answer, actual_chat = LLMChat(prompt, MODEL, MODE, actual_chat)
            return jsonify({'answer':answer.content, 'success':True})
    except Exception as e:
        return jsonify({'success':False, "error_code":0, 'description':f"Unexpected error: {e}"})


@app.route('/add_doc', methods=['POST'])
def add_file():
    ## Retrieve post data and flags
    message = request.json # Get file path
    if 'file_path' not in message.keys():
        return jsonify({'success':False,"error_code":100, 'description':f"The compulsary value \"file_path\" was not found in the json."})
    file_path = message['file_path']
    name = file_path.split('/')[-1] # Get file name

    force = False
    if "force" in message.keys():
        warnings.warn_explicit('force value must be True or False, if not the result might be unexpected')
        force = message['force']

    if "rename" in message.keys():
        name  = message['rename']
    
    # Check the new file won't destroy an older one
    if name in os.listdir(DOCUMENT_FOLDER) and not force:
        return jsonify({'success':False,"error_code":101, 'description':f"There is alredy a file named {name}.\n \
                Add the value \"rename\" in the request json to save with another name or the \"force\" value to rewrite the document data."})
    else:
        # Save the file
        try:
            with open(file_path,'rb') as start:
                with open (DOCUMENT_FOLDER+'/'+ name, 'wb') as end:
                    end.write(start.read())
            return jsonify({'success':True, "path":DOCUMENT_FOLDER+'/'+ name})
        except FileNotFoundError:
            return jsonify({'success':False, "error_code":102, 'description':f"The file {file_path} doesn't exists."})
        except Exception as e:
            return jsonify({'success':False, "error_code":0, 'description':f"TUnexpected error: {e}"})
            

@app.route('/remove_doc', methods=['POST'])
def delete_doc():
    message = request.json # Get file name
    if 'file_name' not in message.keys():
        return jsonify({'success':False,"error_code":100, 'description':f"The compulsary value \"file_name\" was not found in the json."})
    file_name = message['file_name']
    file_name.replace(' ', '_').replace('/','-').replace('\\','-').split('.')[0] # We clean the name

    clear = 0 # Number of chunks deleted
    if "clear_database" in message.keys():
        clear = message["clear_database"] # clear= True (must clean db)
        
    try:
        os.remove(f"{DOCUMENT_FOLDER}/{file_name}.pdf")
        if clear:
            clear = delete_embeddings(file_name, REDIS_DB) # clear= Number of chunks deleted
    except FileNotFoundError:
            return jsonify({'success':False, "error_code":102, 'description':f"The is no file named {file_name}."})
    except Exception as e:
            return jsonify({'success':False, "error_code":0, 'description':f"TUnexpected error: {e}"})
    return jsonify({'success':True, "description":f" The file {file_name} was deleted", 'database_cleared':f"{clear} chunks deleted"})


@app.route("/upload", methods=['POST'])
def upload(): # Saves a file in the files folder and updates the redis DB
    try:
        uploaded_files = request.files.getlist("files[]") 
        saved_file_paths = []
        if len(uploaded_files) == 0:
            return jsonify({'success': False,"error_code":104, 'description':"No files arrived."})
    except:
        return jsonify({'success': False, "error_code":103, 'description':"Error ocurred while fetching files."})
    try: 
        for file in uploaded_files: # For each file we clean the name and save it in the files folder
            if file.filename.endswith('.pdf'): 
                file.filename = file.filename.replace(' ', '_').replace('/','-').replace('\\','-').split('.')[0] # We clean the name
                filepath = f"{DOCUMENT_FOLDER}/{file.filename}.pdf" # We save the file
                print(file, file.filename)
                file.save(filepath)
                saved_file_paths.append(filepath)
        print("Uploaded files:", saved_file_paths)
    except Exception as e:
        return jsonify({'success': False, "error_code":103, 'description':"No files arrived."})
    try: 
        return embedd_pdf(saved_file_paths) # Updating redis database
    except Exception as e:
        return jsonify({'success':False, "error_code":0, 'description':f"Unexpected error ocurred while embeddign pdfs: {e}"})

@app.route("/files", methods=['GET'])
def pdfs():
    try:
        return jsonify({'success':True, 'files':[file.split('.')[0] for file in os.listdir(DOCUMENT_FOLDER)]})
    except Exception as e:
        print('no ha ido')
        return jsonify({'success':False, "error_code":0, 'description':f"Unexpected error ocurred while loading available files: {e}"})
    
@app.route("/chats", methods=['GET'])
def get_chats():
    try:
        chats = [file for file in os.listdir(CHATS_FOLDER)]
        conversations = []
        for path in chats:
            # with open(CHATS_FOLDER + '/' + path, 'r') as chatFile: Just lists the chat names
            conversations.append({"name":path.split('.')[0].replace('%20',' ')})#, "conversation":json.load(chatFile)}) # Name, conversation
        return jsonify({'success':True, 'chats':conversations})
    except Exception as e:
        print('no ha ido')
        return jsonify({'success':False, "error_code":0, 'description':f"Unexpected error ocurred while loading available chats: {e}"})

@app.route("/chats/<name>", methods=['GET'])
def get_chat(name):
    try:
        with open(CHATS_FOLDER + '/' + name + '.json', 'r') as chatFile:
            conversation = json.load(chatFile)
        return jsonify({'success':True, 'chat':conversation})
    except FileNotFoundError:
        return jsonify({'success':False, "error_code":105, 'description':f"Chat {name} does not exist."})
    except Exception as e:
        print('no ha ido')
        return jsonify({'success':False, "error_code":0, 'description':f"Unexpected error ocurred while loading chat {name}: {e}"})

@app.route("/createChat/<name>", methods=["POST"])
def createChat(name):
    name = name.replace(' ','%20') # No spaces in names
    if name in [i.split('.')[0] for  i in os.listdir(CHATS_FOLDER)]: # That name alredy exists
        return jsonify({'success':False, "error_code":106, 'description':f"Chat {name} alredy exist."})
    elif '.' in name: # Name can't have . in it's name
        return jsonify({'success':False, "error_code":107, 'description':f"Chat {name} can't have \".\"."})
    elif name[0] in [str(i) for i in range(10)]: # Name can't start with a number
        return jsonify({'success':False, "error_code":108, 'description':f"Chat {name} can't start with a number."})
    with open(CHATS_FOLDER + '/' + name + '.json','w') as f:
        f.write("[]") # Creates an empty array for the conversation
    return jsonify({'success':True, 'path': name + '.json'})

@app.route("/deleteChat/<name>", methods=["POST"])
def deleteChat(name):
    name = name.replace(' ','%20') # No spaces in names
    if name not in [i.split('.')[0] for  i in os.listdir(CHATS_FOLDER)]: # That name alredy exists
        return jsonify({'success':False, "error_code":105, 'description':f"Chat {name} doesn't exist."})
    os.remove(CHATS_FOLDER + '/' + name + '.json')
    return jsonify({'success':True, 'deleted': name + '.json'})

if __name__ == '__main__':
    app.run(host='localhost', port=13001)