"""
Segmentation module for YouTube processing.
Provides functions for segmenting and processing YouTube video transcripts.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import timedelta

# Import dependency checker
from ...utils.dependency_checker import optional_dependency

# Import processing modules
from ...processing.summarizer import summarize_text
from ...processing.keypoints_extractor import extract_keypoints, extract_glossary
from ...processing.active_recall_gen import generate_questions

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.youtube.segmentation")

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

def format_seconds_to_timestamp(seconds: float) -> str:
    """
    Format seconds to a timestamp string in format HH:MM:SS.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    try:
        td = timedelta(seconds=seconds)
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except Exception as e:
        logger.error(f"Error formatting seconds to timestamp: {str(e)}")
        return "00:00:00"

def segment_transcript(transcript: List[Dict[str, Any]], segment_method: str = "fixed", segment_size: int = 30, min_segment_size: int = 10) -> List[Dict[str, Any]]:
    """
    Segment a transcript into smaller chunks for processing.
    
    Args:
        transcript (List[Dict[str, Any]]): List of transcript segments with text and timestamps
        segment_method (str): Method for segmentation. Options: "fixed", "topic", "smart"
        segment_size (int): Size of segments in seconds (for fixed method) or number of segments (for topic method)
        min_segment_size (int): Minimum segment size in seconds
        
    Returns:
        List[Dict[str, Any]]: List of segmented transcripts with text and timestamps
    """
    logger.info(f"Segmenting transcript using method: {segment_method}")
    
    if not transcript:
        logger.warning("Empty transcript, cannot segment")
        return []
    
    # Sort transcript by start time
    transcript = sorted(transcript, key=lambda x: x.get('start', 0))
    
    # Fixed-size segmentation
    if segment_method == "fixed":
        return segment_transcript_fixed(transcript, segment_size, min_segment_size)
    
    # Topic-based segmentation
    elif segment_method == "topic":
        return segment_transcript_topic(transcript, segment_size, min_segment_size)
    
    # Smart segmentation (combines fixed and topic)
    elif segment_method == "smart":
        return segment_transcript_smart(transcript, segment_size, min_segment_size)
    
    # Default to fixed segmentation
    else:
        logger.warning(f"Unknown segmentation method: {segment_method}. Using fixed segmentation.")
        return segment_transcript_fixed(transcript, segment_size, min_segment_size)

def segment_transcript_fixed(transcript: List[Dict[str, Any]], segment_size: int = 30, min_segment_size: int = 10) -> List[Dict[str, Any]]:
    """
    Segment a transcript into fixed-size chunks.
    
    Args:
        transcript (List[Dict[str, Any]]): List of transcript segments with text and timestamps
        segment_size (int): Size of segments in seconds
        min_segment_size (int): Minimum segment size in seconds
        
    Returns:
        List[Dict[str, Any]]: List of segmented transcripts with text and timestamps
    """
    logger.info(f"Segmenting transcript into fixed-size chunks of {segment_size} seconds")
    
    segments = []
    current_segment = {
        "start": transcript[0].get('start', 0),
        "end": 0,
        "text": "",
        "timestamp": format_seconds_to_timestamp(transcript[0].get('start', 0))
    }
    
    for item in transcript:
        start_time = item.get('start', 0)
        text = item.get('text', '')
        
        # If this item would exceed the segment size, start a new segment
        if start_time - current_segment["start"] >= segment_size and len(current_segment["text"]) > 0:
            # Finalize current segment
            current_segment["end"] = start_time
            segments.append(current_segment)
            
            # Start new segment
            current_segment = {
                "start": start_time,
                "end": 0,
                "text": text,
                "timestamp": format_seconds_to_timestamp(start_time)
            }
        else:
            # Add to current segment
            if current_segment["text"]:
                current_segment["text"] += " " + text
            else:
                current_segment["text"] = text
    
    # Add the last segment if it's not empty
    if current_segment["text"] and len(current_segment["text"]) > 0:
        current_segment["end"] = transcript[-1].get('start', 0) + transcript[-1].get('duration', 0)
        segments.append(current_segment)
    
    logger.debug(f"Created {len(segments)} fixed-size segments")
    return segments

