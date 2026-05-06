import json
import os
import pika
from database import SessionLocal
from database_helper.company_database_helper import write_company_to_database
from logger import logger


def _callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        logger.info(f"Received company acts for: {payload.get('company_name')}")
        db = SessionLocal()
        try:
            write_company_to_database(payload, db)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Successfully wrote company acts for: {payload.get('company_name')}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to write company acts to DB: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to parse company acts message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)


def start_company_acts_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
    channel = connection.channel()
    channel.basic_consume(
        queue=os.getenv("COMPANY_ACTS_QUEUE", "company_acts_queue"),
        on_message_callback=_callback,
    )
    logger.info("Waiting for company acts messages...")
    channel.start_consuming()
