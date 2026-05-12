import json
import os
import pika
from database import SessionLocal
from database_helper.company_database_helper import write_company_to_database
from redis_helper.redis_client import redis_client, RESULT_KEY_PREFIX, RESULT_TTL_SECONDS
from logger import logger


def _callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        company_name = payload.get("company_name")
        logger.info(f"Received company acts for: {company_name}")
        db = SessionLocal()

        try:
            write_company_to_database(payload, db)
            redis_client.setex(
                f"{RESULT_KEY_PREFIX}{company_name}",
                RESULT_TTL_SECONDS,
                json.dumps(payload),
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Successfully wrote company acts for: {company_name}")
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
    connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", heartbeat=600, blocked_connection_timeout=300))
    channel = connection.channel()
    channel.basic_consume(
        queue=os.getenv("COMPANY_ACTS_QUEUE", "company_acts"),
        on_message_callback=_callback,
    )
    logger.info("Waiting for company acts messages...")
    channel.start_consuming()
