from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask App!"})
    

@app.route('/get_modules', methods=['GET'])
def get_modules():
    pip_list = subprocess.run(['pip', 'list'], capture_output=True, text=True)
    if pip_list.returncode != 0:
        return jsonify({"error": "Failed to get pip list"}), 500
    items = pip_list.stdout.splitlines()
    modules = [line.split()[0] for line in items[2:]]
    versions = [line.split()[1] for line in items[2:]]
    modules = [{"name": name, "version": version} for name, version in zip(modules, versions)]
    
    return jsonify(modules)

if __name__ == '__main__':
    app.run(debug=True)