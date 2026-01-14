import create_jwt
from fastapi import FastAPI, requests, exceptions
from dotenv import load_dotenv
from database import db_dependency, Base, engine
from models import UserCreate, UserResponseModel, UserModel, UserLogin

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post('/login', response_model=UserResponseModel)
def login(payload: UserLogin, db: db_dependency):
    auth_email = payload.email
    auth_password = payload.password
    user_record = db.query(UserModel).filter(UserModel.email == auth_email).first()
    if not user_record or user_record.password != auth_password:
        return exceptions.HTTPException(status_code=401, detail="Invalid credentials")
    else:
        token = create_jwt.create_access_token(data={"email": payload.email, "admin": True})
        return UserResponseModel(id=user_record.id, name=user_record.name, email=user_record.email, jwt_token=token)
    

@app.post('/register', response_model=UserResponseModel)
def register(payload: UserCreate, db: db_dependency):
    existing_user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if existing_user:
        return exceptions.HTTPException(status_code=400, detail="User already exists")
    
    token = create_jwt.create_access_token(data={"email": payload.email, "admin": True})
    new_user = UserModel(
        name=payload.name,
        email=payload.email,
        password=payload.password,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponseModel(name=new_user.name, email=new_user.email, jwt_token=token)

@app.post('/del_user/{email}')
def delete_user(email: str, db: db_dependency):
    user_record = db.query(UserModel).filter(UserModel.email == email).first()
    if not user_record:
        return exceptions.HTTPException(status_code=404, detail="User not found")
    
    db.delete(user_record)
    db.commit()
    return {"detail": "User deleted successfully"}

@app.get('/validate')
def validate_token(request: requests.Request):
    token = request.headers.get("Authorization")
    if not token:
        return exceptions.HTTPException(status_code=401, detail="Token missing")
    
    jwt = token.split(" ")[1]
    is_valid, error= create_jwt.verify_jwt_token(jwt)
    if not is_valid:
        return exceptions.HTTPException(status_code=401, detail=error)
    
    return {"detail": "Token is valid"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)