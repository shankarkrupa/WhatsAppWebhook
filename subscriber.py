import redis
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import config
import time

class EmailSender:
    """Email sender utility"""
    
    @staticmethod
    def send_email(subject: str, body: str, to_email: str = None) -> bool:
        """Send an email with the given subject and body"""
        if not to_email:
            to_email = config.EMAIL_TO
        
        # Skip if SMTP is not configured
        if not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
            print("SMTP credentials not configured, skipping email send")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = config.EMAIL_FROM or config.SMTP_USERNAME
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            
            # Send email
            text = msg.as_string()
            server.sendmail(msg['From'], to_email, text)
            server.quit()
            
            print(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False


class RedisSubscriber:
    """Redis subscriber for WhatsApp messages"""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
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
            
            # Subscribe to channel
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe(config.REDIS_CHANNEL)
            print(f"Subscribed to Redis channel: {config.REDIS_CHANNEL}")
        except Exception as e:
            print(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None
            self.pubsub = None
    
    def process_message(self, message_data: dict):
        """Process a WhatsApp message from Redis"""
        print(f"Processing message: {message_data.get('message_id')}")
        
        # Extract links from the message
        links = message_data.get("links", "")
        
        if links:
            # Prepare email content
            subject = f"WhatsApp Link from {message_data.get('sender_name', 'Unknown')}"
            body = f"""
WhatsApp Message Details:
--------------------------
From: {message_data.get('sender_name', 'Unknown')} ({message_data.get('wa_id', 'N/A')})
Message Type: {message_data.get('message_type', 'N/A')}
Message Body: {message_data.get('message_body', 'N/A')}

Links Found:
{links}

Message ID: {message_data.get('message_id', 'N/A')}
"""
            # Send email
            EmailSender.send_email(subject, body)
        else:
            print(f"No links found in message {message_data.get('message_id')}")
    
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
