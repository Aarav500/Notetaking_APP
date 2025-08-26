"""
Dependency checker module for AI Note System.
Provides utilities for checking and handling optional dependencies.
"""

import importlib.util
import logging
import sys
from typing import Dict, List, Optional, Tuple, Union, Callable

# Create a logger for this module
logger = logging.getLogger("ai_note_system.dependency_checker")

# Define dependency groups with their packages and friendly names
DEPENDENCY_GROUPS = {
    "pdf": {
        "packages": ["fitz", "pdf2image"],
        "friendly_names": ["PyMuPDF", "pdf2image"],
        "install_command": "pip install PyMuPDF pdf2image",
        "description": "PDF processing"
    },
    "ocr": {
        "packages": ["pytesseract"],
        "friendly_names": ["pytesseract"],
        "install_command": "pip install pytesseract",
        "description": "Optical Character Recognition"
    },
    "speech": {
        "packages": ["speech_recognition", "whisper"],
        "friendly_names": ["SpeechRecognition", "openai-whisper"],
        "install_command": "pip install SpeechRecognition openai-whisper",
        "description": "Speech recognition"
    },
    "youtube": {
        "packages": ["yt_dlp", "youtube_transcript_api", "pydub", "cv2"],
        "friendly_names": ["yt-dlp", "youtube-transcript-api", "pydub", "opencv-python"],
        "install_command": "pip install yt-dlp youtube-transcript-api pydub opencv-python",
        "description": "YouTube video processing"
    },
    "visualization": {
        "packages": ["graphviz"],
        "friendly_names": ["graphviz"],
        "install_command": "pip install graphviz",
        "description": "Visualization generation"
    },
    "data": {
        "packages": ["pandas", "numpy"],
        "friendly_names": ["pandas", "numpy"],
        "install_command": "pip install pandas numpy",
        "description": "Data processing"
    },
    "embeddings": {
        "packages": ["sentence_transformers"],
        "friendly_names": ["sentence-transformers"],
        "install_command": "pip install sentence-transformers",
        "description": "Text embeddings"
    },
    "web": {
        "packages": ["fastapi", "uvicorn"],
        "friendly_names": ["fastapi", "uvicorn"],
        "install_command": "pip install fastapi uvicorn",
        "description": "Web API"
    },
    "notion": {
        "packages": ["notion_client"],
        "friendly_names": ["notion-client"],
        "install_command": "pip install notion-client",
        "description": "Notion integration"
    },
    "google": {
        "packages": ["googleapiclient"],
        "friendly_names": ["google-api-python-client"],
        "install_command": "pip install google-api-python-client",
        "description": "Google API integration"
    },
    "export": {
        "packages": ["markdown", "weasyprint", "genanki"],
        "friendly_names": ["markdown", "weasyprint", "genanki"],
        "install_command": "pip install markdown weasyprint genanki",
        "description": "Export functionality"
    }
}

def check_package(package_name: str) -> bool:
    """
    Check if a package is installed.
    
    Args:
        package_name (str): The name of the package to check
        
    Returns:
        bool: True if the package is installed, False otherwise
    """
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        return False

def check_dependency_group(group_name: str) -> Tuple[bool, List[str]]:
    """
    Check if all packages in a dependency group are installed.
    
    Args:
        group_name (str): The name of the dependency group to check
        
    Returns:
        Tuple[bool, List[str]]: A tuple containing:
            - bool: True if all packages in the group are installed, False otherwise
            - List[str]: A list of missing packages
    """
    if group_name not in DEPENDENCY_GROUPS:
        logger.warning(f"Unknown dependency group: {group_name}")
        return False, []
    
    group = DEPENDENCY_GROUPS[group_name]
    missing_packages = []
    
    for package in group["packages"]:
        if not check_package(package):
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def get_friendly_names(packages: List[str], group_name: str) -> List[str]:
    """
    Get the friendly names for a list of packages in a dependency group.
    
    Args:
        packages (List[str]): The list of package names
        group_name (str): The name of the dependency group
        
    Returns:
        List[str]: A list of friendly names for the packages
    """
    if group_name not in DEPENDENCY_GROUPS:
        return packages
    
    group = DEPENDENCY_GROUPS[group_name]
    friendly_names = []
    
    for package in packages:
        try:
            index = group["packages"].index(package)
            friendly_names.append(group["friendly_names"][index])
        except (ValueError, IndexError):
            friendly_names.append(package)
    
    return friendly_names

def format_error_message(group_name: str, missing_packages: List[str]) -> str:
    """
    Format an error message for missing dependencies.
    
    Args:
        group_name (str): The name of the dependency group
        missing_packages (List[str]): A list of missing packages
        
    Returns:
        str: A formatted error message
    """
    if group_name not in DEPENDENCY_GROUPS:
        return f"Missing dependencies: {', '.join(missing_packages)}"
    
    group = DEPENDENCY_GROUPS[group_name]
    friendly_names = get_friendly_names(missing_packages, group_name)
    
    message = f"Missing dependencies for {group['description']}: {', '.join(friendly_names)}\n"
    message += f"Install with: {group['install_command']}"
    
    return message

def require_dependencies(group_name: str, raise_error: bool = True) -> bool:
    """
    Check if all packages in a dependency group are installed and raise an error or log a warning if not.
    
    Args:
        group_name (str): The name of the dependency group to check
        raise_error (bool, optional): Whether to raise an error if dependencies are missing. Defaults to True.
        
    Returns:
        bool: True if all packages in the group are installed, False otherwise
        
    Raises:
        ImportError: If dependencies are missing and raise_error is True
    """
    all_installed, missing_packages = check_dependency_group(group_name)
    
    if not all_installed:
        error_message = format_error_message(group_name, missing_packages)
        
        if raise_error:
            raise ImportError(error_message)
        else:
            logger.warning(error_message)
    
    return all_installed

def optional_dependency(group_name: str) -> Callable:
    """
    Decorator for functions that require optional dependencies.
    If the dependencies are missing, the function will log a warning and return None.
    
    Args:
        group_name (str): The name of the dependency group required by the function
        
    Returns:
        Callable: A decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                require_dependencies(group_name, raise_error=True)
                return func(*args, **kwargs)
            except ImportError as e:
                logger.warning(f"Skipping {func.__name__} due to missing dependencies: {e}")
                return None
        return wrapper
    return decorator

def fallback_on_missing_dependency(group_name: str, fallback_func: Callable) -> Callable:
    """
    Decorator for functions that should use a fallback function if dependencies are missing.
    
    Args:
        group_name (str): The name of the dependency group required by the function
        fallback_func (Callable): The fallback function to use if dependencies are missing
        
    Returns:
        Callable: A decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            all_installed, _ = check_dependency_group(group_name)
            
            if all_installed:
                return func(*args, **kwargs)
            else:
                logger.info(f"Using fallback for {func.__name__} due to missing dependencies")
                return fallback_func(*args, **kwargs)
        return wrapper
    return decorator