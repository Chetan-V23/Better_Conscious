from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from database import Base

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    jwt_token: str | None = None

class User(BaseModel):
    name: str
    email: str
    jwt_token: str | None = None


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    jwt_token = Column(String, nullable=True)