"""
Agents module for AI Note System.
Provides intelligent agents for personalized learning and quiz generation.
"""

from .learning_agent import LearningAgent, LearningStyle, KnowledgeLevel, create_learning_agent_from_config
from .quiz_agent import QuizAgent, QuizType, DifficultyLevel, create_quiz_agent_from_config