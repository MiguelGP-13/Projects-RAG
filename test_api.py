from flask import Flask, jsonify, request, send_from_directory, redirect
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a local directory for documents
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documentos')
os.makedirs(DOCS_DIR, exist_ok=True)

#### CREATE API backend ####
app = Flask(__name__, static_folder='html', static_url_path='')

# Load all documents embedded to the database
@app.route("/update", methods=['POST'])
def initialize_redis():
    print('Petición de actualización recibida!!')
    logger.info('Update request received!')
    return jsonify({'success': True, 'message': 'Database updated successfully'})

@app.route("/query", methods=['POST'])
def query_database():
    try:
        message = request.json
        logger.info(f"Query received: {json.dumps(message)}")
        print(f"Query received: {json.dumps(message)}")
        
        # Return a sample response
        return jsonify({
            'answer': 'This is a sample response from the API backend.',
            'references': ['GA_61CD_615001030_2S_2024-25.pdf#1', 'sample.pdf#1'],
            'reference_text': ['This is text to highlight in document 1', 'This is text to highlight in document 2']
        })
    except Exception as e:
        logger.error(f"Error in query: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/add_doc', methods=['POST'])
def add_file():
    try:
        file = request.files.get('file')
        if file:
            logger.info(f"File upload request received: {file.filename}")
            print(f"File upload request received: {file.filename}")
            
            return jsonify({'success': True, 'message': f'File {file.filename} processed successfully'})
        else:
            logger.warning("No file in request")
            return jsonify({'error': 'No file in request'}), 400
    except Exception as e:
        logger.error(f"Error in add_doc: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/remove_doc', methods=['POST'])
def delete_doc():
    try:
        data = request.json
        filename = data.get('filename', '')
        logger.info(f"Delete request received for file: {filename}")
        print(f"Delete request received for file: {filename}")
            
        return jsonify({'success': True, 'message': f'File {filename} deleted successfully'})
    except Exception as e:
        logger.error(f"Error in remove_doc: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
