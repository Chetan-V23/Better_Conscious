import requests, os
from logger import logger

def forward_company_info_request(sms: str, email_id: str, jwt_token: str):
    company_info_svc = os.getenv("COMPANY_INFO_SVC_URL", "http://localhost:8085")
    logger.info("Calling company info service POST /company for email=%s", email_id)
    response = requests.post(
        f"{company_info_svc}/company",
        json={"sms": sms, "email_id": email_id},
        headers={"Authorization": jwt_token},
    )
    if response.status_code != 200:
        logger.error(
            "Company info service POST /company failed status=%s response=%s",
            response.status_code,
            response.text,
        )
        return None, (response.text, response.status_code)
    logger.info("Company info service POST /company succeeded for email=%s", email_id)
    return response.json(), None


def get_company_info_request(company_name: str):
    company_info_svc = os.getenv("COMPANY_INFO_SVC_URL", "http://localhost:8085")
    logger.info("Calling company info service GET /company for company_name=%s", company_name)
    response = requests.get(
        f"{company_info_svc}/company",
        params={"company_name": company_name},
    )
    if response.status_code != 200:
        logger.error(
            "Company info service GET /company failed status=%s response=%s",
            response.status_code,
            response.text,
        )
        return None, (response.text, response.status_code)
    logger.info("Company info service GET /company succeeded for company_name=%s", company_name)
    return response.json(), None
