"""
Example custom processor for home automation integration.

This example demonstrates how to create a custom message processor
that can be plugged into the WhatsApp webhook system.
"""
from typing import Dict, Any
from processors.base import MessageProcessor


class HomeAutomationProcessor(MessageProcessor):
    """
    Example processor for home automation integration.
    
    This processor demonstrates how to create a custom processor that:
    - Detects specific commands in WhatsApp messages
    - Triggers home automation actions
    - Can be easily integrated with home automation systems
    """
    
    def __init__(self, home_automation_api_url: str = None):
        """
        Initialize the home automation processor.
        
        Args:
            home_automation_api_url: URL of your home automation API endpoint
        """
        self.api_url = home_automation_api_url
        self.commands = {
            "lights on": self._lights_on,
            "lights off": self._lights_off,
            "temperature": self._get_temperature,
            "status": self._get_status,
        }
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a message and check for home automation commands.
        
        Args:
            message_data: Dictionary containing the message data
        
        Returns:
            bool: True if processing was successful, False otherwise
        """
        print(f"[{self.name}] Processing message: {message_data.get('message_id')}")
        
        message_body = message_data.get("message_body", "").lower().strip()
        
        # Check if message contains a recognized command
        for command, handler in self.commands.items():
            if command in message_body:
                print(f"[{self.name}] Detected command: {command}")
                try:
                    handler(message_data)
                    return True
                except Exception as e:
                    print(f"[{self.name}] Error executing command: {str(e)}")
                    return False
        
        # No command detected, skip
        print(f"[{self.name}] No home automation command detected")
        return True
    
    def _lights_on(self, message_data: Dict[str, Any]):
        """Handle 'lights on' command"""
        print(f"[{self.name}] Executing: Turn lights ON")
        # Here you would call your home automation API
        # Example:
        # requests.post(f"{self.api_url}/lights/on")
        
    def _lights_off(self, message_data: Dict[str, Any]):
        """Handle 'lights off' command"""
        print(f"[{self.name}] Executing: Turn lights OFF")
        # Here you would call your home automation API
        # Example:
        # requests.post(f"{self.api_url}/lights/off")
        
    def _get_temperature(self, message_data: Dict[str, Any]):
        """Handle 'temperature' command"""
        print(f"[{self.name}] Executing: Get temperature")
        # Here you would query your home automation API
        # Example:
        # response = requests.get(f"{self.api_url}/sensors/temperature")
        # temp = response.json()["temperature"]
        # You could then use the EmailNotificationProcessor or another
        # method to send the response back to the user
        
    def _get_status(self, message_data: Dict[str, Any]):
        """Handle 'status' command"""
        print(f"[{self.name}] Executing: Get home status")
        # Here you would query your home automation API
        # Example:
        # response = requests.get(f"{self.api_url}/status")
        # status = response.json()


# Example usage:
if __name__ == "__main__":
    from subscriber import RedisSubscriber
    from processors.email_processor import EmailNotificationProcessor
    
    # Create custom processors
    home_automation = HomeAutomationProcessor(
        home_automation_api_url="http://localhost:8080/api"
    )
    email_processor = EmailNotificationProcessor()
    
    # Initialize subscriber with custom processors
    subscriber = RedisSubscriber(processors=[
        home_automation,
        email_processor
    ])
    
    # Start listening for messages
    subscriber.start_listening()
