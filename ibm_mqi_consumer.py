import pymqi
import config
import logging

# Set up logging for error messages
logging.basicConfig(level=logging.INFO)
# Define the connection details
queue_manager = 'QM1'  # Name of your Queue Manager
queue_name = config.QUEUE_NAME   # Name of the queue from which you want to get the message
host = config.HOST  # IP or hostname of the MQ server
port = config.PORT  # Port number (default is usually 1414)
channel = config.CHANNEL  # Channel name (ensure it's configured correctly in MQ)
output_file = config.OUTPUT_FILE_IBM_MQ
# Create the connection to the Queue Manager
conn_info = f'{host}({port})'
qmgr = pymqi.connect(queue_manager, channel, conn_info)

# Open the queue in 'get' mode
queue = pymqi.Queue(qmgr, queue_name)
message_len = queue.get_length()  # Get the length of the message
# Retrieve the message from the queue (non-blocking)
try:
    message = queue.get()  # This will retrieve the message from the queue
    print(f"Received message: {message}")
    with open(output_file, 'a') as f:
        f.write(f"{message}\n")  # Append the message to the file
     
    logging.info(f"Message saved to {output_file}")
except pymqi.MQMIError as e:
    print(f"Error while getting message: {e}")
    logging.error(f"Error while consuming messages: {e}")
# while True:
#     try:
#         message = queue.get(wait=5)  # wait for 5 seconds for a new message
#         print(f"Received message: {message}")
#     except pymqi.MQMIError:
#         print("No more messages.")
#         break

# Close the queue and disconnect from the queue manager
queue.close()
qmgr.disconnect()
