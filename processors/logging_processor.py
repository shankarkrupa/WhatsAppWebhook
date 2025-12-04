"""
Logging processor - simple example processor for demonstration
"""
from typing import Dict, Any
from processors.base import MessageProcessor


class LoggingProcessor(MessageProcessor):
    """
    Simple processor that logs message details to console.
    This is an example processor to demonstrate the extensibility of the system.
    """
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        """
        Log message details to console.
        
        Args:
            message_data: Dictionary containing the message data
        
        Returns:
            bool: Always returns True as logging can't really fail
        """
        print(f"[{self.name}] Logging message details:")
        print(f"  - Message ID: {message_data.get('message_id', 'N/A')}")
        print(f"  - From: {message_data.get('sender_name', 'Unknown')} ({message_data.get('wa_id', 'N/A')})")
        print(f"  - Type: {message_data.get('message_type', 'N/A')}")
        print(f"  - Body: {message_data.get('message_body', 'N/A')[:50]}...")  # First 50 chars
        print(f"  - Links: {message_data.get('links', 'None')}")
        
        return True
