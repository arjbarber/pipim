from flask import Flask, jsonify, request
import subprocess
import requests
import webbrowser
import os
import json
import urllib.request
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
from waitress import serve
from platform import system

class PipimBackend:
    def __init__(self):
        self.app = Flask(__name__)
        self.DOCS = {}
        self.base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
        self.init_docs()
        self.setup_routes()

    def init_docs(self):
        docs_path = os.path.join(self.base_path, 'backend', 'documentations.csv')
        with open(docs_path, 'r') as file:
            for line in file:
                name, url = line.strip().split(',')
                self.DOCS[name] = url

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({"message": "yoooo!"})

        @self.app.route('/get_modules', methods=['GET'])
        def get_modules():
            pip_list = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
            if pip_list.returncode != 0:
                return jsonify({"error": "Failed to get pip list"}), 500
            items = pip_list.stdout.splitlines()
            modules = [line.split()[0] for line in items[2:]]
            versions = [line.split()[1] for line in items[2:]]
            modules = [{"name": name, "version": version} for name, version in zip(modules, versions)]

            json_path = os.path.join(self.base_path, 'packages.json')
            saved_modules = []
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
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

            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name], capture_output=True, text=True)
            if result.returncode != 0:
                return jsonify({"error": result.stderr}), 500

            return jsonify({"message": f"Package {package_name} installed successfully!"})

        @self.app.route('/uninstall_package', methods=['POST'])
        def uninstall_package():
            package_name = request.json.get('package_name')
            if not package_name:
                return jsonify({"error": "Package name is required"}), 400

            result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', package_name], capture_output=True, text=True)
            if result.returncode != 0:
                return jsonify({"error": result.stderr}), 500

            return jsonify({"message": f"Package {package_name} uninstalled successfully!"})

        @self.app.route('/save_packages_locally', methods=['POST'])
        def save_packages_locally():
            packages = request.json.get('packages')
            if not packages:
                return jsonify({"error": "No packages provided"}), 400

            json_path = os.path.join(self.base_path, 'packages.json')
            with open(json_path, 'w') as f:
                json.dump(packages, f, indent=2)

            return jsonify({"message": "Packages saved locally!"})

        @self.app.route('/install_python', methods=['GET'])
        def install_python():

            if system() == "Windows":
                PYTHON_URL = "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe"
                install_cmd = [
                    "python_installer.exe",
                    "/quiet",
                    "InstallAllUsers=1",
                    "PrependPath=1",
                    "Include_test=0"
                ]
            elif system() == "Darwin":
                PYTHON_URL = "https://www.python.org/ftp/python/3.12.2/python-3.12.2-macos11.pkg"
                install_cmd = [
                    "sudo",
                    "installer",
                    "-pkg",
                    "python_installer.pkg",
                    "-target",
                    "/"
                ]
            else:
                return jsonify({"error": "Unsupported OS"}), 400

            temp_dir = tempfile.gettempdir()
            installer_filename = "python_installer.exe" if system() == "Windows" else "python_installer.pkg"
            installer_path = os.path.join(temp_dir, installer_filename)

            urllib.request.urlretrieve(PYTHON_URL, installer_path)

            try:
                subprocess.run(install_cmd, check=True)
                return jsonify({"message": "Python installation triggered."}), 200
            except subprocess.CalledProcessError as e:
                return jsonify({"error": f"Installation failed: {str(e)}"}), 500

        @self.app.route('/search_for_packages', methods=['GET'])
        def search_for_packages():
            query = request.args.get('q')
            if not query:
                return jsonify({"error": "Missing 'q' parameter"}), 400

            search_url = f"https://pypi.org/search/?q={query}"

            try:
                options = webdriver.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument("user-agent=Mozilla/5.0")
                options.add_argument('--headless=new')

                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                driver.get(search_url)

                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".package-snippet"))
                )
                time.sleep(2)

                results = []
                packages = driver.find_elements(By.CSS_SELECTOR, '.package-snippet')
                for package in packages:
                    try:
                        name = package.find_element(By.CSS_SELECTOR, '.package-snippet__name').text.strip()
                        summary = package.find_element(By.CSS_SELECTOR, '.package-snippet__description').text.strip()
                        results.append({"name": name, "summary": summary})
                    except Exception as e:
                        print(f"Error processing package {query}: {e}")
                        continue

                driver.quit()
                return jsonify({"packages": results})

            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/package_documentation', methods=['POST'])
        def package_documentation():
            package_name = request.json.get('package_name')
            if not package_name:
                return jsonify({"error": "Package name is required"}), 400

            if package_name in self.DOCS:
                url = self.DOCS[package_name]
            else:
                url = f"https://pypi.org/project/{package_name}/"

            webbrowser.open(url)
            return jsonify({"message": f"Opening documentation for {package_name}"})

    def run(self, **kwargs):
        serve(self.app, host='127.0.0.1', port=5050, threads=10)

if __name__ == "__main__":
    backend = PipimBackend()
    backend.run()