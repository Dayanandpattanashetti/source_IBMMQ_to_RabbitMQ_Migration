# IBM MQ config
URL = 'https://api.example.com/data' # URL for reading payload from request
QUEUE_MANAGER = 'QM1'  # Name of your Queue Manager
QUEUE_NAME = 'MYQUEUE'  # Name of the queue you want to put the message on
HOST = 'your-mq-host'  # IP or hostname of the MQ server
PORT = '1414'  # Port number (default is usually 1414)
CHANNEL = 'MYCHANNEL'  # Channel name (ensure it's configured correctly in MQ)
OUTPUT_FILE_IBM_MQ = 'received_messages_ibm_mq.txt'

# Rabbit MQ config
URL_FOR_RABBITMQ = 'https://api.example.com/data' # URL for reading payload from request
RABBIT_MQ_HOST = 'rabit-mq-host'
RABBIT_MQ_QUEUE_NAME='queue_name'
OUTPUT_FILE_RABBIT_MQ = 'received_messages_rabbit_mq.txt'