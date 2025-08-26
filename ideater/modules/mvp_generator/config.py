"""
Configuration module for the MVP Generator.

This module handles loading environment variables and configuration settings.
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger("ideater.modules.mvp_generator.config")

# Load environment variables from .env file
load_dotenv()

class MVPGeneratorConfig:
    """Configuration class for the MVP Generator module."""
    
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
        
        # Load GitHub token from environment variables
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found in environment variables. GitHub integration will be limited.")
        
        # Load GitHub username from environment variables
        self.github_username = os.getenv("GITHUB_USERNAME")
        if not self.github_username:
            logger.warning("GITHUB_USERNAME not found in environment variables. GitHub integration will be limited.")
        
        # Load boilerplate templates directory from environment variables or use default
        self.templates_dir = os.getenv("MVP_TEMPLATES_DIR", "templates/boilerplate")
        
        # Load feature prioritization method from environment variables or use default
        self.prioritization_method = os.getenv("MVP_PRIORITIZATION_METHOD", "RICE")  # RICE or MoSCoW
    
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
    
    def get_github_token(self) -> Optional[str]:
        """Get the GitHub token."""
        return self.github_token
    
    def get_github_username(self) -> Optional[str]:
        """Get the GitHub username."""
        return self.github_username
    
    def get_templates_dir(self) -> str:
        """Get the boilerplate templates directory."""
        return self.templates_dir
    
    def get_prioritization_method(self) -> str:
        """Get the feature prioritization method."""
        return self.prioritization_method
    
    def get_github_config(self) -> Dict[str, Any]:
        """Get the GitHub configuration."""
        return {
            "token": self.github_token,
            "username": self.github_username
        }

# Create a singleton instance
config = MVPGeneratorConfig()