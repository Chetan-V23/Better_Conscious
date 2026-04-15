from pydantic import BaseModel

class CompanyPayload(BaseModel):
    sms: str