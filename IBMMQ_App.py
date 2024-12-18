import os
import sys
import time
import json
import signal
import configparser
from datetime import datetime
from typing import Callable, Dict, Any
from dataclasses import dataclass
import pymqi


@dataclass
class MQConfig:
    queue_manager: str
    channel: str
    host: str
    port: int
    queue_name: str
    username: str
    password: str
    batch_size: int
    wait_timeout: int
    max_retries: int
    retry_delay: int
    cipher_spec: str

    @classmethod
    def load_config(cls, config_path='config.ini'):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        config = configparser.ConfigParser()
        config.read(config_path)

        return cls(
            queue_manager=config.get('ibmmq', 'queue_manager'),
            channel=config.get('ibmmq', 'channel'),
            host=config.get('ibmmq', 'host'),
            port=config.getint('ibmmq', 'port'),
            queue_name=config.get('ibmmq', 'queue_name'),
            username=config.get('ibmmq', 'username'),
            password=config.get('ibmmq', 'password'),
            batch_size=config.getint('application', 'batch_size'),
            wait_timeout=config.getint('application', 'wait_timeout'),
            max_retries=config.getint('application', 'max_retries'),
            retry_delay=config.getint('application', 'retry_delay'),
            cipher_spec=config.get('application', 'cipher_spec')
        )


class MQConnection:
    def __init__(self, config: MQConfig):
        self.config = config
        self.queue_manager = None
        self.queue = None

    def connect(self):
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
            except pymqi.MQMIError:
                if attempt == self.config.max_retries - 1:
                    raise
                time.sleep(self.config.retry_delay)

    def close(self):
        try:
            if self.queue:
                self.queue.close()
            if self.queue_manager:
                self.queue_manager.disconnect()
        except Exception:
            pass


class MessageProducer(MQConnection):
    def send_message(self, message: Dict[str, Any]):
        try:
            if not self.queue_manager:
                self.connect()

            message_text = json.dumps(message)
            md = pymqi.MD()
            md.Format = pymqi.CMQC.MQFMT_STRING
            md.Persistence = pymqi.CMQC.MQPER_PERSISTENT

            self.queue.put(message_text.encode(), md)
            print(f"Message sent successfully: {message}")
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            raise


class MessageSubscriber(MQConnection):
    def start_listening(self, callback: Callable[[dict], None]):
        try:
            if not self.queue_manager:
                self.connect()

            md = pymqi.MD()
            gmo = pymqi.GMO()
            gmo.Options = pymqi.CMQC.MQGMO_WAIT | pymqi.CMQC.MQGMO_FAIL_IF_QUIESCING
            gmo.WaitInterval = self.config.wait_timeout

            while True:
                messages = []
                for _ in range(self.config.batch_size):
                    try:
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


def publish_message():
    try:
        config = MQConfig.load_config()
        producer = MessageProducer(config)
        message_content = sys.argv[1] if len(sys.argv) > 1 else "Default message"
        message = {
            "id": int(time.time()),
            "content": message_content,
            "timestamp": datetime.now().isoformat()
        }

        producer.send_message(message)
        print("Message published successfully!")
    except Exception as e:
        print(f"Error publishing message: {str(e)}")
        sys.exit(1)
    finally:
        if 'producer' in locals():
            producer.close()


def receive_messages():
    class MessageReceiver:
        def __init__(self):
            self.running = True
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)

        def signal_handler(self, signum, frame):
            print("\nReceived signal to stop...")
            self.running = False
            sys.exit(0)

        def process_message(self, message):
            print("\nReceived message:")
            print(f"ID: {message.get('id')}")
            print(f"Content: {message.get('content')}")
            print(f"Timestamp: {message.get('timestamp')}")
            print("-" * 50)

    try:
        config = MQConfig.load_config()
        receiver = MessageReceiver()
        subscriber = MessageSubscriber(config)

        print("Starting message receiver...")
        print("Press Ctrl+C to stop")
        subscriber.start_listening(receiver.process_message)
    except KeyboardInterrupt:
        print("\nStopping message receiver...")
    except Exception as e:
        print(f"Error in message receiver: {str(e)}")
        sys.exit(1)
    finally:
        if 'subscriber' in locals():
            subscriber.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "receive":
        receive_messages()
    else:
        publish_message()
