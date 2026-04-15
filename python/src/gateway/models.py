from pydantic import BaseModel


class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserRequestForCompanyInfo(BaseModel):
    company_name: str
