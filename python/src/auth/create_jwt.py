from jose import jwt
import time
import os

ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: int = 3600):
    """
    Data - dict with username and admin [bool]
    """
    SECRET_KEY = os.getenv("SECRETJWTKEY")
    to_encode = data.copy()
    expire = int(time.time()) + expires_delta
    to_encode.update({"exp": expire})
    to_encode.update({"iat": int(time.time())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> tuple:
    SECRET_KEY = os.getenv("SECRETJWTKEY")
    print(token)
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.JWTClaimsError:
        return False, "Invalid claims in token"
    except jwt.JWTError as e:
        return False, f"Invalid token: {str(e)}"
    except Exception as e:
        return False, f"Error decoding token: {str(e)}"
    return True, ""