"""
Architecture & Tech Suggestion Bot module for the Ideater application.

This module handles the generation of architecture and technology stack suggestions,
database design recommendations, hosting/CI/CD/DevOps overviews, and code repository
structure plans.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple

# OpenAI is optional for tests and offline runs
try:
    import openai  # type: ignore
except Exception:
    # Create a minimal stub module so that tests using @patch('openai.OpenAI') still work
    import sys
    import types
    _stub = types.ModuleType('openai')
    class _OpenAIStub:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("openai package not installed; this is a stub. Tests should patch openai.OpenAI.")
    _stub.OpenAI = _OpenAIStub
    # allow setting api_key attribute without error
    _stub.api_key = None
    sys.modules['openai'] = _stub
    openai = _stub  # type: ignore
from pydantic import BaseModel

# Import configuration
from .config import config

# Set up logging
logger = logging.getLogger("ideater.modules.architecture_bot")

class ArchitectureRequest(BaseModel):
    """Request model for architecture and tech suggestions."""
    project_description: str
    project_type: str  # web, mobile, desktop, api, etc.
    scale: Optional[str] = None  # small, medium, large, enterprise
    user_requirements: Optional[List[str]] = None
    technical_constraints: Optional[List[str]] = None
    preferences: Optional[Dict[str, Any]] = None  # e.g., {"frontend": ["React", "Vue"], "database": ["PostgreSQL"]}

class FrontendStack(BaseModel):
    """Model for frontend stack suggestions."""
    framework: str
    ui_library: Optional[str] = None
    state_management: Optional[str] = None
    styling_solution: Optional[str] = None
    build_tools: Optional[List[str]] = None
    testing_tools: Optional[List[str]] = None
    recommended_packages: Optional[List[Dict[str, str]]] = None  # [{"name": "package-name", "purpose": "description"}]
    rationale: str

class BackendStack(BaseModel):
    """Model for backend stack suggestions."""
    language: str
    framework: str
    orm: Optional[str] = None
    api_style: Optional[str] = None  # REST, GraphQL, etc.
    authentication: Optional[str] = None
    authorization: Optional[str] = None
    recommended_packages: Optional[List[Dict[str, str]]] = None
    rationale: str

class DatabaseDesign(BaseModel):
    """Model for database design suggestions."""
    database_type: str  # relational, document, graph, etc.
    recommended_system: str  # PostgreSQL, MongoDB, etc.
    schema_overview: Optional[List[Dict[str, Any]]] = None  # [{"entity": "User", "fields": [...], "relationships": [...]}]
    indexing_strategy: Optional[str] = None
    scaling_approach: Optional[str] = None
    rationale: str

class DevOpsOverview(BaseModel):
    """Model for DevOps overview."""
    hosting_recommendation: str
    ci_cd_pipeline: Dict[str, Any]
    deployment_strategy: str
    monitoring_tools: List[str]
    logging_strategy: str
    security_considerations: List[str]
    cost_estimation: Optional[Dict[str, Any]] = None
    rationale: str

class RepoStructure(BaseModel):
    """Model for repository structure."""
    structure: Dict[str, Any]  # Nested dictionary representing folder structure
    modularization_approach: str
    file_naming_conventions: Dict[str, str]
    recommended_tools: List[Dict[str, str]]  # [{"name": "tool-name", "purpose": "description"}]
    rationale: str

class ArchitectureResult(BaseModel):
    """Result model for architecture and tech suggestions."""
    frontend_stack: FrontendStack
    backend_stack: BackendStack
    database_design: DatabaseDesign
    devops_overview: DevOpsOverview
    repo_structure: RepoStructure
    general_recommendations: List[str]
    potential_challenges: List[str]

class ArchitectureBot:
    """
    Architecture & Tech Suggestion Bot class that handles the generation of
    architecture and technology stack suggestions.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the Architecture Bot.
        
        Args:
            openai_api_key: OpenAI API key (optional, can be set via environment variable)
        """
        # Use provided API key or get from config
        self.openai_api_key = openai_api_key or config.get_openai_api_key()
        
        # Set OpenAI API key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("No OpenAI API key provided. API calls will fail.")
        
        # Get other configuration settings
        self.model = config.get_openai_model()
        self.temperature = config.get_temperature()
        self.max_tokens = config.get_max_tokens()
        
        logger.info(f"Initialized Architecture Bot with model: {self.model}")
    
    def generate_architecture(self, request: ArchitectureRequest) -> ArchitectureResult:
        """
        Generate architecture and tech suggestions based on the request.
        
        Args:
            request: The architecture request
            
        Returns:
            The architecture result
        """
        logger.info(f"Generating architecture for project type: {request.project_type}")
        
        # Generate frontend stack
        frontend_stack = self._generate_frontend_stack(request)
        
        # Generate backend stack
        backend_stack = self._generate_backend_stack(request)
        
        # Generate database design
        database_design = self._generate_database_design(request)
        
        # Generate DevOps overview
        devops_overview = self._generate_devops_overview(request)
        
        # Generate repository structure
        repo_structure = self._generate_repo_structure(request)
        
        # Generate general recommendations and potential challenges
        general_recommendations, potential_challenges = self._generate_recommendations_and_challenges(request)
        
        # Create and return the result
        result = ArchitectureResult(
            frontend_stack=frontend_stack,
            backend_stack=backend_stack,
            database_design=database_design,
            devops_overview=devops_overview,
            repo_structure=repo_structure,
            general_recommendations=general_recommendations,
            potential_challenges=potential_challenges
        )
        
        logger.info(f"Architecture generation completed for project type: {request.project_type}")
        return result
    
    def _generate_frontend_stack(self, request: ArchitectureRequest) -> FrontendStack:
        """Generate frontend stack suggestions."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this project description: "{request.project_description}"
            
            Generate a comprehensive frontend stack recommendation for a {request.project_type} project.
            
            Include:
            1. Main framework recommendation
            2. UI library recommendation
            3. State management solution
            4. Styling approach
            5. Build tools
            6. Testing tools
            7. Key packages/libraries to consider
            8. Rationale for these choices
            
            Format your response as a JSON object with the following structure:
            {{
                "framework": "string",
                "ui_library": "string",
                "state_management": "string",
                "styling_solution": "string",
                "build_tools": ["string"],
                "testing_tools": ["string"],
                "recommended_packages": [
                    {{"name": "package-name", "purpose": "description"}}
                ],
                "rationale": "string"
            }}
            """
            
            if request.scale:
                prompt += f"\nThe project scale is: {request.scale}"
                
            if request.user_requirements:
                requirements_str = ", ".join(request.user_requirements)
                prompt += f"\nUser requirements include: {requirements_str}"
                
            if request.technical_constraints:
                constraints_str = ", ".join(request.technical_constraints)
                prompt += f"\nTechnical constraints include: {constraints_str}"
                
            if request.preferences and "frontend" in request.preferences:
                preferences_str = ", ".join(request.preferences["frontend"])
                prompt += f"\nFrontend preferences include: {preferences_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect and frontend specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the frontend stack from the response
            content = response.choices[0].message.content.strip()
            frontend_data = json.loads(content)
            
            # Convert to FrontendStack object
            frontend_stack = FrontendStack(
                framework=frontend_data.get("framework", ""),
                ui_library=frontend_data.get("ui_library"),
                state_management=frontend_data.get("state_management"),
                styling_solution=frontend_data.get("styling_solution"),
                build_tools=frontend_data.get("build_tools"),
                testing_tools=frontend_data.get("testing_tools"),
                recommended_packages=frontend_data.get("recommended_packages"),
                rationale=frontend_data.get("rationale", "")
            )
            
            logger.info(f"Generated frontend stack with framework: {frontend_stack.framework}")
            return frontend_stack
            
        except Exception as e:
            logger.error(f"Error generating frontend stack: {str(e)}")
            # Fallback to default frontend stack
            return FrontendStack(
                framework="React",
                ui_library="Material-UI",
                state_management="Redux Toolkit",
                styling_solution="CSS Modules",
                build_tools=["Webpack", "Babel"],
                testing_tools=["Jest", "React Testing Library"],
                recommended_packages=[
                    {"name": "axios", "purpose": "HTTP client for API requests"},
                    {"name": "react-router", "purpose": "Routing solution"},
                    {"name": "formik", "purpose": "Form handling"}
                ],
                rationale=f"React is a widely-used, well-supported framework suitable for {request.project_type} applications. This stack provides a good balance of performance, developer experience, and community support."
            )
    
    def _generate_backend_stack(self, request: ArchitectureRequest) -> BackendStack:
        """Generate backend stack suggestions."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this project description: "{request.project_description}"
            
            Generate a comprehensive backend stack recommendation for a {request.project_type} project.
            
            Include:
            1. Programming language
            2. Framework
            3. ORM/database access layer
            4. API style (REST, GraphQL, etc.)
            5. Authentication approach
            6. Authorization strategy
            7. Key packages/libraries to consider
            8. Rationale for these choices
            
            Format your response as a JSON object with the following structure:
            {{
                "language": "string",
                "framework": "string",
                "orm": "string",
                "api_style": "string",
                "authentication": "string",
                "authorization": "string",
                "recommended_packages": [
                    {{"name": "package-name", "purpose": "description"}}
                ],
                "rationale": "string"
            }}
            """
            
            if request.scale:
                prompt += f"\nThe project scale is: {request.scale}"
                
            if request.user_requirements:
                requirements_str = ", ".join(request.user_requirements)
                prompt += f"\nUser requirements include: {requirements_str}"
                
            if request.technical_constraints:
                constraints_str = ", ".join(request.technical_constraints)
                prompt += f"\nTechnical constraints include: {constraints_str}"
                
            if request.preferences and "backend" in request.preferences:
                preferences_str = ", ".join(request.preferences["backend"])
                prompt += f"\nBackend preferences include: {preferences_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect and backend specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the backend stack from the response
            content = response.choices[0].message.content.strip()
            backend_data = json.loads(content)
            
            # Convert to BackendStack object
            backend_stack = BackendStack(
                language=backend_data.get("language", ""),
                framework=backend_data.get("framework", ""),
                orm=backend_data.get("orm"),
                api_style=backend_data.get("api_style"),
                authentication=backend_data.get("authentication"),
                authorization=backend_data.get("authorization"),
                recommended_packages=backend_data.get("recommended_packages"),
                rationale=backend_data.get("rationale", "")
            )
            
            logger.info(f"Generated backend stack with language: {backend_stack.language} and framework: {backend_stack.framework}")
            return backend_stack
            
        except Exception as e:
            logger.error(f"Error generating backend stack: {str(e)}")
            # Fallback to default backend stack
            return BackendStack(
                language="Python",
                framework="FastAPI",
                orm="SQLAlchemy",
                api_style="REST",
                authentication="JWT",
                authorization="Role-based access control",
                recommended_packages=[
                    {"name": "pydantic", "purpose": "Data validation and settings management"},
                    {"name": "alembic", "purpose": "Database migrations"},
                    {"name": "pytest", "purpose": "Testing framework"}
                ],
                rationale=f"Python with FastAPI provides a modern, high-performance framework suitable for {request.project_type} applications. This stack offers excellent developer productivity, type safety, and automatic API documentation."
            )
    
    def _generate_database_design(self, request: ArchitectureRequest) -> DatabaseDesign:
        """Generate database design suggestions."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this project description: "{request.project_description}"
            
            Generate a comprehensive database design recommendation for a {request.project_type} project.
            
            Include:
            1. Database type (relational, document, graph, etc.)
            2. Recommended database system
            3. High-level schema overview (main entities and relationships)
            4. Indexing strategy
            5. Scaling approach
            6. Rationale for these choices
            
            Format your response as a JSON object with the following structure:
            {{
                "database_type": "string",
                "recommended_system": "string",
                "schema_overview": [
                    {{
                        "entity": "string",
                        "fields": ["string"],
                        "relationships": ["string"]
                    }}
                ],
                "indexing_strategy": "string",
                "scaling_approach": "string",
                "rationale": "string"
            }}
            """
            
            if request.scale:
                prompt += f"\nThe project scale is: {request.scale}"
                
            if request.user_requirements:
                requirements_str = ", ".join(request.user_requirements)
                prompt += f"\nUser requirements include: {requirements_str}"
                
            if request.technical_constraints:
                constraints_str = ", ".join(request.technical_constraints)
                prompt += f"\nTechnical constraints include: {constraints_str}"
                
            if request.preferences and "database" in request.preferences:
                preferences_str = ", ".join(request.preferences["database"])
                prompt += f"\nDatabase preferences include: {preferences_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert database architect and designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the database design from the response
            content = response.choices[0].message.content.strip()
            database_data = json.loads(content)
            
            # Convert to DatabaseDesign object
            database_design = DatabaseDesign(
                database_type=database_data.get("database_type", ""),
                recommended_system=database_data.get("recommended_system", ""),
                schema_overview=database_data.get("schema_overview"),
                indexing_strategy=database_data.get("indexing_strategy"),
                scaling_approach=database_data.get("scaling_approach"),
                rationale=database_data.get("rationale", "")
            )
            
            logger.info(f"Generated database design with type: {database_design.database_type} and system: {database_design.recommended_system}")
            return database_design
            
        except Exception as e:
            logger.error(f"Error generating database design: {str(e)}")
            # Fallback to default database design
            return DatabaseDesign(
                database_type="Relational",
                recommended_system="PostgreSQL",
                schema_overview=[
                    {
                        "entity": "User",
                        "fields": ["id", "username", "email", "password_hash", "created_at"],
                        "relationships": ["Has many Projects"]
                    },
                    {
                        "entity": "Project",
                        "fields": ["id", "title", "description", "user_id", "created_at"],
                        "relationships": ["Belongs to User"]
                    }
                ],
                indexing_strategy="Index foreign keys and frequently queried fields",
                scaling_approach="Vertical scaling initially, with horizontal read replicas as needed",
                rationale=f"A relational database like PostgreSQL provides ACID compliance and structured data storage suitable for most {request.project_type} applications. It offers a good balance of features, performance, and ecosystem support."
            )
    
    def _generate_devops_overview(self, request: ArchitectureRequest) -> DevOpsOverview:
        """Generate DevOps overview."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this project description: "{request.project_description}"
            
            Generate a comprehensive DevOps overview for a {request.project_type} project.
            
            Include:
            1. Hosting recommendation
            2. CI/CD pipeline structure
            3. Deployment strategy
            4. Monitoring tools
            5. Logging strategy
            6. Security considerations
            7. Cost estimation (if possible)
            8. Rationale for these choices
            
            Format your response as a JSON object with the following structure:
            {{
                "hosting_recommendation": "string",
                "ci_cd_pipeline": {{
                    "provider": "string",
                    "stages": ["string"]
                }},
                "deployment_strategy": "string",
                "monitoring_tools": ["string"],
                "logging_strategy": "string",
                "security_considerations": ["string"],
                "cost_estimation": {{
                    "monthly_estimate": "string",
                    "breakdown": ["string"]
                }},
                "rationale": "string"
            }}
            """
            
            if request.scale:
                prompt += f"\nThe project scale is: {request.scale}"
                
            if request.user_requirements:
                requirements_str = ", ".join(request.user_requirements)
                prompt += f"\nUser requirements include: {requirements_str}"
                
            if request.technical_constraints:
                constraints_str = ", ".join(request.technical_constraints)
                prompt += f"\nTechnical constraints include: {constraints_str}"
                
            if request.preferences and "devops" in request.preferences:
                preferences_str = ", ".join(request.preferences["devops"])
                prompt += f"\nDevOps preferences include: {preferences_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert DevOps engineer and cloud architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the DevOps overview from the response
            content = response.choices[0].message.content.strip()
            devops_data = json.loads(content)
            
            # Convert to DevOpsOverview object
            devops_overview = DevOpsOverview(
                hosting_recommendation=devops_data.get("hosting_recommendation", ""),
                ci_cd_pipeline=devops_data.get("ci_cd_pipeline", {}),
                deployment_strategy=devops_data.get("deployment_strategy", ""),
                monitoring_tools=devops_data.get("monitoring_tools", []),
                logging_strategy=devops_data.get("logging_strategy", ""),
                security_considerations=devops_data.get("security_considerations", []),
                cost_estimation=devops_data.get("cost_estimation"),
                rationale=devops_data.get("rationale", "")
            )
            
            logger.info(f"Generated DevOps overview with hosting: {devops_overview.hosting_recommendation}")
            return devops_overview
            
        except Exception as e:
            logger.error(f"Error generating DevOps overview: {str(e)}")
            # Fallback to default DevOps overview
            return DevOpsOverview(
                hosting_recommendation="AWS (Amazon Web Services)",
                ci_cd_pipeline={
                    "provider": "GitHub Actions",
                    "stages": ["Lint", "Test", "Build", "Deploy"]
                },
                deployment_strategy="Blue-Green deployment",
                monitoring_tools=["AWS CloudWatch", "Prometheus", "Grafana"],
                logging_strategy="Centralized logging with ELK stack (Elasticsearch, Logstash, Kibana)",
                security_considerations=[
                    "HTTPS with TLS 1.3",
                    "Regular security audits",
                    "Dependency vulnerability scanning",
                    "AWS IAM with least privilege principle"
                ],
                cost_estimation={
                    "monthly_estimate": "$100-$300",
                    "breakdown": ["Compute: $50-$150", "Database: $20-$50", "Storage: $10-$30", "Other services: $20-$70"]
                },
                rationale=f"AWS provides a comprehensive suite of services suitable for {request.project_type} applications. This setup offers a good balance of reliability, scalability, and cost-effectiveness."
            )
    
    def _generate_repo_structure(self, request: ArchitectureRequest) -> RepoStructure:
        """Generate repository structure."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this project description: "{request.project_description}"
            
            Generate a comprehensive repository structure for a {request.project_type} project.
            
            Include:
            1. Folder structure (as a nested object)
            2. Modularization approach
            3. File naming conventions
            4. Recommended tools for code quality, linting, etc.
            5. Rationale for these choices
            
            Format your response as a JSON object with the following structure:
            {{
                "structure": {{
                    "folder_name": {{
                        "subfolder_name": ["file1.ext", "file2.ext"],
                        "another_subfolder": {{}}
                    }}
                }},
                "modularization_approach": "string",
                "file_naming_conventions": {{
                    "components": "string",
                    "tests": "string"
                }},
                "recommended_tools": [
                    {{"name": "tool-name", "purpose": "description"}}
                ],
                "rationale": "string"
            }}
            """
            
            if request.scale:
                prompt += f"\nThe project scale is: {request.scale}"
                
            if request.user_requirements:
                requirements_str = ", ".join(request.user_requirements)
                prompt += f"\nUser requirements include: {requirements_str}"
                
            if request.technical_constraints:
                constraints_str = ", ".join(request.technical_constraints)
                prompt += f"\nTechnical constraints include: {constraints_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect with deep knowledge of repository organization and best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the repository structure from the response
            content = response.choices[0].message.content.strip()
            repo_data = json.loads(content)
            
            # Convert to RepoStructure object
            repo_structure = RepoStructure(
                structure=repo_data.get("structure", {}),
                modularization_approach=repo_data.get("modularization_approach", ""),
                file_naming_conventions=repo_data.get("file_naming_conventions", {}),
                recommended_tools=repo_data.get("recommended_tools", []),
                rationale=repo_data.get("rationale", "")
            )
            
            logger.info(f"Generated repository structure with approach: {repo_structure.modularization_approach}")
            return repo_structure
            
        except Exception as e:
            logger.error(f"Error generating repository structure: {str(e)}")
            # Fallback to default repository structure
            return RepoStructure(
                structure={
                    "src": {
                        "components": {
                            "common": ["Button.js", "Card.js", "Input.js"],
                            "layout": ["Header.js", "Footer.js", "Sidebar.js"]
                        },
                        "pages": ["Home.js", "About.js", "Contact.js"],
                        "utils": ["api.js", "helpers.js", "constants.js"],
                        "hooks": ["useAuth.js", "useFetch.js"],
                        "context": ["AuthContext.js"]
                    },
                    "public": ["index.html", "favicon.ico", "robots.txt"],
                    "tests": {
                        "unit": {},
                        "integration": {},
                        "e2e": {}
                    },
                    "docs": ["README.md", "CONTRIBUTING.md", "LICENSE"],
                    "scripts": ["setup.js", "build.js"]
                },
                modularization_approach="Feature-based modularization with shared components",
                file_naming_conventions={
                    "components": "PascalCase.js",
                    "utils": "camelCase.js",
                    "tests": "ComponentName.test.js"
                },
                recommended_tools=[
                    {"name": "ESLint", "purpose": "Code linting and style enforcement"},
                    {"name": "Prettier", "purpose": "Code formatting"},
                    {"name": "Husky", "purpose": "Git hooks for pre-commit checks"},
                    {"name": "Jest", "purpose": "Testing framework"}
                ],
                rationale=f"This structure follows industry best practices for {request.project_type} applications, with a clear separation of concerns and modular organization. It balances flexibility with consistency and makes it easy for new developers to understand the codebase."
            )
    
    def _generate_recommendations_and_challenges(self, request: ArchitectureRequest) -> Tuple[List[str], List[str]]:
        """Generate general recommendations and potential challenges."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this project description: "{request.project_description}"
            
            Generate general recommendations and potential challenges for a {request.project_type} project.
            
            Format your response as a JSON object with the following structure:
            {{
                "general_recommendations": ["string"],
                "potential_challenges": ["string"]
            }}
            """
            
            if request.scale:
                prompt += f"\nThe project scale is: {request.scale}"
                
            if request.user_requirements:
                requirements_str = ", ".join(request.user_requirements)
                prompt += f"\nUser requirements include: {requirements_str}"
                
            if request.technical_constraints:
                constraints_str = ", ".join(request.technical_constraints)
                prompt += f"\nTechnical constraints include: {constraints_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software architect with experience in identifying project risks and success factors."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the recommendations and challenges from the response
            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            
            general_recommendations = data.get("general_recommendations", [])
            potential_challenges = data.get("potential_challenges", [])
            
            logger.info(f"Generated {len(general_recommendations)} recommendations and {len(potential_challenges)} challenges")
            return general_recommendations, potential_challenges
            
        except Exception as e:
            logger.error(f"Error generating recommendations and challenges: {str(e)}")
            # Fallback to default recommendations and challenges
            return [
                "Start with a minimum viable product (MVP) and iterate",
                "Implement automated testing from the beginning",
                "Use a consistent code style and documentation approach",
                "Consider accessibility requirements early in development",
                "Plan for scalability even if initial user base is small"
            ], [
                "Balancing feature scope with timeline constraints",
                "Ensuring consistent performance across different devices/browsers",
                "Managing technical debt during rapid development",
                "Securing user data and complying with relevant regulations",
                "Handling integration with third-party services reliably"
            ]