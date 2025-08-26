"""
Test script for YouTube video processing functionality.
This script demonstrates how to use the YouTube video processing features.
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai_note_system.test_youtube")

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import YouTube processing module
from ai_note_system.inputs.youtube_input import process_youtube_video

def test_youtube_processing():
    """Test YouTube video processing functionality."""
    logger.info("Testing YouTube video processing functionality")
    
    # Sample YouTube URL (a short educational video)
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with an actual educational video
    
    # Create output directory for test results
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # Process the YouTube video
    logger.info(f"Processing YouTube video: {youtube_url}")
    
    result = process_youtube_video(
        youtube_url=youtube_url,
        title=None,  # Use video title
        tags=["test", "youtube"],
        save_audio=False,
        use_transcript=True,
        transcript_language=None,  # Auto-detect
        segment_method="fixed",
        segment_size=60,  # 60-second segments
        process_segments=True,
        model="gpt-3.5-turbo",  # Use a faster model for testing
        generate_summary=True,
        generate_keypoints=True,
        generate_glossary=False,
        generate_questions=True,
        num_questions=2,
        max_keypoints=3,
        export_markdown=True,
        markdown_path=os.path.join(output_dir, "youtube_test.md")
    )
    
    # Check if processing was successful
    if "error" in result:
        logger.error(f"Error processing YouTube video: {result['error']}")
        return False
    
    # Print some information about the processed video
    logger.info(f"Successfully processed video: {result.get('title', 'Unknown')}")
    logger.info(f"Video ID: {result.get('video_id', 'Unknown')}")
    
    # Check if segments were processed
    segments = result.get("processed_segments", [])
    logger.info(f"Processed {len(segments)} segments")
    
    # Check if Markdown was exported
    if "markdown_path" in result:
        logger.info(f"Markdown exported to: {result['markdown_path']}")
    
    return True

def test_youtube_transcript_only():
    """Test YouTube transcript extraction only."""
    logger.info("Testing YouTube transcript extraction")
    
    # Sample YouTube URL (a short educational video)
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with an actual educational video
    
    # Process the YouTube video (transcript only)
    logger.info(f"Extracting transcript from YouTube video: {youtube_url}")
    
    result = process_youtube_video(
        youtube_url=youtube_url,
        use_transcript=True,
        process_segments=False,
        export_markdown=False
    )
    
    # Check if processing was successful
    if "error" in result:
        logger.error(f"Error extracting transcript: {result['error']}")
        return False
    
    # Print some information about the transcript
    transcript = result.get("transcript", [])
    logger.info(f"Extracted transcript with {len(transcript)} segments")
    
    # Print the first few transcript segments
    for i, segment in enumerate(transcript[:3]):
        start = segment.get("start", 0)
        text = segment.get("text", "")
        logger.info(f"[{start:.2f}s] {text}")
    
    return True

if __name__ == "__main__":
    try:
        # Test full processing
        success = test_youtube_processing()
        
        # Test transcript extraction only
        # success = test_youtube_transcript_only()
        
        if not success:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)