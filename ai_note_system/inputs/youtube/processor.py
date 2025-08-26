"""
Processor module for YouTube processing.
Provides the main function for processing YouTube videos.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import dependency checker
from ...utils.dependency_checker import optional_dependency, check_dependency_group

# Import submodules
from .video_info import extract_video_id, get_video_info
from .transcript import download_transcript, extract_transcript_from_subtitles, get_best_transcript
from .segmentation import segment_transcript, process_segment
from .export import generate_markdown_export, export_to_file

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.youtube.processor")

# Check YouTube processing dependencies
YOUTUBE_DEPS_AVAILABLE, missing_youtube_deps = check_dependency_group("youtube")

@optional_dependency("youtube")
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
    Process a YouTube video by extracting audio, downloading transcript, and processing content.
    
    Args:
        youtube_url (str): URL of the YouTube video
        title (str, optional): Title for the video. If None, will use the video title from YouTube.
        tags (list, optional): List of tags for categorization
        save_audio (bool): Whether to save the audio file
        audio_dir (str, optional): Directory to save audio file. If None, uses a temporary directory.
        use_transcript (bool): Whether to use the official transcript if available
        transcript_language (str, optional): Language code for transcript. If None, tries to get the default transcript.
        segment_method (str): Method for segmentation. Options: "fixed", "topic", "smart"
        segment_size (int): Size of segments in seconds (for fixed method) or number of segments (for topic method)
        process_segments (bool): Whether to process segments with AI
        model (str): LLM model to use for processing
        generate_summary (bool): Whether to generate a summary
        generate_keypoints (bool): Whether to generate keypoints
        generate_glossary (bool): Whether to generate a glossary
        generate_questions (bool): Whether to generate questions
        num_questions (int): Number of questions to generate
        max_keypoints (int): Maximum number of keypoints to generate
        export_markdown (bool): Whether to export results to Markdown
        markdown_path (str, optional): Path to save Markdown file. If None, uses a default path.
        
    Returns:
        Dict[str, Any]: Dictionary containing processed video information
    """
    logger.info(f"Processing YouTube video: {youtube_url}")
    
    # Check if YouTube dependencies are available
    if not YOUTUBE_DEPS_AVAILABLE:
        missing_deps = ", ".join(missing_youtube_deps)
        logger.error(f"Missing YouTube processing dependencies: {missing_deps}")
        logger.info("Install required dependencies with: pip install yt-dlp youtube-transcript-api pydub opencv-python")
        return {"error": f"Missing dependencies: {missing_deps}"}
    
    try:
        # Extract video ID from URL
        video_id = extract_video_id(youtube_url)
        if not video_id:
            logger.error(f"Could not extract video ID from URL: {youtube_url}")
            return {"error": f"Invalid YouTube URL: {youtube_url}"}
        
        # Get video information
        video_info = get_video_info(video_id)
        if "error" in video_info:
            logger.error(f"Error getting video information: {video_info['error']}")
            # Continue processing, as we can still work with transcript
        
        # Use video title if not provided
        if not title and "title" in video_info:
            title = video_info["title"]
        
        # Get transcript
        transcript = []
        if use_transcript:
            transcript = get_best_transcript(video_id, transcript_language)
            
            if not transcript:
                logger.warning("Could not get transcript. Processing will continue without transcript.")
        
        # Initialize result dictionary
        result = {
            "video_id": video_id,
            "title": title or "YouTube Video",
            "url": youtube_url,
            "video_info": video_info,
            "transcript": transcript,
            "tags": tags or []
        }
        
        # Segment transcript if available
        if transcript:
            segments = segment_transcript(
                transcript,
                segment_method=segment_method,
                segment_size=segment_size
            )
            
            # Process segments if requested
            if process_segments and segments:
                processed_segments = []
                
                for segment in segments:
                    processed_segment = process_segment(
                        segment,
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
                
                # Generate overall summary and keypoints from segment summaries and keypoints
                if generate_summary:
                    try:
                        all_summaries = " ".join([s.get("summary", "") for s in processed_segments if "summary" in s])
                        if all_summaries:
                            from ...processing.summarizer import summarize_text
                            result["summary"] = summarize_text(all_summaries, model=model)
                    except Exception as e:
                        logger.error(f"Error generating overall summary: {str(e)}")
                
                if generate_keypoints:
                    try:
                        all_keypoints = []
                        for s in processed_segments:
                            if "keypoints" in s:
                                all_keypoints.extend(s["keypoints"])
                        
                        # Limit to max_keypoints * 2 for the overall video
                        result["keypoints"] = all_keypoints[:max_keypoints * 2]
                    except Exception as e:
                        logger.error(f"Error generating overall keypoints: {str(e)}")
        
        # Export to Markdown if requested
        if export_markdown:
            if not markdown_path:
                # Create a default path
                safe_title = "".join(c if c.isalnum() else "_" for c in result.get("title", "YouTube_Video"))
                safe_title = safe_title[:40]  # Limit length
                markdown_path = f"{safe_title}_{video_id}.md"
            
            export_success = export_to_file(
                result,
                markdown_path,
                format="markdown",
                include_transcript=True,
                include_segments=True,
                include_summaries=generate_summary,
                include_keypoints=generate_keypoints,
                include_questions=generate_questions,
                include_glossary=generate_glossary
            )
            
            if export_success:
                result["markdown_path"] = markdown_path
            else:
                logger.error(f"Failed to export to Markdown: {markdown_path}")
        
        logger.info(f"YouTube video processing complete: {youtube_url}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing YouTube video: {str(e)}")
        return {"error": str(e)}

@optional_dependency("youtube")
def batch_process_youtube_videos(
    youtube_urls: List[str],
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Process multiple YouTube videos in batch.
    
    Args:
        youtube_urls (List[str]): List of YouTube video URLs
        **kwargs: Additional arguments to pass to process_youtube_video
        
    Returns:
        List[Dict[str, Any]]: List of results for each video
    """
    logger.info(f"Batch processing {len(youtube_urls)} YouTube videos")
    
    results = []
    for url in youtube_urls:
        try:
            result = process_youtube_video(url, **kwargs)
            results.append(result)
        except Exception as e:
            logger.error(f"Error processing YouTube video {url}: {str(e)}")
            results.append({"url": url, "error": str(e)})
    
    return results