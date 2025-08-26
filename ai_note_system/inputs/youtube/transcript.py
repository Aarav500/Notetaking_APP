"""
Transcript module for YouTube processing.
Provides functions for downloading and processing YouTube video transcripts.
"""

import os
import re
import logging
import tempfile
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

# Import dependency checker
from ...utils.dependency_checker import optional_dependency, check_dependency_group

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.youtube.transcript")

# Check YouTube processing dependencies
YOUTUBE_DEPS_AVAILABLE, missing_youtube_deps = check_dependency_group("youtube")

# Try to import youtube_transcript_api
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"YouTube transcript API not available: {e}")
    TRANSCRIPT_API_AVAILABLE = False

@optional_dependency("youtube")
def download_transcript(video_id: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Download transcript for a YouTube video using youtube_transcript_api.
    
    Args:
        video_id (str): The YouTube video ID
        language (str, optional): Language code for transcript. If None, tries to get the default transcript.
        
    Returns:
        List[Dict[str, Any]]: List of transcript segments with text and timestamps
    """
    logger.info(f"Downloading transcript for YouTube video: {video_id}")
    
    if not TRANSCRIPT_API_AVAILABLE:
        logger.warning("YouTube Transcript API not available. Install with: pip install youtube-transcript-api")
        return []
    
    try:
        # Get available transcript languages
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # If language is specified, try to get that language
        if language:
            try:
                transcript = transcript_list.find_transcript([language])
                return transcript.fetch()
            except Exception as e:
                logger.warning(f"Could not find transcript in language {language}: {str(e)}")
                # Fall back to default behavior
        
        # Try to get the default transcript (usually in the video's original language)
        try:
            transcript = transcript_list.find_transcript(['en'])  # Try English first
            return transcript.fetch()
        except Exception:
            # If English not available, get the first available transcript
            try:
                transcript = list(transcript_list)[0]
                return transcript.fetch()
            except Exception as e:
                logger.error(f"Could not get any transcript: {str(e)}")
                logger.debug("This could be due to: 1) No transcripts available, 2) Video is private, 3) Video doesn't exist")
                return []
    
    except Exception as e:
        logger.error(f"Error downloading transcript: {str(e)}")
        logger.debug("This could be due to API limitations or network issues")
        return []

@optional_dependency("youtube")
def extract_transcript_from_subtitles(video_id: str, output_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Extract transcript from subtitles using yt-dlp.
    
    Args:
        video_id (str): The YouTube video ID
        output_dir (str, optional): Directory to save temporary files. If None, uses a temp directory.
        
    Returns:
        List[Dict[str, Any]]: List of transcript segments with text and timestamps
    """
    logger.info(f"Extracting transcript from subtitles for YouTube video: {video_id}")
    
    try:
        # Create temp directory if not specified
        if not output_dir:
            temp_dir = tempfile.mkdtemp()
            output_dir = temp_dir
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Download subtitles using yt-dlp
        url = f"https://www.youtube.com/watch?v={video_id}"
        subtitle_path = os.path.join(output_dir, f"{video_id}.en.vtt")
        
        cmd = [
            "yt-dlp",
            "--skip-download",  # Don't download the video
            "--write-auto-sub",  # Write auto-generated subtitles
            "--sub-format", "vtt",  # VTT format
            "--sub-lang", "en",  # English subtitles
            "-o", os.path.join(output_dir, f"{video_id}"),  # Output filename
            url  # YouTube URL
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if subtitles were downloaded
        subtitle_files = [f for f in os.listdir(output_dir) if f.startswith(video_id) and f.endswith(".vtt")]
        
        if not subtitle_files:
            logger.warning("No subtitle files found")
            logger.debug("This could be due to: 1) No auto-generated subtitles available, 2) Video is private, 3) Video doesn't exist")
            return []
        
        # Use the first subtitle file found
        subtitle_path = os.path.join(output_dir, subtitle_files[0])
        
        # Parse VTT file to extract transcript
        transcript = parse_vtt_file(subtitle_path)
        
        # Clean up temporary files
        if not output_dir:
            for file in subtitle_files:
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
        
        return transcript
        
    except subprocess.SubprocessError as e:
        logger.error(f"Error running yt-dlp: {e}")
        logger.info("Make sure yt-dlp is installed with: pip install yt-dlp")
        return []
    except Exception as e:
        logger.error(f"Error extracting transcript from subtitles: {str(e)}")
        logger.debug("This could be due to issues with the subtitle format or parsing")
        return []

def parse_vtt_file(vtt_path: str) -> List[Dict[str, Any]]:
    """
    Parse a VTT subtitle file to extract transcript with timestamps.
    
    Args:
        vtt_path (str): Path to the VTT file
        
    Returns:
        List[Dict[str, Any]]: List of transcript segments with text and timestamps
    """
    logger.info(f"Parsing VTT file: {vtt_path}")
    
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Regular expression to match timestamp and text
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\s*(.*?)(?=\n\d{2}:\d{2}:\d{2}\.\d{3}|$)'
        
        # Find all matches
        matches = re.findall(pattern, content, re.DOTALL)
        
        transcript = []
        for start, end, text in matches:
            # Clean up text (remove HTML tags, extra whitespace, etc.)
            clean_text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
            clean_text = re.sub(r'\n', ' ', clean_text)  # Replace newlines with spaces
            clean_text = re.sub(r'\s+', ' ', clean_text)  # Replace multiple spaces with a single space
            clean_text = clean_text.strip()
            
            if clean_text:  # Only add non-empty segments
                # Convert timestamps to seconds
                start_seconds = convert_timestamp_to_seconds(start)
                end_seconds = convert_timestamp_to_seconds(end)
                
                transcript.append({
                    'text': clean_text,
                    'start': start_seconds,
                    'duration': end_seconds - start_seconds
                })
        
        logger.debug(f"Parsed {len(transcript)} segments from VTT file")
        return transcript
        
    except Exception as e:
        logger.error(f"Error parsing VTT file: {str(e)}")
        return []

def convert_timestamp_to_seconds(timestamp: str) -> float:
    """
    Convert a timestamp in format HH:MM:SS.mmm to seconds.
    
    Args:
        timestamp (str): Timestamp in format HH:MM:SS.mmm
        
    Returns:
        float: Timestamp in seconds
    """
    try:
        h, m, s = timestamp.split(':')
        return float(h) * 3600 + float(m) * 60 + float(s)
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {str(e)}")
        return 0.0

def get_best_transcript(video_id: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get the best available transcript for a YouTube video.
    Tries to download the official transcript first, then falls back to auto-generated subtitles.
    
    Args:
        video_id (str): The YouTube video ID
        language (str, optional): Language code for transcript. If None, tries to get the default transcript.
        
    Returns:
        List[Dict[str, Any]]: List of transcript segments with text and timestamps
    """
    logger.info(f"Getting best transcript for YouTube video: {video_id}")
    
    # Try to get official transcript first
    transcript = download_transcript(video_id, language)
    
    # If official transcript is not available, try auto-generated subtitles
    if not transcript:
        logger.info("Official transcript not available, trying auto-generated subtitles")
        transcript = extract_transcript_from_subtitles(video_id)
    
    return transcript