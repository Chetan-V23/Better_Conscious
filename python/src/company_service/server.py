from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from database import db_dependency, Base, engine
from dotenv import load_dotenv
import pika
import os
from models.company_request_model import CompanyPayload
from company_processor.company_processor import process_company_by_sms
from logger import logger

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

if DEBUG_MODE:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    print("Debugger listening on port 5678..")
    debugpy.wait_for_client()

load_dotenv()

Base.metadata.create_all(bind=engine)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()


app = FastAPI()

@app.post("/company}}")
def company_info_sms(payload: CompanyPayload, db: db_dependency):

    logger.info(f"Received request to process company info for sms: {payload.sms}")
    process_company_by_sms(payload.sms)