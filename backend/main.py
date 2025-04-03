from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    print(jsonify({"message": "Welcome to the Flask App!"}))

@app.route('/setup', methods=['GET'])
def get_modules():
    print(subprocess.run(['pip', 'list']))

if __name__ == '__main__':
    app.run(debug=True)