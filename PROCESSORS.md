# Message Processors Guide

## Overview

The WhatsApp Webhook system now supports pluggable message processors, allowing you to extend the functionality by adding custom processors that react to incoming messages. This is particularly useful for home automation developers who want to integrate WhatsApp messages with their automation systems.

## Architecture

The processor system uses a simple plugin architecture:

1. **MessageProcessor Base Class**: An abstract base class that defines the interface for all processors
2. **Concrete Processors**: Implementations of the base class that handle specific tasks
3. **RedisSubscriber**: Manages and executes all registered processors for each message

## Built-in Processors

### EmailNotificationProcessor
Sends email notifications for messages containing links.

```python
from processors.email_processor import EmailNotificationProcessor

processor = EmailNotificationProcessor()
```

### LoggingProcessor
Logs message details to the console for debugging and monitoring.

```python
from processors.logging_processor import LoggingProcessor

processor = LoggingProcessor()
```

## Creating Custom Processors

### Step 1: Inherit from MessageProcessor

```python
from typing import Dict, Any
from processors.base import MessageProcessor


class MyCustomProcessor(MessageProcessor):
    def process(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a WhatsApp message.
        
        Args:
            message_data: Dictionary containing:
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
            bool: True if successful, False otherwise
        """
        print(f"Processing message: {message_data.get('message_id')}")
        
        # Your custom logic here
        
        return True
```

### Step 2: Implement Your Logic

```python
class CommandProcessor(MessageProcessor):
    def process(self, message_data: Dict[str, Any]) -> bool:
        message_body = message_data.get("message_body", "").lower()
        
        if "help" in message_body:
            print("User requested help")
            # Send help message
            
        elif "status" in message_body:
            print("User requested status")
            # Send status information
            
        return True
```

## Using Custom Processors

### Option 1: Initialize RedisSubscriber with Custom Processors

```python
from subscriber import RedisSubscriber
from processors.email_processor import EmailNotificationProcessor
from processors.example_home_automation import HomeAutomationProcessor

# Create processor instances
email_processor = EmailNotificationProcessor()
home_automation = HomeAutomationProcessor(
    home_automation_api_url="http://localhost:8080/api"
)

# Initialize subscriber with custom processors
subscriber = RedisSubscriber(processors=[
    email_processor,
    home_automation
])

# Start listening
subscriber.start_listening()
```

### Option 2: Add Processors Dynamically

```python
from subscriber import RedisSubscriber

# Initialize with default processors
subscriber = RedisSubscriber()

# Add custom processor
custom_processor = MyCustomProcessor()
subscriber.add_processor(custom_processor)

# Start listening
subscriber.start_listening()
```

### Option 3: Remove Processors

```python
# Remove a processor by name
subscriber.remove_processor("LoggingProcessor")
```

## Advanced Examples

### Home Automation Integration

See `processors/example_home_automation.py` for a complete example of a home automation processor that:
- Detects commands in messages (e.g., "lights on", "temperature")
- Triggers automation actions
- Can be extended with API calls to your automation system

### Database Logger Processor

```python
from processors.base import MessageProcessor
from typing import Dict, Any
import sqlite3

class DatabaseLoggerProcessor(MessageProcessor):
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO message_log (message_id, sender, body, timestamp)
                VALUES (?, ?, ?, datetime('now'))
            """, (
                message_data.get('message_id'),
                message_data.get('sender_name'),
                message_data.get('message_body')
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"[{self.name}] Error logging to database: {e}")
            return False
```

### API Webhook Forwarder

```python
from processors.base import MessageProcessor
from typing import Dict, Any
import requests

class WebhookForwarderProcessor(MessageProcessor):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        try:
            response = requests.post(
                self.webhook_url,
                json=message_data,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[{self.name}] Error forwarding to webhook: {e}")
            return False
```

## Best Practices

1. **Error Handling**: Always wrap your logic in try-except blocks to prevent one processor from crashing the entire system.

2. **Return Values**: Return `True` for successful processing (or when there's nothing to process), `False` only for actual errors.

3. **Logging**: Use `print()` statements with the processor name prefix for debugging:
   ```python
   print(f"[{self.name}] Processing message...")
   ```

4. **Performance**: Keep processing logic lightweight. For heavy operations, consider using background tasks or queues.

5. **Testing**: Write unit tests for your custom processors (see `test_processors.py` for examples).

6. **Modularity**: Keep processors focused on a single responsibility. Create multiple processors instead of one monolithic processor.

## Processor Execution Flow

1. Message arrives from Redis
2. RedisSubscriber receives the message
3. For each registered processor:
   - Call `processor.process(message_data)`
   - Catch and log any exceptions
   - Continue to next processor (even if current one fails)
4. Processing complete

## Configuration

The default processors (EmailNotificationProcessor and LoggingProcessor) are automatically initialized when you create a RedisSubscriber without arguments:

```python
# Uses default processors
subscriber = RedisSubscriber()
```

To disable default processors and use only custom ones:

```python
# No default processors
subscriber = RedisSubscriber(processors=[])

# Add only the ones you want
subscriber.add_processor(MyCustomProcessor())
```

## Testing Your Processors

Use the mock testing pattern shown in `test_processors.py`:

```python
import pytest
from unittest.mock import Mock, patch

def test_my_processor():
    processor = MyCustomProcessor()
    
    message_data = {
        "message_id": "test_123",
        "sender_name": "Test User",
        "wa_id": "1234567890",
        "message_type": "text",
        "message_body": "Test message",
        "links": ""
    }
    
    result = processor.process(message_data)
    assert result is True
```

## Migration from Old Code

The old `EmailSender.send_email()` method is still available for backward compatibility but is deprecated. Update your code to use the new processor system:

**Old way:**
```python
from subscriber import EmailSender

EmailSender.send_email("Subject", "Body")
```

**New way:**
```python
from processors.email_processor import EmailNotificationProcessor

processor = EmailNotificationProcessor()
message_data = {...}  # Your message data
processor.process(message_data)
```

## Troubleshooting

### Processor Not Being Called

1. Check that the processor is registered:
   ```python
   print(f"Registered processors: {[p.name for p in subscriber.processors]}")
   ```

2. Verify Redis connection is working

3. Check for exceptions in your processor's `process()` method

### Processor Failing Silently

Add more logging to your processor:
```python
def process(self, message_data):
    print(f"[{self.name}] Starting processing...")
    try:
        # Your logic
        print(f"[{self.name}] Processing successful")
        return True
    except Exception as e:
        print(f"[{self.name}] Error: {e}")
        return False
```

## Support

For issues or questions about the processor system:
1. Check existing processors for examples
2. Review the test files for usage patterns
3. Open an issue on GitHub
