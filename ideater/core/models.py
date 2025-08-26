"""
Database models for the Ideater application.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class ProjectStatus(enum.Enum):
    """Status of a project."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ModuleStatus(enum.Enum):
    """Status of a module."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OutputFormat(enum.Enum):
    """Format of an output."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    GITHUB = "github"
    NOTION = "notion"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="owner")


class Project(Base):
    """Project model for storing ideation projects."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    original_idea = Column(Text, nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    modules = relationship("Module", back_populates="project", cascade="all, delete-orphan")
    diagrams = relationship("Diagram", back_populates="project", cascade="all, delete-orphan")
    outputs = relationship("Output", back_populates="project", cascade="all, delete-orphan")


class Module(Base):
    """Module model for storing module-specific data."""
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    module_type = Column(String(50), nullable=False)  # idea_expander, architecture_bot, etc.
    status = Column(Enum(ModuleStatus), default=ModuleStatus.NOT_STARTED)
    data = Column(JSON)  # Store module-specific data as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="modules")


class Diagram(Base):
    """Diagram model for storing visualization data."""
    __tablename__ = "diagrams"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    diagram_type = Column(String(50), nullable=False)  # flowchart, sequence, state_machine, component
    content = Column(Text, nullable=False)  # Store diagram content (e.g., Mermaid or Graphviz code)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="diagrams")


class Output(Base):
    """Output model for storing generated outputs."""
    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    title = Column(String(100), nullable=False)
    description = Column(Text)
    format = Column(Enum(OutputFormat), nullable=False)
    content = Column(Text)  # For text-based outputs
    file_path = Column(String(255))  # For file-based outputs
    external_url = Column(String(255))  # For outputs stored externally (e.g., GitHub, Notion)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="outputs")


# Module-specific models

class IdeaExpander(Base):
    """Idea Expander module data."""
    __tablename__ = "idea_expander"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    refined_idea = Column(Text)
    value_propositions = Column(JSON)  # List of value propositions
    unique_selling_points = Column(JSON)  # List of USPs
    competitor_comparison = Column(JSON)  # Competitor comparison table
    feature_prioritization = Column(JSON)  # Feature prioritization matrix
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ArchitectureBot(Base):
    """Architecture & Tech Suggestion Bot module data."""
    __tablename__ = "architecture_bot"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    frontend_stack = Column(JSON)  # Frontend stack suggestions
    backend_stack = Column(JSON)  # Backend stack suggestions
    database_design = Column(JSON)  # Database design suggestions
    devops_overview = Column(JSON)  # DevOps overview
    repo_structure = Column(JSON)  # Repository structure
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FlowchartView(Base):
    """Flowchart & UX Ideation View module data."""
    __tablename__ = "flowchart_view"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    flowcharts = Column(JSON)  # List of flowcharts
    sequence_diagrams = Column(JSON)  # List of sequence diagrams
    state_machine_diagrams = Column(JSON)  # List of state machine diagrams
    component_diagrams = Column(JSON)  # List of component diagrams
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CodeBreakdown(Base):
    """Pseudo-Code + Task Breakdown module data."""
    __tablename__ = "code_breakdown"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    pseudocode = Column(JSON)  # Module-wise pseudocode
    api_routes = Column(JSON)  # API route mapping
    user_stories = Column(JSON)  # User stories in JIRA format
    file_structure = Column(JSON)  # Suggested file structure
    function_list = Column(JSON)  # List of functions to implement
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MVPGenerator(Base):
    """Auto-MVP Generator module data."""
    __tablename__ = "mvp_generator"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    mvp_checklist = Column(JSON)  # MVP checklist
    feature_priority = Column(JSON)  # Feature prioritization
    fallback_logic = Column(JSON)  # Fallback logic
    boilerplate_repo_url = Column(String(255))  # URL to boilerplate repo
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestPlanGenerator(Base):
    """Testing and Debug Plan Generator module data."""
    __tablename__ = "test_plan_generator"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    unit_test_structure = Column(JSON)  # Unit test structure
    test_scenarios = Column(JSON)  # Test scenarios
    mock_apis = Column(JSON)  # Mock API definitions
    edge_cases = Column(JSON)  # Edge cases
    test_data = Column(JSON)  # Test data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RoadmapAssistant(Base):
    """Growth & Future Roadmap Assistant module data."""
    __tablename__ = "roadmap_assistant"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    feature_timeline = Column(JSON)  # Feature timeline
    scalability_plan = Column(JSON)  # Scalability plan
    ai_integration_roadmap = Column(JSON)  # AI integration roadmap
    monetization_options = Column(JSON)  # Monetization options
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WhiteboardCollaboration(Base):
    """AI Whiteboard Collaboration module data."""
    __tablename__ = "whiteboard_collaboration"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"))
    whiteboard_data = Column(JSON)  # Whiteboard data
    agent_interactions = Column(JSON)  # Agent interactions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)