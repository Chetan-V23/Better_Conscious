import pika
import json
from logger import logger

def send_company_to_process_through_rabbit_mq(company_name: str,username: str, rmq_channel: pika.adapters.blocking_connection.BlockingChannel):
    """
    send company name to rabbit mq to process
    """
    logger.info(f"Sending company name: {company_name} to rabbit mq to process, with username: {username}")
    message = {
        "company_name": company_name,
        "company_acts": None,
        "username": username,
        }
        
    rmq_channel.basic_publish(
        exchange='',
        routing_key='company_data_queue',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
        ))
    