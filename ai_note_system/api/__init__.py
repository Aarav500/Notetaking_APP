"""
API module for AI Note System.
Provides interfaces for LLMs and embeddings.
"""

from .llm_interface import LLMInterface, get_llm_interface
from .embedding_interface import EmbeddingInterface, get_embedding_interface, create_embedding_interface_from_config