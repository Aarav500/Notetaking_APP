"""
YouTube processing package for AI Note System.
This package provides modules for processing YouTube videos, including:
- Extracting video information
- Downloading and processing transcripts
- Segmenting transcripts
- Generating exports
"""

# Import dependency checker
from ...utils.dependency_checker import require_dependencies, check_dependency_group, optional_dependency, fallback_on_missing_dependency

# Check YouTube processing dependencies
YOUTUBE_DEPS_AVAILABLE, missing_youtube_deps = check_dependency_group("youtube")

# Import submodules
from .video_info import extract_video_id, get_video_info
from .transcript import (
    download_transcript, 
    extract_transcript_from_subtitles, 
    parse_vtt_file, 
    get_best_transcript
)
from .segmentation import (
    segment_transcript, 
    process_segment, 
    convert_timestamp_to_seconds, 
    format_seconds_to_timestamp
)
from .export import generate_markdown_export, export_to_file

# Import main processing function
from .processor import process_youtube_video, batch_process_youtube_videos

# For backward compatibility, ensure all functions from the original module are available
# If any function is missing from the new modules, it will be imported from the original module
try:
    from ..youtube_input import *
    # Override with our new implementations
    from .video_info import *
    from .transcript import *
    from .segmentation import *
    from .export import *
    from .processor import *
except ImportError:
    logger.warning("Could not import from original youtube_input.py for backward compatibility")

# For backward compatibility with the original youtube_input.py and to export new functions
__all__ = [
    # Video info functions
    'extract_video_id',
    'get_video_info',
    
    # Transcript functions
    'download_transcript',
    'extract_transcript_from_subtitles',
    'parse_vtt_file',
    'get_best_transcript',
    
    # Segmentation functions
    'segment_transcript',
    'process_segment',
    'convert_timestamp_to_seconds',
    'format_seconds_to_timestamp',
    
    # Export functions
    'generate_markdown_export',
    'export_to_file',
    
    # Processing functions
    'process_youtube_video',
    'batch_process_youtube_videos',
    
    # Constants
    'YOUTUBE_DEPS_AVAILABLE'
]