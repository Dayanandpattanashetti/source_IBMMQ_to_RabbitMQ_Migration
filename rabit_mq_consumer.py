import pika
import config
import logging

# Set up logging for error messages
logging.basicConfig(level=logging.INFO)
# Define the connection details
rabbitmq_host = config.RABBIT_MQ_HOST  # RabbitMQ server hostname or IP
queue_name = config.RABBIT_MQ_QUEUE_NAME     # The name of the queue to consume messages from
output_file = config.OUTPUT_FILE_RABBIT_MQ
# Callback function to handle the incoming message
def callback(ch, method, properties, body):
    try:
        # Decode the message (assuming it's a byte string)
        message = body.decode()
        
        # Print the message to the console (optional)
        print(f"Received message: {message}")
        
        # Write the received message to a file
        with open(output_file, 'a') as f:
            f.write(f"{message}\n")  # Append each message to the file
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logging.info(f"Message saved to {output_file}")

    except Exception as e:
        logging.error(f"Error while processing message: {e}")
        # Optionally, you could nack the message if you want to requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# Establish a connection to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()
try:
    # Declare the queue (ensure it exists before consuming messages)
    channel.queue_declare(queue=queue_name)

    # Set up the consumer to consume messages from the queue
    channel.basic_consume(queue=queue_name,
                        on_message_callback=callback,
                        auto_ack=True)  # auto_ack=True will automatically acknowledge the message

    # Start consuming messages
    print(f"Waiting for messages from {queue_name}. To exit press CTRL+C")
    channel.start_consuming()
except Exception as e:
        logging.error(f"Error while consuming messages: {e}")
finally:
    # Ensure the channel and connection are properly closed
    if channel and channel.is_open:
        channel.close()
