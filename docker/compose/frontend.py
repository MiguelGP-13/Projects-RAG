from flask import Flask, send_from_directory

app = Flask(__name__, static_folder='Frontend')

@app.route('/')
def root():
    return send_from_directory(app.static_folder, 'main.html')

@app.route('/<path:path>')
def static_files(path):
    print(path)
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
