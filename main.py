import redis
import os
import redis.exceptions
from tqdm import tqdm
from flask import Flask, jsonify, request
import json
from utils import *

## Load enviroment variables
modo = os.getenv('MODO')
DB_PASS = os.getenv('DB_PASSWORD')
MODELO_EMBEDDING = os.getenv('EMBEDDINGS')
MODELO = os.getenv('MODELO')
DIMENSION = os.getenv('DIMENSION')
CHUNK_SIZE = os.getenv('CHUNK_SIZE')
CONTEXT_SIZE = os.getenv('CONTEXT_SIZE')
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
def initialize_redis():
    pdfs  = [doc for doc in os.listdir('documentos') if doc.endswith('.pdf')]
    for pdf in tqdm(pdfs, desc="Processing PDFs", unit="file"):
        create_embeddings_pdf(pdf, CHUNK_SIZE, MODELO_EMBEDDING, REDIS_DB)


@app.route("/query", methods=['GET'])
def query_database():
    message = json.dumps(request.json)
    print(message)
    prompt = message['prompt']
    answer, context, context_text = query(prompt, MODELO, MODELO_EMBEDDING, REDIS_DB, INDICE_REDIS, CONTEXT_SIZE)
    return {'answer':answer.content, 'references':context, 'reference_text':context_text}

@app.route('/add_doc', methods=['POST'])
def add_file():
    message = json.dumps(request.json)
    print(message)
    prompt = message['file_path']
    name = file_path.split('/')[-1]
    with open(file_path,'r') as start:
        with open ('/documentos'+name, 'w') as end:
            end.write(start.read())
            

@app.route('/delete_doc', methods=['POST'])
def delete_doc(file_name):
    os.remove('/documentos'+file_name)

# if __name__ == '__main__':
#     app.run(host='127.0.0.3', port=8000)