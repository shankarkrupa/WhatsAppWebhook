"""
Tests for the message processor system
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from processors.base import MessageProcessor
from processors.email_processor import EmailNotificationProcessor
from processors.logging_processor import LoggingProcessor
from subscriber import RedisSubscriber


class MockProcessor(MessageProcessor):
    """Mock processor for testing"""
    
    def __init__(self):
        self.processed_messages = []
        self.should_fail = False
    
    def process(self, message_data):
        self.processed_messages.append(message_data)
        return not self.should_fail


class TestMessageProcessorBase:
    """Tests for the MessageProcessor base class"""
    
    def test_processor_name_property(self):
        """Test that processor name property returns class name"""
        processor = MockProcessor()
        assert processor.name == "MockProcessor"


class TestEmailNotificationProcessor:
    """Tests for EmailNotificationProcessor"""
    
    def test_process_message_with_links(self):
        """Test processing a message with links"""
        with patch('processors.email_processor.config') as mock_config, \
             patch('processors.email_processor.smtplib.SMTP') as mock_smtp:
            
            mock_config.SMTP_USERNAME = "test@example.com"
            mock_config.SMTP_PASSWORD = "password"
            mock_config.SMTP_HOST = "smtp.example.com"
            mock_config.SMTP_PORT = 587
            mock_config.EMAIL_FROM = "test@example.com"
            mock_config.EMAIL_TO = "recipient@example.com"
            
            mock_server = MagicMock()
            mock_smtp.return_value = mock_server
            
            processor = EmailNotificationProcessor()
            message_data = {
                "message_id": "msg_123",
                "sender_name": "John Doe",
                "wa_id": "1234567890",
                "message_type": "text",
                "message_body": "Check this https://example.com",
                "links": "https://example.com"
            }
            
            result = processor.process(message_data)
            assert result is True
            mock_server.sendmail.assert_called_once()
    
    def test_process_message_without_links(self):
        """Test processing a message without links"""
        processor = EmailNotificationProcessor()
        message_data = {
            "message_id": "msg_124",
            "sender_name": "Jane Doe",
            "wa_id": "0987654321",
            "message_type": "text",
            "message_body": "Hello world",
            "links": ""
        }
        
        result = processor.process(message_data)
        # Should return True but not send email
        assert result is True
    
    def test_process_message_no_smtp_credentials(self):
        """Test processing when SMTP credentials are not configured"""
        with patch('processors.email_processor.config') as mock_config:
            mock_config.SMTP_USERNAME = ""
            mock_config.SMTP_PASSWORD = ""
            
            processor = EmailNotificationProcessor()
            message_data = {
                "message_id": "msg_125",
                "sender_name": "Test User",
                "wa_id": "1111111111",
                "message_type": "text",
                "message_body": "Check https://test.com",
                "links": "https://test.com"
            }
            
            result = processor.process(message_data)
            assert result is False


class TestLoggingProcessor:
    """Tests for LoggingProcessor"""
    
    def test_process_message(self):
        """Test that logging processor logs message details"""
        processor = LoggingProcessor()
        message_data = {
            "message_id": "msg_126",
            "sender_name": "Test User",
            "wa_id": "2222222222",
            "message_type": "text",
            "message_body": "Test message",
            "links": ""
        }
        
        result = processor.process(message_data)
        assert result is True


class TestRedisSubscriberWithProcessors:
    """Tests for RedisSubscriber with multiple processors"""
    
    def test_init_with_default_processors(self):
        """Test initialization with default processors"""
        with patch('subscriber.redis.Redis'):
            subscriber = RedisSubscriber()
            assert len(subscriber.processors) == 2
            assert any(isinstance(p, EmailNotificationProcessor) for p in subscriber.processors)
            assert any(isinstance(p, LoggingProcessor) for p in subscriber.processors)
    
    def test_init_with_custom_processors(self):
        """Test initialization with custom processors"""
        with patch('subscriber.redis.Redis'):
            mock_processor = MockProcessor()
            subscriber = RedisSubscriber(processors=[mock_processor])
            assert len(subscriber.processors) == 1
            assert subscriber.processors[0] == mock_processor
    
    def test_add_processor(self):
        """Test adding a processor dynamically"""
        with patch('subscriber.redis.Redis'):
            subscriber = RedisSubscriber(processors=[])
            assert len(subscriber.processors) == 0
            
            mock_processor = MockProcessor()
            subscriber.add_processor(mock_processor)
            assert len(subscriber.processors) == 1
            assert subscriber.processors[0] == mock_processor
    
    def test_remove_processor(self):
        """Test removing a processor by name"""
        with patch('subscriber.redis.Redis'):
            mock_processor = MockProcessor()
            subscriber = RedisSubscriber(processors=[mock_processor])
            assert len(subscriber.processors) == 1
            
            result = subscriber.remove_processor("MockProcessor")
            assert result is True
            assert len(subscriber.processors) == 0
    
    def test_remove_nonexistent_processor(self):
        """Test removing a processor that doesn't exist"""
        with patch('subscriber.redis.Redis'):
            subscriber = RedisSubscriber(processors=[])
            result = subscriber.remove_processor("NonExistent")
            assert result is False
    
    def test_process_message_with_multiple_processors(self):
        """Test that all processors are called when processing a message"""
        with patch('subscriber.redis.Redis'):
            mock_processor1 = MockProcessor()
            mock_processor2 = MockProcessor()
            
            subscriber = RedisSubscriber(processors=[mock_processor1, mock_processor2])
            
            message_data = {
                "message_id": "msg_127",
                "sender_name": "Test",
                "wa_id": "3333333333",
                "message_type": "text",
                "message_body": "Test",
                "links": ""
            }
            
            subscriber.process_message(message_data)
            
            assert len(mock_processor1.processed_messages) == 1
            assert len(mock_processor2.processed_messages) == 1
            assert mock_processor1.processed_messages[0] == message_data
            assert mock_processor2.processed_messages[0] == message_data
    
    def test_process_message_with_failing_processor(self):
        """Test that processing continues even if one processor fails"""
        with patch('subscriber.redis.Redis'):
            mock_processor1 = MockProcessor()
            mock_processor1.should_fail = True
            mock_processor2 = MockProcessor()
            
            subscriber = RedisSubscriber(processors=[mock_processor1, mock_processor2])
            
            message_data = {
                "message_id": "msg_128",
                "sender_name": "Test",
                "wa_id": "4444444444",
                "message_type": "text",
                "message_body": "Test",
                "links": ""
            }
            
            # Should not raise an exception
            subscriber.process_message(message_data)
            
            # Both processors should have been called
            assert len(mock_processor1.processed_messages) == 1
            assert len(mock_processor2.processed_messages) == 1
    
    def test_process_message_with_exception_in_processor(self):
        """Test that processing continues even if one processor raises an exception"""
        
        class ExceptionProcessor(MessageProcessor):
            def process(self, message_data):
                raise ValueError("Test exception")
        
        with patch('subscriber.redis.Redis'):
            exception_processor = ExceptionProcessor()
            mock_processor = MockProcessor()
            
            subscriber = RedisSubscriber(processors=[exception_processor, mock_processor])
            
            message_data = {
                "message_id": "msg_129",
                "sender_name": "Test",
                "wa_id": "5555555555",
                "message_type": "text",
                "message_body": "Test",
                "links": ""
            }
            
            # Should not raise an exception
            subscriber.process_message(message_data)
            
            # Second processor should still have been called
            assert len(mock_processor.processed_messages) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
