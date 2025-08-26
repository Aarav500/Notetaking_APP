"""
Tests for the Pseudo-Code + Task Breakdown module.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock

# Import the module to test
from ideater.modules.code_breakdown.code_breakdown import (
    CodeBreakdown,
    ProgrammingLanguage,
    PseudocodeRequest,
    PseudocodeResult,
    APIRouteRequest,
    APIRouteResult,
    UserStoryRequest,
    UserStoryResult,
    FileStructureRequest,
    FileStructureResult,
    FileNode,
    FunctionListRequest,
    FunctionListResult,
    Function
)

class TestCodeBreakdown(unittest.TestCase):
    """Test cases for the Pseudo-Code + Task Breakdown module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create an instance of CodeBreakdown
        self.code_breakdown = CodeBreakdown()
        
        # Sample project description for testing
        self.project_description = "A web application that helps students learn programming concepts through interactive exercises and quizzes."
    
    @patch('openai.OpenAI')
    def test_generate_pseudocode(self, mock_openai):
        """Test the generate_pseudocode method."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="def main():\n    # Initialize application\n    app = initialize_app()\n    \n    # Start the application\n    app.run()"))
        ]
        
        # Configure the mock to return the mock response
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        self.code_breakdown.client = mock_client
        
        # Create a request
        request = PseudocodeRequest(
            description=self.project_description,
            language=ProgrammingLanguage.PYTHON,
            module_names=["main"],
            include_comments=True,
            detail_level="medium"
        )
        
        # Call the method being tested
        result = self.code_breakdown.generate_pseudocode(request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, PseudocodeResult)
        
        # Assert that the OpenAI API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Assert that the result contains the expected data
        self.assertIn("main", result.pseudocode)
        self.assertEqual(result.language, ProgrammingLanguage.PYTHON)
    
    @patch('openai.OpenAI')
    def test_generate_api_routes(self, mock_openai):
        """Test the generate_api_routes method."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "routes": [
                    {
                        "path": "/api/exercises",
                        "method": "GET",
                        "description": "Get all exercises",
                        "parameters": [],
                        "response": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}, "title": {"type": "string"}}}}
                    }
                ]
            })))
        ]
        
        # Configure the mock to return the mock response
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        self.code_breakdown.client = mock_client
        
        # Create a request
        request = APIRouteRequest(
            description=self.project_description,
            api_style="REST",
            include_parameters=True,
            include_response_types=True
        )
        
        # Call the method being tested
        result = self.code_breakdown.generate_api_routes(request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, APIRouteResult)
        
        # Assert that the OpenAI API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Assert that the result contains the expected data
        self.assertEqual(len(result.routes), 1)
        self.assertEqual(result.routes[0].path, "/api/exercises")
        self.assertEqual(result.routes[0].method, "GET")
        self.assertEqual(result.api_style, "REST")
    
    @patch('openai.OpenAI')
    def test_generate_user_stories(self, mock_openai):
        """Test the generate_user_stories method."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "user_stories": [
                    {
                        "id": "US-001",
                        "role": "Student",
                        "goal": "complete interactive exercises",
                        "benefit": "to learn programming concepts",
                        "acceptance_criteria": ["Can access exercises", "Can submit solutions", "Can receive feedback"]
                    }
                ]
            })))
        ]
        
        # Configure the mock to return the mock response
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        self.code_breakdown.client = mock_client
        
        # Create a request
        request = UserStoryRequest(
            description=self.project_description,
            format="JIRA",
            include_acceptance_criteria=True,
            include_story_points=True
        )
        
        # Call the method being tested
        result = self.code_breakdown.generate_user_stories(request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, UserStoryResult)
        
        # Assert that the OpenAI API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Assert that the result contains the expected data
        self.assertEqual(len(result.user_stories), 1)
        self.assertEqual(result.user_stories[0].role, "Student")
        self.assertEqual(result.format, "JIRA")
    
    @patch('openai.OpenAI')
    def test_generate_file_structure(self, mock_openai):
        """Test the generate_file_structure method."""
        # Set up mock responses
        mock_structure_response = MagicMock()
        mock_structure_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "root": {
                    "name": "project_root",
                    "type": "directory",
                    "children": [
                        {
                            "name": "app.py",
                            "type": "file",
                            "description": "Main application entry point"
                        }
                    ]
                }
            })))
        ]
        
        mock_explanation_response = MagicMock()
        mock_explanation_response.choices = [
            MagicMock(message=MagicMock(content="This file structure follows a standard Python web application layout."))
        ]
        
        # Configure the mock to return the mock responses
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [mock_structure_response, mock_explanation_response]
        self.code_breakdown.client = mock_client
        
        # Create a request
        request = FileStructureRequest(
            description=self.project_description,
            language=ProgrammingLanguage.PYTHON,
            framework="Flask",
            include_descriptions=True
        )
        
        # Call the method being tested
        result = self.code_breakdown.generate_file_structure(request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, FileStructureResult)
        
        # Assert that the OpenAI API was called twice (once for structure, once for explanation)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        
        # Assert that the result contains the expected data
        self.assertEqual(result.root.name, "project_root")
        self.assertEqual(len(result.root.children), 1)
        self.assertEqual(result.root.children[0].name, "app.py")
        self.assertEqual(result.language, ProgrammingLanguage.PYTHON)
        self.assertEqual(result.framework, "Flask")
        self.assertIsNotNone(result.explanation)
    
    @patch('openai.OpenAI')
    def test_generate_function_list(self, mock_openai):
        """Test the generate_function_list method."""
        # Set up mock responses
        mock_functions_response = MagicMock()
        mock_functions_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "functions": [
                    {
                        "name": "initialize_app",
                        "module": "app",
                        "description": "Initialize the web application",
                        "parameters": [
                            {"name": "config", "type": "dict", "description": "Configuration settings"}
                        ],
                        "return_type": "Flask",
                        "complexity": "O(1)"
                    }
                ]
            })))
        ]
        
        mock_explanation_response = MagicMock()
        mock_explanation_response.choices = [
            MagicMock(message=MagicMock(content="This function list provides the core functionality for a Flask web application."))
        ]
        
        # Configure the mock to return the mock responses
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [mock_functions_response, mock_explanation_response]
        self.code_breakdown.client = mock_client
        
        # Create a request
        request = FunctionListRequest(
            description=self.project_description,
            language=ProgrammingLanguage.PYTHON,
            module_names=["app", "models", "views"],
            include_parameters=True,
            include_return_types=True,
            include_descriptions=True
        )
        
        # Call the method being tested
        result = self.code_breakdown.generate_function_list(request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, FunctionListResult)
        
        # Assert that the OpenAI API was called twice (once for functions, once for explanation)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        
        # Assert that the result contains the expected data
        self.assertEqual(len(result.functions), 1)
        self.assertEqual(result.functions[0].name, "initialize_app")
        self.assertEqual(result.functions[0].module, "app")
        self.assertEqual(result.language, ProgrammingLanguage.PYTHON)
        self.assertIsNotNone(result.explanation)
    
    def test_error_handling(self):
        """Test error handling in the CodeBreakdown class."""
        # Create a CodeBreakdown instance with no client
        code_breakdown = CodeBreakdown()
        code_breakdown.client = None
        
        # Test generate_pseudocode error handling
        result = code_breakdown.generate_pseudocode(PseudocodeRequest(
            description=self.project_description,
            language=ProgrammingLanguage.PYTHON
        ))
        self.assertIn("OpenAI client not available", list(result.pseudocode.values())[0])
        
        # Test generate_function_list error handling
        result = code_breakdown.generate_function_list(FunctionListRequest(
            description=self.project_description,
            language=ProgrammingLanguage.PYTHON
        ))
        self.assertEqual(len(result.functions), 1)
        self.assertEqual(result.functions[0].module, "main")
        self.assertIn("OpenAI client not available", result.functions[0].description)

if __name__ == '__main__':
    unittest.main()