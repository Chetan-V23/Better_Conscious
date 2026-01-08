import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("No credentials provided",401)
    basic_auth = (auth.email, auth.password)
    auth_server = os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
    response = requests.post(f"{auth_server}/login", auth=basic_auth)
    if response.status_code != 200:
        return None, (response.json().get("detail","Login failed"), response.status_code)
    token = response.json().get("jwt_token")
    return token, None

def validate_token(token):
    auth_server = os.getenv("AUTH_SERVER_URL", "http://localhost:8000")
    response = requests.get(f"{auth_server}/validate", headers={"Authorization": f"{token}"})
    if response.status_code != 200:
        return None, (response.txt, response.status_code)
    
    return response.txt, None