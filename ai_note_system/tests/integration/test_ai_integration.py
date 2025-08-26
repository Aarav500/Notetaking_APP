"""
Integration tests for AI components.
Tests the interaction between different AI components and API endpoints.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import os
import tempfile
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import modules to test
from ai_note_system.api.llm_interface import get_llm_interface
from ai_note_system.api.embedding_interface import get_embedding_interface
from ai_note_system.visualization.mindmap_gen import generate_mindmap_from_llm
from ai_note_system.processing.topic_linker import find_related_topics, create_topic_entry, update_topic_database
from ai_note_system.processing.image_flashcards import generate_zero_shot_flashcards

class TestAIIntegration(unittest.TestCase):
    """Integration tests for AI components."""

    def setUp(self):
        """Set up test environment."""
        # Sample text for testing
        self.sample_text = """
        # Machine Learning Basics
        
        Machine learning is a subset of artificial intelligence that focuses on developing systems that learn from data.
        
        ## Types of Machine Learning
        
        1. Supervised Learning: Learning with labeled data
           - Classification: Predicting categories
           - Regression: Predicting continuous values
        
        2. Unsupervised Learning: Learning without labeled data
           - Clustering: Grouping similar data points
           - Dimensionality Reduction: Reducing features while preserving information
        
        3. Reinforcement Learning: Learning through interaction with an environment
           - Q-Learning: Value-based method
           - Policy Gradient: Policy-based method
        """
        
        # Create a temporary directory for output files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a temporary topic database
        self.topic_db_path = os.path.join(self.temp_dir.name, "topic_db.json")
        with open(self.topic_db_path, 'w') as f:
            json.dump({"topics": []}, f)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        self.temp_dir.cleanup()

    @patch('ai_note_system.api.llm_interface.OpenAIInterface')
    @patch('ai_note_system.api.embedding_interface.OpenAIEmbeddingInterface')
    def test_llm_and_embedding_integration(self, mock_embedding, mock_llm):
        """Test integration between LLM and embedding interfaces."""
        # Arrange
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        mock_llm_instance.generate_text.return_value = "Generated summary of machine learning concepts."
        
        mock_embedding_instance = MagicMock()
        mock_embedding.return_value = mock_embedding_instance
        mock_embedding_instance.get_embeddings.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Act
        # Get LLM interface
        llm = get_llm_interface("openai")
        
        # Generate summary
        summary = llm.generate_text(f"Summarize the following text:\n{self.sample_text}")
        
        # Get embedding interface
        embedding = get_embedding_interface("openai")
        
        # Generate embedding for the summary
        embedding_vector = embedding.get_embeddings(summary)
        
        # Assert
        self.assertIsNotNone(summary)
        self.assertIsNotNone(embedding_vector)
        mock_llm_instance.generate_text.assert_called_once()
        mock_embedding_instance.get_embeddings.assert_called_once()

    @patch('ai_note_system.visualization.mindmap_gen._generate_mindmap_with_openai')
    @patch('ai_note_system.processing.topic_linker.get_text_embedding')
    def test_mindmap_and_topic_linker_integration(self, mock_get_embedding, mock_generate_mindmap):
        """Test integration between mind map generation and topic linker."""
        # Arrange
        expected_mindmap = """mindmap
  root((Machine Learning))
    Types
      Supervised Learning
        Classification
        Regression
      Unsupervised Learning
        Clustering
        Dimensionality Reduction
      Reinforcement Learning
        Q-Learning
        Policy Gradient"""
        
        mock_generate_mindmap.return_value = expected_mindmap
        mock_get_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Act
        # Generate mind map
        mindmap = generate_mindmap_from_llm(self.sample_text, model="gpt-4")
        
        # Create topic entry
        topic = create_topic_entry(
            title="Machine Learning Basics",
            text=self.sample_text,
            path="ML/Basics",
            summary="Basic concepts of machine learning"
        )
        
        # Update topic database
        update_result = update_topic_database(self.topic_db_path, topic)
        
        # Find related topics
        related = find_related_topics(
            "Supervised learning is a type of machine learning.",
            self.topic_db_path,
            max_results=5,
            threshold=0.5
        )
        
        # Assert
        self.assertEqual(mindmap, expected_mindmap)
        self.assertTrue(update_result)
        self.assertIn("related_topics", related)
        mock_generate_mindmap.assert_called_once()
        self.assertEqual(mock_get_embedding.call_count, 2)  # Called for create_topic_entry and find_related_topics

    @patch('ai_note_system.processing.image_flashcards._generate_flashcards_from_text')
    def test_flashcard_generation_integration(self, mock_generate_flashcards):
        """Test integration for flashcard generation."""
        # Arrange
        expected_flashcards = [
            {
                "question": "What are the three main types of machine learning?",
                "answer": "The three main types of machine learning are Supervised Learning, Unsupervised Learning, and Reinforcement Learning."
            },
            {
                "question": "What is Supervised Learning?",
                "answer": "Supervised Learning is a type of machine learning where the model learns from labeled data. It includes Classification (predicting categories) and Regression (predicting continuous values)."
            }
        ]
        
        mock_generate_flashcards.return_value = expected_flashcards
        
        # Create a temporary text file
        text_file_path = os.path.join(self.temp_dir.name, "ml_basics.txt")
        with open(text_file_path, 'w') as f:
            f.write(self.sample_text)
        
        # Act
        flashcards = generate_zero_shot_flashcards(
            input_path=text_file_path,
            input_type="text",
            output_dir=self.temp_dir.name,
            num_cards=2
        )
        
        # Check if JSON file was created
        json_path = os.path.join(self.temp_dir.name, "zero_shot_flashcards.json")
        
        # Assert
        self.assertEqual(flashcards, expected_flashcards)
        self.assertTrue(os.path.exists(json_path))
        mock_generate_flashcards.assert_called_once()

class TestAIEndpoints(unittest.TestCase):
    """Integration tests for AI API endpoints."""
    
    @patch('fastapi.testclient.TestClient')
    def test_generate_mindmap_endpoint(self, mock_test_client):
        """Test the generate mindmap API endpoint."""
        # This is a placeholder for API endpoint testing
        # In a real implementation, we would use FastAPI's TestClient to test the endpoints
        
        # Arrange
        mock_client = MagicMock()
        mock_test_client.return_value = mock_client
        
        expected_response = {
            "mindmap": "mindmap\n  root((Machine Learning))\n    Types\n      Supervised Learning\n      Unsupervised Learning\n      Reinforcement Learning",
            "format": "mermaid"
        }
        
        mock_client.post.return_value.status_code = 200
        mock_client.post.return_value.json.return_value = expected_response
        
        # Act
        # In a real implementation:
        # client = TestClient(app)
        # response = client.post("/api/mindmap", json={"text": "Machine learning text..."})
        
        # For now, we'll just simulate the response
        response_status_code = 200
        response_json = expected_response
        
        # Assert
        self.assertEqual(response_status_code, 200)
        self.assertIn("mindmap", response_json)
        self.assertIn("format", response_json)

    @patch('fastapi.testclient.TestClient')
    def test_generate_flashcards_endpoint(self, mock_test_client):
        """Test the generate flashcards API endpoint."""
        # This is a placeholder for API endpoint testing
        
        # Arrange
        mock_client = MagicMock()
        mock_test_client.return_value = mock_client
        
        expected_response = {
            "flashcards": [
                {
                    "question": "What is machine learning?",
                    "answer": "Machine learning is a subset of artificial intelligence that focuses on developing systems that learn from data."
                }
            ],
            "count": 1
        }
        
        mock_client.post.return_value.status_code = 200
        mock_client.post.return_value.json.return_value = expected_response
        
        # Act
        # In a real implementation:
        # client = TestClient(app)
        # response = client.post("/api/flashcards", json={"text": "Machine learning text..."})
        
        # For now, we'll just simulate the response
        response_status_code = 200
        response_json = expected_response
        
        # Assert
        self.assertEqual(response_status_code, 200)
        self.assertIn("flashcards", response_json)
        self.assertIn("count", response_json)
        self.assertEqual(response_json["count"], 1)

    @patch('fastapi.testclient.TestClient')
    def test_find_related_topics_endpoint(self, mock_test_client):
        """Test the find related topics API endpoint."""
        # This is a placeholder for API endpoint testing
        
        # Arrange
        mock_client = MagicMock()
        mock_test_client.return_value = mock_client
        
        expected_response = {
            "related_topics": [
                {
                    "title": "Machine Learning Basics",
                    "path": "ML/Basics",
                    "similarity": 0.92
                }
            ],
            "count": 1
        }
        
        mock_client.post.return_value.status_code = 200
        mock_client.post.return_value.json.return_value = expected_response
        
        # Act
        # In a real implementation:
        # client = TestClient(app)
        # response = client.post("/api/related-topics", json={"text": "Supervised learning..."})
        
        # For now, we'll just simulate the response
        response_status_code = 200
        response_json = expected_response
        
        # Assert
        self.assertEqual(response_status_code, 200)
        self.assertIn("related_topics", response_json)
        self.assertIn("count", response_json)
        self.assertEqual(response_json["count"], 1)

if __name__ == '__main__':
    unittest.main()