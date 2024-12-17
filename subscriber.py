# subscriber.py
import json
import time
from typing import Callable
import pymqi
from config import MQConfig

class MessageSubscriber:
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
    
    def start_listening(self, callback: Callable[[dict], None]):
        """Start listening for messages with the specified callback"""
        try:
            if not self.queue_manager:
                self.connect()
            
            # Create message descriptor and get message options
            md = pymqi.MD()
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
            gmo.WaitInterval = self.config.wait_timeout
            
            print(f"Started listening to queue: {self.config.queue_name}")
            
            while True:
                messages = []
                for _ in range(self.config.batch_size):
                    try:
                        # Reset message descriptor for each message
                        md = pymqi.MD()
                        message = self.queue.get(None, md, gmo)
                        if message:
                            message_text = message.decode()
                            messages.append(json.loads(message_text))
                    except pymqi.MQMIError as error:
                        if error.comp == pymqi.CMQC.MQCC_FAILED and error.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                            break
                        raise
                
                if messages:
                    for msg in messages:
                        try:
                            callback(msg)
                        except Exception as e:
                            print(f"Error processing message: {str(e)}")
                
        except Exception as e:
            print(f"Error in message listening: {str(e)}")
            raise
        finally:
            self.close()
    
    def close(self):
        """Close the connection"""
        try:
            if self.queue:
                self.queue.close()
            if self.queue_manager:
                self.queue_manager.disconnect()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
