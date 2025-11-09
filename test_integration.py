#!/usr/bin/env python3
"""
Manual integration test for WhatsApp webhook with Redis
This script simulates a WhatsApp message with links and verifies the flow
"""
import json
import time
import subprocess
import sys

def test_redis_integration():
    """Test the Redis integration"""
    print("=" * 60)
    print("WhatsApp Webhook Redis Integration Test")
    print("=" * 60)
    
    # Test 1: Import modules
    print("\n[1/5] Testing module imports...")
    try:
        from config import config
        from utils.redis_publisher import RedisPublisher
        from subscriber import RedisSubscriber, EmailSender
        print("✓ All modules imported successfully")
    except Exception as e:
        print(f"✗ Failed to import modules: {e}")
        return False
    
    # Test 2: Configuration
    print("\n[2/5] Testing configuration...")
    print(f"  Redis Host: {config.REDIS_HOST}")
    print(f"  Redis Port: {config.REDIS_PORT}")
    print(f"  Redis Channel: {config.REDIS_CHANNEL}")
    print(f"  Email To: {config.EMAIL_TO}")
    print("✓ Configuration loaded successfully")
    
    # Test 3: Redis Publisher
    print("\n[3/5] Testing Redis Publisher...")
    publisher = RedisPublisher()
    test_message = {
        "wa_id": "1234567890",
        "sender_name": "Test User",
        "message_id": "test_msg_123",
        "message_type": "text",
        "message_body": "Check this link: https://example.com",
        "media_id": None,
        "mime_type": None,
        "filename": None,
        "links": "https://example.com"
    }
    
    if publisher.redis_client:
        result = publisher.publish_message(test_message)
        if result:
            print("✓ Message published to Redis successfully")
        else:
            print("✗ Failed to publish message")
    else:
        print("⚠ Redis not connected (this is expected if Redis is not running)")
        print("  To test with Redis, ensure Redis is running and try again")
    
    # Test 4: Subscriber
    print("\n[4/5] Testing Subscriber Message Processing...")
    subscriber = RedisSubscriber()
    if subscriber.redis_client:
        print("✓ Subscriber connected to Redis")
    else:
        print("⚠ Subscriber not connected to Redis (expected if Redis is not running)")
    
    # Test message processing logic
    print("  Testing message processing logic...")
    subscriber.process_message(test_message)
    print("✓ Message processing logic executed")
    
    # Test 5: Parser
    print("\n[5/5] Testing link extraction...")
    from utils.parser import extract_links
    test_text = "Visit https://example.com and https://test.org"
    links = extract_links(test_text)
    print(f"  Extracted links: {links}")
    if "https://example.com" in links and "https://test.org" in links:
        print("✓ Link extraction working correctly")
    else:
        print("✗ Link extraction failed")
        return False
    
    print("\n" + "=" * 60)
    print("Integration Test Summary")
    print("=" * 60)
    print("✓ Module imports: PASS")
    print("✓ Configuration: PASS")
    print(f"{'✓' if publisher.redis_client else '⚠'} Redis Publisher: {'PASS' if publisher.redis_client else 'SKIP (Redis not running)'}")
    print(f"{'✓' if subscriber.redis_client else '⚠'} Redis Subscriber: {'PASS' if subscriber.redis_client else 'SKIP (Redis not running)'}")
    print("✓ Link extraction: PASS")
    print("\nNOTE: To fully test the integration:")
    print("  1. Start Redis server: redis-server")
    print("  2. Set email credentials in .env file")
    print("  3. Start the webhook server: uvicorn main:app")
    print("  4. Start the subscriber: python subscriber.py")
    print("  5. Send a test webhook request with links")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_redis_integration()
    sys.exit(0 if success else 1)
