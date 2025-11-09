from utils.parser import parse_whatsapp_message
from utils.redis_publisher import redis_publisher
from fastapi import FastAPI, Depends, Request
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
from models import WhatsAppMessage
import json

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#needed when models.py schema is updated
#Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("")
async def root():
  return {"message": "Vanakkam"}

app.post("/")
async def root():
  return {"message": "Post received"}

@app.get("/test")
async def test():
  print("test API")
  return {"status": "All okay"}

@app.get("/whatsappwebhook")
async def acknowledge_whatsapp_message(request: Request):
  token = request.query_params.get("hub.verify_token")
  challenge = request.query_params.get("hub.challenge")
  if not challenge is None:
   return int(challenge)
  else:
   return {"query_params": request.query_params}

@app.post("/whatsappwebhook")
async def receive_whatsapp_message(request: Request, db: Session = Depends(get_db)):
    print("whatsappwebhook called")
    headers = dict(request.headers)
    payload = await request.json()
    print("payload initialized")

    try:
        payload = payload["entry"][0]["changes"][0]["value"]
        print(payload)
        message = payload["messages"][0]
        #print(message)
        contact = payload["contacts"][0]["profile"]
        wa_id = payload["contacts"][0]["wa_id"]
        print("going to parse the received payload as whatsapp message")

        parsed = parse_whatsapp_message(message)
        print("parsed successfully")

        db_msg = WhatsAppMessage(
            wa_id=wa_id,
            sender_name=contact.get("name"),
            message_id=message.get("id"),
            message_type=parsed["message_type"],
            message_body=parsed["message_body"],
            media_id=parsed["media_id"],
            mime_type=parsed["mime_type"],
            filename=parsed["filename"],
            links=parsed["links"],
            headers=json.dumps(headers)
        )
        db.add(db_msg)
        db.commit()
        print("received message is saved")
        
        # Publish to Redis
        message_data = {
            "wa_id": wa_id,
            "sender_name": contact.get("name"),
            "message_id": message.get("id"),
            "message_type": parsed["message_type"],
            "message_body": parsed["message_body"],
            "media_id": parsed["media_id"],
            "mime_type": parsed["mime_type"],
            "filename": parsed["filename"],
            "links": parsed["links"]
        }
        redis_publisher.publish_message(message_data)
        
        return {"status": "logged"}
    except Exception as e:
        print(str(e))
        return {"error": str(e)}

@app.get("/whatsappmessages")
def read_whatsappmessages(session: Session=Depends(get_db)):
 messages = session.query(WhatsAppMessage).all()
 return messages
