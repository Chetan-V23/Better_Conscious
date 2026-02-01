from dotenv import load_dotenv
import pika
import os
import sys

load_dotenv()


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq"
        )
    )
    channel = connection.channel()

    def callback(ch, method, properties, body):
        #RUN LLM
        
        err = None
        if err:
            ch.basic_nack(delivery_tag = method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag = method.delivery_tag)
        pass

    channel.basic_consume(
        queue=os.getenv("COMPANY_NAME_QUEUE"), on_message_callback=callback
    )

    print("Waiting for messages...")
    channel.start_consuming()

if __name__== "__main__":
    
    try:
        main()
    except KeyboardInterrupt:
        print("Done")
        #Graceful shutdown
        try:
            sys.exit()
        except SystemExit:
            os._exit(0)