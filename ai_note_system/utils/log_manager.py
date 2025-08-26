"""
Log Manager module for AI Note System.
Handles log rotation and offloading to Oracle Object Storage.
"""

import os
import logging
import datetime
import gzip
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

# Import Oracle Object Storage client
from storage.oracle_object_storage import OracleObjectStorage

# Setup logging
logger = logging.getLogger("ai_note_system.utils.log_manager")

class ObjectStorageRotatingFileHandler(RotatingFileHandler):
    """
    A rotating file handler that offloads old logs to Oracle Object Storage.
    """
    
    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 10 * 1024 * 1024,  # 10MB
        backupCount: int = 5,
        encoding: Optional[str] = None,
        delay: bool = False,
        object_storage: Optional[OracleObjectStorage] = None,
        bucket_name: Optional[str] = None,
        compress: bool = True
    ):
        """
        Initialize the handler.
        
        Args:
            filename (str): Log file path
            mode (str): File open mode
            maxBytes (int): Maximum file size in bytes before rotation
            backupCount (int): Number of backup files to keep
            encoding (Optional[str]): File encoding
            delay (bool): Delay file opening until first log record
            object_storage (Optional[OracleObjectStorage]): Oracle Object Storage client
            bucket_name (Optional[str]): Oracle Object Storage bucket name
            compress (bool): Whether to compress logs before uploading
        """
        super().__init__(
            filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay
        )
        self.object_storage = object_storage
        self.bucket_name = bucket_name
        self.compress = compress
        
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        
        This method is called when the log file size exceeds maxBytes.
        It rotates the log files and uploads the oldest one to Object Storage.
        """
        # First, do the standard rotation
        super().doRollover()
        
        # If object storage is not configured, skip upload
        if not self.object_storage or not self.bucket_name:
            return
            
        # Get the oldest log file (the one that would be deleted next)
        oldest_log = f"{self.baseFilename}.{self.backupCount}"
        
        # If the oldest log file exists, upload it to Object Storage
        if os.path.exists(oldest_log):
            try:
                # Generate object name with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                base_name = Path(self.baseFilename).name
                object_name = f"logs/{base_name}-{timestamp}"
                
                # Compress the log file if needed
                if self.compress:
                    compressed_log = f"{oldest_log}.gz"
                    with open(oldest_log, 'rb') as f_in:
                        with gzip.open(compressed_log, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    upload_path = compressed_log
                    object_name = f"{object_name}.gz"
                else:
                    upload_path = oldest_log
                
                # Upload to Object Storage
                self.object_storage.upload_file(
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    file_path=upload_path
                )
                
                logger.info(f"Uploaded log file to Object Storage: {object_name}")
                
                # Clean up compressed file if it was created
                if self.compress and os.path.exists(compressed_log):
                    os.remove(compressed_log)
                    
            except Exception as e:
                logger.error(f"Error uploading log file to Object Storage: {e}")


def setup_logging(
    log_dir: str = "logs",
    log_level: int = logging.INFO,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    object_storage: Optional[OracleObjectStorage] = None,
    bucket_name: Optional[str] = None
) -> None:
    """
    Set up logging with rotation and Object Storage offloading.
    
    Args:
        log_dir (str): Directory to store log files
        log_level (int): Logging level
        max_size (int): Maximum log file size in bytes
        backup_count (int): Number of backup files to keep
        object_storage (Optional[OracleObjectStorage]): Oracle Object Storage client
        bucket_name (Optional[str]): Oracle Object Storage bucket name
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler with rotation and Object Storage offloading
    log_file = os.path.join(log_dir, "ai_note_system.log")
    file_handler = ObjectStorageRotatingFileHandler(
        filename=log_file,
        maxBytes=max_size,
        backupCount=backup_count,
        object_storage=object_storage,
        bucket_name=bucket_name
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    logger.info("Logging configured with Object Storage offloading")


def get_object_storage_client() -> Optional[OracleObjectStorage]:
    """
    Get Oracle Object Storage client if credentials are available.
    
    Returns:
        Optional[OracleObjectStorage]: Oracle Object Storage client or None
    """
    try:
        # Check if Oracle Cloud credentials are available
        if (os.environ.get("OCI_CONFIG_FILE") or 
            (os.environ.get("OCI_USER_ID") and 
             os.environ.get("OCI_TENANCY_ID") and 
             os.environ.get("OCI_FINGERPRINT") and 
             os.environ.get("OCI_KEY_FILE"))):
            
            # Create Oracle Object Storage client
            from storage.oracle_object_storage import OracleObjectStorage
            return OracleObjectStorage()
        
        return None
    except Exception as e:
        logger.error(f"Error creating Oracle Object Storage client: {e}")
        return None