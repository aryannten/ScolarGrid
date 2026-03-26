"""
Tests for Google Gemini AI service

Tests the Gemini API integration and error handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services import gemini_service


class TestGeminiClient:
    """Test Gemini client initialization"""
    
    def test_get_gemini_client_missing_api_key(self):
        """Test that missing API key raises ValueError"""
        with patch('app.services.gemini_service.settings') as mock_settings:
            mock_settings.gemini_api_key = ""
            
            with pytest.raises(ValueError, match="GEMINI_API_KEY is not configured"):
                gemini_service.get_gemini_client()
    
    def test_get_gemini_client_import_error(self):
        """Test that import error is handled gracefully"""
        with patch('app.services.gemini_service.settings') as mock_settings:
            mock_settings.gemini_api_key = "test-key"
            
            with patch('builtins.__import__', side_effect=ImportError("Module not found")):
                with pytest.raises(Exception, match="Google Generative AI library not installed"):
                    gemini_service.get_gemini_client()


class TestSendMessage:
    """Test send_message function"""
    
    @pytest.mark.asyncio
    async def test_send_message_empty_message(self):
        """Test that empty message raises ValueError"""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            await gemini_service.send_message("")
    
    @pytest.mark.asyncio
    async def test_send_message_too_long(self):
        """Test that message exceeding max length raises ValueError"""
        long_message = "a" * 10001
        with pytest.raises(ValueError, match="Message is too long"):
            await gemini_service.send_message(long_message)
    
    @pytest.mark.asyncio
    async def test_send_message_quota_exceeded(self):
        """Test quota exceeded error handling"""
        with patch('app.services.gemini_service.get_gemini_client') as mock_client:
            mock_model = Mock()
            mock_chat = Mock()
            mock_chat.send_message = Mock(side_effect=Exception("quota exceeded"))
            mock_model.start_chat.return_value = mock_chat
            mock_client.return_value = mock_model
            
            with pytest.raises(Exception, match="AI service quota exceeded"):
                await gemini_service.send_message("test message")
    
    @pytest.mark.asyncio
    async def test_send_message_api_key_error(self):
        """Test API key error handling"""
        with patch('app.services.gemini_service.get_gemini_client') as mock_client:
            mock_model = Mock()
            mock_chat = Mock()
            mock_chat.send_message = Mock(side_effect=Exception("invalid api key"))
            mock_model.start_chat.return_value = mock_chat
            mock_client.return_value = mock_model
            
            with pytest.raises(Exception, match="AI service authentication failed"):
                await gemini_service.send_message("test message")
    
    @pytest.mark.asyncio
    async def test_send_message_timeout_error(self):
        """Test timeout error handling"""
        with patch('app.services.gemini_service.get_gemini_client') as mock_client:
            mock_model = Mock()
            mock_chat = Mock()
            mock_chat.send_message = Mock(side_effect=Exception("request timeout"))
            mock_model.start_chat.return_value = mock_chat
            mock_client.return_value = mock_model
            
            with pytest.raises(Exception, match="AI service request timed out"):
                await gemini_service.send_message("test message")


class TestSendMessageStream:
    """Test send_message_stream function"""
    
    @pytest.mark.asyncio
    async def test_send_message_stream_empty_message(self):
        """Test that empty message raises ValueError"""
        with pytest.raises(ValueError, match="Message cannot be empty"):
            async for _ in gemini_service.send_message_stream(""):
                pass
    
    @pytest.mark.asyncio
    async def test_send_message_stream_too_long(self):
        """Test that message exceeding max length raises ValueError"""
        long_message = "a" * 10001
        with pytest.raises(ValueError, match="Message is too long"):
            async for _ in gemini_service.send_message_stream(long_message):
                pass


class TestBuildConversationHistory:
    """Test build_conversation_history function"""
    
    def test_build_conversation_history_empty(self):
        """Test building history from empty list"""
        history = gemini_service.build_conversation_history([])
        assert history == []
    
    def test_build_conversation_history_with_messages(self):
        """Test building history from messages"""
        # Mock AIMessage objects
        mock_msg1 = Mock()
        mock_msg1.role = "user"
        mock_msg1.content = "Hello"
        
        mock_msg2 = Mock()
        mock_msg2.role = "assistant"
        mock_msg2.content = "Hi there!"
        
        history = gemini_service.build_conversation_history([mock_msg1, mock_msg2])
        
        assert len(history) == 2
        assert history[0] == {"role": "user", "parts": ["Hello"]}
        assert history[1] == {"role": "model", "parts": ["Hi there!"]}
