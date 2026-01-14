from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    name: str 
    email: str
    password: str

class UserResponseModel(BaseModel):
    name: str
    email: str
    jwt_token: str | None = None


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)