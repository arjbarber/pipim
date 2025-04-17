from flask import Flask, jsonify, request
import subprocess
from bs4 import BeautifulSoup
import requests
import webbrowser
import os
import json

class PipimBackend:
    def __init__(self):
        self.app = Flask(__name__)
        self.DOCS = {}
        self.init_docs()
        self.setup_routes()

    def init_docs(self):
        with open(os.path.join('backend', 'documentations.csv'), 'r') as file:
            for line in file:
                name, url = line.strip().split(',')
                self.DOCS[name] = url
        print("Documentations loaded")

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({"message": "yoooo!"})

        @self.app.route('/get_modules', methods=['GET'])
        def get_modules():
            pip_list = subprocess.run(['pip', 'list'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if pip_list.returncode != 0:
                return jsonify({"error": "Failed to get pip list"}), 500
            items = pip_list.stdout.splitlines()
            modules = [line.split()[0] for line in items[2:]]
            versions = [line.split()[1] for line in items[2:]]
            modules = [{"name": name, "version": version} for name, version in zip(modules, versions)]
            saved_modules = []
            if os.path.exists('packages.json'):
                with open('packages.json', 'r') as f:
                    saved_modules = json.load(f)

            if len(saved_modules) == len(modules):
                for i in range(len(saved_modules)):
                    if saved_modules[i]['name'] != modules[i]['name']:
                        print("Modules are different")
                        return jsonify({"modules": modules, "saved": False})

                print("Modules are the same")
                return jsonify({"modules": saved_modules, "saved": True})
            else:
                print("Modules are different")
                return jsonify({"modules": modules, "saved": False})

        @self.app.route('/get_module_info', methods=['POST'])
        def get_module_info():
            package_name = request.json.get('package_name')
            if not package_name:
                return jsonify({"error": "Package name is required"}), 400

            r = requests.get(f"https://pypi.org/pypi/{package_name}/json")

            if r.status_code != 200:
                return jsonify({"error": "Package not found"}), 404
            data = r.json()
            package_info = {
                "name": data["info"]["name"],
                "version": data["info"]["version"],
                "summary": data["info"]["summary"],
                "author": data["info"]["author"]
            }

            return jsonify(package_info)

        @self.app.route('/install_package', methods=['POST'])
        def install_package():
            package_name = request.json.get('package_name')
            if not package_name:
                return jsonify({"error": "Package name is required"}), 400

            result = subprocess.run(['pip', 'install', package_name], capture_output=True, text=True)
            if result.returncode != 0:
                return jsonify({"error": result.stderr}), 500

            return jsonify({"message": f"Package {package_name} installed successfully!"})

        @self.app.route('/uninstall_package', methods=['POST'])
        def uninstall_package():
            package_name = request.json.get('package_name')
            if not package_name:
                return jsonify({"error": "Package name is required"}), 400

            result = subprocess.run(['pip', 'uninstall', '-y', package_name], capture_output=True, text=True)
            print(result)
            if result.returncode != 0:
                return jsonify({"error": result.stderr}), 500

            return jsonify({"message": f"Package {package_name} uninstalled successfully!"})

        @self.app.route('/save_packages_locally', methods=['POST'])
        def save_packages_locally():
            packages = request.json.get('packages')
            if not packages:
                return jsonify({"error": "No packages provided"}), 400

            with open('packages.json', 'w') as f:
                json.dump(packages, f, indent=2)
            print("Packages saved locally")

            return jsonify({"message": "Packages saved locally!"})

        @self.app.route('/install_python', methods=['GET'])
        def install_python():
            # implement later
            print("started Install")
            print(subprocess.run(["curl", "-o", "python-installer.exe", "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"]))
            print("finished install")

            return jsonify({"message": "yeah it works haha"}), 200

        @self.app.route('/search_for_packages', methods=['GET'])
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

            return jsonify(results)

        @self.app.route('/package_documentation', methods=['POST'])
        def package_documentation():
            package_name = request.json.get('package_name')
            if not package_name:
                return jsonify({"error": "Package name is required"}), 400

            if package_name in self.DOCS:
                url = self.DOCS[package_name]
            else:
                url = f"https://pypi.org/project/{package_name}/"
                # If the package is not in the local documentation, open the PyPI page
            webbrowser.open(url)

            return jsonify({"message": f"Opening documentation for {package_name}"})

    def run(self, **kwargs):
        self.app.run(**kwargs)


# To use this class in another file:
# from backend.main import PipimApp
# app_instance = PipimApp()
# app_instance.run(debug=True)