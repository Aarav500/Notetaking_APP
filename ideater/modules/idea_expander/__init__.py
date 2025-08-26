"""
Idea Expander module for the Ideater application.

This module handles the expansion of initial ideas into refined statements,
value propositions, unique selling points, competitor comparisons, and
feature prioritization matrices.
"""

from .idea_expander import (
    IdeaExpander,
    IdeaExpansionRequest,
    IdeaExpansionResult,
    ValueProposition,
    UniqueSellingPoint,
    CompetitorComparison,
    FeaturePriority
)

__all__ = [
    'IdeaExpander',
    'IdeaExpansionRequest',
    'IdeaExpansionResult',
    'ValueProposition',
    'UniqueSellingPoint',
    'CompetitorComparison',
    'FeaturePriority'
]