"""
Unit tests for the mind map generation module.
"""

import unittest
from unittest.mock import patch, MagicMock

# Import the module to test
from ai_note_system.visualization.mindmap_gen import (
    generate_mindmap_from_llm,
    _generate_mindmap_with_openai,
    _generate_mindmap_with_huggingface,
    extract_mindmap_from_text
)

class TestMindMapGeneration(unittest.TestCase):
    """Test cases for the mind map generation module."""

    def setUp(self):
        """Set up test environment."""
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
        
        ## Common Algorithms
        
        - Linear Regression
        - Decision Trees
        - Neural Networks
        - Support Vector Machines
        - K-Means Clustering
        """
        
        self.expected_mindmap_structure = """mindmap
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
        Policy Gradient
    Algorithms
      Linear Regression
      Decision Trees
      Neural Networks
      Support Vector Machines
      K-Means Clustering"""

    @patch('ai_note_system.visualization.mindmap_gen._generate_mindmap_with_openai')
    def test_generate_mindmap_from_llm_openai(self, mock_openai_gen):
        """Test generate_mindmap_from_llm with OpenAI model."""
        # Arrange
        mock_openai_gen.return_value = self.expected_mindmap_structure
        
        # Act
        result = generate_mindmap_from_llm(self.sample_text, model="gpt-4")
        
        # Assert
        self.assertEqual(result, self.expected_mindmap_structure)
        mock_openai_gen.assert_called_once_with(self.sample_text, "gpt-4", None)

    @patch('ai_note_system.visualization.mindmap_gen._generate_mindmap_with_huggingface')
    def test_generate_mindmap_from_llm_huggingface(self, mock_hf_gen):
        """Test generate_mindmap_from_llm with Hugging Face model."""
        # Arrange
        mock_hf_gen.return_value = self.expected_mindmap_structure
        
        # Act
        result = generate_mindmap_from_llm(self.sample_text, model="mistral-7b-instruct")
        
        # Assert
        self.assertEqual(result, self.expected_mindmap_structure)
        mock_hf_gen.assert_called_once_with(self.sample_text, "mistral-7b-instruct", None)

    @patch('ai_note_system.visualization.mindmap_gen.extract_mindmap_from_text')
    def test_generate_mindmap_from_llm_fallback(self, mock_extract):
        """Test generate_mindmap_from_llm with unsupported model."""
        # Arrange
        mock_extract.return_value = self.expected_mindmap_structure
        
        # Act
        result = generate_mindmap_from_llm(self.sample_text, model="unsupported-model")
        
        # Assert
        self.assertEqual(result, self.expected_mindmap_structure)
        mock_extract.assert_called_once_with(self.sample_text, None)

    @patch('openai.OpenAI')
    def test_generate_mindmap_with_openai(self, mock_openai):
        """Test _generate_mindmap_with_openai function."""
        # Arrange
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = f"```mermaid\n{self.expected_mindmap_structure}\n```"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Act
        result = _generate_mindmap_with_openai(self.sample_text, model="gpt-4")
        
        # Assert
        self.assertEqual(result, self.expected_mindmap_structure)
        mock_client.chat.completions.create.assert_called_once()

    @patch('transformers.pipeline')
    def test_generate_mindmap_with_huggingface(self, mock_pipeline):
        """Test _generate_mindmap_with_huggingface function."""
        # Arrange
        mock_pipe = MagicMock()
        mock_pipeline.return_value = mock_pipe
        
        mock_pipe.return_value = [{"generated_text": f"```mermaid\n{self.expected_mindmap_structure}\n```"}]
        
        # Act
        result = _generate_mindmap_with_huggingface(self.sample_text, model="mistral-7b-instruct")
        
        # Assert
        self.assertEqual(result, self.expected_mindmap_structure)
        mock_pipeline.assert_called_once()

    def test_extract_mindmap_from_text(self):
        """Test extract_mindmap_from_text function."""
        # Act
        result = extract_mindmap_from_text(self.sample_text)
        
        # Assert
        self.assertIn("mindmap", result)
        self.assertIn("Machine Learning", result)
        self.assertIn("Supervised Learning", result)
        self.assertIn("Unsupervised Learning", result)
        self.assertIn("Reinforcement Learning", result)

if __name__ == '__main__':
    unittest.main()