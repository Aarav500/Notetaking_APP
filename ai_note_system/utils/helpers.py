"""
Helper utilities for AI Note System.
Provides miscellaneous utility functions used across the system.
"""

import os
import re
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

from . import logger

log = logger.get_logger()

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path (str): Path to the directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)
    log.debug(f"Ensured directory exists: {directory_path}")

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The file extension (lowercase, without the dot)
    """
    return os.path.splitext(file_path)[1].lower().lstrip('.')

def is_valid_file_type(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        file_path (str): Path to the file
        allowed_extensions (List[str]): List of allowed extensions (without the dot)
        
    Returns:
        bool: True if the file has an allowed extension, False otherwise
    """
    extension = get_file_extension(file_path)
    return extension in allowed_extensions

def generate_file_hash(file_path: str) -> str:
    """
    Generate a hash for a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: The file hash
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def save_json(data: Any, file_path: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data (Any): Data to save
        file_path (str): Path to the file
    """
    # Ensure the directory exists
    ensure_directory_exists(os.path.dirname(file_path))
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    log.debug(f"Saved JSON data to {file_path}")

def load_json(file_path: str) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        Any: The loaded data
        
    Raises:
        FileNotFoundError: If the file is not found
        json.JSONDecodeError: If the file is not valid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        log.debug(f"Loaded JSON data from {file_path}")
        return data
        
    except FileNotFoundError:
        log.error(f"JSON file not found: {file_path}")
        raise
        
    except json.JSONDecodeError as e:
        log.error(f"Error decoding JSON file {file_path}: {e}")
        raise

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: The sanitized filename
    """
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    return sanitized

def get_timestamp() -> str:
    """
    Get a formatted timestamp for the current time.
    
    Returns:
        str: The formatted timestamp (YYYY-MM-DD_HH-MM-SS)
    """
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text (str): The text to truncate
        max_length (int, optional): The maximum length. Defaults to 100.
        suffix (str, optional): The suffix to add if truncated. Defaults to "...".
        
    Returns:
        str: The truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_time_delta(seconds: float) -> str:
    """
    Format a time delta in seconds to a human-readable string.
    
    Args:
        seconds (float): The time delta in seconds
        
    Returns:
        str: The formatted time delta
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def extract_text_between_markers(text: str, start_marker: str, end_marker: str) -> Optional[str]:
    """
    Extract text between two markers.
    
    Args:
        text (str): The text to search in
        start_marker (str): The start marker
        end_marker (str): The end marker
        
    Returns:
        Optional[str]: The extracted text, or None if not found
    """
    pattern = f"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return None