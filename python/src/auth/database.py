import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Annotated

PG_USER = os.getenv("POSTGRES_ADMIN_USER", "authuser")
PG_PASSWORD = os.getenv("POSTGRES_ADMIN_PASSWORD")
DATABASE_SERVER = os.getenv("DATABASE_SERVER")
#For testing
# DATABASE_SERVER = "localhost:5432/conscious_auth"
SQLALCHEMY_DATABASE_URL = f'postgresql://{PG_USER}:{PG_PASSWORD}:@{DATABASE_SERVER}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]