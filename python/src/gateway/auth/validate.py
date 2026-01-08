import os, requests
from auth_svc.access import validate_token

def token(request):
    if not "Authorization" in request.headers:
        return None, ("No credentials provided",401)
    
    token = request.headers.get("Authorization").split(" ")[1]

    if not token:
        return None, ("No token provided",401)
    
    validate_token(token)