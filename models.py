from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from datetime import datetime

class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id = Column(Integer, primary_key=True, index=True)
    wa_id = Column(String, index=True)
    sender_name = Column(String)
    message_id = Column(String, unique=True)
    message_type = Column(String)
    message_body = Column(Text)
    media_id = Column(String, nullable=True)
    mime_type = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    links = Column(Text)
    headers = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
