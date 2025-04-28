import requests

BACKEND_URL = "http://127.0.0.1:5000/"

requests.post(BACKEND_URL + "get_module_info", json={"package_name": "bs4"})