"""
End-to-end tests for user flows.
Tests the complete user flows from input to output.
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

class TestUserFlows(unittest.TestCase):
    """End-to-end tests for user flows."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
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
        
        # Create a sample text file
        self.text_file_path = os.path.join(self.temp_dir.name, "ml_basics.txt")
        with open(self.text_file_path, 'w') as f:
            f.write(self.sample_text)
        
        # Create a sample image file (mock)
        self.image_file_path = os.path.join(self.temp_dir.name, "ml_diagram.png")
        with open(self.image_file_path, 'w') as f:
            f.write("mock image content")
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        self.temp_dir.cleanup()

    @patch('ai_note_system.inputs.text_input.process_text')
    @patch('ai_note_system.visualization.mindmap_gen.generate_mindmap_from_llm')
    @patch('ai_note_system.processing.image_flashcards.generate_zero_shot_flashcards')
    def test_text_to_mindmap_and_flashcards_flow(self, mock_flashcards, mock_mindmap, mock_process_text):
        """Test the flow from text input to mind map and flashcards generation."""
        # Arrange
        processed_content = {
            "title": "Machine Learning Basics",
            "text": self.sample_text,
            "summary": "Overview of machine learning types including supervised, unsupervised, and reinforcement learning.",
            "keypoints": [
                "Machine learning is a subset of artificial intelligence.",
                "Supervised learning works with labeled data.",
                "Unsupervised learning works without labeled data.",
                "Reinforcement learning involves interaction with an environment."
            ]
        }
        
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
        
        mock_process_text.return_value = processed_content
        mock_mindmap.return_value = expected_mindmap
        mock_flashcards.return_value = expected_flashcards
        
        # Act - Simulate the user flow
        
        # Step 1: Process text input
        content = mock_process_text(self.text_file_path)
        
        # Step 2: Generate mind map from processed content
        mindmap = mock_mindmap(content["text"])
        
        # Step 3: Generate flashcards from processed content
        flashcards = mock_flashcards(
            input_path=self.text_file_path,
            input_type="text",
            output_dir=self.temp_dir.name,
            num_cards=2
        )
        
        # Assert
        self.assertEqual(content["title"], "Machine Learning Basics")
        self.assertEqual(mindmap, expected_mindmap)
        self.assertEqual(flashcards, expected_flashcards)
        mock_process_text.assert_called_once_with(self.text_file_path)
        mock_mindmap.assert_called_once_with(self.sample_text)
        mock_flashcards.assert_called_once()

    @patch('ai_note_system.inputs.ocr_input.process_image')
    @patch('ai_note_system.processing.image_flashcards.generate_qa_for_image')
    @patch('ai_note_system.visualization.image_mindmap.generate_mindmap_from_image')
    def test_image_to_flashcards_flow(self, mock_image_mindmap, mock_qa, mock_process_image):
        """Test the flow from image input to flashcards generation."""
        # Arrange
        processed_content = {
            "title": "Machine Learning Diagram",
            "text": "Extracted text from the machine learning diagram showing supervised, unsupervised, and reinforcement learning.",
            "image_path": self.image_file_path
        }
        
        expected_qa = {
            "question": "What are the three main branches of machine learning shown in the diagram?",
            "answer": "The diagram shows three main branches of machine learning: Supervised Learning, Unsupervised Learning, and Reinforcement Learning."
        }
        
        expected_mindmap = """mindmap
  root((Machine Learning Diagram))
    Supervised Learning
    Unsupervised Learning
    Reinforcement Learning"""
        
        mock_process_image.return_value = processed_content
        mock_qa.return_value = expected_qa
        mock_image_mindmap.return_value = expected_mindmap
        
        # Act - Simulate the user flow
        
        # Step 1: Process image input
        content = mock_process_image(self.image_file_path)
        
        # Step 2: Generate Q&A for the image
        qa_pair = mock_qa(
            image_path=content["image_path"],
            content_text=content["text"],
            title=content["title"]
        )
        
        # Step 3: Generate mind map from the image
        mindmap = mock_image_mindmap(content["image_path"])
        
        # Assert
        self.assertEqual(content["title"], "Machine Learning Diagram")
        self.assertEqual(qa_pair, expected_qa)
        self.assertEqual(mindmap, expected_mindmap)
        mock_process_image.assert_called_once_with(self.image_file_path)
        mock_qa.assert_called_once()
        mock_image_mindmap.assert_called_once_with(self.image_file_path)

    @patch('ai_note_system.inputs.text_input.process_text')
    @patch('ai_note_system.processing.topic_linker.create_topic_entry')
    @patch('ai_note_system.processing.topic_linker.update_topic_database')
    @patch('ai_note_system.processing.topic_linker.find_related_topics')
    def test_note_taking_and_linking_flow(self, mock_find_related, mock_update_db, mock_create_topic, mock_process_text):
        """Test the flow of taking notes and linking them to related topics."""
        # Arrange
        processed_content = {
            "title": "Machine Learning Basics",
            "text": self.sample_text,
            "summary": "Overview of machine learning types."
        }
        
        topic_entry = {
            "title": "Machine Learning Basics",
            "path": "ML/Basics",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "summary": "Overview of machine learning types."
        }
        
        related_topics = {
            "related_topics": [
                {
                    "title": "Deep Learning Fundamentals",
                    "path": "ML/Deep_Learning",
                    "similarity": 0.85
                },
                {
                    "title": "Neural Networks",
                    "path": "ML/Neural_Networks",
                    "similarity": 0.78
                }
            ],
            "count": 2
        }
        
        mock_process_text.return_value = processed_content
        mock_create_topic.return_value = topic_entry
        mock_update_db.return_value = True
        mock_find_related.return_value = related_topics
        
        # Create a mock topic database
        topic_db_path = os.path.join(self.temp_dir.name, "topic_db.json")
        with open(topic_db_path, 'w') as f:
            json.dump({"topics": []}, f)
        
        # Act - Simulate the user flow
        
        # Step 1: Process text input
        content = mock_process_text(self.text_file_path)
        
        # Step 2: Create topic entry
        topic = mock_create_topic(
            title=content["title"],
            text=content["text"],
            path="ML/Basics",
            summary=content["summary"]
        )
        
        # Step 3: Update topic database
        update_result = mock_update_db(topic_db_path, topic)
        
        # Step 4: Find related topics
        related = mock_find_related(
            "Neural networks are a type of supervised learning model.",
            topic_db_path,
            max_results=5,
            threshold=0.7
        )
        
        # Assert
        self.assertEqual(content["title"], "Machine Learning Basics")
        self.assertEqual(topic["title"], "Machine Learning Basics")
        self.assertTrue(update_result)
        self.assertEqual(related["count"], 2)
        self.assertEqual(related["related_topics"][0]["title"], "Deep Learning Fundamentals")
        mock_process_text.assert_called_once_with(self.text_file_path)
        mock_create_topic.assert_called_once()
        mock_update_db.assert_called_once_with(topic_db_path, topic)
        mock_find_related.assert_called_once()

    @patch('ai_note_system.inputs.youtube_input.process_youtube_video')
    @patch('ai_note_system.processing.image_flashcards.process_source_for_flashcards')
    def test_youtube_to_flashcards_flow(self, mock_process_source, mock_process_youtube):
        """Test the flow from YouTube video to flashcards generation."""
        # Arrange
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        processed_video = {
            "title": "Introduction to Machine Learning",
            "video_id": "dQw4w9WgXcQ",
            "transcript": "This is a transcript of the machine learning video...",
            "summary": "This video introduces machine learning concepts.",
            "keypoints": [
                "Machine learning is a subset of AI",
                "There are three main types of machine learning"
            ],
            "processed_segments": [
                {
                    "start": 0,
                    "end": 60,
                    "text": "Introduction to machine learning concepts",
                    "summary": "Brief overview of what machine learning is"
                },
                {
                    "start": 60,
                    "end": 120,
                    "text": "Types of machine learning explained",
                    "summary": "Explanation of supervised, unsupervised, and reinforcement learning"
                }
            ]
        }
        
        flashcard_result = {
            "success": True,
            "flashcards": [
                {
                    "question": "What is machine learning?",
                    "answer": "Machine learning is a subset of artificial intelligence that focuses on developing systems that learn from data."
                },
                {
                    "question": "What are the three main types of machine learning?",
                    "answer": "The three main types are supervised learning, unsupervised learning, and reinforcement learning."
                }
            ],
            "output_dir": os.path.join(self.temp_dir.name, "flashcards"),
            "json_path": os.path.join(self.temp_dir.name, "flashcards", "image_flashcards.json")
        }
        
        mock_process_youtube.return_value = processed_video
        mock_process_source.return_value = flashcard_result
        
        # Act - Simulate the user flow
        
        # Step 1: Process YouTube video
        video_content = mock_process_youtube(
            youtube_url=youtube_url,
            generate_summary=True,
            generate_keypoints=True,
            process_segments=True
        )
        
        # Step 2: Generate flashcards from the video
        flashcards = mock_process_source(
            source_path=youtube_url,
            source_type="video",
            content=video_content,
            output_dir=os.path.join(self.temp_dir.name, "flashcards"),
            num_cards=2
        )
        
        # Assert
        self.assertEqual(video_content["title"], "Introduction to Machine Learning")
        self.assertEqual(len(video_content["processed_segments"]), 2)
        self.assertTrue(flashcards["success"])
        self.assertEqual(len(flashcards["flashcards"]), 2)
        mock_process_youtube.assert_called_once()
        mock_process_source.assert_called_once()

if __name__ == '__main__':
    unittest.main()