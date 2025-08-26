"""
Architecture & Tech Suggestion Bot module for the Ideater application.

This module handles the generation of architecture and technology stack suggestions,
database design recommendations, hosting/CI/CD/DevOps overviews, and code repository
structure plans.
"""

from .architecture_bot import (
    ArchitectureBot,
    ArchitectureRequest,
    ArchitectureResult,
    FrontendStack,
    BackendStack,
    DatabaseDesign,
    DevOpsOverview,
    RepoStructure
)

__all__ = [
    'ArchitectureBot',
    'ArchitectureRequest',
    'ArchitectureResult',
    'FrontendStack',
    'BackendStack',
    'DatabaseDesign',
    'DevOpsOverview',
    'RepoStructure'
]