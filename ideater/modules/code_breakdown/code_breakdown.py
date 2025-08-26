"""
Pseudo-Code + Task Breakdown module for the Ideater application.

This module provides functionality for generating pseudocode, API route mappings,
user stories, file structures, and function lists based on project descriptions.
"""

import os
import json
import logging
from enum import Enum
from typing import List, Dict, Any, Optional, Union

try:
    import openai
except ImportError:
    openai = None

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for when pydantic is not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(**kwargs):
        return None

from .config import config

# Set up logging
logger = logging.getLogger("ideater.modules.code_breakdown")

# Data Models
class ProgrammingLanguage(str, Enum):
    """Enum for programming languages."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    RUBY = "ruby"
    PHP = "php"
    SWIFT = "swift"
    KOTLIN = "kotlin"
    DART = "dart"
    OTHER = "other"

class APIFramework(str, Enum):
    """Enum for API frameworks."""
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    SOAP = "soap"
    WEBSOCKET = "websocket"
    OTHER = "other"

class PseudocodeRequest(BaseModel):
    """Request model for generating pseudocode."""
    description: str
    language: Optional[ProgrammingLanguage] = ProgrammingLanguage.PYTHON
    module_names: Optional[List[str]] = None
    include_comments: bool = True
    detail_level: str = "medium"  # "low", "medium", "high"

class PseudocodeResult(BaseModel):
    """Result model for generated pseudocode."""
    pseudocode: Dict[str, str]  # module_name -> pseudocode
    explanation: Optional[str] = None
    language: ProgrammingLanguage

class APIRouteRequest(BaseModel):
    """Request model for generating API routes."""
    description: str
    framework: Optional[APIFramework] = APIFramework.REST
    base_path: Optional[str] = None
    include_auth: bool = True
    include_validation: bool = True

class APIRoute(BaseModel):
    """Model for an API route."""
    path: str
    method: str
    description: str
    request_body: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None
    auth_required: bool = False
    parameters: Optional[List[Dict[str, Any]]] = None

class APIRouteResult(BaseModel):
    """Result model for generated API routes."""
    routes: List[APIRoute]
    explanation: Optional[str] = None
    framework: APIFramework
    base_path: Optional[str] = None

class UserStoryRequest(BaseModel):
    """Request model for generating user stories."""
    description: str
    user_roles: Optional[List[str]] = None
    format: str = "jira"  # "jira", "github", "plain"
    include_acceptance_criteria: bool = True
    include_priority: bool = True

class UserStory(BaseModel):
    """Model for a user story."""
    title: str
    description: str
    user_role: str
    acceptance_criteria: Optional[List[str]] = None
    priority: Optional[str] = None  # "high", "medium", "low"
    story_points: Optional[int] = None

class UserStoryResult(BaseModel):
    """Result model for generated user stories."""
    stories: List[UserStory]
    explanation: Optional[str] = None
    format: str

class FileStructureRequest(BaseModel):
    """Request model for generating file structure."""
    description: str
    language: Optional[ProgrammingLanguage] = ProgrammingLanguage.PYTHON
    framework: Optional[str] = None
    include_test_files: bool = True
    include_config_files: bool = True

class FileNode(BaseModel):
    """Model for a file or directory in the file structure."""
    name: str
    type: str  # "file" or "directory"
    description: Optional[str] = None
    children: Optional[List['FileNode']] = None

class FileStructureResult(BaseModel):
    """Result model for generated file structure."""
    root: FileNode
    explanation: Optional[str] = None
    language: ProgrammingLanguage
    framework: Optional[str] = None

class FunctionListRequest(BaseModel):
    """Request model for generating function list."""
    description: str
    language: Optional[ProgrammingLanguage] = ProgrammingLanguage.PYTHON
    module_names: Optional[List[str]] = None
    include_parameters: bool = True
    include_return_types: bool = True
    include_descriptions: bool = True

class Function(BaseModel):
    """Model for a function in the function list."""
    name: str
    module: str
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    return_type: Optional[str] = None
    complexity: Optional[str] = None  # "O(1)", "O(n)", etc.

class FunctionListResult(BaseModel):
    """Result model for generated function list."""
    functions: List[Function]
    explanation: Optional[str] = None
    language: ProgrammingLanguage

class CodeBreakdown:
    """
    Main class for the Pseudo-Code + Task Breakdown module.
    
    This class provides methods for generating pseudocode, API route mappings,
    user stories, file structures, and function lists based on project descriptions.
    """
    
    def __init__(self):
        """Initialize the CodeBreakdown."""
        self.openai_api_key = config.get_openai_api_key()
        self.openai_model = config.get_openai_model()
        self.temperature = config.get_temperature()
        self.max_tokens = config.get_max_tokens()
        self.github_token = config.get_github_token()
        self.jira_credentials = config.get_jira_credentials()
        
        # Initialize OpenAI client if available
        if openai and self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.client = openai.OpenAI()
        else:
            self.client = None
            logger.warning("OpenAI client not available. Some features may not work.")
    
    def generate_pseudocode(self, request: PseudocodeRequest) -> PseudocodeResult:
        """
        Generate pseudocode based on the request.
        
        Args:
            request: The pseudocode request.
            
        Returns:
            The pseudocode result.
        """
        logger.info(f"Generating pseudocode for language: {request.language}")
        
        # Generate pseudocode using OpenAI
        pseudocode = {}
        
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate pseudocode.")
            return PseudocodeResult(
                pseudocode={"main": "# OpenAI client not available\n# Please check your API key and try again"},
                language=request.language
            )
        
        try:
            # If module names are provided, generate pseudocode for each module
            if request.module_names:
                for module_name in request.module_names:
                    pseudocode[module_name] = self._generate_module_pseudocode(
                        description=request.description,
                        module_name=module_name,
                        language=request.language,
                        include_comments=request.include_comments,
                        detail_level=request.detail_level
                    )
            else:
                # Otherwise, generate a single pseudocode block
                pseudocode["main"] = self._generate_module_pseudocode(
                    description=request.description,
                    module_name="main",
                    language=request.language,
                    include_comments=request.include_comments,
                    detail_level=request.detail_level
                )
            
            # Generate explanation
            explanation = self._generate_pseudocode_explanation(
                description=request.description,
                pseudocode=pseudocode,
                language=request.language
            )
            
            return PseudocodeResult(
                pseudocode=pseudocode,
                explanation=explanation,
                language=request.language
            )
            
        except Exception as e:
            logger.error(f"Error generating pseudocode: {str(e)}")
            return PseudocodeResult(
                pseudocode={"error": f"# Error generating pseudocode: {str(e)}"},
                language=request.language
            )
    
    def generate_api_routes(self, request: APIRouteRequest) -> APIRouteResult:
        """
        Generate API routes based on the request.
        
        Args:
            request: The API route request.
            
        Returns:
            The API route result.
        """
        logger.info(f"Generating API routes for framework: {request.framework}")
        
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate API routes.")
            return APIRouteResult(
                routes=[
                    APIRoute(
                        path="/error",
                        method="GET",
                        description="Error: OpenAI client not available. Please check your API key and try again."
                    )
                ],
                framework=request.framework,
                base_path=request.base_path
            )
        
        try:
            # Create a prompt for generating the API routes
            prompt = f"""
            You are an expert API designer. Please generate API routes for a {request.framework.value.upper()} API based on the following project description:
            
            {request.description}
            """
            
            if request.base_path:
                prompt += f"\n\nBase path: {request.base_path}"
            
            prompt += f"\n\nInclude authentication: {request.include_auth}"
            prompt += f"\nInclude validation: {request.include_validation}"
            
            # Add framework-specific instructions
            if request.framework == APIFramework.REST:
                prompt += """
                \nFor each API route, please provide:
                1. Path (e.g., /users/{id})
                2. HTTP method (GET, POST, PUT, DELETE, etc.)
                3. Description
                4. Request body schema (if applicable)
                5. Response schema
                6. Whether authentication is required
                7. Path and query parameters (if applicable)
                
                Return the API routes in JSON format with the following structure:
                {
                    "routes": [
                        {
                            "path": "/example",
                            "method": "GET",
                            "description": "Example endpoint",
                            "request_body": null,
                            "response": {"example": "value"},
                            "auth_required": true,
                            "parameters": [
                                {"name": "param", "in": "query", "required": true, "type": "string"}
                            ]
                        }
                    ]
                }
                """
            elif request.framework == APIFramework.GRAPHQL:
                prompt += """
                \nPlease provide:
                1. Query types
                2. Mutation types
                3. Type definitions
                4. Resolver functions
                
                Return the GraphQL schema in JSON format with the following structure:
                {
                    "routes": [
                        {
                            "path": "Query.example",
                            "method": "query",
                            "description": "Example query",
                            "request_body": {"id": "ID!"},
                            "response": {"example": "ExampleType"},
                            "auth_required": true,
                            "parameters": []
                        }
                    ]
                }
                """
            elif request.framework == APIFramework.GRPC:
                prompt += """
                \nPlease provide:
                1. Service definitions
                2. Method definitions
                3. Message types
                
                Return the gRPC services in JSON format with the following structure:
                {
                    "routes": [
                        {
                            "path": "ExampleService.GetExample",
                            "method": "unary",
                            "description": "Get example by ID",
                            "request_body": {"id": "string"},
                            "response": {"example": "Example"},
                            "auth_required": true,
                            "parameters": []
                        }
                    ]
                }
                """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert API designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the API routes from the response
            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            
            # Parse the routes
            routes = []
            for route_data in data.get("routes", []):
                routes.append(APIRoute(**route_data))
            
            # Generate explanation
            explanation = self._generate_api_routes_explanation(
                description=request.description,
                routes=routes,
                framework=request.framework
            )
            
            return APIRouteResult(
                routes=routes,
                explanation=explanation,
                framework=request.framework,
                base_path=request.base_path
            )
            
        except Exception as e:
            logger.error(f"Error generating API routes: {str(e)}")
            return APIRouteResult(
                routes=[
                    APIRoute(
                        path="/error",
                        method="GET",
                        description=f"Error generating API routes: {str(e)}"
                    )
                ],
                framework=request.framework,
                base_path=request.base_path
            )
    
    def generate_user_stories(self, request: UserStoryRequest) -> UserStoryResult:
        """
        Generate user stories based on the request.
        
        Args:
            request: The user story request.
            
        Returns:
            The user story result.
        """
        logger.info(f"Generating user stories in format: {request.format}")
        
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate user stories.")
            return UserStoryResult(
                stories=[
                    UserStory(
                        title="Error: OpenAI client not available",
                        description="Please check your API key and try again.",
                        user_role="user"
                    )
                ],
                format=request.format
            )
        
        try:
            # Create a prompt for generating the user stories
            prompt = f"""
            You are an expert in agile development and user story creation. Please generate user stories based on the following project description:
            
            {request.description}
            """
            
            if request.user_roles:
                prompt += f"\n\nUser roles to consider: {', '.join(request.user_roles)}"
            else:
                prompt += "\n\nPlease identify appropriate user roles based on the project description."
            
            prompt += f"\n\nFormat: {request.format}"
            prompt += f"\nInclude acceptance criteria: {request.include_acceptance_criteria}"
            prompt += f"\nInclude priority: {request.include_priority}"
            
            # Add format-specific instructions
            if request.format == "jira":
                prompt += """
                \nPlease format the user stories in JIRA format:
                
                Title: As a [role], I want [feature] so that [benefit]
                Description: Additional details about the user story
                User Role: The role of the user
                Acceptance Criteria: List of criteria that must be met for the story to be considered complete
                Priority: High, Medium, or Low
                Story Points: Estimated effort (1, 2, 3, 5, 8, 13)
                
                Return the user stories in JSON format with the following structure:
                {
                    "stories": [
                        {
                            "title": "As a user, I want to log in so that I can access my account",
                            "description": "The user should be able to log in using their email and password.",
                            "user_role": "user",
                            "acceptance_criteria": ["User can enter email and password", "User can click login button", "User is redirected to dashboard on success"],
                            "priority": "high",
                            "story_points": 3
                        }
                    ]
                }
                """
            elif request.format == "github":
                prompt += """
                \nPlease format the user stories in GitHub issue format:
                
                Title: User Story: [Short description]
                Description: 
                **As a** [role]
                **I want** [feature]
                **So that** [benefit]
                
                Additional details about the user story
                
                **Acceptance Criteria:**
                - Criterion 1
                - Criterion 2
                
                **Priority:** High/Medium/Low
                
                Return the user stories in JSON format with the following structure:
                {
                    "stories": [
                        {
                            "title": "User Story: Login functionality",
                            "description": "**As a** user\\n**I want** to log in\\n**So that** I can access my account\\n\\nThe user should be able to log in using their email and password.",
                            "user_role": "user",
                            "acceptance_criteria": ["User can enter email and password", "User can click login button", "User is redirected to dashboard on success"],
                            "priority": "high",
                            "story_points": 3
                        }
                    ]
                }
                """
            else:  # plain
                prompt += """
                \nPlease format the user stories in plain format:
                
                Title: [Short description]
                Description: As a [role], I want [feature] so that [benefit]. Additional details about the user story.
                User Role: The role of the user
                Acceptance Criteria: List of criteria that must be met for the story to be considered complete
                Priority: High, Medium, or Low
                Story Points: Estimated effort (1, 2, 3, 5, 8, 13)
                
                Return the user stories in JSON format with the following structure:
                {
                    "stories": [
                        {
                            "title": "Login functionality",
                            "description": "As a user, I want to log in so that I can access my account. The user should be able to log in using their email and password.",
                            "user_role": "user",
                            "acceptance_criteria": ["User can enter email and password", "User can click login button", "User is redirected to dashboard on success"],
                            "priority": "high",
                            "story_points": 3
                        }
                    ]
                }
                """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert in agile development and user story creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the user stories from the response
            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            
            # Parse the stories
            stories = []
            for story_data in data.get("stories", []):
                # Remove acceptance criteria if not requested
                if not request.include_acceptance_criteria:
                    story_data.pop("acceptance_criteria", None)
                
                # Remove priority if not requested
                if not request.include_priority:
                    story_data.pop("priority", None)
                
                stories.append(UserStory(**story_data))
            
            # Generate explanation
            explanation = self._generate_user_stories_explanation(
                description=request.description,
                stories=stories,
                format=request.format
            )
            
            return UserStoryResult(
                stories=stories,
                explanation=explanation,
                format=request.format
            )
            
        except Exception as e:
            logger.error(f"Error generating user stories: {str(e)}")
            return UserStoryResult(
                stories=[
                    UserStory(
                        title=f"Error generating user stories",
                        description=f"Error: {str(e)}",
                        user_role="user"
                    )
                ],
                format=request.format
            )
    
    def generate_file_structure(self, request: FileStructureRequest) -> FileStructureResult:
        """
        Generate file structure based on the request.
        
        Args:
            request: The file structure request.
            
        Returns:
            The file structure result.
        """
        logger.info(f"Generating file structure for language: {request.language}")
        
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate file structure.")
            root = FileNode(
                name="project_root",
                type="directory",
                description="Error: OpenAI client not available. Please check your API key and try again.",
                children=[]
            )
            return FileStructureResult(
                root=root,
                language=request.language,
                framework=request.framework
            )
        
        try:
            # Create a prompt for generating the file structure
            prompt = f"""
            You are an expert software architect. Please generate a file structure for a project based on the following description:
            
            {request.description}
            
            Programming language: {request.language.value}
            """
            
            if request.framework:
                prompt += f"\nFramework: {request.framework}"
            
            prompt += f"\nInclude test files: {request.include_test_files}"
            prompt += f"\nInclude configuration files: {request.include_config_files}"
            
            # Add language-specific instructions
            if request.language == ProgrammingLanguage.PYTHON:
                prompt += """
                \nPlease follow Python best practices for project structure, including:
                - Use of packages and modules
                - Separation of concerns
                - Proper naming conventions
                - Inclusion of setup.py, requirements.txt, etc.
                """
            elif request.language in [ProgrammingLanguage.JAVASCRIPT, ProgrammingLanguage.TYPESCRIPT]:
                prompt += """
                \nPlease follow JavaScript/TypeScript best practices for project structure, including:
                - Use of modules and components
                - Separation of concerns
                - Proper naming conventions
                - Inclusion of package.json, tsconfig.json, etc.
                """
            elif request.language == ProgrammingLanguage.JAVA:
                prompt += """
                \nPlease follow Java best practices for project structure, including:
                - Use of packages and classes
                - Separation of concerns
                - Proper naming conventions
                - Inclusion of pom.xml or build.gradle
                """
            
            # Add framework-specific instructions
            if request.framework:
                if request.framework.lower() in ["django", "flask", "fastapi"]:
                    prompt += f"""
                    \nPlease follow {request.framework} best practices for project structure, including:
                    - Proper organization of apps/modules
                    - Separation of models, views, and templates/controllers
                    - Configuration files specific to {request.framework}
                    """
                elif request.framework.lower() in ["react", "vue", "angular"]:
                    prompt += f"""
                    \nPlease follow {request.framework} best practices for project structure, including:
                    - Proper organization of components
                    - Separation of state management, views, and services
                    - Configuration files specific to {request.framework}
                    """
                elif request.framework.lower() in ["spring", "spring boot"]:
                    prompt += f"""
                    \nPlease follow {request.framework} best practices for project structure, including:
                    - Proper organization of controllers, services, and repositories
                    - Separation of concerns
                    - Configuration files specific to {request.framework}
                    """
            
            prompt += """
            \nReturn the file structure in JSON format with the following structure:
            {
                "root": {
                    "name": "project_root",
                    "type": "directory",
                    "description": "Root directory of the project",
                    "children": [
                        {
                            "name": "src",
                            "type": "directory",
                            "description": "Source code directory",
                            "children": [
                                {
                                    "name": "main.py",
                                    "type": "file",
                                    "description": "Main entry point of the application"
                                }
                            ]
                        }
                    ]
                }
            }
            """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the file structure from the response
            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            
            # Parse the file structure
            root_data = data.get("root", {})
            
            # Create the root node
            root = self._create_file_node_from_dict(root_data)
            
            # Generate explanation
            explanation = self._generate_file_structure_explanation(
                description=request.description,
                root=root,
                language=request.language,
                framework=request.framework
            )
            
            return FileStructureResult(
                root=root,
                explanation=explanation,
                language=request.language,
                framework=request.framework
            )
            
        except Exception as e:
            logger.error(f"Error generating file structure: {str(e)}")
            root = FileNode(
                name="project_root",
                type="directory",
                description=f"Error generating file structure: {str(e)}",
                children=[]
            )
            return FileStructureResult(
                root=root,
                language=request.language,
                framework=request.framework
            )
    
    def _create_file_node_from_dict(self, data: Dict[str, Any]) -> FileNode:
        """
        Create a FileNode from a dictionary.
        
        Args:
            data: The dictionary containing file node data.
            
        Returns:
            The created FileNode.
        """
        children = None
        if "children" in data and data["children"]:
            children = [self._create_file_node_from_dict(child) for child in data["children"]]
        
        return FileNode(
            name=data.get("name", ""),
            type=data.get("type", ""),
            description=data.get("description"),
            children=children
        )
    
    def _generate_file_structure_explanation(
        self,
        description: str,
        root: FileNode,
        language: ProgrammingLanguage,
        framework: Optional[str] = None
    ) -> str:
        """
        Generate an explanation for the file structure.
        
        Args:
            description: The project description.
            root: The root node of the file structure.
            language: The programming language.
            framework: The framework (optional).
            
        Returns:
            The generated explanation.
        """
        try:
            # Create a prompt for generating the explanation
            prompt = f"""
            You are an expert software architect. Please explain the following file structure for a project based on this description:
            
            Project description:
            {description}
            
            Programming language: {language.value}
            """
            
            if framework:
                prompt += f"\nFramework: {framework}"
            
            prompt += "\n\nFile Structure:"
            prompt += self._format_file_node_for_prompt(root, 0)
            
            prompt += "\n\nPlease provide a clear and concise explanation of the file structure, including its purpose, organization, and how it addresses the project requirements. Also include any patterns or best practices used in the file structure design."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the explanation from the response
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating file structure explanation: {str(e)}")
            return f"Error generating explanation: {str(e)}"
    
    def _format_file_node_for_prompt(self, node: FileNode, level: int) -> str:
        """
        Format a file node for inclusion in a prompt.
        
        Args:
            node: The file node to format.
            level: The indentation level.
            
        Returns:
            The formatted file node.
        """
        indent = "    " * level
        result = f"\n{indent}- {node.name} ({node.type})"
        
        if node.description:
            result += f": {node.description}"
        
        if node.children:
            for child in node.children:
                result += self._format_file_node_for_prompt(child, level + 1)
        
        return result
    
    def generate_function_list(self, request: FunctionListRequest) -> FunctionListResult:
        """
        Generate function list based on the request.
        
        Args:
            request: The function list request.
            
        Returns:
            The function list result.
        """
        logger.info(f"Generating function list for language: {request.language}")
        
        # Check if OpenAI client is available
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate function list.")
            return FunctionListResult(
                functions=[
                    Function(
                        name="example_function",
                        module="main",
                        description="OpenAI client not available. Please check your API key and try again."
                    )
                ],
                language=request.language
            )
        
        try:
            # Create a prompt for generating the function list
            prompt = f"""
            You are an expert programmer. Based on the following project description, generate a list of functions that would be needed to implement this project:
            
            Project description:
            {request.description}
            
            Programming language: {request.language.value}
            
            For each function, provide:
            1. Function name (following {request.language.value} naming conventions)
            2. Module name (which module/file this function belongs to)
            """
            
            if request.include_descriptions:
                prompt += "\n3. Brief description of what the function does"
            
            if request.include_parameters:
                prompt += "\n4. Parameters (name and type)"
            
            if request.include_return_types:
                prompt += "\n5. Return type"
                
            if request.module_names:
                module_names_str = ", ".join(request.module_names)
                prompt += f"\n\nPlease focus on functions for the following modules: {module_names_str}"
            
            prompt += """
            
            Format your response as a JSON array with objects containing the following fields:
            {
                "name": "function_name",
                "module": "module_name",
                "description": "Function description",
                "parameters": [
                    {"name": "param_name", "type": "param_type", "description": "param description"}
                ],
                "return_type": "return type",
                "complexity": "time complexity (e.g., O(n))"
            }
            
            Note: The "complexity" field is optional and should be included only if you can reasonably estimate the time complexity.
            """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the function list from the response
            content = response.choices[0].message.content.strip()
            functions_data = json.loads(content)
            
            # Convert to Function objects
            functions = []
            for func_data in functions_data.get("functions", []):
                functions.append(
                    Function(
                        name=func_data.get("name", ""),
                        module=func_data.get("module", ""),
                        description=func_data.get("description"),
                        parameters=func_data.get("parameters"),
                        return_type=func_data.get("return_type"),
                        complexity=func_data.get("complexity")
                    )
                )
            
            # Generate explanation
            explanation = self._generate_function_list_explanation(
                description=request.description,
                functions=functions,
                language=request.language
            )
            
            return FunctionListResult(
                functions=functions,
                explanation=explanation,
                language=request.language
            )
            
        except Exception as e:
            logger.error(f"Error generating function list: {str(e)}")
            return FunctionListResult(
                functions=[
                    Function(
                        name="error_function",
                        module="error",
                        description=f"Error generating function list: {str(e)}"
                    )
                ],
                language=request.language
            )
    
    def _generate_function_list_explanation(
        self,
        description: str,
        functions: List[Function],
        language: ProgrammingLanguage
    ) -> str:
        """
        Generate an explanation for the function list.
        
        Args:
            description: The project description.
            functions: The list of functions.
            language: The programming language.
            
        Returns:
            The generated explanation.
        """
        try:
            # Create a prompt for generating the explanation
            prompt = f"""
            You are an expert programmer. Please explain the following function list for a project based on this description:
            
            Project description:
            {description}
            
            Programming language: {language.value}
            
            Function list:
            """
            
            # Add each function to the prompt
            for i, func in enumerate(functions, 1):
                prompt += f"\n\n{i}. {func.name} (in module: {func.module})"
                
                if func.description:
                    prompt += f"\n   Description: {func.description}"
                
                if func.parameters:
                    params_str = ", ".join([f"{p.get('name', '')}: {p.get('type', '')}" for p in func.parameters])
                    prompt += f"\n   Parameters: {params_str}"
                
                if func.return_type:
                    prompt += f"\n   Returns: {func.return_type}"
                
                if func.complexity:
                    prompt += f"\n   Complexity: {func.complexity}"
            
            prompt += """
            
            Please provide a clear and concise explanation of the function list, including:
            1. How the functions work together to fulfill the project requirements
            2. The overall architecture and design patterns reflected in the function list
            3. Any notable dependencies or relationships between functions
            4. How the functions are organized across modules
            5. Any potential improvements or considerations for the implementation
            """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer and software architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the explanation from the response
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating function list explanation: {str(e)}")
            return f"Error generating explanation: {str(e)}"
    
    def _generate_module_pseudocode(
        self,
        description: str,
        module_name: str,
        language: ProgrammingLanguage,
        include_comments: bool,
        detail_level: str
    ) -> str:
        """
        Generate pseudocode for a specific module.
        
        Args:
            description: The project description.
            module_name: The name of the module.
            language: The programming language.
            include_comments: Whether to include comments.
            detail_level: The level of detail.
            
        Returns:
            The generated pseudocode.
        """
        try:
            # Create a prompt for generating the pseudocode
            prompt = f"""
            You are an expert programmer. Please generate pseudocode for a module named '{module_name}' based on the following project description:
            
            {description}
            
            Programming language: {language.value}
            Detail level: {detail_level}
            """
            
            if include_comments:
                prompt += "\nPlease include detailed comments explaining the code."
            else:
                prompt += "\nPlease include minimal comments, only where necessary."
            
            prompt += f"\n\nReturn only the pseudocode for the '{module_name}' module without any additional text or explanation."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the pseudocode from the response
            pseudocode = response.choices[0].message.content.strip()
            
            return pseudocode
            
        except Exception as e:
            logger.error(f"Error generating pseudocode for module {module_name}: {str(e)}")
            return f"# Error generating pseudocode for module {module_name}: {str(e)}"
    
    def _generate_pseudocode_explanation(
        self,
        description: str,
        pseudocode: Dict[str, str],
        language: ProgrammingLanguage
    ) -> str:
        """
        Generate an explanation for the pseudocode.
        
        Args:
            description: The project description.
            pseudocode: The generated pseudocode.
            language: The programming language.
            
        Returns:
            The generated explanation.
        """
        try:
            # Create a prompt for generating the explanation
            prompt = f"""
            You are an expert programmer. Please explain the following pseudocode for a project based on this description:
            
            Project description:
            {description}
            
            Pseudocode:
            """
            
            for module_name, code in pseudocode.items():
                prompt += f"\n\nModule: {module_name}\n```{language.value}\n{code}\n```"
            
            prompt += "\n\nPlease provide a clear and concise explanation of the pseudocode, including its purpose, structure, and how it addresses the project requirements."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert programmer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the explanation from the response
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating pseudocode explanation: {str(e)}")
            return f"Error generating explanation: {str(e)}"
    
    def _generate_api_routes_explanation(
        self,
        description: str,
        routes: List[APIRoute],
        framework: APIFramework
    ) -> str:
        """
        Generate an explanation for the API routes.
        
        Args:
            description: The project description.
            routes: The generated API routes.
            framework: The API framework.
            
        Returns:
            The generated explanation.
        """
        try:
            # Create a prompt for generating the explanation
            prompt = f"""
            You are an expert API designer. Please explain the following {framework.value.upper()} API routes for a project based on this description:
            
            Project description:
            {description}
            
            API Routes:
            """
            
            for route in routes:
                prompt += f"\n\nPath: {route.path}"
                prompt += f"\nMethod: {route.method}"
                prompt += f"\nDescription: {route.description}"
                prompt += f"\nAuth Required: {route.auth_required}"
                
                if route.request_body:
                    prompt += f"\nRequest Body: {json.dumps(route.request_body, indent=2)}"
                
                if route.response:
                    prompt += f"\nResponse: {json.dumps(route.response, indent=2)}"
                
                if route.parameters:
                    prompt += f"\nParameters: {json.dumps(route.parameters, indent=2)}"
            
            prompt += "\n\nPlease provide a clear and concise explanation of the API routes, including their purpose, structure, and how they address the project requirements. Also include any patterns or best practices used in the API design."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert API designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the explanation from the response
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating API routes explanation: {str(e)}")
            return f"Error generating explanation: {str(e)}"
    
    def _generate_user_stories_explanation(
        self,
        description: str,
        stories: List[UserStory],
        format: str
    ) -> str:
        """
        Generate an explanation for the user stories.
        
        Args:
            description: The project description.
            stories: The generated user stories.
            format: The user story format.
            
        Returns:
            The generated explanation.
        """
        try:
            # Create a prompt for generating the explanation
            prompt = f"""
            You are an expert in agile development and user story creation. Please explain the following user stories for a project based on this description:
            
            Project description:
            {description}
            
            User Stories:
            """
            
            for i, story in enumerate(stories, 1):
                prompt += f"\n\n{i}. Title: {story.title}"
                prompt += f"\nDescription: {story.description}"
                prompt += f"\nUser Role: {story.user_role}"
                
                if story.acceptance_criteria:
                    criteria_text = "\n   - " + "\n   - ".join(story.acceptance_criteria)
                    prompt += f"\nAcceptance Criteria:{criteria_text}"
                
                if story.priority:
                    prompt += f"\nPriority: {story.priority}"
                
                if story.story_points:
                    prompt += f"\nStory Points: {story.story_points}"
            
            prompt += f"\n\nFormat: {format}"
            prompt += "\n\nPlease provide a clear and concise explanation of the user stories, including their purpose, coverage, and how they address the project requirements. Also include any patterns or best practices used in the user story creation."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert in agile development and user story creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the explanation from the response
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating user stories explanation: {str(e)}")
            return f"Error generating explanation: {str(e)}"