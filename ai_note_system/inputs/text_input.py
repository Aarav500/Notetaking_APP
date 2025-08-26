"""
Text input module for AI Note System.
Handles processing of raw text input.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.text_input")

def process_text(
    text: str,
    title: Optional[str] = None,
    tags: Optional[list] = None,
    save_raw: bool = True,
    raw_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process raw text input.
    
    Args:
        text (str): The raw text to process
        title (str, optional): Title for the text. If None, will generate from content.
        tags (list, optional): List of tags for categorization
        save_raw (bool): Whether to save the raw text to disk
        raw_dir (str, optional): Directory to save raw text. If None, uses default.
        
    Returns:
        Dict[str, Any]: Dictionary containing processed text information
    """
    logger.info("Processing text input")
    
    if not text:
        logger.warning("Empty text provided")
        return {"error": "Empty text provided"}
    
    # Generate title from text if not provided
    if not title:
        title = generate_title_from_text(text)
    
    # Create metadata
    timestamp = datetime.now().isoformat()
    
    # Create result dictionary
    result = {
        "title": title,
        "text": text,
        "word_count": len(text.split()),
        "char_count": len(text),
        "timestamp": timestamp,
        "source_type": "text",
        "tags": tags or []
    }
    
    # Save raw text if requested
    if save_raw:
        save_raw_text(text, title, timestamp, raw_dir)
    
    logger.debug(f"Text processed: {title} ({result['word_count']} words)")
    return result

def generate_title_from_text(text: str, max_length: int = 50) -> str:
    """
    Generate a title from the text content.
    
    Args:
        text (str): The text content
        max_length (int): Maximum title length
        
    Returns:
        str: Generated title
    """
    # Simple approach: use first line or first sentence
    first_line = text.strip().split('\n')[0].strip()
    
    # If first line is too long, truncate it
    if len(first_line) > max_length:
        title = first_line[:max_length].strip() + "..."
    else:
        title = first_line
    
    # If title is still empty, use a timestamp-based title
    if not title:
        title = f"Note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return title

def save_raw_text(
    text: str,
    title: str,
    timestamp: str,
    raw_dir: Optional[str] = None
) -> str:
    """
    Save raw text to disk.
    
    Args:
        text (str): The text content
        title (str): The title
        timestamp (str): ISO format timestamp
        raw_dir (str, optional): Directory to save raw text. If None, uses default.
        
    Returns:
        str: Path to the saved file
    """
    # Use default raw directory if not specified
    if not raw_dir:
        # Get the path to the data/raw directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        raw_dir = os.path.join(project_dir, "data", "raw")
    
    # Ensure directory exists
    os.makedirs(raw_dir, exist_ok=True)
    
    # Create a safe filename from title
    safe_title = "".join(c if c.isalnum() else "_" for c in title)
    safe_title = safe_title[:40]  # Limit length
    
    # Create filename with timestamp
    timestamp_str = datetime.fromisoformat(timestamp).strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp_str}.txt"
    file_path = os.path.join(raw_dir, filename)
    
    # Save text to file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.debug(f"Raw text saved to {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving raw text: {e}")
        return ""

def load_text_from_file(file_path: str) -> Dict[str, Any]:
    """
    Load text from a file.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        Dict[str, Any]: Dictionary containing text information
    """
    logger.info(f"Loading text from file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract title from filename
        filename = os.path.basename(file_path)
        title = os.path.splitext(filename)[0]
        
        # If filename has timestamp, remove it
        if '_' in title and title.split('_')[-1].isdigit():
            title = '_'.join(title.split('_')[:-1])
        
        # Replace underscores with spaces
        title = title.replace('_', ' ').strip()
        
        return process_text(text, title)
        
    except Exception as e:
        logger.error(f"Error loading text from file: {e}")
        return {"error": f"Error loading text from file: {e}"}