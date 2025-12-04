#!/usr/bin/env python3
"""
Demo script showing how to use the pluggable message processor system
"""
from processors.base import MessageProcessor
from subscriber import RedisSubscriber
from processors.email_processor import EmailNotificationProcessor
from processors.logging_processor import LoggingProcessor
from typing import Dict, Any


# Example 1: Simple custom processor
class GreetingProcessor(MessageProcessor):
    """Responds to greetings in messages"""
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        message_body = message_data.get("message_body", "").lower()
        
        greetings = ["hello", "hi", "hey", "greetings"]
        if any(greeting in message_body for greeting in greetings):
            sender = message_data.get("sender_name", "Unknown")
            print(f"[{self.name}] Detected greeting from {sender}!")
            print(f"[{self.name}] Could respond with: 'Hello {sender}! How can I help you?'")
        
        return True


# Example 2: Command processor
class CommandProcessor(MessageProcessor):
    """Processes commands from messages"""
    
    def __init__(self):
        self.commands = {
            "help": self._help_command,
            "status": self._status_command,
            "info": self._info_command,
        }
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        message_body = message_data.get("message_body", "").lower().strip()
        
        for command, handler in self.commands.items():
            if command in message_body:
                handler(message_data)
                return True
        
        return True
    
    def _help_command(self, message_data):
        print(f"[{self.name}] Help command detected")
        print(f"[{self.name}] Available commands: help, status, info")
    
    def _status_command(self, message_data):
        print(f"[{self.name}] Status command detected")
        print(f"[{self.name}] System is running normally")
    
    def _info_command(self, message_data):
        print(f"[{self.name}] Info command detected")
        print(f"[{self.name}] WhatsApp Webhook System v1.0")


def demo_default_processors():
    """Demo using default processors"""
    print("\n" + "="*60)
    print("DEMO 1: Default Processors (Email + Logging)")
    print("="*60)
    
    # Create subscriber with default processors
    subscriber = RedisSubscriber()
    
    # Simulate a message with links
    test_message = {
        "wa_id": "1234567890",
        "sender_name": "John Doe",
        "message_id": "msg_001",
        "message_type": "text",
        "message_body": "Check out this link: https://example.com",
        "media_id": None,
        "mime_type": None,
        "filename": None,
        "links": "https://example.com"
    }
    
    print("\nProcessing test message:")
    subscriber.process_message(test_message)


def demo_custom_processors():
    """Demo using custom processors"""
    print("\n" + "="*60)
    print("DEMO 2: Custom Processors (Greeting + Command)")
    print("="*60)
    
    # Create custom processors
    greeting_processor = GreetingProcessor()
    command_processor = CommandProcessor()
    
    # Create subscriber with custom processors
    subscriber = RedisSubscriber(processors=[
        greeting_processor,
        command_processor
    ])
    
    # Test messages
    test_messages = [
        {
            "wa_id": "1234567890",
            "sender_name": "Alice",
            "message_id": "msg_002",
            "message_type": "text",
            "message_body": "Hello! How are you?",
            "links": ""
        },
        {
            "wa_id": "0987654321",
            "sender_name": "Bob",
            "message_id": "msg_003",
            "message_type": "text",
            "message_body": "status",
            "links": ""
        },
        {
            "wa_id": "1111111111",
            "sender_name": "Charlie",
            "message_id": "msg_004",
            "message_type": "text",
            "message_body": "Can you help me?",
            "links": ""
        }
    ]
    
    for msg in test_messages:
        print(f"\nProcessing message from {msg['sender_name']}:")
        subscriber.process_message(msg)


def demo_mixed_processors():
    """Demo using a mix of default and custom processors"""
    print("\n" + "="*60)
    print("DEMO 3: Mixed Processors (All Together)")
    print("="*60)
    
    # Create all processors
    email_processor = EmailNotificationProcessor()
    logging_processor = LoggingProcessor()
    greeting_processor = GreetingProcessor()
    command_processor = CommandProcessor()
    
    # Create subscriber with all processors
    subscriber = RedisSubscriber(processors=[
        email_processor,
        logging_processor,
        greeting_processor,
        command_processor
    ])
    
    # Test message with multiple features
    test_message = {
        "wa_id": "2222222222",
        "sender_name": "Eve",
        "message_id": "msg_005",
        "message_type": "text",
        "message_body": "Hi! Please check https://github.com and send me the status",
        "links": "https://github.com"
    }
    
    print("\nProcessing complex message:")
    subscriber.process_message(test_message)


def demo_dynamic_processor_management():
    """Demo adding and removing processors dynamically"""
    print("\n" + "="*60)
    print("DEMO 4: Dynamic Processor Management")
    print("="*60)
    
    # Start with no processors
    subscriber = RedisSubscriber(processors=[])
    print(f"\nInitial processors: {[p.name for p in subscriber.processors]}")
    
    # Add processors one by one
    print("\nAdding LoggingProcessor...")
    subscriber.add_processor(LoggingProcessor())
    
    print("\nAdding GreetingProcessor...")
    subscriber.add_processor(GreetingProcessor())
    
    print(f"\nCurrent processors: {[p.name for p in subscriber.processors]}")
    
    # Process a message
    test_message = {
        "wa_id": "3333333333",
        "sender_name": "Frank",
        "message_id": "msg_006",
        "message_type": "text",
        "message_body": "Hello there!",
        "links": ""
    }
    
    print("\nProcessing message with all processors:")
    subscriber.process_message(test_message)
    
    # Remove a processor
    print("\nRemoving LoggingProcessor...")
    subscriber.remove_processor("LoggingProcessor")
    
    print(f"\nCurrent processors: {[p.name for p in subscriber.processors]}")
    
    print("\nProcessing message again with remaining processors:")
    subscriber.process_message(test_message)


if __name__ == "__main__":
    print("\n")
    print("="*60)
    print("WhatsApp Webhook - Message Processor System Demo")
    print("="*60)
    print("\nThis demo shows how to use the pluggable message processor system")
    print("for extending WhatsApp webhook functionality.")
    
    try:
        demo_default_processors()
        demo_custom_processors()
        demo_mixed_processors()
        demo_dynamic_processor_management()
        
        print("\n" + "="*60)
        print("Demo Complete!")
        print("="*60)
        print("\nKey Takeaways:")
        print("1. Multiple processors can be registered and executed for each message")
        print("2. Processors can be default (built-in) or custom")
        print("3. Easy to create custom processors by inheriting MessageProcessor")
        print("4. Processors can be added/removed dynamically")
        print("5. Perfect for home automation, command processing, and custom workflows")
        print("\nSee PROCESSORS.md for detailed documentation!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
