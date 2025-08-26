"""
Wikipedia Crawler for AI Note System.
Handles crawling, downloading, and parsing Wikipedia content.
"""

import os
import logging
import json
import re
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

from .base_crawler import BaseCrawler

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.crawlers.wikipedia_crawler")

class WikipediaCrawler(BaseCrawler):
    """
    Crawler for Wikipedia content.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Wikipedia crawler.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
        """
        super().__init__(config)
        self.source_name = "wikipedia"
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.user_agent = config.get("user_agent", "AI Note System/1.0 (https://github.com/yourusername/ai_note_system)")
    
    def crawl(
        self, 
        query: str, 
        max_results: int = 10,
        download_dir: Optional[str] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Crawl Wikipedia for content related to the query.
        
        Args:
            query (str): The query to search for
            max_results (int): Maximum number of results to retrieve
            download_dir (str, optional): Directory to save downloaded files. If None, uses default.
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Dictionary containing crawl results
        """
        logger.info(f"Crawling Wikipedia for: {query}")
        
        # Set up download directory
        if not download_dir:
            # Get the path to the data/research/wikipedia directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            download_dir = os.path.join(project_dir, "data", "research", "wikipedia", self.sanitize_filename(query))
        
        # Ensure directory exists
        os.makedirs(download_dir, exist_ok=True)
        
        # Search for articles
        search_results = self._search_wikipedia(query, max_results, verbose)
        
        # Initialize results
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "download_dir": download_dir,
            "articles": []
        }
        
        # Download and parse each article
        for page_id, title in search_results:
            try:
                # Download article content
                article_content = self._get_article_content(page_id, verbose)
                
                # Save article content
                filename = f"{self.sanitize_filename(title)}.json"
                file_path = os.path.join(download_dir, filename)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(article_content, f, indent=2, ensure_ascii=False)
                
                # Parse article content
                parsed_content = self.parse(article_content, verbose)
                
                # Add to results
                results["articles"].append({
                    "title": title,
                    "page_id": page_id,
                    "file_path": file_path,
                    "summary": parsed_content.get("summary", ""),
                    "sections": parsed_content.get("sections", []),
                    "categories": parsed_content.get("categories", []),
                    "links": parsed_content.get("links", [])
                })
                
                if verbose:
                    logger.info(f"Downloaded and parsed article: {title}")
            
            except Exception as e:
                logger.error(f"Error processing article {title}: {e}")
        
        # Save metadata
        self.save_metadata(results, download_dir, "wikipedia_results.json")
        
        logger.info(f"Completed Wikipedia crawl for: {query}")
        return results
    
    def download(
        self, 
        url: str, 
        download_dir: str,
        filename: Optional[str] = None,
        verbose: bool = False
    ) -> str:
        """
        Download content from a Wikipedia URL.
        
        Args:
            url (str): The Wikipedia URL to download from
            download_dir (str): Directory to save downloaded files
            filename (str, optional): Filename to save as. If None, derives from URL.
            verbose (bool): Whether to print verbose output
            
        Returns:
            str: Path to the downloaded file
        """
        logger.info(f"Downloading from Wikipedia URL: {url}")
        
        # Extract page title from URL
        match = re.search(r'/wiki/(.+)$', url)
        if match:
            title = match.group(1).replace('_', ' ')
        else:
            title = url.split('/')[-1]
        
        # Get page ID from title
        page_id = self._get_page_id(title, verbose)
        
        if not page_id:
            logger.error(f"Could not find page ID for title: {title}")
            return ""
        
        # Get article content
        article_content = self._get_article_content(page_id, verbose)
        
        # Determine filename
        if not filename:
            filename = f"{self.sanitize_filename(title)}.json"
        
        # Ensure directory exists
        os.makedirs(download_dir, exist_ok=True)
        
        # Save article content
        file_path = os.path.join(download_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article_content, f, indent=2, ensure_ascii=False)
            logger.debug(f"Wikipedia article saved to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error saving Wikipedia article: {e}")
            return ""
    
    def parse(
        self, 
        content: Union[str, bytes, Path, Dict], 
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Parse Wikipedia article content.
        
        Args:
            content (Union[str, bytes, Path, Dict]): Content to parse or path to file
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Dictionary containing parsed content
        """
        logger.info("Parsing Wikipedia article content")
        
        # If content is a file path, load it
        if isinstance(content, (str, Path)) and not isinstance(content, dict):
            try:
                with open(content, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            except Exception as e:
                logger.error(f"Error loading content from file: {e}")
                return {"error": str(e)}
        
        # If content is a string that looks like JSON, parse it
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except Exception:
                # Not JSON, treat as raw text
                return {
                    "summary": content[:500] + "..." if len(content) > 500 else content,
                    "text": content,
                    "sections": [],
                    "categories": [],
                    "links": []
                }
        
        # Extract data from the API response
        parsed = {}
        
        # Extract title
        if isinstance(content, dict) and "title" in content:
            parsed["title"] = content["title"]
        
        # Extract summary (first paragraph)
        if isinstance(content, dict) and "extract" in content:
            extract = content["extract"]
            # Find the first paragraph (text before first heading)
            first_heading_match = re.search(r'==\s*([^=]+)\s*==', extract)
            if first_heading_match:
                first_heading_pos = first_heading_match.start()
                summary = extract[:first_heading_pos].strip()
            else:
                # No headings, use first few sentences
                sentences = extract.split('. ')
                summary = '. '.join(sentences[:3]) + ('.' if not sentences[2].endswith('.') else '')
            
            parsed["summary"] = summary
            parsed["text"] = extract
        
        # Extract sections
        sections = []
        if isinstance(content, dict) and "extract" in content:
            extract = content["extract"]
            # Find all section headings
            section_matches = re.finditer(r'(==+)\s*([^=]+)\s*\1', extract)
            
            last_pos = 0
            for match in section_matches:
                heading = match.group(2).strip()
                level = len(match.group(1))
                start_pos = match.end()
                
                # Add the section
                sections.append({
                    "title": heading,
                    "level": level - 1,  # Convert to 1-based level
                    "content": ""  # Will be filled in next iteration or at the end
                })
                
                # Fill in content for the previous section
                if sections:
                    prev_section = sections[-2] if len(sections) > 1 else None
                    if prev_section:
                        prev_section["content"] = extract[last_pos:match.start()].strip()
                
                last_pos = start_pos
            
            # Fill in content for the last section
            if sections:
                sections[-1]["content"] = extract[last_pos:].strip()
        
        parsed["sections"] = sections
        
        # Extract categories
        if isinstance(content, dict) and "categories" in content:
            parsed["categories"] = [cat["title"].replace("Category:", "") for cat in content["categories"]]
        else:
            parsed["categories"] = []
        
        # Extract links
        if isinstance(content, dict) and "links" in content:
            parsed["links"] = [link["title"] for link in content["links"]]
        else:
            parsed["links"] = []
        
        return parsed
    
    def _search_wikipedia(
        self, 
        query: str, 
        max_results: int = 10,
        verbose: bool = False
    ) -> List[tuple]:
        """
        Search Wikipedia for articles related to the query.
        
        Args:
            query (str): The query to search for
            max_results (int): Maximum number of results to retrieve
            verbose (bool): Whether to print verbose output
            
        Returns:
            List[tuple]: List of (page_id, title) tuples
        """
        logger.debug(f"Searching Wikipedia for: {query}")
        
        # Set up API parameters
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results
        }
        
        # Make API request
        try:
            # Construct URL with parameters
            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            
            # Create request with headers
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            
            # Make request
            with urllib.request.urlopen(req) as response:
                # Read and decode response
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
            
            # Extract search results
            search_results = []
            if "query" in data and "search" in data["query"]:
                for result in data["query"]["search"]:
                    search_results.append((result["pageid"], result["title"]))
            
            if verbose:
                logger.info(f"Found {len(search_results)} Wikipedia articles for: {query}")
            
            return search_results
        
        except Exception as e:
            logger.error(f"Error searching Wikipedia: {e}")
            return []
    
    def _get_page_id(
        self, 
        title: str,
        verbose: bool = False
    ) -> Optional[int]:
        """
        Get the page ID for a Wikipedia article title.
        
        Args:
            title (str): The article title
            verbose (bool): Whether to print verbose output
            
        Returns:
            Optional[int]: The page ID, or None if not found
        """
        logger.debug(f"Getting page ID for Wikipedia article: {title}")
        
        # Set up API parameters
        params = {
            "action": "query",
            "format": "json",
            "titles": title
        }
        
        # Make API request
        try:
            # Construct URL with parameters
            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            
            # Create request with headers
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            
            # Make request
            with urllib.request.urlopen(req) as response:
                # Read and decode response
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
            
            # Extract page ID
            if "query" in data and "pages" in data["query"]:
                pages = data["query"]["pages"]
                for page_id, page_data in pages.items():
                    if page_id != "-1":  # -1 means page not found
                        return int(page_id)
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting Wikipedia page ID: {e}")
            return None
    
    def _get_article_content(
        self, 
        page_id: int,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Get the content of a Wikipedia article by page ID.
        
        Args:
            page_id (int): The page ID
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Dictionary containing article content
        """
        logger.debug(f"Getting content for Wikipedia article with page ID: {page_id}")
        
        # Set up API parameters
        params = {
            "action": "query",
            "format": "json",
            "pageids": page_id,
            "prop": "extracts|categories|links",
            "exintro": 0,  # Get full article, not just intro
            "explaintext": 1,  # Get plain text, not HTML
            "cllimit": 500,  # Get up to 500 categories
            "pllimit": 500  # Get up to 500 links
        }
        
        # Make API request
        try:
            # Construct URL with parameters
            url = f"{self.api_url}?{urllib.parse.urlencode(params)}"
            
            # Create request with headers
            req = urllib.request.Request(url, headers={"User-Agent": self.user_agent})
            
            # Make request
            with urllib.request.urlopen(req) as response:
                # Read and decode response
                response_data = response.read().decode('utf-8')
                data = json.loads(response_data)
            
            # Extract article content
            if "query" in data and "pages" in data["query"]:
                pages = data["query"]["pages"]
                if str(page_id) in pages:
                    return pages[str(page_id)]
            
            return {}
        
        except Exception as e:
            logger.error(f"Error getting Wikipedia article content: {e}")
            return {}