def segment_transcript_topic(transcript: List[Dict[str, Any]], num_segments: int = 5, min_segment_size: int = 10) -> List[Dict[str, Any]]:
    """
    Segment a transcript based on topic changes.
    This is a simplified implementation that divides the transcript into roughly equal segments.
    A more advanced implementation would use NLP to detect topic changes.
    
    Args:
        transcript (List[Dict[str, Any]]): List of transcript segments with text and timestamps
        num_segments (int): Target number of segments
        min_segment_size (int): Minimum segment size in seconds
        
    Returns:
        List[Dict[str, Any]]: List of segmented transcripts with text and timestamps
    """
    logger.info(f"Segmenting transcript into approximately {num_segments} topic-based segments")
    
    # Get total duration
    if not transcript:
        return []
    
    total_duration = transcript[-1].get('start', 0) + transcript[-1].get('duration', 0) - transcript[0].get('start', 0)
    
    # Calculate segment size based on total duration and number of segments
    segment_size = max(min_segment_size, total_duration / num_segments)
    
    # Use fixed segmentation with the calculated segment size
    return segment_transcript_fixed(transcript, int(segment_size), min_segment_size)

def segment_transcript_smart(transcript: List[Dict[str, Any]], segment_size: int = 30, min_segment_size: int = 10) -> List[Dict[str, Any]]:
    """
    Smart segmentation of transcript.
    This is a placeholder for a more advanced segmentation method that would use NLP to detect
    natural breaks in the content, sentence boundaries, etc.
    
    Args:
        transcript (List[Dict[str, Any]]): List of transcript segments with text and timestamps
        segment_size (int): Base size of segments in seconds
        min_segment_size (int): Minimum segment size in seconds
        
    Returns:
        List[Dict[str, Any]]: List of segmented transcripts with text and timestamps
    """
    logger.info("Using smart segmentation for transcript")
    
    # For now, just use fixed segmentation
    # In a real implementation, this would use NLP to detect natural breaks
    logger.warning("Smart segmentation not fully implemented, falling back to fixed segmentation")
    return segment_transcript_fixed(transcript, segment_size, min_segment_size)

@optional_dependency("youtube")
def process_segment(segment: Dict[str, Any], model: str = "gpt-4", generate_summary: bool = True, 
                   generate_keypoints: bool = True, generate_glossary: bool = False, 
                   generate_questions: bool = True, num_questions: int = 3, max_keypoints: int = 5) -> Dict[str, Any]:
    """
    Process a transcript segment to generate summary, keypoints, glossary, and questions.
    
    Args:
        segment (Dict[str, Any]): Transcript segment with text and timestamps
        model (str): LLM model to use for processing
        generate_summary (bool): Whether to generate a summary
        generate_keypoints (bool): Whether to generate keypoints
        generate_glossary (bool): Whether to generate a glossary
        generate_questions (bool): Whether to generate questions
        num_questions (int): Number of questions to generate
        max_keypoints (int): Maximum number of keypoints to generate
        
    Returns:
        Dict[str, Any]: Processed segment with summary, keypoints, glossary, and questions
    """
    logger.info(f"Processing segment: {segment.get('timestamp', '')}")
    
    text = segment.get('text', '')
    if not text:
        logger.warning("Empty segment text, skipping processing")
        return segment
    
    processed_segment = segment.copy()
    
    # Generate summary
    if generate_summary:
        try:
            summary = summarize_text(text, model=model)
            processed_segment['summary'] = summary
            logger.debug(f"Generated summary for segment: {segment.get('timestamp', '')}")
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            processed_segment['summary'] = ""
    
    # Generate keypoints
    if generate_keypoints:
        try:
            keypoints = extract_keypoints(text, model=model, max_points=max_keypoints)
            processed_segment['keypoints'] = keypoints
            logger.debug(f"Generated {len(keypoints)} keypoints for segment: {segment.get('timestamp', '')}")
        except Exception as e:
            logger.error(f"Error generating keypoints: {str(e)}")
            processed_segment['keypoints'] = []
    
    # Generate glossary
    if generate_glossary:
        try:
            glossary = extract_glossary(text, model=model)
            processed_segment['glossary'] = glossary
            logger.debug(f"Generated glossary for segment: {segment.get('timestamp', '')}")
        except Exception as e:
            logger.error(f"Error generating glossary: {str(e)}")
            processed_segment['glossary'] = {}
    
    # Generate questions
    if generate_questions:
        try:
            questions = generate_questions(text, model=model, num_questions=num_questions)
            processed_segment['questions'] = questions
            logger.debug(f"Generated {len(questions)} questions for segment: {segment.get('timestamp', '')}")
        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            processed_segment['questions'] = []
    
    return processed_segment