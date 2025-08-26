"""
Unit tests for the topic linker module.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import tempfile

# Import the module to test
from ai_note_system.processing.topic_linker import (
    find_related_topics,
    get_text_embedding,
    find_similar_topics,
    cosine_similarity,
    format_flat_results,
    format_hierarchical_results,
    create_topic_entry,
    update_topic_database
)

class TestTopicLinker(unittest.TestCase):
    """Test cases for the topic linker module."""

    def setUp(self):
        """Set up test environment."""
        # Sample text for testing
        self.sample_text = """
        Neural networks are a class of machine learning models inspired by the human brain.
        They consist of layers of interconnected nodes or "neurons" that process information.
        Deep learning is a subset of neural networks with multiple hidden layers.
        """
        
        # Sample embedding for testing
        self.sample_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Sample topic database for testing
        self.sample_topic_db = {
            "topics": [
                {
                    "title": "Neural Networks",
                    "path": "ML/Neural_Networks",
                    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "summary": "Basic overview of neural networks"
                },
                {
                    "title": "Deep Learning",
                    "path": "ML/Deep_Learning",
                    "embedding": [0.15, 0.25, 0.35, 0.45, 0.55],
                    "summary": "Advanced neural networks with multiple layers"
                },
                {
                    "title": "Reinforcement Learning",
                    "path": "ML/RL",
                    "embedding": [0.5, 0.4, 0.3, 0.2, 0.1],
                    "summary": "Learning through interaction with environment"
                }
            ]
        }
        
        # Create a temporary file for the topic database
        self.temp_db_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        with open(self.temp_db_file.name, 'w') as f:
            json.dump(self.sample_topic_db, f)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if os.path.exists(self.temp_db_file.name):
            os.unlink(self.temp_db_file.name)

    @patch('ai_note_system.processing.topic_linker.get_text_embedding')
    @patch('ai_note_system.processing.topic_linker.find_similar_topics')
    def test_find_related_topics(self, mock_find_similar, mock_get_embedding):
        """Test find_related_topics function."""
        # Arrange
        mock_get_embedding.return_value = self.sample_embedding
        mock_find_similar.return_value = [
            {"title": "Neural Networks", "path": "ML/Neural_Networks", "similarity": 0.95},
            {"title": "Deep Learning", "path": "ML/Deep_Learning", "similarity": 0.85}
        ]
        
        # Act
        result = find_related_topics(
            self.sample_text,
            self.sample_topic_db,
            max_results=2,
            threshold=0.8
        )
        
        # Assert
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["related_topics"]), 2)
        self.assertEqual(result["related_topics"][0]["title"], "Neural Networks")
        mock_get_embedding.assert_called_once_with(self.sample_text, "all-MiniLM-L6-v2")
        mock_find_similar.assert_called_once()

    @patch('ai_note_system.processing.topic_linker.get_text_embedding')
    def test_find_related_topics_with_file_path(self, mock_get_embedding):
        """Test find_related_topics function with file path."""
        # Arrange
        mock_get_embedding.return_value = self.sample_embedding
        
        # Act
        result = find_related_topics(
            self.sample_text,
            self.temp_db_file.name,
            max_results=2,
            threshold=0.8
        )
        
        # Assert
        self.assertIn("related_topics", result)
        self.assertIn("count", result)
        mock_get_embedding.assert_called_once()

    def test_find_related_topics_empty_text(self):
        """Test find_related_topics function with empty text."""
        # Act
        result = find_related_topics("", self.sample_topic_db)
        
        # Assert
        self.assertIn("error", result)

    @patch('sentence_transformers.SentenceTransformer')
    def test_get_text_embedding_sentence_transformers(self, mock_st):
        """Test get_text_embedding function with SentenceTransformer."""
        # Arrange
        mock_model = MagicMock()
        mock_model.encode.return_value = self.sample_embedding
        mock_st.return_value = mock_model
        
        # Act
        result = get_text_embedding(self.sample_text)
        
        # Assert
        self.assertEqual(result, self.sample_embedding)
        mock_model.encode.assert_called_once_with(self.sample_text)

    @patch('sentence_transformers.SentenceTransformer', side_effect=ImportError)
    @patch('openai.OpenAI')
    def test_get_text_embedding_openai_fallback(self, mock_openai, mock_st):
        """Test get_text_embedding function with OpenAI fallback."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_data = MagicMock()
        mock_data.embedding = self.sample_embedding
        
        mock_response = MagicMock()
        mock_response.data = [mock_data]
        
        mock_client.embeddings.create.return_value = mock_response
        
        # Act
        result = get_text_embedding(self.sample_text)
        
        # Assert
        self.assertEqual(result, self.sample_embedding)
        mock_client.embeddings.create.assert_called_once()

    def test_find_similar_topics(self):
        """Test find_similar_topics function."""
        # Act
        result = find_similar_topics(
            self.sample_embedding,
            self.sample_topic_db,
            max_results=2,
            threshold=0.7
        )
        
        # Assert
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)

    def test_find_similar_topics_empty_db(self):
        """Test find_similar_topics function with empty database."""
        # Act
        result = find_similar_topics(
            self.sample_embedding,
            {"topics": []},
            max_results=2,
            threshold=0.7
        )
        
        # Assert
        self.assertEqual(result, [])

    def test_cosine_similarity(self):
        """Test cosine_similarity function."""
        # Arrange
        vec1 = [1, 0, 0, 0, 0]
        vec2 = [0, 1, 0, 0, 0]
        vec3 = [1, 0, 0, 0, 0]
        
        # Act
        similarity1 = cosine_similarity(vec1, vec2)
        similarity2 = cosine_similarity(vec1, vec3)
        
        # Assert
        self.assertEqual(similarity1, 0)
        self.assertEqual(similarity2, 1)

    def test_format_flat_results(self):
        """Test format_flat_results function."""
        # Arrange
        similarities = [
            (self.sample_topic_db["topics"][0], 0.95),
            (self.sample_topic_db["topics"][1], 0.85)
        ]
        
        # Act
        result = format_flat_results(similarities)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Neural Networks")
        self.assertEqual(result[0]["similarity"], 0.95)
        self.assertEqual(result[1]["title"], "Deep Learning")
        self.assertEqual(result[1]["similarity"], 0.85)

    def test_format_hierarchical_results(self):
        """Test format_hierarchical_results function."""
        # Arrange
        similarities = [
            (self.sample_topic_db["topics"][0], 0.95),
            (self.sample_topic_db["topics"][1], 0.85)
        ]
        
        # Act
        result = format_hierarchical_results(similarities)
        
        # Assert
        self.assertEqual(len(result), 1)  # One category: ML
        self.assertEqual(result[0]["category"], "ML")
        self.assertEqual(len(result[0]["topics"]), 2)
        self.assertEqual(result[0]["topics"][0]["title"], "Neural Networks")
        self.assertEqual(result[0]["topics"][1]["title"], "Deep Learning")

    @patch('ai_note_system.processing.topic_linker.get_text_embedding')
    def test_create_topic_entry(self, mock_get_embedding):
        """Test create_topic_entry function."""
        # Arrange
        mock_get_embedding.return_value = self.sample_embedding
        
        # Act
        result = create_topic_entry(
            title="Test Topic",
            text="This is a test topic",
            path="Test/Path",
            summary="Test summary"
        )
        
        # Assert
        self.assertEqual(result["title"], "Test Topic")
        self.assertEqual(result["path"], "Test/Path")
        self.assertEqual(result["embedding"], self.sample_embedding)
        self.assertEqual(result["summary"], "Test summary")
        mock_get_embedding.assert_called_once()

    def test_update_topic_database(self):
        """Test update_topic_database function."""
        # Arrange
        new_topic = {
            "title": "New Topic",
            "path": "New/Path",
            "embedding": [0.1, 0.2, 0.3],
            "summary": "New summary"
        }
        
        # Act
        result = update_topic_database(self.temp_db_file.name, new_topic)
        
        # Assert
        self.assertTrue(result)
        
        # Verify the topic was added
        with open(self.temp_db_file.name, 'r') as f:
            updated_db = json.load(f)
            self.assertEqual(len(updated_db["topics"]), 4)
            self.assertEqual(updated_db["topics"][3]["title"], "New Topic")

if __name__ == '__main__':
    unittest.main()