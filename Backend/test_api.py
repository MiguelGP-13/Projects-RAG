from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/update", methods=['POST'])
def update_redis():
    return jsonify({'success': True, "pdfs_created": ["sample1.pdf", "sample2.pdf"], "number_of_chunks": "12 new chunks were created"})

@app.route("/query", methods=['POST'])
def query_database():
    data = request.json
    prompt = data.get("prompt", "")
    print(prompt)
    return jsonify({
        'answer': f"Mock response for prompt: {prompt}",
        'references': ["ref1", "ref2"],
        'reference_text': ["This is mock context 1.", "This is mock context 2."],
        'success': True
    })

@app.route("/add_doc", methods=['POST'])
def add_file():
    data = request.json
    file_path = data.get("file_path", "mock/path/to/file.pdf")
    return jsonify({'success': True, "path": f"/mock/files/{file_path.split('/')[-1]}"})

@app.route("/remove_doc", methods=['POST'])
def delete_doc():
    data = request.json
    file_name = data.get("file_name", "unknown.pdf")
    return jsonify({'success': True, "description": f"Mock deletion of {file_name}", "database_cleared": "8 chunks deleted"})

@app.route("/upload", methods=['POST'])
def upload():
    return jsonify({'success': True, "pdfs_created": ["uploaded_mock.pdf"], "number_of_chunks": "6 new chunks were created"})

@app.route("/files", methods=['GET'])
def pdfs():
    return jsonify({'success': True, 'files': ["mock_doc1", "mock_doc2", "mock_doc3"]})

if __name__ == "__main__":
    app.run(host='127.0.0.3', debug=True, port=13001)
