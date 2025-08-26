"""
Unit tests for the LLM interface module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import json

# Import the module to test
from ai_note_system.api.llm_interface import (
    LLMInterface,
    OpenAIInterface,
    HuggingFaceInterface,
    get_llm_interface
)

class TestLLMInterface(unittest.TestCase):
    """Test cases for the LLM interface."""

    def setUp(self):
        """Set up test environment."""
        # Set environment variables for testing
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    @patch('ai_note_system.api.llm_interface.OpenAIInterface')
    def test_get_llm_interface_openai(self, mock_openai):
        """Test get_llm_interface with OpenAI provider."""
        # Arrange
        mock_openai.return_value = MagicMock()
        
        # Act
        interface = get_llm_interface("openai")
        
        # Assert
        self.assertIsNotNone(interface)
        mock_openai.assert_called_once()

    @patch('ai_note_system.api.llm_interface.HuggingFaceInterface')
    def test_get_llm_interface_huggingface(self, mock_hf):
        """Test get_llm_interface with HuggingFace provider."""
        # Arrange
        mock_hf.return_value = MagicMock()
        
        # Act
        interface = get_llm_interface("huggingface")
        
        # Assert
        self.assertIsNotNone(interface)
        mock_hf.assert_called_once()

    def test_get_llm_interface_invalid(self):
        """Test get_llm_interface with invalid provider."""
        # Act & Assert
        with self.assertRaises(ValueError):
            get_llm_interface("invalid_provider")

class TestOpenAIInterface(unittest.TestCase):
    """Test cases for the OpenAI interface."""

    def setUp(self):
        """Set up test environment."""
        # Set environment variables for testing
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        
        # Create patch for OpenAI client
        self.openai_patch = patch('openai.OpenAI')
        self.mock_openai = self.openai_patch.start()
        
        # Mock the OpenAI client
        self.mock_client = MagicMock()
        self.mock_openai.return_value = self.mock_client
        
        # Mock the chat completions
        self.mock_chat = MagicMock()
        self.mock_client.chat = MagicMock()
        self.mock_client.chat.completions = self.mock_chat
        
    def tearDown(self):
        """Clean up after tests."""
        # Stop patches
        self.openai_patch.stop()
        
        # Remove environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        # Act
        interface = OpenAIInterface(api_key="custom_api_key")
        
        # Assert
        self.assertEqual(interface.api_key, "custom_api_key")
        self.mock_openai.assert_called_once()

    def test_init_with_env_api_key(self):
        """Test initialization with environment API key."""
        # Act
        interface = OpenAIInterface()
        
        # Assert
        self.assertEqual(interface.api_key, "test_api_key")
        self.mock_openai.assert_called_once()

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        # Arrange
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
            
        # Act & Assert
        with self.assertRaises(ValueError):
            OpenAIInterface()

    @patch('openai.OpenAI')
    def test_generate_text(self, mock_openai):
        """Test generate_text method."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Generated text"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create.return_value = mock_response
        
        interface = OpenAIInterface()
        
        # Act
        result = interface.generate_text("Test prompt")
        
        # Assert
        self.assertEqual(result, "Generated text")
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_generate_chat_response(self, mock_openai):
        """Test generate_chat_response method."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Chat response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create.return_value = mock_response
        
        interface = OpenAIInterface()
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        
        # Act
        result = interface.generate_chat_response(messages)
        
        # Assert
        self.assertEqual(result, "Chat response")
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_generate_structured_output(self, mock_openai):
        """Test generate_structured_output method."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '{"key": "value"}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create.return_value = mock_response
        
        interface = OpenAIInterface()
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        
        # Act
        result = interface.generate_structured_output("Test prompt", schema)
        
        # Assert
        self.assertEqual(result, {"key": "value"})
        mock_client.chat.completions.create.assert_called_once()

    @patch('tiktoken.encoding_for_model')
    def test_count_tokens(self, mock_encoding_for_model):
        """Test count_tokens method."""
        # Arrange
        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]
        mock_encoding_for_model.return_value = mock_encoding
        
        interface = OpenAIInterface()
        
        # Act
        result = interface.count_tokens("Test text")
        
        # Assert
        self.assertEqual(result, 5)
        mock_encoding.encode.assert_called_once_with("Test text")

if __name__ == '__main__':
    unittest.main()