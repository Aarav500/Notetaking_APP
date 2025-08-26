"""
Unit tests for the embedding interface module.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

# Import the module to test
from ai_note_system.api.embedding_interface import (
    EmbeddingInterface,
    OpenAIEmbeddingInterface,
    SentenceTransformersInterface,
    get_embedding_interface
)

class TestEmbeddingInterface(unittest.TestCase):
    """Test cases for the embedding interface."""

    def setUp(self):
        """Set up test environment."""
        # Set environment variables for testing
        os.environ["OPENAI_API_KEY"] = "test_api_key"
        
    def tearDown(self):
        """Clean up after tests."""
        # Remove environment variables
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    @patch('ai_note_system.api.embedding_interface.OpenAIEmbeddingInterface')
    def test_get_embedding_interface_openai(self, mock_openai):
        """Test get_embedding_interface with OpenAI provider."""
        # Arrange
        mock_openai.return_value = MagicMock()
        
        # Act
        interface = get_embedding_interface("openai")
        
        # Assert
        self.assertIsNotNone(interface)
        mock_openai.assert_called_once()

    @patch('ai_note_system.api.embedding_interface.SentenceTransformersInterface')
    def test_get_embedding_interface_sentence_transformers(self, mock_st):
        """Test get_embedding_interface with SentenceTransformers provider."""
        # Arrange
        mock_st.return_value = MagicMock()
        
        # Act
        interface = get_embedding_interface("sentence-transformers")
        
        # Assert
        self.assertIsNotNone(interface)
        mock_st.assert_called_once()

    @patch('ai_note_system.api.embedding_interface.HuggingFaceEmbeddingInterface')
    def test_get_embedding_interface_huggingface(self, mock_hf):
        """Test get_embedding_interface with HuggingFace provider."""
        # Arrange
        mock_hf.return_value = MagicMock()
        
        # Act
        interface = get_embedding_interface("huggingface")
        
        # Assert
        self.assertIsNotNone(interface)
        mock_hf.assert_called_once()

    def test_get_embedding_interface_invalid(self):
        """Test get_embedding_interface with invalid provider."""
        # Act & Assert
        with self.assertRaises(ValueError):
            get_embedding_interface("invalid_provider")

class TestOpenAIEmbeddingInterface(unittest.TestCase):
    """Test cases for the OpenAI embedding interface."""

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
        
        # Mock the embeddings
        self.mock_embeddings = MagicMock()
        self.mock_client.embeddings = self.mock_embeddings
        
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
        interface = OpenAIEmbeddingInterface(api_key="custom_api_key")
        
        # Assert
        self.assertEqual(interface.api_key, "custom_api_key")
        self.mock_openai.assert_called_once()

    def test_init_with_env_api_key(self):
        """Test initialization with environment API key."""
        # Act
        interface = OpenAIEmbeddingInterface()
        
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
            OpenAIEmbeddingInterface()

    @patch('openai.OpenAI')
    def test_get_embeddings_single_text(self, mock_openai):
        """Test get_embeddings method with single text."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_data_item = MagicMock()
        mock_data_item.embedding = [0.1, 0.2, 0.3]
        
        mock_response = MagicMock()
        mock_response.data = [mock_data_item]
        
        mock_client.embeddings.create.return_value = mock_response
        
        interface = OpenAIEmbeddingInterface()
        
        # Act
        result = interface.get_embeddings("Test text")
        
        # Assert
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_client.embeddings.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_get_embeddings_multiple_texts(self, mock_openai):
        """Test get_embeddings method with multiple texts."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_data_item1 = MagicMock()
        mock_data_item1.embedding = [0.1, 0.2, 0.3]
        
        mock_data_item2 = MagicMock()
        mock_data_item2.embedding = [0.4, 0.5, 0.6]
        
        mock_response = MagicMock()
        mock_response.data = [mock_data_item1, mock_data_item2]
        
        mock_client.embeddings.create.return_value = mock_response
        
        interface = OpenAIEmbeddingInterface()
        
        # Act
        result = interface.get_embeddings(["Text 1", "Text 2"])
        
        # Assert
        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_client.embeddings.create.assert_called_once()

    def test_get_embedding_dimension(self):
        """Test get_embedding_dimension method."""
        # Arrange
        interface = OpenAIEmbeddingInterface(model="text-embedding-3-small")
        
        # Act
        result = interface.get_embedding_dimension()
        
        # Assert
        self.assertEqual(result, 1536)

    @patch('numpy.dot')
    @patch('numpy.linalg.norm')
    def test_compute_similarity(self, mock_norm, mock_dot):
        """Test compute_similarity method."""
        # Arrange
        mock_dot.return_value = 0.5
        mock_norm.side_effect = [1.0, 1.0]
        
        interface = OpenAIEmbeddingInterface()
        
        # Act
        result = interface.compute_similarity([0.1, 0.2, 0.3], [0.4, 0.5, 0.6])
        
        # Assert
        self.assertEqual(result, 0.75)  # (1 + 0.5) / 2
        mock_dot.assert_called_once()
        self.assertEqual(mock_norm.call_count, 2)

class TestSentenceTransformersInterface(unittest.TestCase):
    """Test cases for the SentenceTransformers interface."""

    @patch('sentence_transformers.SentenceTransformer')
    def test_init(self, mock_st):
        """Test initialization."""
        # Arrange
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model
        
        # Act
        interface = SentenceTransformersInterface(model_name="all-MiniLM-L6-v2")
        
        # Assert
        self.assertEqual(interface.model_name, "all-MiniLM-L6-v2")
        self.assertEqual(interface._embedding_dimension, 384)
        mock_st.assert_called_once_with("all-MiniLM-L6-v2", device="cpu")

    @patch('sentence_transformers.SentenceTransformer')
    def test_get_embeddings_single_text(self, mock_st):
        """Test get_embeddings method with single text."""
        # Arrange
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_st.return_value = mock_model
        
        interface = SentenceTransformersInterface()
        
        # Act
        result = interface.get_embeddings("Test text")
        
        # Assert
        self.assertEqual(result, [0.1, 0.2, 0.3])
        mock_model.encode.assert_called_once()

    @patch('sentence_transformers.SentenceTransformer')
    def test_get_embeddings_multiple_texts(self, mock_st):
        """Test get_embeddings method with multiple texts."""
        # Arrange
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_st.return_value = mock_model
        
        interface = SentenceTransformersInterface()
        
        # Act
        result = interface.get_embeddings(["Text 1", "Text 2"])
        
        # Assert
        self.assertEqual(result, [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_model.encode.assert_called_once()

    @patch('sentence_transformers.SentenceTransformer')
    def test_get_embedding_dimension(self, mock_st):
        """Test get_embedding_dimension method."""
        # Arrange
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model
        
        interface = SentenceTransformersInterface()
        
        # Act
        result = interface.get_embedding_dimension()
        
        # Assert
        self.assertEqual(result, 384)

    @patch('sentence_transformers.SentenceTransformer')
    @patch('sklearn.metrics.pairwise.cosine_similarity')
    def test_compute_similarity(self, mock_cosine_similarity, mock_st):
        """Test compute_similarity method."""
        # Arrange
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_st.return_value = mock_model
        
        mock_cosine_similarity.return_value = np.array([[0.5]])
        
        interface = SentenceTransformersInterface()
        
        # Act
        result = interface.compute_similarity([0.1, 0.2, 0.3], [0.4, 0.5, 0.6])
        
        # Assert
        self.assertEqual(result, 0.75)  # (1 + 0.5) / 2
        mock_cosine_similarity.assert_called_once()

if __name__ == '__main__':
    unittest.main()