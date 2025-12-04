"""
Email notification processor for messages with links
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from processors.base import MessageProcessor
from config import config


class EmailNotificationProcessor(MessageProcessor):
    """
    Processor that sends email notifications for messages containing links.
    """
    
    def process(self, message_data: Dict[str, Any]) -> bool:
        """
        Process a message and send email notification if it contains links.
        
        Args:
            message_data: Dictionary containing the message data
        
        Returns:
            bool: True if email was sent successfully or skipped (no links), False on error
        """
        print(f"[{self.name}] Processing message: {message_data.get('message_id')}")
        
        # Extract links from the message
        links = message_data.get("links", "")
        
        if not links:
            print(f"[{self.name}] No links found in message {message_data.get('message_id')}")
            return True  # Not an error, just nothing to process
        
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
        return self._send_email(subject, body)
    
    def _send_email(self, subject: str, body: str, to_email: str = None) -> bool:
        """Send an email with the given subject and body"""
        if not to_email:
            to_email = config.EMAIL_TO
        
        # Skip if SMTP is not configured
        if not config.SMTP_USERNAME or not config.SMTP_PASSWORD:
            print(f"[{self.name}] SMTP credentials not configured, skipping email send")
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
            
            print(f"[{self.name}] Email sent successfully to {to_email}")
            return True
        except Exception as e:
            print(f"[{self.name}] Error sending email: {str(e)}")
            return False
