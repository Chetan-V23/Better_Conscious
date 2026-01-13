from pydantic import BaseModel


class UserLoginRequest(BaseModel):
    email: str
    password: str

class UserRequestForCompanyInfo(BaseModel):
    user_id: int
    company_name: str
    token: str