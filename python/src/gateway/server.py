import os, json
from fastapi import FastAPI, requests, exceptions
from dotenv import load_dotenv

from database import db_dependency, Base, engine
from auth_svc.access import login
from models import UserLoginRequest

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/login")
def login(payload: UserLoginRequest):
    token, err = login(payload)

    if not err:
        return token
    else:
        return err
    
@app.get("/upload")
def upload(db: db_dependency):
    return {"message": "Upload endpoint"}