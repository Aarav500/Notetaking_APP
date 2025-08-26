"""
Processing pipeline package for AI Note System.
Contains modules for processing text input into structured notes.
"""

# Import modules to make them available when importing the package
from . import summarizer
from . import keypoints_extractor
from . import active_recall_gen
from . import topic_linker
from . import misconception_checker
from . import simplifier

# Export key functions for easier access
from .summarizer import summarize_text
from .keypoints_extractor import extract_keypoints, extract_glossary
from .active_recall_gen import generate_questions, generate_mcqs, generate_fill_blanks
from .topic_linker import find_related_topics, create_topic_entry, update_topic_database
from .misconception_checker import check_misconceptions, simplify_explanation
from .simplifier import simplify_text, explain_concept, eli5

__all__ = [
    'summarizer',
    'keypoints_extractor',
    'active_recall_gen',
    'topic_linker',
    'misconception_checker',
    'simplifier',
    'summarize_text',
    'extract_keypoints',
    'extract_glossary',
    'generate_questions',
    'generate_mcqs',
    'generate_fill_blanks',
    'find_related_topics',
    'create_topic_entry',
    'update_topic_database',
    'check_misconceptions',
    'simplify_explanation',
    'simplify_text',
    'explain_concept',
    'eli5'
]