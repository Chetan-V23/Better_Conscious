import re
from database import db_dependency
from database_helper.company_database_helper import get_company_if_exists_in_database, get_company_acts_from_database
from rabbit_mq_helper.company_queue import send_company_to_process_through_rabbit_mq
from fastapi.exceptions import HTTPException
from logger import logger

def process_company_by_sms(sms: str, db: db_dependency):
    """
    this method returns company name, id and acts, after retreiving from the database if it exists
    """
    company_name = _parse_company_name_from_sms(sms)
    try:
        company_info = get_company_if_exists_in_database(company_name=company_name, db=db)
        if company_info:
            company_acts = get_company_acts_from_database(company_info=company_info, db=db)
            if not company_acts:
                logger.error(f"Company: {company_name} exists in the database but has no acts, this should not happen")
                raise HTTPException(status_code=500, detail="Company not processed properly")
            return company_acts, 200
            
        else:
            send_company_to_process_through_rabbit_mq(company_name)
            #TODO: IMPLEMENT A REDIS LOCK TO WAIT FOR THE COMPANY TO BE PROCESSED AND THEN RETRIEVE THE DATA FROM THE DATABASE
    except Exception as e:
        logger.error(f"Error processing company info for sms: {sms}, error: {str(e)}")
        return str(e), 500

_SMS_MERCHANT_PATTERNS = [
    # ICICI "spent on DATE on MERCHANT." — e.g. "on 19-Feb-26 on IRON HILL U O L."
    re.compile(r'on\s+\d{1,2}-[A-Za-z]+-\d{2,4}\s+on\s+(.+?)\.', re.IGNORECASE),
    # ICICI UPI "debited; MERCHANT credited" — e.g. "; SARAVAN A credited."
    re.compile(r';\s*(.+?)\s+credited', re.IGNORECASE),
    # HDFC "At MERCHANT On DATE" — e.g. "At PYU*Swiggy Food On 2026-03-09"
    re.compile(r'\bAt\s+(.+?)\s+On\s+\d{4}-', re.IGNORECASE),
]

def _parse_company_name_from_sms(sms: str) -> str | None:
    for pattern in _SMS_MERCHANT_PATTERNS:
        match = pattern.search(sms)
        if match:
            return match.group(1).strip()
    return None
