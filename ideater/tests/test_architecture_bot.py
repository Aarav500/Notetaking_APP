"""
Tests for the Architecture & Tech Suggestion Bot module.
"""

import unittest
import os
import json
from unittest.mock import patch, MagicMock

# Import the module to test
from ideater.modules.architecture_bot.architecture_bot import (
    ArchitectureBot,
    ArchitectureRequest,
    ArchitectureResult,
    FrontendStack,
    BackendStack,
    DatabaseDesign,
    DevOpsOverview,
    RepoStructure
)

class TestArchitectureBot(unittest.TestCase):
    """Test cases for the Architecture & Tech Suggestion Bot module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock OpenAI API key for testing
        self.api_key = "test_api_key"
        
        # Create an instance of ArchitectureBot with the mock API key
        self.architecture_bot = ArchitectureBot(openai_api_key=self.api_key)
        
        # Create a sample request
        self.request = ArchitectureRequest(
            project_description="A web application that helps developers learn design patterns through interactive examples and quizzes",
            project_type="web",
            scale="medium",
            user_requirements=["Mobile responsive", "Offline access", "Interactive visualizations"],
            technical_constraints=["Must use modern JavaScript", "Must be accessible"],
            preferences={
                "frontend": ["React", "TypeScript"],
                "backend": ["Node.js"],
                "database": ["PostgreSQL"]
            }
        )
    
    @patch('openai.OpenAI')
    def test_generate_architecture(self, mock_openai):
        """Test the generate_architecture method."""
        # Set up mock response for frontend stack
        mock_frontend_response = MagicMock()
        mock_frontend_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "framework": "React",
                "ui_library": "Material-UI",
                "state_management": "Redux Toolkit",
                "styling_solution": "Styled Components",
                "build_tools": ["Webpack", "Babel"],
                "testing_tools": ["Jest", "React Testing Library"],
                "recommended_packages": [
                    {"name": "react-router", "purpose": "Routing"},
                    {"name": "axios", "purpose": "API requests"}
                ],
                "rationale": "React with TypeScript provides a robust foundation for interactive web applications."
            })))
        ]
        
        # Set up mock response for backend stack
        mock_backend_response = MagicMock()
        mock_backend_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "language": "JavaScript (Node.js)",
                "framework": "Express.js",
                "orm": "Sequelize",
                "api_style": "REST",
                "authentication": "JWT",
                "authorization": "Role-based access control",
                "recommended_packages": [
                    {"name": "passport", "purpose": "Authentication middleware"},
                    {"name": "joi", "purpose": "Data validation"}
                ],
                "rationale": "Express.js on Node.js provides a lightweight and flexible backend for web applications."
            })))
        ]
        
        # Set up mock response for database design
        mock_database_response = MagicMock()
        mock_database_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "database_type": "Relational",
                "recommended_system": "PostgreSQL",
                "schema_overview": [
                    {
                        "entity": "User",
                        "fields": ["id", "username", "email", "password_hash"],
                        "relationships": ["Has many Quizzes", "Has many Completions"]
                    },
                    {
                        "entity": "DesignPattern",
                        "fields": ["id", "name", "category", "description"],
                        "relationships": ["Has many Examples", "Has many Quizzes"]
                    }
                ],
                "indexing_strategy": "Index foreign keys and frequently queried fields",
                "scaling_approach": "Vertical scaling initially, with read replicas as needed",
                "rationale": "PostgreSQL provides robust ACID compliance and relational integrity for structured data."
            })))
        ]
        
        # Set up mock response for DevOps overview
        mock_devops_response = MagicMock()
        mock_devops_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "hosting_recommendation": "AWS",
                "ci_cd_pipeline": {
                    "provider": "GitHub Actions",
                    "stages": ["Lint", "Test", "Build", "Deploy"]
                },
                "deployment_strategy": "Blue-Green deployment",
                "monitoring_tools": ["AWS CloudWatch", "Sentry"],
                "logging_strategy": "Centralized logging with ELK stack",
                "security_considerations": ["HTTPS", "Input validation", "Rate limiting"],
                "cost_estimation": {
                    "monthly_estimate": "$100-$200",
                    "breakdown": ["Compute: $50-$100", "Database: $20-$50", "Other: $30-$50"]
                },
                "rationale": "AWS provides a comprehensive suite of services for hosting web applications."
            })))
        ]
        
        # Set up mock response for repository structure
        mock_repo_response = MagicMock()
        mock_repo_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "structure": {
                    "frontend": {
                        "src": {
                            "components": {},
                            "pages": {},
                            "hooks": {},
                            "utils": {}
                        },
                        "public": {}
                    },
                    "backend": {
                        "src": {
                            "controllers": {},
                            "models": {},
                            "routes": {},
                            "middleware": {}
                        }
                    }
                },
                "modularization_approach": "Feature-based modularization",
                "file_naming_conventions": {
                    "components": "PascalCase.tsx",
                    "hooks": "useHookName.ts",
                    "utils": "camelCase.ts"
                },
                "recommended_tools": [
                    {"name": "ESLint", "purpose": "Code linting"},
                    {"name": "Prettier", "purpose": "Code formatting"}
                ],
                "rationale": "This structure follows best practices for React and Node.js applications."
            })))
        ]
        
        # Set up mock response for recommendations and challenges
        mock_recommendations_response = MagicMock()
        mock_recommendations_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "general_recommendations": [
                    "Start with a minimum viable product (MVP)",
                    "Implement automated testing from the beginning",
                    "Use TypeScript for type safety"
                ],
                "potential_challenges": [
                    "Ensuring offline functionality works reliably",
                    "Creating interactive visualizations that work on mobile",
                    "Managing state across complex interactive examples"
                ]
            })))
        ]
        
        # Configure the mock to return the mock responses
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            mock_frontend_response,
            mock_backend_response,
            mock_database_response,
            mock_devops_response,
            mock_repo_response,
            mock_recommendations_response
        ]
        mock_openai.return_value = mock_client
        
        # Call the method being tested
        result = self.architecture_bot.generate_architecture(self.request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, ArchitectureResult)
        
        # Assert that the OpenAI API was called the expected number of times
        self.assertEqual(mock_client.chat.completions.create.call_count, 6)
        
        # Assert that the result contains the expected data
        self.assertEqual(result.frontend_stack.framework, "React")
        self.assertEqual(result.backend_stack.framework, "Express.js")
        self.assertEqual(result.database_design.recommended_system, "PostgreSQL")
        self.assertEqual(result.devops_overview.hosting_recommendation, "AWS")
        self.assertIn("frontend", result.repo_structure.structure)
        self.assertEqual(len(result.general_recommendations), 3)
        self.assertEqual(len(result.potential_challenges), 3)
    
    @patch('openai.OpenAI')
    def test_generate_frontend_stack(self, mock_openai):
        """Test the _generate_frontend_stack method."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "framework": "React",
                "ui_library": "Material-UI",
                "state_management": "Redux Toolkit",
                "styling_solution": "Styled Components",
                "build_tools": ["Webpack", "Babel"],
                "testing_tools": ["Jest", "React Testing Library"],
                "recommended_packages": [
                    {"name": "react-router", "purpose": "Routing"},
                    {"name": "axios", "purpose": "API requests"}
                ],
                "rationale": "React with TypeScript provides a robust foundation for interactive web applications."
            })))
        ]
        
        # Configure the mock to return the mock response
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Call the method being tested
        frontend_stack = self.architecture_bot._generate_frontend_stack(self.request)
        
        # Assert that the OpenAI API was called
        mock_client.chat.completions.create.assert_called_once()
        
        # Assert that the result is of the correct type
        self.assertIsInstance(frontend_stack, FrontendStack)
        
        # Assert that the result contains the expected data
        self.assertEqual(frontend_stack.framework, "React")
        self.assertEqual(frontend_stack.ui_library, "Material-UI")
        self.assertEqual(frontend_stack.state_management, "Redux Toolkit")
    
    def test_error_handling(self):
        """Test error handling in the generate_architecture method."""
        # Create a request with an empty project description
        empty_request = ArchitectureRequest(
            project_description="",
            project_type="web"
        )
        
        # Call the method being tested
        result = self.architecture_bot.generate_architecture(empty_request)
        
        # Assert that the result is of the correct type
        self.assertIsInstance(result, ArchitectureResult)
        
        # Assert that the result contains fallback values
        self.assertEqual(result.frontend_stack.framework, "React")
        self.assertEqual(result.backend_stack.language, "Python")
        self.assertEqual(result.database_design.database_type, "Relational")
        self.assertEqual(result.devops_overview.hosting_recommendation, "AWS (Amazon Web Services)")
        self.assertIn("src", result.repo_structure.structure)
        self.assertGreater(len(result.general_recommendations), 0)
        self.assertGreater(len(result.potential_challenges), 0)

if __name__ == '__main__':
    unittest.main()