# WhatsAppWebhook

A FastAPI-based webhook for receiving WhatsApp messages with Redis integration and email notifications.

## Features

- Receives WhatsApp webhook messages
- Stores messages in a database (SQLite/PostgreSQL)
- Publishes messages to Redis for asynchronous processing
- Email notifications for messages containing links
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

The subscriber will listen for messages on the Redis channel and send email notifications for messages containing links.

## How it Works

1. WhatsApp sends webhook POST requests to `/whatsappwebhook`
2. The webhook handler:
   - Parses the message
   - Stores it in the database
   - Publishes it to Redis channel
3. The Redis subscriber:
   - Listens for messages on the channel
   - Extracts links from messages
   - Sends email notifications with the links

## API Endpoints

- `GET /`: Health check
- `POST /`: Test endpoint
- `GET /test`: Test API
- `GET /whatsappwebhook`: Webhook verification endpoint
- `POST /whatsappwebhook`: Webhook message receiver
- `GET /whatsappmessages`: List all stored messages