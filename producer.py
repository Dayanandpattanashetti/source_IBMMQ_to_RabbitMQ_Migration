# producer.py
import json
import time
from typing import Dict, Any
import pymqi
from config import MQConfig

class MessageProducer:
    def __init__(self, config: MQConfig):
        self.config = config
        self.queue_manager = None
        self.queue = None
        
    def connect(self):
        """Establish connection to IBM MQ"""
        for attempt in range(self.config.max_retries):
            try:
                conn_info = {
                    'ChannelName': self.config.channel,
                    'ConnectionName': f'{self.config.host}({self.config.port})',
                    'SecurityExit': None,
                    'CipherSpec': self.config.cipher_spec
                }
                
                self.queue_manager = pymqi.QueueManager(None)
                self.queue_manager.connectWithOptions(
                    self.config.queue_manager,
                    user=self.config.username,
                    password=self.config.password,
                    opts=pymqi.CMQC.MQCNO_CLIENT_BINDING,
                    cd=conn_info
                )
                
                self.queue = pymqi.Queue(self.queue_manager, self.config.queue_name)
                return
                
            except pymqi.MQMIError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                print(f"Connection attempt {attempt + 1} failed. Retrying in {self.config.retry_delay} seconds...")
                time.sleep(self.config.retry_delay)
    
    def send_message(self, message: Dict[str, Any]):
        """Send a message to the queue"""
        try:
            if not self.queue_manager:
                self.connect()
                
            message_text = json.dumps(message)
            
            # Create message descriptor
            md = pymqi.MD()
            md.Format = pymqi.CMQC.MQFMT_STRING
            md.Persistence = pymqi.CMQC.MQPER_PERSISTENT
            
            # Put the message
            self.queue.put(message_text.encode(), md)
            print(f"Message sent successfully: {message}")
            
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            raise
    
    def close(self):
        """Close the connection"""
        try:
            if self.queue:
                self.queue.close()
            if self.queue_manager:
                self.queue_manager.disconnect()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
