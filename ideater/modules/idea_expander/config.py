"""
Configuration module for the Idea Expander.

This module handles loading environment variables and configuration settings.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger("ideater.modules.idea_expander.config")

# Load environment variables from .env file
load_dotenv()

class IdeaExpanderConfig:
    """Configuration class for the Idea Expander module."""
    
    def __init__(self):
        """Initialize the configuration."""
        # Load OpenAI API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        
        # Load OpenAI model from environment variables or use default
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        # Load temperature from environment variables or use default
        try:
            self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        except ValueError:
            logger.warning("Invalid OPENAI_TEMPERATURE value, using default 0.7")
            self.temperature = 0.7
        
        # Load max tokens from environment variables or use default
        try:
            self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        except ValueError:
            logger.warning("Invalid OPENAI_MAX_TOKENS value, using default 1000")
            self.max_tokens = 1000
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get the OpenAI API key."""
        return self.openai_api_key
    
    def get_openai_model(self) -> str:
        """Get the OpenAI model."""
        return self.openai_model
    
    def get_temperature(self) -> float:
        """Get the temperature for OpenAI API calls."""
        return self.temperature
    
    def get_max_tokens(self) -> int:
        """Get the max tokens for OpenAI API calls."""
        return self.max_tokens

# Create a singleton instance
config = IdeaExpanderConfig()