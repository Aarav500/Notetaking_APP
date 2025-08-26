# YouTube Processing Package

This package provides functionality for processing YouTube videos, including:
- Extracting video information
- Downloading and processing transcripts
- Segmenting transcripts
- Processing segments with AI
- Exporting results to various formats

## Overview

The YouTube processing functionality has been modularized into separate components:

- **video_info.py**: Functions for extracting video IDs and retrieving video information
- **transcript.py**: Functions for downloading and processing transcripts
- **segmentation.py**: Functions for segmenting and processing transcript segments
- **export.py**: Functions for exporting processed content to various formats
- **processor.py**: Main processing functions that orchestrate the entire pipeline

## Usage

### Basic Usage

```python
from ai_note_system.inputs.youtube import process_youtube_video

# Process a YouTube video
result = process_youtube_video(
    youtube_url="https://www.youtube.com/watch?v=VIDEO_ID",
    generate_summary=True,
    generate_keypoints=True,
    generate_questions=True,
    export_markdown=True
)

# Access the processed data
video_info = result.get("video_info", {})
transcript = result.get("transcript", [])
processed_segments = result.get("processed_segments", [])
summary = result.get("summary", "")
keypoints = result.get("keypoints", [])
```

### Batch Processing

```python
from ai_note_system.inputs.youtube import batch_process_youtube_videos

# Process multiple YouTube videos
urls = [
    "https://www.youtube.com/watch?v=VIDEO_ID_1",
    "https://www.youtube.com/watch?v=VIDEO_ID_2",
    "https://www.youtube.com/watch?v=VIDEO_ID_3"
]

results = batch_process_youtube_videos(
    youtube_urls=urls,
    generate_summary=True,
    generate_keypoints=True,
    export_markdown=True
)

# Access the results
for result in results:
    if "error" in result:
        print(f"Error processing {result.get('url', 'unknown')}: {result['error']}")
    else:
        print(f"Successfully processed: {result.get('title', 'unknown')}")
```

### Advanced Usage

You can also use the individual components directly:

```python
from ai_note_system.inputs.youtube import (
    extract_video_id,
    get_video_info,
    get_best_transcript,
    segment_transcript,
    process_segment,
    generate_markdown_export
)

# Extract video ID
video_id = extract_video_id("https://www.youtube.com/watch?v=VIDEO_ID")

# Get video information
video_info = get_video_info(video_id)

# Get transcript
transcript = get_best_transcript(video_id)

# Segment transcript
segments = segment_transcript(transcript, segment_method="fixed", segment_size=30)

# Process segments
processed_segments = []
for segment in segments:
    processed_segment = process_segment(
        segment,
        model="gpt-4",
        generate_summary=True,
        generate_keypoints=True,
        generate_questions=True
    )
    processed_segments.append(processed_segment)

# Generate Markdown export
markdown = generate_markdown_export({
    "video_info": video_info,
    "transcript": transcript,
    "processed_segments": processed_segments
})
```

## Dependencies

This package requires the following dependencies:
- yt-dlp
- youtube-transcript-api
- pydub
- opencv-python

These dependencies are optional and will be checked at runtime. If any are missing, helpful error messages will be displayed with installation instructions.

## Error Handling

All functions in this package include comprehensive error handling and logging. If a dependency is missing, a helpful error message will be displayed with installation instructions. If an error occurs during processing, it will be logged and returned in the result dictionary.

## Backward Compatibility

This package maintains backward compatibility with the original `youtube_input.py` module. All functions from the original module are still available through this package, so existing code will continue to work without changes.

## New Features

Compared to the original implementation, this package adds:
- Better error handling for missing dependencies
- More informative error messages
- Batch processing capabilities
- Additional export options
- More modular and maintainable code structure