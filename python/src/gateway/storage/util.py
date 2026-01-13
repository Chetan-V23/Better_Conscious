import json
from database import db_dependency
from table_models.company_info import CompanyInfo

def upload_company_data_to_rabbitmq(company_name: str, db: db_dependency):
    company_name = CompanyInfo(company_name=company_name)
    db.add(company_name)
    db.commit()
    db.refresh(company_name)