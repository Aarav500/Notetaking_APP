"""
Configuration module for the Flowchart View.

This module handles loading environment variables and configuration settings.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger("ideater.modules.flowchart_view.config")

# Load environment variables from .env file
load_dotenv()

class FlowchartViewConfig:
    """Configuration class for the Flowchart View module."""
    
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
        
        # Load Mermaid CLI path from environment variables or use default
        self.mermaid_cli_path = os.getenv("MERMAID_CLI_PATH", "mmdc")
        
        # Load Graphviz path from environment variables or use default
        self.graphviz_path = os.getenv("GRAPHVIZ_PATH", "dot")
    
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
    
    def get_mermaid_cli_path(self) -> str:
        """Get the path to the Mermaid CLI executable."""
        return self.mermaid_cli_path
    
    def get_graphviz_path(self) -> str:
        """Get the path to the Graphviz dot executable."""
        return self.graphviz_path

# Create a singleton instance
config = FlowchartViewConfig()