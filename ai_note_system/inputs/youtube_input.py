"""
YouTube input module for AI Note System.
Handles processing of YouTube videos by extracting audio, downloading transcripts, and processing content.
"""

import os
import logging
import tempfile
import re
import json
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import subprocess
from datetime import timedelta

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.youtube_input")

# Import text_input for processing transcribed text
from . import text_input
from . import speech_input

# Import processing modules
from ..processing.summarizer import summarize_text
from ..processing.keypoints_extractor import extract_keypoints, extract_glossary
from ..processing.active_recall_gen import generate_questions

# Import dependency checker
from ..utils.dependency_checker import require_dependencies, check_dependency_group, optional_dependency, fallback_on_missing_dependency

# Check YouTube processing dependencies
YOUTUBE_DEPS_AVAILABLE, missing_youtube_deps = check_dependency_group("youtube")
if not YOUTUBE_DEPS_AVAILABLE:
    logger.warning(f"Some YouTube processing dependencies are missing. Limited functionality will be available.")
    for package in missing_youtube_deps:
        logger.debug(f"Missing YouTube dependency: {package}")

# Try to import youtube_transcript_api
try:
    require_dependencies("youtube", raise_error=False)
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError as e:
    logger.warning(f"YouTube transcript API not available: {e}")
    TRANSCRIPT_API_AVAILABLE = False

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
def download_audio(video_id: str, output_dir: Optional[str] = None) -> Optional[str]:
    """
    Download audio from a YouTube video.
    
    Args:
        video_id (str): The YouTube video ID
        output_dir (str, optional): Directory to save the audio file. If None, uses a temporary directory.
        
    Returns:
        Optional[str]: Path to the downloaded audio file if successful, None otherwise
    """
    logger.info(f"Downloading audio for YouTube video: {video_id}")
    
    try:
        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{video_id}.mp3")
        else:
            # Use a temporary directory
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, f"{video_id}.mp3")
        
        # Download audio using yt-dlp
        url = f"https://www.youtube.com/watch?v={video_id}"
        cmd = [
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", "mp3",  # Convert to mp3
            "--audio-quality", "0",  # Best quality
            "-o", output_path,  # Output path
            url  # YouTube URL
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Check if the file was downloaded successfully
        if os.path.exists(output_path):
            logger.info(f"Audio downloaded successfully: {output_path}")
            return output_path
        else:
            logger.error(f"Audio file not found after download: {output_path}")
            return None
        
    except subprocess.SubprocessError as e:
        logger.error(f"Error running yt-dlp: {e}")
        logger.info("Make sure yt-dlp is installed and in your PATH")
        return None
    except Exception as e:
        logger.error(f"Error downloading audio: {str(e)}")
        return None

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
        
        # Regular expression to extract timestamps and text
        pattern = r'(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\s*(.*?)(?=\n\d{2}:\d{2}:\d{2}\.\d{3}|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        transcript = []
        for start_time, end_time, text in matches:
            # Convert timestamps to seconds
            start_seconds = convert_timestamp_to_seconds(start_time)
            end_seconds = convert_timestamp_to_seconds(end_time)
            
            # Clean up text (remove HTML tags, extra whitespace, etc.)
            clean_text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()  # Remove extra whitespace
            
            if clean_text:  # Only add non-empty segments
                transcript.append({
                    'text': clean_text,
                    'start': start_seconds,
                    'duration': end_seconds - start_seconds
                })
        
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
        hours, minutes, seconds = timestamp.split(':')
        total_seconds = (int(hours) * 3600) + (int(minutes) * 60) + float(seconds)
        return total_seconds
    except Exception as e:
        logger.error(f"Error converting timestamp {timestamp}: {str(e)}")
        return 0.0

def format_seconds_to_timestamp(seconds: float) -> str:
    """
    Format seconds to a timestamp string (HH:MM:SS).
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def get_best_transcript(video_id: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get the best available transcript for a YouTube video.
    Tries official transcript first, then falls back to extracted subtitles.
    
    Args:
        video_id (str): The YouTube video ID
        language (str, optional): Language code for transcript
        
    Returns:
        List[Dict[str, Any]]: List of transcript segments with text and timestamps
    """
    logger.info(f"Getting best transcript for YouTube video: {video_id}")
    
    # Try to get official transcript first
    transcript = download_transcript(video_id, language)
    
    # If official transcript is not available, try to extract from subtitles
    if not transcript:
        logger.info("Official transcript not available, trying to extract from subtitles")
        transcript = extract_transcript_from_subtitles(video_id)
    
    # If still no transcript, return empty list
    if not transcript:
        logger.warning("Could not get any transcript")
        
    return transcript

def get_video_info(video_id: str) -> Dict[str, Any]:
    """
    Get information about a YouTube video.
    
    Args:
        video_id (str): The YouTube video ID
        
    Returns:
        Dict[str, Any]: Video information including title, description, etc.
    """
    logger.info(f"Getting information for YouTube video: {video_id}")
    
    try:
        # Check if yt-dlp is installed
        try:
            subprocess.run(["yt-dlp", "--version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.error("yt-dlp is not installed. Please install it with 'pip install yt-dlp'.")
            return {}
        
        # Get video info using yt-dlp
        url = f"https://www.youtube.com/watch?v={video_id}"
        cmd = [
            "yt-dlp",
            "--skip-download",  # Don't download the video
            "--print", "title,description,duration,upload_date,uploader,view_count",  # Print info
            url  # YouTube URL
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Parse the output
        output = result.stdout.strip().split('\n')
        
        if len(output) >= 6:
            info = {
                "title": output[0],
                "description": output[1],
                "duration": output[2],
                "upload_date": output[3],
                "uploader": output[4],
                "view_count": output[5]
            }
        else:
            # Fallback to minimal info
            info = {
                "title": f"YouTube Video {video_id}",
                "description": "",
                "video_id": video_id
            }
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return {
            "title": f"YouTube Video {video_id}",
            "description": "",
            "video_id": video_id,
            "error": str(e)
        }

def process_segment(
    segment: Dict[str, Any],
    model: str = "gpt-4",
    generate_summary: bool = True,
    generate_keypoints: bool = True,
    generate_glossary: bool = False,
    generate_questions: bool = True,
    num_questions: int = 3,
    max_keypoints: int = 5
) -> Dict[str, Any]:
    """
    Process a segment through various processing pipelines.
    
    Args:
        segment (Dict[str, Any]): The segment to process
        model (str): The model to use for processing
        generate_summary (bool): Whether to generate a summary
        generate_keypoints (bool): Whether to extract key points
        generate_glossary (bool): Whether to extract glossary terms
        generate_questions (bool): Whether to generate questions
        num_questions (int): Number of questions to generate
        max_keypoints (int): Maximum number of key points to extract
        
    Returns:
        Dict[str, Any]: The processed segment with added information
    """
    logger.info(f"Processing segment: {segment.get('timestamp', 'unknown')}")
    
    # Create a copy of the segment to avoid modifying the original
    processed = segment.copy()
    
    # Get the segment text
    text = segment.get("text", "")
    
    if not text:
        logger.warning("Empty segment text, skipping processing")
        return processed
    
    # Generate summary if requested
    if generate_summary:
        try:
            summary_result = summarize_text(
                text=text,
                model=model,
                max_length=100,
                format="paragraph"
            )
            processed["summary"] = summary_result.get("summary", "")
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            processed["summary"] = ""
    
    # Extract key points if requested
    if generate_keypoints:
        try:
            keypoints_result = extract_keypoints(
                text=text,
                model=model,
                max_points=max_keypoints,
                hierarchical=False
            )
            processed["keypoints"] = keypoints_result.get("key_points", [])
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            processed["keypoints"] = []
    
    # Extract glossary terms if requested
    if generate_glossary:
        try:
            glossary_result = extract_glossary(
                text=text,
                model=model,
                max_terms=5,
                include_definitions=True
            )
            processed["glossary"] = glossary_result.get("glossary", {})
        except Exception as e:
            logger.error(f"Error extracting glossary: {str(e)}")
            processed["glossary"] = {}
    
    # Generate questions if requested
    if generate_questions:
        try:
            questions_result = generate_questions(
                text=text,
                model=model,
                count=num_questions,
                question_type="open_ended"
            )
            processed["questions"] = questions_result
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            processed["questions"] = []
    
    return processed

def segment_transcript(
    transcript: List[Dict[str, Any]],
    segment_method: str = "fixed",
    segment_size: int = 30,
    min_segment_size: int = 10
) -> List[Dict[str, Any]]:
    """
    Segment a transcript into smaller chunks.
    
    Args:
        transcript (List[Dict[str, Any]]): The transcript to segment
        segment_method (str): Method to use for segmentation ('fixed', 'topic', 'smart')
        segment_size (int): Size of segments in seconds (for 'fixed' method)
        min_segment_size (int): Minimum size of segments in seconds
        
    Returns:
        List[Dict[str, Any]]: List of segmented transcripts
    """
    logger.info(f"Segmenting transcript using method: {segment_method}")
    
    if not transcript:
        logger.warning("Empty transcript, cannot segment")
        return []
    
    # Sort transcript by start time
    sorted_transcript = sorted(transcript, key=lambda x: x.get('start', 0))
    
    # Fixed-size segmentation (by time)
    if segment_method == "fixed":
        segments = []
        current_segment = {
            "start": sorted_transcript[0].get('start', 0),
            "end": 0,
            "text": "",
            "items": []
        }
        
        for item in sorted_transcript:
            item_start = item.get('start', 0)
            item_duration = item.get('duration', 0)
            item_end = item_start + item_duration
            
            # If this item would make the segment too long, start a new segment
            if item_start - current_segment["start"] >= segment_size and len(current_segment["items"]) > 0:
                # Finalize current segment
                current_segment["end"] = current_segment["items"][-1].get('start', 0) + current_segment["items"][-1].get('duration', 0)
                segments.append(current_segment)
                
                # Start new segment
                current_segment = {
                    "start": item_start,
                    "end": 0,
                    "text": "",
                    "items": []
                }
            
            # Add item to current segment
            current_segment["items"].append(item)
            current_segment["text"] += " " + item.get('text', '')
            
        # Add the last segment if it has items
        if current_segment["items"]:
            current_segment["end"] = current_segment["items"][-1].get('start', 0) + current_segment["items"][-1].get('duration', 0)
            current_segment["text"] = current_segment["text"].strip()
            segments.append(current_segment)
        
        return segments
    
    # Topic-based segmentation (simple approach - look for long pauses)
    elif segment_method == "topic":
        segments = []
        current_segment = {
            "start": sorted_transcript[0].get('start', 0),
            "end": 0,
            "text": "",
            "items": []
        }
        
        for i, item in enumerate(sorted_transcript):
            item_start = item.get('start', 0)
            item_duration = item.get('duration', 0)
            item_end = item_start + item_duration
            
            # Check if there's a significant pause after this item
            if i < len(sorted_transcript) - 1:
                next_start = sorted_transcript[i+1].get('start', 0)
                pause_duration = next_start - item_end
                
                # If there's a significant pause (> 2 seconds) and the current segment is long enough
                if pause_duration > 2 and item_end - current_segment["start"] >= min_segment_size:
                    # Add item to current segment
                    current_segment["items"].append(item)
                    current_segment["text"] += " " + item.get('text', '')
                    
                    # Finalize current segment
                    current_segment["end"] = item_end
                    current_segment["text"] = current_segment["text"].strip()
                    segments.append(current_segment)
                    
                    # Start new segment
                    if i + 1 < len(sorted_transcript):
                        current_segment = {
                            "start": sorted_transcript[i+1].get('start', 0),
                            "end": 0,
                            "text": "",
                            "items": []
                        }
                    continue
            
            # Add item to current segment
            current_segment["items"].append(item)
            current_segment["text"] += " " + item.get('text', '')
        
        # Add the last segment if it has items
        if current_segment["items"]:
            current_segment["end"] = current_segment["items"][-1].get('start', 0) + current_segment["items"][-1].get('duration', 0)
            current_segment["text"] = current_segment["text"].strip()
            segments.append(current_segment)
        
        return segments
    
    # Smart segmentation (would use NLP to detect topic changes - simplified version here)
    elif segment_method == "smart":
        # For now, just use topic-based segmentation
        # In a real implementation, this would use NLP to detect topic changes
        return segment_transcript(transcript, "topic", segment_size, min_segment_size)
    
    else:
        logger.warning(f"Unknown segmentation method: {segment_method}, using fixed")
        return segment_transcript(transcript, "fixed", segment_size, min_segment_size)

def generate_markdown_export(
    processed_video: Dict[str, Any],
    include_transcript: bool = False,
    include_segments: bool = True,
    include_summaries: bool = True,
    include_keypoints: bool = True,
    include_questions: bool = True,
    include_glossary: bool = False
) -> str:
    """
    Generate a Markdown export of the processed YouTube video.
    
    Args:
        processed_video (Dict[str, Any]): The processed video data
        include_transcript (bool): Whether to include the full transcript
        include_segments (bool): Whether to include individual segments
        include_summaries (bool): Whether to include summaries
        include_keypoints (bool): Whether to include key points
        include_questions (bool): Whether to include questions
        include_glossary (bool): Whether to include glossary terms
        
    Returns:
        str: The Markdown content
    """
    logger.info("Generating Markdown export")
    
    # Extract video information
    title = processed_video.get("title", "Untitled Video")
    video_id = processed_video.get("video_id", "")
    video_url = processed_video.get("video_url", "")
    video_info = processed_video.get("video_info", {})
    
    # Start building the Markdown content
    markdown = []
    
    # Add title and video information
    markdown.append(f"# {title}")
    markdown.append("")
    markdown.append(f"Video: [{title}]({video_url})")
    
    # Add video metadata if available
    if video_info:
        markdown.append("")
        markdown.append("## Video Information")
        markdown.append("")
        
        if "uploader" in video_info:
            markdown.append(f"- **Channel**: {video_info['uploader']}")
        
        if "upload_date" in video_info:
            markdown.append(f"- **Upload Date**: {video_info['upload_date']}")
        
        if "duration" in video_info:
            markdown.append(f"- **Duration**: {video_info['duration']}")
        
        if "view_count" in video_info:
            markdown.append(f"- **Views**: {video_info['view_count']}")
        
        if "description" in video_info and video_info["description"]:
            markdown.append("")
            markdown.append("### Description")
            markdown.append("")
            markdown.append(video_info["description"])
    
    # Add table of contents
    markdown.append("")
    markdown.append("## Table of Contents")
    markdown.append("")
    
    toc_items = []
    
    if include_summaries and "segment_summaries" in processed_video:
        toc_items.append("- [Summary](#summary)")
    
    if include_keypoints and "all_keypoints" in processed_video:
        toc_items.append("- [Key Points](#key-points)")
    
    if include_questions and "all_questions" in processed_video:
        toc_items.append("- [Questions](#questions)")
    
    if include_glossary and "glossary" in processed_video:
        toc_items.append("- [Glossary](#glossary)")
    
    if include_segments and "processed_segments" in processed_video:
        toc_items.append("- [Segments](#segments)")
        
        # Add segment links to TOC
        segments = processed_video.get("processed_segments", [])
        for i, segment in enumerate(segments):
            timestamp = segment.get("timestamp", "")
            segment_title = f"Segment {i+1}: {timestamp}"
            segment_anchor = f"segment-{i+1}"
            toc_items.append(f"  - [{segment_title}](#{segment_anchor})")
    
    if include_transcript and "transcript" in processed_video:
        toc_items.append("- [Full Transcript](#full-transcript)")
    
    markdown.extend(toc_items)
    
    # Add summary section
    if include_summaries and "segment_summaries" in processed_video:
        markdown.append("")
        markdown.append("## Summary")
        markdown.append("")
        markdown.append(processed_video["segment_summaries"])
    
    # Add key points section
    if include_keypoints and "all_keypoints" in processed_video:
        markdown.append("")
        markdown.append("## Key Points")
        markdown.append("")
        
        for keypoint in processed_video["all_keypoints"]:
            markdown.append(f"- {keypoint}")
    
    # Add questions section
    if include_questions and "all_questions" in processed_video:
        markdown.append("")
        markdown.append("## Questions")
        markdown.append("")
        
        for i, question in enumerate(processed_video["all_questions"]):
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
                timestamp = question.get("timestamp", "")
                youtube_url = question.get("youtube_url", "")
                
                markdown.append(f"### Question {i+1}")
                markdown.append(f"[{timestamp}]({youtube_url})")
                markdown.append("")
                markdown.append(f"**Q: {q_text}**")
                markdown.append("")
                markdown.append(f"A: {answer}")
                markdown.append("")
    
    # Add glossary section
    if include_glossary and "glossary" in processed_video:
        markdown.append("")
        markdown.append("## Glossary")
        markdown.append("")
        
        glossary = processed_video.get("glossary", {})
        for term, definition in glossary.items():
            markdown.append(f"**{term}**: {definition}")
            markdown.append("")
    
    # Add segments section
    if include_segments and "processed_segments" in processed_video:
        markdown.append("")
        markdown.append("## Segments")
        
        segments = processed_video.get("processed_segments", [])
        for i, segment in enumerate(segments):
            timestamp = segment.get("timestamp", "")
            youtube_url = segment.get("youtube_url", "")
            text = segment.get("text", "")
            summary = segment.get("summary", "")
            keypoints = segment.get("keypoints", [])
            questions = segment.get("questions", [])
            
            markdown.append("")
            markdown.append(f"### Segment {i+1}: {timestamp} <a name='segment-{i+1}'></a>")
            markdown.append(f"[Watch this segment]({youtube_url})")
            markdown.append("")
            
            if summary:
                markdown.append("#### Summary")
                markdown.append("")
                markdown.append(summary)
                markdown.append("")
            
            if keypoints:
                markdown.append("#### Key Points")
                markdown.append("")
                for keypoint in keypoints:
                    markdown.append(f"- {keypoint}")
                markdown.append("")
            
            if questions:
                markdown.append("#### Questions")
                markdown.append("")
                for j, question in enumerate(questions):
                    if isinstance(question, dict):
                        q_text = question.get("question", "")
                        answer = question.get("answer", "")
                        
                        markdown.append(f"**Q{j+1}: {q_text}**")
                        markdown.append("")
                        markdown.append(f"A: {answer}")
                        markdown.append("")
            
            markdown.append("#### Transcript")
            markdown.append("")
            markdown.append(text)
    
    # Add full transcript section
    if include_transcript and "transcript" in processed_video:
        markdown.append("")
        markdown.append("## Full Transcript")
        markdown.append("")
        
        transcript = processed_video.get("transcript", [])
        for item in transcript:
            start = item.get("start", 0)
            text = item.get("text", "")
            timestamp = format_seconds_to_timestamp(start)
            youtube_url = f"{video_url}&t={int(start)}"
            
            markdown.append(f"[{timestamp}]({youtube_url}) {text}")
    
    # Join all lines and return
    return "\n".join(markdown)

def process_youtube_video(
    youtube_url: str,
    title: Optional[str] = None,
    tags: Optional[list] = None,
    save_audio: bool = False,
    audio_dir: Optional[str] = None,
    use_transcript: bool = True,
    transcript_language: Optional[str] = None,
    segment_method: str = "fixed",
    segment_size: int = 30,
    process_segments: bool = True,
    model: str = "gpt-4",
    generate_summary: bool = True,
    generate_keypoints: bool = True,
    generate_glossary: bool = False,
    generate_questions: bool = True,
    num_questions: int = 3,
    max_keypoints: int = 5,
    export_markdown: bool = False,
    markdown_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a YouTube video by downloading transcript or extracting audio and transcribing it.
    
    Args:
        youtube_url (str): The YouTube URL
        title (str, optional): Title for the note. If None, uses the video title.
        tags (list, optional): List of tags for categorization
        save_audio (bool): Whether to save the audio file
        audio_dir (str, optional): Directory to save the audio file. If None, uses default.
        use_transcript (bool): Whether to try to use official transcript
        transcript_language (str, optional): Language code for transcript
        segment_method (str): Method to use for segmentation ('fixed', 'topic', 'smart')
        segment_size (int): Size of segments in seconds (for 'fixed' method)
        process_segments (bool): Whether to process segments individually
        
    Returns:
        Dict[str, Any]: Dictionary containing processed video information
    """
    logger.info(f"Processing YouTube video: {youtube_url}")
    
    # Extract video ID from URL
    video_id = extract_video_id(youtube_url)
    if not video_id:
        return {"error": f"Invalid YouTube URL: {youtube_url}"}
    
    # Get video information
    video_info = get_video_info(video_id)
    
    # Use video title if no title is provided
    if not title and "title" in video_info:
        title = video_info["title"]
    
    # Initialize result dictionary
    result = {
        "title": title or f"YouTube Video {video_id}",
        "source_type": "youtube",
        "video_id": video_id,
        "video_url": youtube_url,
        "video_info": video_info,
        "tags": tags or ["youtube"]
    }
    
    # Try to get transcript if requested
    transcript = []
    if use_transcript:
        logger.info("Attempting to get transcript")
        transcript = get_best_transcript(video_id, transcript_language)
    
    # If transcript is available, process it
    if transcript:
        logger.info(f"Transcript available with {len(transcript)} segments")
        
        # Combine all transcript segments into a single text
        full_text = " ".join([item.get('text', '') for item in transcript])
        
        # Add transcript to result
        result["transcript"] = transcript
        result["text"] = full_text
        result["word_count"] = len(full_text.split())
        result["char_count"] = len(full_text)
        
        # Segment the transcript
        segments = segment_transcript(transcript, segment_method, segment_size)
        result["segments"] = segments
        
        # Process segments if requested
        if process_segments and segments:
            logger.info(f"Processing {len(segments)} segments")
            processed_segments = []
            
            for i, segment in enumerate(segments):
                segment_text = segment["text"]
                segment_start = segment["start"]
                segment_end = segment["end"]
                
                # Create a timestamp string for the segment
                timestamp = f"{format_seconds_to_timestamp(segment_start)} - {format_seconds_to_timestamp(segment_end)}"
                
                # Create base segment with metadata
                base_segment = {
                    "index": i,
                    "start": segment_start,
                    "end": segment_end,
                    "timestamp": timestamp,
                    "text": segment_text,
                    "youtube_url": f"{youtube_url}&t={int(segment_start)}"
                }
                
                # Process the segment through processing pipelines
                processed_segment = process_segment(
                    segment=base_segment,
                    model=model,
                    generate_summary=generate_summary,
                    generate_keypoints=generate_keypoints,
                    generate_glossary=generate_glossary,
                    generate_questions=generate_questions,
                    num_questions=num_questions,
                    max_keypoints=max_keypoints
                )
                
                processed_segments.append(processed_segment)
            
            result["processed_segments"] = processed_segments
            
            # Generate a combined summary from all segment summaries if requested
            if generate_summary and processed_segments:
                combined_summaries = "\n\n".join([
                    f"[{segment['timestamp']}] {segment.get('summary', '')}" 
                    for segment in processed_segments 
                    if segment.get('summary')
                ])
                result["segment_summaries"] = combined_summaries
            
            # Collect all key points from all segments if requested
            if generate_keypoints and processed_segments:
                all_keypoints = []
                for segment in processed_segments:
                    segment_keypoints = segment.get('keypoints', [])
                    if segment_keypoints:
                        # Add timestamp reference to each keypoint
                        timestamped_keypoints = [
                            f"[{segment['timestamp']}] {keypoint}" 
                            for keypoint in segment_keypoints
                        ]
                        all_keypoints.extend(timestamped_keypoints)
                result["all_keypoints"] = all_keypoints
            
            # Collect all questions from all segments if requested
            if generate_questions and processed_segments:
                all_questions = []
                for segment in processed_segments:
                    segment_questions = segment.get('questions', [])
                    if segment_questions:
                        # Add timestamp reference to each question
                        for question in segment_questions:
                            if isinstance(question, dict):
                                question["timestamp"] = segment["timestamp"]
                                question["video_position"] = int(segment["start"])
                                question["youtube_url"] = segment["youtube_url"]
                                all_questions.append(question)
                result["all_questions"] = all_questions
        
        return result
    
    # If no transcript is available, fall back to audio transcription
    logger.info("No transcript available, falling back to audio transcription")
    
    # Download audio
    audio_path = download_audio(video_id, audio_dir if save_audio else None)
    if not audio_path:
        return {"error": f"Failed to download audio for video: {video_id}"}
    
    try:
        # Transcribe audio
        transcription_result = speech_input.transcribe_audio(
            audio_path,
            engine="whisper",
            language=transcript_language,
            model_size="base"
        )
        
        if "error" in transcription_result:
            return {"error": transcription_result["error"]}
        
        # Extract text from transcription result
        transcribed_text = transcription_result.get("text", "")
        
        # Process the transcribed text
        result["text"] = transcribed_text
        result["word_count"] = len(transcribed_text.split())
        result["char_count"] = len(transcribed_text)
        
        # Clean up audio file if not saving
        if not save_audio and os.path.exists(audio_path):
            os.remove(audio_path)
            logger.debug(f"Deleted temporary audio file: {audio_path}")
        
        # Generate Markdown export if requested
        if export_markdown:
            logger.info("Generating Markdown export")
            markdown_content = generate_markdown_export(
                processed_video=result,
                include_transcript=False,  # Full transcript might be too verbose
                include_segments=True,
                include_summaries=generate_summary,
                include_keypoints=generate_keypoints,
                include_questions=generate_questions,
                include_glossary=generate_glossary
            )
            
            # Save Markdown to file if path is provided
            if markdown_path:
                try:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(os.path.abspath(markdown_path)), exist_ok=True)
                    
                    # Write Markdown to file
                    with open(markdown_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    
                    logger.info(f"Markdown export saved to: {markdown_path}")
                    result["markdown_path"] = markdown_path
                except Exception as e:
                    logger.error(f"Error saving Markdown export: {str(e)}")
                    result["markdown_error"] = str(e)
            
            # Add Markdown content to result
            result["markdown_content"] = markdown_content
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing YouTube video: {str(e)}")
        
        # Clean up audio file if not saving
        if not save_audio and audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {"error": f"Error processing YouTube video: {str(e)}"}