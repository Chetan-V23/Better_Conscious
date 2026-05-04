from pydantic import BaseModel

class CompanyPayload(BaseModel):
    sms: str
    email_id: str