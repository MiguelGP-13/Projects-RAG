import redis
import os
import warnings
import redis.exceptions
from tqdm import tqdm
from flask import Flask, jsonify, request
import json
from utils import *

from dotenv import load_dotenv

load_dotenv('.env.settings')  # carga el archivo con tus variables
load_dotenv('.env.secrets')

## Load enviroment variables
modo = os.getenv('MODO')
DB_PASS = os.getenv('DB_PASSWORD')
MODELO_EMBEDDING = os.getenv('EMBEDDINGS')
MODELO = os.getenv('MODELO')
DIMENSION = os.getenv('DIMENSION')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE'))
CONTEXT_SIZE = os.getenv('CONTEXT_SIZE')
DOCUMENT_FOLDER = os.getenv('DOCUMENT_FOLDER')
if modo=='Externo':
    API_KEY = os.getenv('API_MODELO')
    API_EMBEDDING = os.getenv('API_EMBEDDINGS')


## Create conexion to db and create index to search embeddings
REDIS_DB = redis.Redis(host='localhost', port=6379, password=DB_PASS)
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
app = Flask(__name__)

# Load all documents embedded to the database
@app.route("/update", methods=['POST'])
def update_redis(): # list with pdf paths
    message = request.json 
    if "pdfs_array" in message.keys():
        pdfs = message["pdfs_array"]
    else:
        pdfs  = [doc for doc in os.listdir(DOCUMENT_FOLDER) if doc.endswith('.pdf')]

    n_chunks = 0
    for pdf in tqdm(pdfs, desc="Processing PDFs", unit="file"):
        n_chunks += create_embeddings_pdf(pdf, CHUNK_SIZE, MODELO_EMBEDDING, REDIS_DB)
    
    return {'success':True, "pdfs_created":pdfs, "number_of_chunks": f"{n_chunks} new chunks were created"}

@app.route("/query", methods=['POST'])
def query_database():
    message = request.json
    if 'prompt' not in message.keys():
        return {'success':False,"error_code":100, 'description':f"The compulsary value \"prompt\" was not found in the json."}
    prompt = message['prompt']
    try:
        answer, context, context_text = query(prompt, MODELO, MODELO_EMBEDDING, REDIS_DB, INDICE_REDIS, CONTEXT_SIZE)
        return {'answer':answer.content, 'references':context, 'reference_text':context_text}
    except Exception as e:
        return {'success':False, "error_code":0, 'description':f"TUnexpected error: {e}"}

@app.route('/add_doc', methods=['POST'])
def add_file():
    ## Retrieve post data and flags
    message = request.json # Get file path
    if 'file_path' not in message.keys():
        return {'success':False,"error_code":100, 'description':f"The compulsary value \"file_path\" was not found in the json."}
    file_path = message['file_path']
    name = file_path.split('/')[-1] # Get file name

    force = False
    if "force" in message.keys():
        if force == True or force== False:
            warnings.warn_explicit('force value must be True or False, if not the result might be unexpected')
        force = message['force']

    if "rename" in message.keys():
        name  = message['rename']
    
    # Check the new file won't destroy an older one
    if name in os.listdir(DOCUMENT_FOLDER) and not force:
        return {'success':False,"error_code":101, 'description':f"There is alredy a file named {name}.\n \
                Add the value \"rename\" in the request json to save with another name or the \"force\" value to rewrite the document data."}
    else:
        # Save the file
        try:
            with open(file_path,'rb') as start:
                with open (DOCUMENT_FOLDER+'/'+ name, 'wb') as end:
                    end.write(start.read())
            return {'success':True, "path":DOCUMENT_FOLDER+'/'+ name}
        except FileNotFoundError:
            return {'success':False, "error_code":102, 'description':f"The file {file_path} doesn't exists."}
        except Exception as e:
            return {'success':False, "error_code":0, 'description':f"TUnexpected error: {e}"}
            

@app.route('/remove_doc', methods=['POST'])
def delete_doc():
    message = request.json # Get file name
    if 'file_name' not in message.keys():
        return {'success':False,"error_code":100, 'description':f"The compulsary value \"file_name\" was not found in the json."}
    file_name = message['file_name']

    clear = 0 # Number of chunks deleted
    if "clear_database" in message.keys():
        clear = message["clear_database"] # clear= True (must clean db)
        
    try:
        os.remove(DOCUMENT_FOLDER+'/' + file_name)
        if clear:
            clear = delete_embeddings(file_name, REDIS_DB) # clear= Number of chunks deleted
    except FileNotFoundError:
            return {'success':False, "error_code":102, 'description':f"The is no file named {file_name}."}
    except Exception as e:
            return {'success':False, "error_code":0, 'description':f"TUnexpected error: {e}"}
    return {'success':True, "description":f" The file {file_name} was deleted", 'database_cleared':f"{clear} chunks deleted"} 

if __name__ == '__main__':
    app.run(host='127.0.0.3', port=1234)