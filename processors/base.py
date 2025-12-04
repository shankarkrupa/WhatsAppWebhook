"""
Base message processor interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class MessageProcessor(ABC):
    """
    Base class for message processors.
    All custom processors should inherit from this class and implement the process method.
    """
    
    @abstractmethod
    def process(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a WhatsApp message.
        
        Args:
            message_data: Dictionary containing the message data with keys:
                - wa_id: WhatsApp ID of the sender
                - sender_name: Name of the sender
                - message_id: Unique message ID
                - message_type: Type of message (text, image, etc.)
                - message_body: Body/content of the message
                - media_id: Media ID if applicable
                - mime_type: MIME type if applicable
                - filename: Filename if applicable
                - links: Extracted links from the message
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        pass
    
    @property
    def name(self) -> str:
        """
        Returns the name of the processor for logging purposes.
        Default implementation returns the class name.
        """
        return self.__class__.__name__
