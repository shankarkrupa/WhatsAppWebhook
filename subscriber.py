import redis
import json
from config import config
import time
from typing import List
from processors.base import MessageProcessor
from processors.email_processor import EmailNotificationProcessor
from processors.logging_processor import LoggingProcessor


class EmailSender:
    """Email sender utility - DEPRECATED: Use EmailNotificationProcessor instead"""
    
    @staticmethod
    def send_email(subject: str, body: str, to_email: str = None) -> bool:
        """
        Send an email with the given subject and body.
        
        DEPRECATED: This method is maintained for backward compatibility.
        Use EmailNotificationProcessor for new implementations.
        """
        from processors.email_processor import EmailNotificationProcessor
        processor = EmailNotificationProcessor()
        # Create a minimal message data structure for compatibility
        message_data = {
            "message_id": "legacy",
            "sender_name": "Unknown",
            "wa_id": "N/A",
            "message_type": "N/A",
            "message_body": body,
            "links": "legacy"
        }
        return processor._send_email(subject, body, to_email)


class RedisSubscriber:
    """
    Redis subscriber for WhatsApp messages with support for multiple message processors.
    
    This class allows plugging in multiple processor classes that will be executed
    for each message received from the Redis channel.
    """
    
    def __init__(self, processors: List[MessageProcessor] = None):
        """
        Initialize the RedisSubscriber with optional list of processors.
        
        Args:
            processors: List of MessageProcessor instances to process messages.
                       If None, default processors (EmailNotificationProcessor, LoggingProcessor) are used.
        """
        self.redis_client = None
        self.pubsub = None
        
        # Initialize processors
        if processors is None:
            # Default processors
            self.processors = [
                EmailNotificationProcessor(),
                LoggingProcessor()
            ]
        else:
            self.processors = processors
        
        print(f"Initialized with {len(self.processors)} processor(s):")
        for processor in self.processors:
            print(f"  - {processor.name}")
        
        self._connect()
    
    def add_processor(self, processor: MessageProcessor):
        """
        Add a new processor to the list of processors.
        
        Args:
            processor: A MessageProcessor instance to add
        """
        self.processors.append(processor)
        print(f"Added processor: {processor.name}")
    
    def remove_processor(self, processor_name: str) -> bool:
        """
        Remove a processor by name.
        
        Args:
            processor_name: Name of the processor to remove
        
        Returns:
            bool: True if processor was removed, False if not found
        """
        for i, processor in enumerate(self.processors):
            if processor.name == processor_name:
                self.processors.pop(i)
                print(f"Removed processor: {processor_name}")
                return True
        print(f"Processor not found: {processor_name}")
        return False
    
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
            
            # Subscribe to channel
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(config.REDIS_CHANNEL)
            print(f"Subscribed to Redis channel: {config.REDIS_CHANNEL}")
        except Exception as e:
            print(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
            self.pubsub = None
    
    def process_message(self, message_data: dict):
        """
        Process a WhatsApp message from Redis using all registered processors.
        
        Args:
            message_data: Dictionary containing the message data
        """
        print(f"Processing message: {message_data.get('message_id')}")
        
        # Execute all processors
        for processor in self.processors:
            try:
                success = processor.process(message_data)
                if not success:
                    print(f"[{processor.name}] Processing returned failure")
            except Exception as e:
                print(f"[{processor.name}] Error during processing: {str(e)}")
    
    def start_listening(self):
        """Start listening for messages on Redis channel"""
        if not self.pubsub:
            print("Redis pubsub not initialized. Cannot start listening.")
            return
        
        print("Starting to listen for messages...")
        try:
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    try:
                        message_data = json.loads(message['data'])
                        self.process_message(message_data)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding message: {str(e)}")
                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
        except KeyboardInterrupt:
            print("\nStopping subscriber...")
            self.pubsub.unsubscribe(config.REDIS_CHANNEL)
            self.redis_client.close()
        except Exception as e:
            print(f"Error in subscriber: {str(e)}")
            time.sleep(5)  # Wait before reconnecting
            self._connect()
            self.start_listening()


if __name__ == "__main__":
    subscriber = RedisSubscriber()
    subscriber.start_listening()
