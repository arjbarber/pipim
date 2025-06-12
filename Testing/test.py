import requests
import json

BACKEND_URL = "http://127.0.0.1:5050/"

print(json.dumps(requests.post(BACKEND_URL + "get_module_info", json={"package_name": "flask"}).json(), indent=2))