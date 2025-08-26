"""
Utilities package for AI Note System.
Contains modules for logging, configuration loading, and helper functions.
"""

# Import modules to make them available when importing the package
from . import logger
from . import config_loader
from . import helpers

# Export key functions for easier access
from .logger import get_logger, configure_logger
from .config_loader import load_config
from .helpers import (
    ensure_directory_exists,
    get_file_extension,
    is_valid_file_type,
    generate_file_hash,
    save_json,
    load_json,
    sanitize_filename,
    get_timestamp,
    truncate_text,
    format_time_delta,
    extract_text_between_markers
)

__all__ = [
    'logger',
    'config_loader',
    'helpers',
    'get_logger',
    'configure_logger',
    'load_config',
    'ensure_directory_exists',
    'get_file_extension',
    'is_valid_file_type',
    'generate_file_hash',
    'save_json',
    'load_json',
    'sanitize_filename',
    'get_timestamp',
    'truncate_text',
    'format_time_delta',
    'extract_text_between_markers'
]