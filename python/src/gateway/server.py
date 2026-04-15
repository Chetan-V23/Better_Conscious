from fastapi import FastAPI, Request, exceptions
from dotenv import load_dotenv

from auth_svc.access import login as auth_login
from company_svc.call_service import forward_company_info_request
from auth.validate import token
from models import UserLoginRequest, UserRequestForCompanyInfo
import os


DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

if DEBUG_MODE:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Debugger listening on port 5678..")
    debugpy.wait_for_client()

load_dotenv()

app = FastAPI()

@app.post("/login")
def login(payload: UserLoginRequest):
    token, err = auth_login(payload)

    if not err:
        return token
    else:
        return err
    
@app.get("/company_acts")
def upload(request: Request, payload: UserRequestForCompanyInfo):

    access, err = token(request)
    if err:
        return exceptions.HTTPException(status_code = err[1], detail=err[0])
    if access["admin"] != True:
        raise exceptions.HTTPException(status_code=401, detail="Admin access required")
    if len(payload.company_name) == 0 or payload.company_name is None:
        raise exceptions.HTTPException(status_code=400, detail="Company name is required [company_name]")

    forward_company_info_request(payload.company_name,access)

@app.get("/get_company_info")
def get_company_info(request: Request, db: db_dependency):
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)