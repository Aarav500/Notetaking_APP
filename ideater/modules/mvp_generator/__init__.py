"""
Auto-MVP Generator module for the Ideater application.

This module handles the generation of MVP checklists, feature prioritization,
fallback logic, and boilerplate repository generation.
"""

from .mvp_generator import (
    MVPGenerator,
    MVPChecklistRequest,
    MVPChecklistResult,
    Feature,
    FeaturePriority,
    FallbackLogicRequest,
    FallbackLogicResult,
    FallbackStrategy,
    BoilerplateRepoRequest,
    BoilerplateRepoResult
)

__all__ = [
    'MVPGenerator',
    'MVPChecklistRequest',
    'MVPChecklistResult',
    'Feature',
    'FeaturePriority',
    'FallbackLogicRequest',
    'FallbackLogicResult',
    'FallbackStrategy',
    'BoilerplateRepoRequest',
    'BoilerplateRepoResult'
]