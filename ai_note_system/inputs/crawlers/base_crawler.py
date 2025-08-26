"""
Base Crawler Interface for AI Note System.
Defines the interface for all crawler implementations.
"""

import os
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.crawlers.base_crawler")

class BaseCrawler(ABC):
    """
    Abstract base class for all crawler implementations.
    Defines the interface that all crawlers must implement.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the crawler.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        self.config = config
        self.source_name = "base"  # Override in subclasses
    
    @abstractmethod
    def crawl(
        self, 
        query: str, 
        max_results: int = 10,
        download_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Crawl the source for content related to the query.
        
        Args:
            query (str): The query to search for
            max_results (int): Maximum number of results to retrieve
            download_dir (str, optional): Directory to save downloaded files. If None, uses default.
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Dictionary containing crawl results
        """
        pass
    
    @abstractmethod
    def download(
        self, 
        url: str, 
        download_dir: str,
        filename: Optional[str] = None,
        verbose: bool = False
    ) -> str:
        """
        Download content from a URL.
        
        Args:
            url (str): The URL to download from
            download_dir (str): Directory to save downloaded files
            filename (str, optional): Filename to save as. If None, derives from URL.
            verbose (bool): Whether to print verbose output
            
        Returns:
            str: Path to the downloaded file
        """
        pass
    
    @abstractmethod
    def parse(
        self, 
        content: Union[str, bytes, Path], 
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Parse downloaded content.
        
        Args:
            content (Union[str, bytes, Path]): Content to parse or path to file
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Dictionary containing parsed content
        """
        pass
    
    def save_metadata(
        self, 
        metadata: Dict[str, Any], 
        download_dir: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Save metadata to a JSON file.
        
        Args:
            metadata (Dict[str, Any]): Metadata to save
            download_dir (str): Directory to save metadata file
            filename (str, optional): Filename to save as. If None, uses default.
            
        Returns:
            str: Path to the saved metadata file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.source_name}_metadata_{timestamp}.json"
        
        # Ensure directory exists
        os.makedirs(download_dir, exist_ok=True)
        
        # Save metadata to file
        file_path = os.path.join(download_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.debug(f"Metadata saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            return ""
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename.
        
        Args:
            filename (str): The string to sanitize
            
        Returns:
            str: Sanitized filename
        """
        # Replace invalid characters with underscores
        import re
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        return sanitized