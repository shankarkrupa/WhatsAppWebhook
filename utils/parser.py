import re

def extract_links(text):
    return ", ".join(re.findall(r'https?://\S+', text)) if text else ""

def parse_whatsapp_message(message: dict) -> dict:
    msg_type = message.get("type")
    media_id = None
    mime_type = None
    filename = None
    body = None

    if msg_type == "text":
        body = message.get("text", {}).get("body")

    elif msg_type in ["image", "video", "audio", "document", "sticker"]:
        media = message.get(msg_type, {})
        media_id = media.get("id")
        mime_type = media.get("mime_type")
        filename = media.get("filename")  # Only for documents
        body = media.get("caption") or f"{msg_type} received"

    else:
        body = f"Unsupported message type: {msg_type}"

    return {
        "message_type": msg_type,
        "message_body": body,
        "media_id": media_id,
        "mime_type": mime_type,
        "filename": filename,
        "links": extract_links(body)
    }


def extract_links(text):
    return ", ".join(re.findall(r'https?://\S+', text)) if text else ""

def parse_whatsapp_message(message: dict) -> dict:
    msg_type = message.get("type")
    media_id = None
    mime_type = None
    filename = None
    body = None

    if msg_type == "text":
        body = message.get("text", {}).get("body")

    elif msg_type in ["image", "video", "audio", "document", "sticker"]:
        media = message.get(msg_type, {})
        media_id = media.get("id")
        mime_type = media.get("mime_type")
        filename = media.get("filename")  # Only for documents
        body = media.get("caption") or f"{msg_type} received"

    else:
        body = f"Unsupported message type: {msg_type}"

    return {
        "message_type": msg_type,
        "message_body": body,
        "media_id": media_id,
        "mime_type": mime_type,
        "filename": filename,
        "links": extract_links(body)
    }
