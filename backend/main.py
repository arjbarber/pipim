from flask import Flask, jsonify, request
import subprocess
from bs4 import BeautifulSoup
import requests
import webbrowser

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

@app.route('/install_package', methods=['POST'])
def install_package():
    package_name = request.json.get('package_name')
    if not package_name:
        return jsonify({"error": "Package name is required"}), 400
    
    result = subprocess.run(['pip', 'install', package_name], capture_output=True, text=True)
    if result.returncode != 0:
        return jsonify({"error": result.stderr}), 500
    
    return jsonify({"message": f"Package {package_name} installed successfully!"})

@app.route('/uninstall_package', methods=['POST'])
def uninstall_package():
    package_name = request.json.get('package_name')
    if not package_name:
        return jsonify({"error": "Package name is required"}), 400
    
    result = subprocess.run(['pip', 'uninstall', '-y', package_name], capture_output=True, text=True)
    print(result)
    if result.returncode != 0:
        return jsonify({"error": result.stderr}), 500
    
    return jsonify({"message": f"Package {package_name} uninstalled successfully!"})

@app.route('/install_python', methods=['POST'])
def install_python():
    # implement later
    ...

@app.route('/search_for_packages')
def search_for_packages():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing 'q' parameter"}), 400

    search_url = f"https://pypi.org/search/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data from PyPI"}), 500

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    print(soup)
    listOfPackages = soup.find_all("ul", attrs={"class": "unstyled"})
    print(listOfPackages)
    
    return (jsonify(results))

@app.route('/package_documentation', methods=['POST'])
def package_documentation():
    package_name = request.json.get('package_name')
    if not package_name:
        return jsonify({"error": "Package name is required"}), 400

    url = f"https://pypi.org/project/{package_name}/"
    webbrowser.open(url)

    return jsonify({"message": f"Opening documentation for {package_name}"})

if __name__ == '__main__':
    app.run(debug=True)