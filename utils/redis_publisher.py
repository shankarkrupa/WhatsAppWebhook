import redis
import json
from typing import Optional
from config import config

class RedisPublisher:
    """Redis publisher for WhatsApp messages"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis server"""
        try:
            self.redis_client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                db=config.REDIS_DB,
                password=config.REDIS_PASSWORD,
                decode_responses=True
            )
            # Test the connection
            self.redis_client.ping()
            print(f"Connected to Redis at {config.REDIS_HOST}:{config.REDIS_PORT}")
        except Exception as e:
            print(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
    
    def publish_message(self, message_data: dict) -> bool:
        """Publish a message to Redis channel"""
        if not self.redis_client:
            print("Redis client not connected, skipping publish")
            return False
        
        try:
            message_json = json.dumps(message_data)
            self.redis_client.publish(config.REDIS_CHANNEL, message_json)
            print(f"Published message to Redis channel: {config.REDIS_CHANNEL}")
            return True
        except Exception as e:
            print(f"Error publishing to Redis: {str(e)}")
            return False

# Global Redis publisher instance
redis_publisher = RedisPublisher()
