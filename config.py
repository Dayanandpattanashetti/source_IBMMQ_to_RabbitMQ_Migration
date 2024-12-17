# config.py
import os
import configparser
from dataclasses import dataclass

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
        """Load configuration from INI file"""
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
