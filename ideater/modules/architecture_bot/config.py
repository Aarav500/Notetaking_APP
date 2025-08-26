"""
Configuration module for the Architecture Bot.

This module handles loading environment variables and configuration settings.
"""

import os
import logging
from typing import Optional

# Make python-dotenv optional for lightweight test environments
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - fallback when dotenv not installed
    def load_dotenv(*args, **kwargs):
        return False

# Set up logging
logger = logging.getLogger("ideater.modules.architecture_bot.config")

# Load environment variables from .env file (no-op if fallback)
load_dotenv()

class ArchitectureBotConfig:
    """Configuration class for the Architecture Bot module."""
    
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
            self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
        except ValueError:
            logger.warning("Invalid OPENAI_MAX_TOKENS value, using default 1500")
            self.max_tokens = 1500
    
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
config = ArchitectureBotConfig()