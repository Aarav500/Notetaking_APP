"""
API fallback module for AI Note System.
Provides fallback mechanisms for API changes in critical dependencies.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional, Union, Callable

# Create a logger for this module
logger = logging.getLogger("ai_note_system.utils.api_fallback")

# Import dependency checker
from .dependency_checker import optional_dependency

class APIFallbackManager:
    """
    Manager for handling API fallbacks.
    Provides mechanisms to handle API changes in critical dependencies.
    """
    
    def __init__(self):
        """Initialize the API fallback manager."""
        self.fallbacks = {}
        self.register_default_fallbacks()
    
    def register_fallback(self, api_name: str, function_name: str, fallback_function: Callable) -> None:
        """
        Register a fallback function for an API function.
        
        Args:
            api_name (str): Name of the API (e.g., "openai")
            function_name (str): Name of the function (e.g., "Completion.create")
            fallback_function (Callable): Fallback function to use if the original function fails
        """
        if api_name not in self.fallbacks:
            self.fallbacks[api_name] = {}
        
        self.fallbacks[api_name][function_name] = fallback_function
        logger.debug(f"Registered fallback for {api_name}.{function_name}")
    
    def get_fallback(self, api_name: str, function_name: str) -> Optional[Callable]:
        """
        Get a fallback function for an API function.
        
        Args:
            api_name (str): Name of the API (e.g., "openai")
            function_name (str): Name of the function (e.g., "Completion.create")
            
        Returns:
            Optional[Callable]: Fallback function if registered, None otherwise
        """
        if api_name in self.fallbacks and function_name in self.fallbacks[api_name]:
            return self.fallbacks[api_name][function_name]
        
        return None
    
    def register_default_fallbacks(self) -> None:
        """Register default fallbacks for known APIs."""
        # Register OpenAI fallbacks
        self.register_fallback("openai", "ChatCompletion.create", openai_chat_completion_fallback)
        self.register_fallback("openai", "Embedding.create", openai_embedding_fallback)
        
        # Register other API fallbacks as needed
        # self.register_fallback("other_api", "function_name", other_api_fallback)

# Create a global instance of the API fallback manager
fallback_manager = APIFallbackManager()

def with_fallback(api_name: str, function_name: str):
    """
    Decorator for functions that need fallback mechanisms.
    
    Args:
        api_name (str): Name of the API (e.g., "openai")
        function_name (str): Name of the function (e.g., "Completion.create")
        
    Returns:
        Callable: Decorated function with fallback mechanism
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Error calling {api_name}.{function_name}: {str(e)}")
                
                # Get fallback function
                fallback_func = fallback_manager.get_fallback(api_name, function_name)
                
                if fallback_func:
                    logger.info(f"Using fallback for {api_name}.{function_name}")
                    return fallback_func(*args, **kwargs)
                else:
                    logger.error(f"No fallback available for {api_name}.{function_name}")
                    raise
        
        return wrapper
    
    return decorator

# OpenAI API fallbacks

@optional_dependency("openai")
def openai_chat_completion_fallback(*args, **kwargs) -> Dict[str, Any]:
    """
    Fallback for OpenAI ChatCompletion.create.
    Handles API changes between different versions of the OpenAI API.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Dict[str, Any]: Response similar to the OpenAI API response
    """
    logger.info("Using fallback for OpenAI ChatCompletion.create")
    
    try:
        # Try to import openai
        import openai
        
        # Check if we're using openai < 1.0.0 or >= 1.0.0
        import pkg_resources
        openai_version = pkg_resources.get_distribution("openai").version
        is_old_api = openai_version.startswith("0.")
        
        if is_old_api:
            # Old API (< 1.0.0)
            logger.debug("Using old OpenAI API (< 1.0.0)")
            return openai.ChatCompletion.create(*args, **kwargs)
        else:
            # New API (>= 1.0.0)
            logger.debug("Using new OpenAI API (>= 1.0.0)")
            client = openai.OpenAI()
            return client.chat.completions.create(*args, **kwargs)
    
    except ImportError:
        logger.error("OpenAI package not installed")
        
        # Return a minimal response structure
        return {
            "choices": [
                {
                    "message": {
                        "content": "Error: OpenAI API not available. Please install the openai package."
                    }
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"Error in OpenAI ChatCompletion fallback: {str(e)}")
        
        # Return a minimal response structure with the error message
        return {
            "choices": [
                {
                    "message": {
                        "content": f"Error: {str(e)}"
                    }
                }
            ]
        }

@optional_dependency("openai")
def openai_embedding_fallback(*args, **kwargs) -> Dict[str, Any]:
    """
    Fallback for OpenAI Embedding.create.
    Handles API changes between different versions of the OpenAI API.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Dict[str, Any]: Response similar to the OpenAI API response
    """
    logger.info("Using fallback for OpenAI Embedding.create")
    
    try:
        # Try to import openai
        import openai
        
        # Check if we're using openai < 1.0.0 or >= 1.0.0
        import pkg_resources
        openai_version = pkg_resources.get_distribution("openai").version
        is_old_api = openai_version.startswith("0.")
        
        if is_old_api:
            # Old API (< 1.0.0)
            logger.debug("Using old OpenAI API (< 1.0.0)")
            return openai.Embedding.create(*args, **kwargs)
        else:
            # New API (>= 1.0.0)
            logger.debug("Using new OpenAI API (>= 1.0.0)")
            client = openai.OpenAI()
            return client.embeddings.create(*args, **kwargs)
    
    except ImportError:
        logger.error("OpenAI package not installed")
        
        # Return a minimal response structure with zero embeddings
        return {
            "data": [
                {
                    "embedding": [0.0] * 1536  # Default embedding dimension
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"Error in OpenAI Embedding fallback: {str(e)}")
        
        # Return a minimal response structure with zero embeddings
        return {
            "data": [
                {
                    "embedding": [0.0] * 1536  # Default embedding dimension
                }
            ]
        }

# Example usage of the fallback mechanism
@with_fallback("openai", "ChatCompletion.create")
def generate_text_with_openai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Generate text using the OpenAI API with fallback mechanism.
    
    Args:
        prompt (str): The prompt to generate text from
        model (str): The model to use
        
    Returns:
        str: Generated text
    """
    try:
        import openai
        
        # Check if we're using openai < 1.0.0 or >= 1.0.0
        import pkg_resources
        openai_version = pkg_resources.get_distribution("openai").version
        is_old_api = openai_version.startswith("0.")
        
        if is_old_api:
            # Old API (< 1.0.0)
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        else:
            # New API (>= 1.0.0)
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    
    except Exception as e:
        # This will be caught by the decorator and the fallback will be used
        raise e