Here's the converted RabbitMQ code:

```python
import pika
import json
import config
import logging
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue_name = config.QUEUE_NAME
        self.output_file = config.OUTPUT_FILE_RABBITMQ

    @contextmanager
    def connect(self):
        try:
            credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                virtual_host=config.RABBITMQ_VHOST,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            yield
        finally:
            if self.channel:
                self.channel.close()
            if self.connection:
                self.connection.close()

    def consume_message(self):
        with self.connect():
            method_frame, properties, body = self.channel.basic_get(self.queue_name)
            if method_frame:
                message = body.decode('utf-8')
                print(f"Received message: {message}")
                with open(self.output_file, 'a') as f:
                    f.write(f"{message}\n")
                logging.info(f"Message saved to {self.output_file}")
                self.channel.basic_ack(method_frame.delivery_tag)
            else:
                print("No message available.")

    def consume_messages_continuously(self):
        def callback(ch, method, properties, body):
            message = body.decode('utf-8')
            print(f"Received message: {message}")
            with open(self.output_file, 'a') as f:
                f.write(f"{message}\n")
            logging.info(f"Message saved to {self.output_file}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        with self.connect():
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
            try:
                print("Waiting for messages. To exit press CTRL+C")
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.channel.stop_consuming()

if __name__ == "__main__":
    client = RabbitMQClient()
    try:
        # For single message consumption
        client.consume_message()
        
        # For continuous message consumption
        # client.consume_messages_continuously()
    except pika.exceptions.AMQPError as e:
        logging.error(f"Error while consuming messages: {e}")
```