import json
import requests
import pika
import config

payload = {
    "name": "rabbit_mq_name",
    "message": "successfully message pushed to rabbit mq"
}
# Connection parameters (adjust to your RabbitMQ settings)
rabbitmq_host = config.RABBIT_MQ_HOST  # RabbitMQ server hostname or IP
queue_name = config.RABBIT_MQ_QUEUE_NAME      # Queue name where the message will be sent

# Connect to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

# Declare a queue (if it doesn't already exist)
channel.queue_declare(queue=queue_name)

# # The payload to send
# payload = 'Hello, RabbitMQ! This is a test message.'

# Push the payload to the queue
channel.basic_publish(exchange='',
                      routing_key=queue_name,  # The queue name
                      body=payload)

print(f"Message '{payload}' sent to queue '{queue_name}'.")

# Close the connection
connection.close()
