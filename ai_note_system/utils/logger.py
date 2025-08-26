"""
Logger module for AI Note System.
Provides centralized logging functionality with configurable log levels and output destinations.
"""

import logging
import os
import sys
from pathlib import Path

def setup_logger(log_level="INFO", log_file=None):
    """
    Set up and configure the logger for the AI Note System.
    
    Args:
        log_level (str): The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str, optional): Path to the log file. If None, logs will only be output to console.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("ai_note_system")
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # If log file is specified, add file handler
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    return logger

# Default logger instance
logger = setup_logger()

def get_logger():
    """
    Get the default logger instance.
    
    Returns:
        logging.Logger: The default logger instance
    """
    return logger

def configure_logger(config):
    """
    Configure the logger based on the provided configuration.
    
    Args:
        config (dict): Configuration dictionary containing LOG_LEVEL and LOG_FILE
        
    Returns:
        logging.Logger: Configured logger instance
    """
    global logger
    
    # Get log level and file from config
    log_level = config.get("LOG_LEVEL", "INFO")
    log_file = config.get("LOG_FILE")
    
    # Set up logger with config
    logger = setup_logger(log_level, log_file)
    
    logger.debug(f"Logger configured with level={log_level}, file={log_file}")
    
    return logger