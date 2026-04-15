import os, requests
import json

def login(request):
    email = request.email
    password = request.password
    auth_server = os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
    response = requests.post(f"{auth_server}/login", json={"email": email, "password": password})
    if response.status_code != 200:
        return None, (response.json().get("detail","Login failed"), response.status_code)
    token = response.json().get("jwt_token")
    return token, None

def validate_token(token):
    auth_server = os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
    response = requests.get(f"{auth_server}/validate", headers={"Authorization": f"{token}"})
    if response.status_code != 200:
        return None, (response.text, response.status_code)
    
    return response.json(), False