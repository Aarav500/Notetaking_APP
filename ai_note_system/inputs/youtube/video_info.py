"""
Video information module for YouTube processing.
Provides functions for extracting video IDs and retrieving video information.
"""

import os
import re
import json
import logging
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import dependency checker
from ...utils.dependency_checker import optional_dependency

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.youtube.video_info")

def extract_video_id(youtube_url: str) -> Optional[str]:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        youtube_url (str): The YouTube URL
        
    Returns:
        Optional[str]: The video ID if found, None otherwise
    """
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/|youtube\.com\/watch\?.*v=)([^&\?\/\s]+)',
        r'(?:youtube\.com\/shorts\/)([^&\?\/\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    logger.warning(f"Could not extract video ID from URL: {youtube_url}")
    return None

@optional_dependency("youtube")
def get_video_info(video_id: str) -> Dict[str, Any]:
    """
    Get information about a YouTube video using yt-dlp.
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        Dict[str, Any]: Dictionary containing video information
    """
    logger.info(f"Getting information for YouTube video: {video_id}")
    
    try:
        # Use yt-dlp to get video information
        url = f"https://www.youtube.com/watch?v={video_id}"
        cmd = [
            "yt-dlp",
            "--dump-json",  # Output video information as JSON
            "--skip-download",  # Don't download the video
            url  # YouTube URL
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Parse JSON output
        video_info = json.loads(result.stdout)
        
        # Extract relevant information
        info = {
            "id": video_info.get("id", video_id),
            "title": video_info.get("title", ""),
            "description": video_info.get("description", ""),
            "channel": video_info.get("channel", ""),
            "upload_date": video_info.get("upload_date", ""),
            "duration": video_info.get("duration", 0),
            "view_count": video_info.get("view_count", 0),
            "like_count": video_info.get("like_count", 0),
            "categories": video_info.get("categories", []),
            "tags": video_info.get("tags", [])
        }
        
        logger.debug(f"Video information retrieved successfully for {video_id}")
        return info
        
    except subprocess.SubprocessError as e:
        logger.error(f"Error running yt-dlp: {e}")
        logger.info("Make sure yt-dlp is installed with: pip install yt-dlp")
        return {"id": video_id, "error": str(e)}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing video information: {e}")
        return {"id": video_id, "error": f"JSON decode error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error getting video information: {str(e)}")
        return {"id": video_id, "error": str(e)}