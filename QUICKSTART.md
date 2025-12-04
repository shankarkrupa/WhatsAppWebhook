# Quick Start Guide - Message Processors

## What is it?

The message processor system allows you to easily plug in multiple custom processing classes to handle WhatsApp messages from the subscriber. Perfect for home automation developers!

## 5-Minute Quick Start

### 1. Create Your Custom Processor

```python
from processors.base import MessageProcessor
from typing import Dict, Any

class MyProcessor(MessageProcessor):
    def process(self, message_data: Dict[str, Any]) -> bool:
        # Your custom logic here
        print(f"Processing: {message_data.get('message_body')}")
        return True
```

### 2. Use It with the Subscriber

```python
from subscriber import RedisSubscriber

# Option A: Use with default processors
subscriber = RedisSubscriber()
subscriber.add_processor(MyProcessor())

# Option B: Use only your custom processors
subscriber = RedisSubscriber(processors=[MyProcessor()])

# Start listening
subscriber.start_listening()
```

## Common Use Cases

### Home Automation Commands

```python
class HomeAutomationProcessor(MessageProcessor):
    def process(self, message_data: Dict[str, Any]) -> bool:
        body = message_data.get("message_body", "").lower()
        
        if "lights on" in body:
            # Turn lights on
            print("Turning lights ON")
        elif "lights off" in body:
            # Turn lights off
            print("Turning lights OFF")
        elif "temperature" in body:
            # Get temperature
            print("Current temperature: 72°F")
        
        return True
```

### Webhook Forwarding

```python
import requests

class WebhookForwarder(MessageProcessor):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        try:
            requests.post(self.webhook_url, json=message_data)
            return True
        except:
            return False
```

### Database Logging

```python
import sqlite3

class DatabaseLogger(MessageProcessor):
    def __init__(self, db_path):
        self.db_path = db_path
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        conn = sqlite3.connect(self.db_path)
        # Insert message into database
        conn.close()
        return True
```

## Message Data Structure

Every processor receives a `message_data` dictionary with:

```python
{
    "wa_id": "1234567890",              # WhatsApp ID
    "sender_name": "John Doe",          # Sender's name
    "message_id": "msg_123",            # Unique message ID
    "message_type": "text",             # Type (text, image, etc.)
    "message_body": "Hello world",      # Message content
    "media_id": None,                   # Media ID if applicable
    "mime_type": None,                  # MIME type if applicable
    "filename": None,                   # Filename if applicable
    "links": "https://example.com"      # Extracted links
}
```

## Dynamic Management

```python
# Add processor at runtime
subscriber.add_processor(NewProcessor())

# Remove processor by name
subscriber.remove_processor("OldProcessor")

# List current processors
for p in subscriber.processors:
    print(p.name)
```

## Built-in Processors

1. **EmailNotificationProcessor** - Sends emails for messages with links
2. **LoggingProcessor** - Logs message details to console

## Tips

- Return `True` for success, `False` for errors
- Multiple processors run in sequence
- One failing processor doesn't affect others
- Use `self.name` for logging: `print(f"[{self.name}] message")`
- See `PROCESSORS.md` for detailed documentation
- Run `python demo_processors.py` for interactive examples

## Example: Complete Setup

```python
#!/usr/bin/env python3
from subscriber import RedisSubscriber
from processors.email_processor import EmailNotificationProcessor
from processors.logging_processor import LoggingProcessor
from processors.base import MessageProcessor
from typing import Dict, Any

# Custom processor
class CommandProcessor(MessageProcessor):
    def process(self, message_data: Dict[str, Any]) -> bool:
        body = message_data.get("message_body", "").lower()
        
        if "help" in body:
            print("Commands: help, status, info")
        elif "status" in body:
            print("System: OK")
        
        return True

# Setup and run
if __name__ == "__main__":
    subscriber = RedisSubscriber(processors=[
        EmailNotificationProcessor(),
        LoggingProcessor(),
        CommandProcessor()
    ])
    
    print("Listening for messages...")
    subscriber.start_listening()
```

Save as `my_subscriber.py` and run:
```bash
python my_subscriber.py
```

That's it! You're ready to extend WhatsApp webhook with custom processors.

For more examples, see:
- `PROCESSORS.md` - Full documentation
- `demo_processors.py` - Interactive demo
- `processors/example_home_automation.py` - Home automation example
