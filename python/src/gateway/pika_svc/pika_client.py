import pika

class PikaClient:
    def __init__(self, host='localhost', port=5672):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port))
        self.channel = self.connection.channel()

    def publish_message(self, queue_name, message):
        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,
            ))
        print(f" [x] Sent '{message}' to queue '{queue_name}'")

    def close_connection(self):
        self.connection.close()