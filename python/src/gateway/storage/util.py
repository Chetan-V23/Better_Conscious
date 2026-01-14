import json
from database import db_dependency
from table_models.company_info import CompanyInfo
import pika

def upload_company_data_to_rabbitmq(company_name: str,access_data: dict, db: db_dependency, rmq_channel):
    try:
        company_name = CompanyInfo(company_name=company_name)
        db.add(company_name)
        db.commit()
        db.refresh(company_name)
    except Exception as e:
        return str(e), 500
    
    message = {
        "company_name": company_name.company_name,
        "company_acts": None,
        "username": access_data["username"],
    }
    try:
        rmq_channel.basic_publish(
            exchange='',
            routing_key='company_data_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
            ))
    except Exception as e:
        db.delete(company_name)
        db.commit()
        return str(e), 500
