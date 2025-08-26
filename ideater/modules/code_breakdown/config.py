"""
Configuration module for the Code Breakdown module.

This module handles loading environment variables and configuration settings.
"""

import os
import logging
from typing import Optional

# Set up logging
logger = logging.getLogger("ideater.modules.code_breakdown.config")

# Try to import dotenv
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed. Using environment variables directly.")

class CodeBreakdownConfig:
    """Configuration class for the Code Breakdown module."""
    
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
            self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        except ValueError:
            logger.warning("Invalid OPENAI_MAX_TOKENS value, using default 2000")
            self.max_tokens = 2000
        
        # Load GitHub token from environment variables
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found in environment variables. GitHub integration may not work.")
        
        # Load JIRA API token from environment variables
        self.jira_token = os.getenv("JIRA_API_TOKEN")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_url = os.getenv("JIRA_URL")
        if not all([self.jira_token, self.jira_email, self.jira_url]):
            logger.warning("JIRA credentials not found in environment variables. JIRA integration may not work.")
    
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
    
    def get_jira_credentials(self) -> dict:
        """Get the JIRA credentials."""
        return {
            "token": self.jira_token,
            "email": self.jira_email,
            "url": self.jira_url
        }

# Create a singleton instance
config = CodeBreakdownConfig()