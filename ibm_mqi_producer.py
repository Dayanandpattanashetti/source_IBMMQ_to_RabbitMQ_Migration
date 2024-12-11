import requests
import pymqi
import json
import config


payload = {
    "name": "ibm_mq_name",
    "message": "successfully message pushed to ibm mq"
}
# Step 2: Push the received payload to IBM MQ
queue_manager = config.QUEUE_MANAGER  # Name of your Queue Manager
queue_name = config.QUEUE_NAME  # Name of the queue you want to put the message on
host = config.HOST  # IP or hostname of the MQ server
port = config.PORT  # Port number (default is usually 1414)
# Channel name (ensure it's configured correctly in MQ)
channel = config.CHANNEL

# Create the connection to the Queue Manager
conn_info = f'{host}({port})'
qmgr = pymqi.connect(queue_manager, channel, conn_info)

# Open the queue in 'put' mode
queue = pymqi.Queue(qmgr, queue_name)

# Put the message on the queue
queue.put(payload)

print(f"Message '{payload}' sent to queue '{queue_name}'.")

# Close the queue and disconnect
queue.close()
qmgr.disconnect()
