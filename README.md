# WhatsAppWebhook

A FastAPI-based webhook for receiving WhatsApp messages with Redis integration, email notifications, and **pluggable message processors** for extensible message handling.

## Features

- Receives WhatsApp webhook messages
- Stores messages in a database (SQLite/PostgreSQL)
- Publishes messages to Redis for asynchronous processing
- **Pluggable message processor system** - easily add custom processors for your use cases
- Email notifications for messages containing links (built-in processor)
- Logging and monitoring (built-in processor)
- Perfect for **home automation integration** and custom workflows
- Fully configurable via environment variables

## Setup

### Prerequisites

- Python 3.8+
- Redis server
- SMTP server credentials (for email notifications)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Configuration

All configuration is done via environment variables. See `.env.example` for all available options:

**Redis Configuration:**
- `REDIS_HOST`: Redis server host (default: localhost)
- `REDIS_PORT`: Redis server port (default: 6379)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_PASSWORD`: Redis password (optional)
- `REDIS_CHANNEL`: Redis channel name (default: whatsapp_messages)

**Email Configuration:**
- `SMTP_HOST`: SMTP server host (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `EMAIL_FROM`: From email address
- `EMAIL_TO`: Recipient email address (default: test@krupashankar.com)

**Database Configuration:**
- `DATABASE_URL`: Database connection URL (default: sqlite:///./whatsapp.db)

## Running

### Start the webhook server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start the Redis subscriber (in a separate terminal):
```bash
python subscriber.py
```

The subscriber will listen for messages on the Redis channel and execute all registered processors (email notifications, logging, custom processors, etc.).

## Message Processors

The system now supports **pluggable message processors**, allowing you to easily extend functionality by adding custom processors. This is perfect for home automation developers who want to integrate WhatsApp messages with their automation systems.

### Default Processors

- **EmailNotificationProcessor**: Sends email notifications for messages containing links
- **LoggingProcessor**: Logs message details to console for monitoring

### Creating Custom Processors

See [PROCESSORS.md](PROCESSORS.md) for detailed documentation on:
- Creating custom processors
- Home automation integration examples
- Advanced use cases (database logging, webhook forwarding, etc.)
- Best practices and testing

### Quick Example

```python
from subscriber import RedisSubscriber
from processors.base import MessageProcessor
from typing import Dict, Any

# Create a custom processor
class MyProcessor(MessageProcessor):
    def process(self, message_data: Dict[str, Any]) -> bool:
        print(f"Processing: {message_data.get('message_body')}")
        # Your custom logic here
        return True

# Use it
subscriber = RedisSubscriber(processors=[MyProcessor()])
subscriber.start_listening()
```

## How it Works

1. WhatsApp sends webhook POST requests to `/whatsappwebhook`
2. The webhook handler:
   - Parses the message
   - Stores it in the database
   - Publishes it to Redis channel
3. The Redis subscriber:
   - Listens for messages on the channel
   - Executes all registered message processors
   - Each processor can implement custom logic (email, logging, automation, etc.)

## API Endpoints

- `GET /`: Health check
- `POST /`: Test endpoint
- `GET /test`: Test API
- `GET /whatsappwebhook`: Webhook verification endpoint
- `POST /whatsappwebhook`: Webhook message receiver
- `GET /whatsappmessages`: List all stored messages

## Testing

Run unit tests:
```bash
pip install -r requirements-dev.txt
pytest test_webhook.py test_processors.py -v
```

Run integration test:
```bash
python test_integration.py
```

## Project Structure

```
WhatsAppWebhook/
├── main.py                 # FastAPI application and webhook endpoints
├── config.py              # Configuration management
├── database.py            # Database connection setup
├── models.py              # SQLAlchemy models
├── subscriber.py          # Redis subscriber with processor support
├── processors/            # Message processor modules
│   ├── base.py           # Base MessageProcessor class
│   ├── email_processor.py         # Email notification processor
│   ├── logging_processor.py       # Logging processor
│   └── example_home_automation.py # Example home automation processor
├── utils/
│   ├── parser.py          # WhatsApp message parser
│   └── redis_publisher.py # Redis publisher utility
├── test_webhook.py        # Unit tests
├── test_processors.py     # Processor system tests
├── test_integration.py    # Integration tests
├── PROCESSORS.md          # Processor documentation
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── .env.example           # Example environment configuration
└── .gitignore            # Git ignore rules
```

## Architecture

The system uses a pub/sub pattern with Redis and a pluggable processor architecture:

1. **Webhook Receiver** (main.py): Receives WhatsApp messages and publishes to Redis
2. **Redis**: Acts as a message broker between components
3. **Subscriber** (subscriber.py): Consumes messages from Redis and executes processors
4. **Message Processors**: Pluggable components that handle messages (email, logging, automation, etc.)

This architecture allows for:
- **Scalability**: Multiple subscribers can process messages
- **Reliability**: Messages are queued in Redis
- **Decoupling**: Webhook and message processing are independent
- **Extensibility**: Easy to add new processors without modifying core code
- **Flexibility**: Mix and match processors based on your needs