import redis
import os
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
CHUNK_SIZE = os.getenv('CHUNK_SIZE')
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
def update_redis(pdfs: list = None): # list with pdf paths
    if not pdfs:
        pdfs  = [doc for doc in os.listdir('documentos') if doc.endswith('.pdf')]
    for pdf in tqdm(pdfs, desc="Processing PDFs", unit="file"):
        create_embeddings_pdf(pdf, CHUNK_SIZE, MODELO_EMBEDDING, REDIS_DB)
    print(pdfs, 'actualizados')

@app.route("/query", methods=['POST'])
def query_database():
    message = json.dumps(request.json)
    print(message)
    prompt = message['prompt']
    answer, context, context_text = query(prompt, MODELO, MODELO_EMBEDDING, REDIS_DB, INDICE_REDIS, CONTEXT_SIZE)
    return {'answer':answer.content, 'references':context, 'reference_text':context_text}

@app.route('/add_doc', methods=['POST'])
def add_file():

    ### Bien, pero añadir control de si ya existe el archivo en la carpeta y devolver error

    message = request.json
    print(message, type(message))
    file_path = message['file_path']
    name = file_path.split('/')[-1]
    print(file_path, name, DOCUMENT_FOLDER)
    with open(file_path,'rb') as start:
        with open (DOCUMENT_FOLDER+'/'+ name, 'wb') as end:
            end.write(start.read())
    return {'success':True}
            

@app.route('/remove_doc', methods=['POST'])
def delete_doc(file_name):
    os.remove(DOCUMENT_FOLDER+'/' + file_name)

if __name__ == '__main__':
    app.run(host='127.0.0.3', port=1234)