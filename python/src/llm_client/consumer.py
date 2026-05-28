from dotenv import load_dotenv
import pika
import os
import sys
from llm_caller import start
from logger import logger

load_dotenv()

DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# if DEBUG_MODE:
#     import debugpy
#     debugpy.listen(("0.0.0.0", 5679))
#     print("Debugger listening on port 5679..")
#     debugpy.wait_for_client()

def main():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host="rabbitmq"
            )
        )
        logger.info("Successfully connected to RabbitMQ")
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
        raise
    
    channel = connection.channel()
    logger.info(f"Consuming from queue: {os.getenv('COMPANY_NAME_QUEUE')}")

    def callback(ch, method, properties, body):
        logger.info(f"Received message from queue: {body}")
        try:
            res = start(body, channel)
            if res:
                logger.error(f"Failed to process message, NACKing: {res}")
                ch.basic_nack(delivery_tag=method.delivery_tag)
            else:
                logger.info("Message processed successfully, ACKing")
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Exception in callback: {e}", exc_info=True)
            ch.basic_nack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.getenv("COMPANY_NAME_QUEUE"), on_message_callback=callback
    )

    logger.info("Waiting for messages...")
    channel.start_consuming()

if __name__== "__main__":
    logger.info("Starting LLM Client Consumer")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down gracefully")
        #Graceful shutdown
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        os._exit(1)