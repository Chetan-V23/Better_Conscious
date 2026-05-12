from fastapi import FastAPI, Request, exceptions
from dotenv import load_dotenv

from auth_svc.access import login as auth_login
from company_svc.call_service import forward_company_info_request, get_company_info_request
from auth.validate import token
from models import UserLoginRequest, UserRequestForCompanyInfo
import os
from logger import logger

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
    logger.info("/login request received for email=%s", payload.email)
    token, err = auth_login(payload)

    if not err:
        logger.info("/login successful for email=%s", payload.email)
        return token
    else:
        logger.warning("/login failed for email=%s error=%s", payload.email, err)
        return err

@app.post("/company_acts")
def upload(request: Request, payload: UserRequestForCompanyInfo):
    logger.info("/company_acts request received")

    jwt_token, err = token(request)
    if err:
        logger.warning("/company_acts token validation failed error=%s", err)
        return exceptions.HTTPException(status_code=err[1], detail=err[0])
    if jwt_token["admin"] != True:
        logger.warning("/company_acts unauthorized non-admin user email=%s", jwt_token.get("email"))
        raise exceptions.HTTPException(status_code=401, detail="Admin access required")
    if not payload.sms:
        logger.warning("/company_acts missing sms payload for email=%s", jwt_token.get("email"))
        raise exceptions.HTTPException(status_code=400, detail="SMS is required [sms]")

    logger.info("/company_acts forwarding request for email=%s", jwt_token.get("email"))
    result, err = forward_company_info_request(payload.sms, jwt_token["email"], request.headers["Authorization"])
    if err:
        logger.error("/company_acts downstream error status=%s detail=%s", err[1], err[0])
        raise exceptions.HTTPException(status_code=err[1], detail=err[0])
    logger.info("/company_acts request completed for email=%s", jwt_token.get("email"))
    return result

@app.get("/get_company_info")
def get_company_info(company_name: str):
    logger.info("/get_company_info request received company_name=%s", company_name)
    result, err = get_company_info_request(company_name)
    if err:
        logger.error("/get_company_info downstream error status=%s detail=%s", err[1], err[0])
        raise exceptions.HTTPException(status_code=err[1], detail=err[0])
    logger.info("/get_company_info request completed company_name=%s", company_name)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
