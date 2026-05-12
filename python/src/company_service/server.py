from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from database import db_dependency, Base, engine
from dotenv import load_dotenv
import pika
import os
import threading
from models.company_request_model import CompanyPayload
from company_processor.company_processor import process_company_by_sms
from database_helper.company_database_helper import get_company_if_exists_in_database, get_company_acts_from_database
from rabbit_mq_helper.company_acts_consumer import start_company_acts_consumer
from logger import logger

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

if DEBUG_MODE:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Debugger listening on port 5678..")
    debugpy.wait_for_client()

load_dotenv()

Base.metadata.create_all(bind=engine)

threading.Thread(target=start_company_acts_consumer, daemon=True).start()


app = FastAPI()

@app.post("/company")
def company_info_sms(payload: CompanyPayload, db: db_dependency):
    logger.info(f"Received request to process company info for sms: {payload.sms}")
    result, status = process_company_by_sms(payload.sms, db, email_id=payload.email_id, channel=channel)
    if status != 200:
        raise HTTPException(status_code=status, detail=result)
    return result

@app.get("/company")
def get_company(company_name: str, db: db_dependency):
    logger.info(f"Received request to get company info for: {company_name}")
    company_info = get_company_if_exists_in_database(company_name=company_name, db=db)
    if not company_info:
        raise HTTPException(status_code=404, detail="Company not found")
    company_acts = get_company_acts_from_database(company_info=company_info, db=db)
    return {"company_name": company_info.company_name, "acts": [
        {"title": a.act_title, "severity": a.act_severity, "description": a.act_description}
        for a in company_acts
    ]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)
