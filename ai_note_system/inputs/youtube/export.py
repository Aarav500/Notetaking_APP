"""
Export module for YouTube processing.
Provides functions for exporting processed YouTube video content to various formats.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import dependency checker
from ...utils.dependency_checker import optional_dependency

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.youtube.export")

def generate_markdown_export(processed_video: Dict[str, Any], include_transcript: bool = False, 
                            include_segments: bool = True, include_summaries: bool = True, 
                            include_keypoints: bool = True, include_questions: bool = True, 
                            include_glossary: bool = False) -> str:
    """
    Generate a Markdown export of processed YouTube video content.
    
    Args:
        processed_video (Dict[str, Any]): Processed video data
        include_transcript (bool): Whether to include the full transcript
        include_segments (bool): Whether to include segmented content
        include_summaries (bool): Whether to include segment summaries
        include_keypoints (bool): Whether to include segment keypoints
        include_questions (bool): Whether to include segment questions
        include_glossary (bool): Whether to include segment glossary terms
        
    Returns:
        str: Markdown content
    """
    logger.info("Generating Markdown export for processed YouTube video")
    
    # Initialize markdown content
    markdown = []
    
    # Add video information
    video_info = processed_video.get('video_info', {})
    title = video_info.get('title', 'YouTube Video')
    video_id = video_info.get('id', '')
    
    markdown.append(f"# {title}")
    markdown.append("")
    
    # Add video metadata
    markdown.append("## Video Information")
    markdown.append("")
    markdown.append(f"- **Title**: {title}")
    markdown.append(f"- **URL**: https://www.youtube.com/watch?v={video_id}")
    
    if 'channel' in video_info:
        markdown.append(f"- **Channel**: {video_info['channel']}")
    
    if 'upload_date' in video_info:
        date = video_info['upload_date']
        if len(date) == 8:  # Format YYYYMMDD
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            markdown.append(f"- **Upload Date**: {formatted_date}")
        else:
            markdown.append(f"- **Upload Date**: {date}")
    
    if 'duration' in video_info:
        duration_seconds = video_info['duration']
        hours, remainder = divmod(duration_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        markdown.append(f"- **Duration**: {duration_str}")
    
    markdown.append("")
    
    # Add video summary if available
    if 'summary' in processed_video and processed_video['summary']:
        markdown.append("## Summary")
        markdown.append("")
        markdown.append(processed_video['summary'])
        markdown.append("")
    
    # Add video keypoints if available
    if 'keypoints' in processed_video and processed_video['keypoints']:
        markdown.append("## Key Points")
        markdown.append("")
        for point in processed_video['keypoints']:
            markdown.append(f"- {point}")
        markdown.append("")
    
    # Add full transcript if requested
    if include_transcript and 'transcript' in processed_video and processed_video['transcript']:
        markdown.append("## Full Transcript")
        markdown.append("")
        markdown.append("```")
        for segment in processed_video['transcript']:
            timestamp = format_timestamp(segment.get('start', 0))
            text = segment.get('text', '')
            markdown.append(f"[{timestamp}] {text}")
        markdown.append("```")
        markdown.append("")
    
    # Add segmented content if requested
    if include_segments and 'processed_segments' in processed_video and processed_video['processed_segments']:
        markdown.append("## Segmented Content")
        markdown.append("")
        
        for i, segment in enumerate(processed_video['processed_segments'], 1):
            timestamp = segment.get('timestamp', '')
            markdown.append(f"### Segment {i}: {timestamp}")
            markdown.append("")
            
            # Add segment text
            if 'text' in segment and segment['text']:
                markdown.append("#### Transcript")
                markdown.append("")
                markdown.append("```")
                markdown.append(segment['text'])
                markdown.append("```")
                markdown.append("")
            
            # Add segment summary
            if include_summaries and 'summary' in segment and segment['summary']:
                markdown.append("#### Summary")
                markdown.append("")
                markdown.append(segment['summary'])
                markdown.append("")
            
            # Add segment keypoints
            if include_keypoints and 'keypoints' in segment and segment['keypoints']:
                markdown.append("#### Key Points")
                markdown.append("")
                for point in segment['keypoints']:
                    markdown.append(f"- {point}")
                markdown.append("")
            
            # Add segment questions
            if include_questions and 'questions' in segment and segment['questions']:
                markdown.append("#### Questions")
                markdown.append("")
                for q in segment['questions']:
                    question = q.get('question', '')
                    answer = q.get('answer', '')
                    markdown.append(f"**Q: {question}**")
                    markdown.append("")
                    markdown.append(f"A: {answer}")
                    markdown.append("")
            
            # Add segment glossary
            if include_glossary and 'glossary' in segment and segment['glossary']:
                markdown.append("#### Glossary")
                markdown.append("")
                for term, definition in segment['glossary'].items():
                    markdown.append(f"**{term}**: {definition}")
                    markdown.append("")
    
    # Join all lines
    return "\n".join(markdown)

def format_timestamp(seconds: float) -> str:
    """
    Format seconds to a timestamp string in format HH:MM:SS.
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

@optional_dependency("youtube")
def export_to_file(processed_video: Dict[str, Any], output_path: str, format: str = "markdown", **kwargs) -> bool:
    """
    Export processed YouTube video content to a file.
    
    Args:
        processed_video (Dict[str, Any]): Processed video data
        output_path (str): Path to save the exported file
        format (str): Export format (markdown, json, etc.)
        **kwargs: Additional format-specific options
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    logger.info(f"Exporting processed YouTube video to {format} file: {output_path}")
    
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Generate content based on format
        if format.lower() == "markdown":
            content = generate_markdown_export(processed_video, **kwargs)
        else:
            logger.error(f"Unsupported export format: {format}")
            return False
        
        # Write content to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully exported to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to file: {str(e)}")
        return False