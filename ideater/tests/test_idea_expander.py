"""
Tests for the Idea Expander module.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock

# Import the module to test
from ideater.modules.idea_expander.idea_expander import (
    IdeaExpander,
    IdeaExpansionRequest,
    IdeaExpansionResult,
    ValueProposition,
    UniqueSellingPoint,
    CompetitorComparison,
    FeaturePriority
)

class TestIdeaExpander(unittest.TestCase):
    """Test cases for the Idea Expander module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock OpenAI API key for testing
        self.api_key = "test_api_key"
        
        # Create an instance of IdeaExpander with the mock API key
        self.idea_expander = IdeaExpander(openai_api_key=self.api_key)
        
        # Create a sample request
        self.request = IdeaExpansionRequest(
            original_idea="An app that helps students learn algorithms better",
            industry="Education",
            target_audience="Computer Science Students",
            constraints=["Mobile-friendly", "Offline access"]
        )
    
    @patch('openai.OpenAI')
    def test_expand_idea(self, mock_openai):
        """Test the expand_idea method."""
        # Set up mock response for refined idea
        mock_refined_idea_response = MagicMock()
        mock_refined_idea_response.choices = [
            MagicMock(message=MagicMock(content="AlgoLearn: An interactive mobile application that helps computer science students master algorithms through visualizations, step-by-step explanations, and practice problems, with offline access for learning anywhere."))
        ]
        
        # Set up mock response for value propositions
        mock_value_props_response = MagicMock()
        mock_value_props_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps([
                {
                    "title": "Visual Learning",
                    "description": "Interactive visualizations of algorithms in action",
                    "impact": "Students understand complex concepts 40% faster"
                },
                {
                    "title": "Practice Anywhere",
                    "description": "Offline access to all learning materials",
                    "impact": "Increases study time by allowing learning in any environment"
                },
                {
                    "title": "Personalized Path",
                    "description": "Adaptive learning path based on student performance",
                    "impact": "Improves mastery by focusing on areas needing improvement"
                }
            ])))
        ]
        
        # Set up mock response for USPs
        mock_usps_response = MagicMock()
        mock_usps_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps([
                {
                    "point": "Algorithm Visualization",
                    "description": "Interactive, step-by-step visualization of how algorithms work",
                    "differentiation": "Unlike textbooks or videos, students can manipulate inputs and see results in real-time"
                },
                {
                    "point": "Offline Learning",
                    "description": "Full functionality without internet connection",
                    "differentiation": "Competitors require constant internet access, limiting where students can study"
                }
            ])))
        ]
        
        # Set up mock response for competitor comparison
        mock_competitor_comparison_response = MagicMock()
        mock_competitor_comparison_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "competitors": [
                    {"name": "AlgoExpert", "description": "Online platform for algorithm practice"},
                    {"name": "LeetCode", "description": "Coding challenge platform"}
                ],
                "comparison_matrix": {
                    "Visualization": {"Your Idea": "Yes", "AlgoExpert": "Partial", "LeetCode": "No"},
                    "Offline Access": {"Your Idea": "Yes", "AlgoExpert": "No", "LeetCode": "No"}
                },
                "advantages": ["Better visualization", "Offline access"],
                "disadvantages": ["Fewer practice problems", "New entrant"]
            })))
        ]
        
        # Set up mock response for feature prioritization
        mock_feature_prioritization_response = MagicMock()
        mock_feature_prioritization_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps([
                {
                    "feature": "Algorithm Visualizations",
                    "score": {"Reach": 10, "Impact": 9, "Confidence": 8, "Effort": 7},
                    "priority": "High",
                    "rationale": "Core feature that directly addresses the main value proposition"
                },
                {
                    "feature": "Offline Mode",
                    "score": {"Reach": 8, "Impact": 7, "Confidence": 9, "Effort": 6},
                    "priority": "High",
                    "rationale": "Key differentiator that enables learning anywhere"
                }
            ])))
        ]
        
        # Configure the mock to return the mock responses
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            mock_refined_idea_response,
            mock_value_props_response,
            mock_usps_response,
            mock_competitor_comparison_response,
            mock_feature_prioritization_response
        ]
        mock_openai.return_value = mock_client
        
        # Call the method being tested
        result = self.idea_expander.expand_idea(self.request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, IdeaExpansionResult)
        
        # Assert that the OpenAI API was called the expected number of times
        self.assertEqual(mock_client.chat.completions.create.call_count, 5)
        
        # Assert that the result contains the expected data
        self.assertEqual(result.refined_idea, "AlgoLearn: An interactive mobile application that helps computer science students master algorithms through visualizations, step-by-step explanations, and practice problems, with offline access for learning anywhere.")
        self.assertEqual(len(result.value_propositions), 3)
        self.assertEqual(len(result.unique_selling_points), 2)
        self.assertIsNotNone(result.competitor_comparison)
        self.assertEqual(len(result.feature_prioritization), 2)
    
    @patch('openai.OpenAI')
    def test_generate_refined_idea(self, mock_openai):
        """Test the _generate_refined_idea method."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="AlgoLearn: An interactive mobile application that helps computer science students master algorithms through visualizations, step-by-step explanations, and practice problems, with offline access for learning anywhere."))
        ]
        
        # Configure the mock to return the mock response
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Call the method being tested
        refined_idea = self.idea_expander._generate_refined_idea(self.request)
        
        # Assert that the OpenAI API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Assert that the result is as expected
        self.assertEqual(refined_idea, "AlgoLearn: An interactive mobile application that helps computer science students master algorithms through visualizations, step-by-step explanations, and practice problems, with offline access for learning anywhere.")
    
    def test_error_handling(self):
        """Test error handling in the expand_idea method."""
        # Create a request with an empty original idea
        empty_request = IdeaExpansionRequest(original_idea="")
        
        # Call the method being tested
        result = self.idea_expander.expand_idea(empty_request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, IdeaExpansionResult)
        
        # Assert that the result contains fallback values
        self.assertTrue(result.refined_idea.startswith("Refined version of:"))
        self.assertGreater(len(result.value_propositions), 0)
        self.assertGreater(len(result.unique_selling_points), 0)
        self.assertIsNotNone(result.competitor_comparison)
        self.assertGreater(len(result.feature_prioritization), 0)

if __name__ == '__main__':
    unittest.main()