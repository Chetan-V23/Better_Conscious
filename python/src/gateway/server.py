import os, json
from fastapi import FastAPI, Request, exceptions
from dotenv import load_dotenv

from database import db_dependency, Base, engine
from auth_svc.access import login
from auth import validate
from models import UserLoginRequest
import storage.util as util

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
def upload(request: Request, db: db_dependency):
    access, err = validate.token(request)
    if access["admin"] != True:
        raise exceptions.HTTPException(status_code=401, detail="Admin access required")
    if len(request.body["company_name"]) == 0 or request.body["company_name"] is None:
        raise exceptions.HTTPException(status_code=400, detail="Company name is required [company_name]")

    util.upload_company_data_to_rabbitmq(request.body["company_name"], db)

@app.get("/get_company_info")
def get_company_info(request: Request, db: db_dependency):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)