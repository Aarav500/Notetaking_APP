"""
Image extraction module for AI Note System.
Extracts images from videos and slides for use in flashcards.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.processing.image_extractor")

def extract_images_from_video(
    video_path: str,
    output_dir: Optional[str] = None,
    interval_seconds: float = 30.0,
    min_image_size: int = 200,
    max_images: int = 10,
    detect_slides: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract images from a video file.
    
    Args:
        video_path (str): Path to the video file
        output_dir (str, optional): Directory to save extracted images
        interval_seconds (float): Interval between frames to extract (in seconds)
        min_image_size (int): Minimum size (width or height) for extracted images
        max_images (int): Maximum number of images to extract
        detect_slides (bool): Whether to detect slide transitions
        
    Returns:
        List[Dict[str, Any]]: List of extracted images with metadata
    """
    logger.info(f"Extracting images from video: {video_path}")
    
    # Create output directory if not provided
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="pansophy_images_")
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # Open video file
    try:
        video = cv2.VideoCapture(video_path)
        
        # Check if video opened successfully
        if not video.isOpened():
            logger.error(f"Error opening video file: {video_path}")
            return []
        
        # Get video properties
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        
        logger.info(f"Video properties: {fps} fps, {frame_count} frames, {duration:.2f} seconds")
        
        # Calculate frame interval
        frame_interval = int(fps * interval_seconds)
        
        # Initialize variables
        extracted_images = []
        prev_frame = None
        frame_diff_threshold = 0.2  # Threshold for slide transition detection
        
        # Process video frames
        frame_idx = 0
        while frame_idx < frame_count and len(extracted_images) < max_images:
            # Set frame position
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            
            # Read frame
            ret, frame = video.read()
            if not ret:
                break
            
            # Check if frame should be extracted
            should_extract = False
            
            if detect_slides and prev_frame is not None:
                # Calculate frame difference for slide detection
                diff = calculate_frame_difference(prev_frame, frame)
                if diff > frame_diff_threshold:
                    should_extract = True
                    logger.info(f"Slide transition detected at frame {frame_idx} (diff: {diff:.2f})")
            elif frame_idx % frame_interval == 0:
                should_extract = True
            
            if should_extract:
                # Extract image
                timestamp = frame_idx / fps
                image_path = os.path.join(output_dir, f"frame_{frame_idx:06d}.jpg")
                
                # Save image
                cv2.imwrite(image_path, frame)
                
                # Add to extracted images
                extracted_images.append({
                    "path": image_path,
                    "timestamp": timestamp,
                    "frame_idx": frame_idx,
                    "time_str": format_timestamp(timestamp)
                })
                
                logger.info(f"Extracted image at {format_timestamp(timestamp)} (frame {frame_idx})")
            
            # Update previous frame
            prev_frame = frame.copy()
            
            # Update frame index
            if detect_slides:
                frame_idx += int(fps)  # Check every second for slide transitions
            else:
                frame_idx += frame_interval
        
        # Close video file
        video.release()
        
        return extracted_images
        
    except Exception as e:
        logger.error(f"Error extracting images from video: {str(e)}")
        return []

def extract_images_from_pdf(
    pdf_path: str,
    output_dir: Optional[str] = None,
    max_images: int = 10,
    min_image_size: int = 200
) -> List[Dict[str, Any]]:
    """
    Extract images from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str, optional): Directory to save extracted images
        max_images (int): Maximum number of images to extract
        min_image_size (int): Minimum size (width or height) for extracted images
        
    Returns:
        List[Dict[str, Any]]: List of extracted images with metadata
    """
    logger.info(f"Extracting images from PDF: {pdf_path}")
    
    # Create output directory if not provided
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="pansophy_images_")
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        import fitz  # PyMuPDF
        
        # Open PDF file
        pdf = fitz.open(pdf_path)
        
        # Initialize variables
        extracted_images = []
        image_count = 0
        
        # Process each page
        for page_idx, page in enumerate(pdf):
            # Get images from page
            image_list = page.get_images(full=True)
            
            for img_idx, img in enumerate(image_list):
                if image_count >= max_images:
                    break
                
                # Get image properties
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Skip small images
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                if width < min_image_size or height < min_image_size:
                    continue
                
                # Save image
                image_path = os.path.join(output_dir, f"page_{page_idx+1:03d}_img_{img_idx+1:03d}.{image_ext}")
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                
                # Add to extracted images
                extracted_images.append({
                    "path": image_path,
                    "page": page_idx + 1,
                    "width": width,
                    "height": height,
                    "format": image_ext
                })
                
                logger.info(f"Extracted image from page {page_idx+1} (size: {width}x{height})")
                
                image_count += 1
        
        # Close PDF file
        pdf.close()
        
        return extracted_images
        
    except ImportError:
        logger.error("PyMuPDF (fitz) package not installed. Install with: pip install PyMuPDF")
        return []
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {str(e)}")
        return []

def calculate_frame_difference(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """
    Calculate the difference between two frames.
    
    Args:
        frame1 (np.ndarray): First frame
        frame2 (np.ndarray): Second frame
        
    Returns:
        float: Difference score (0.0 to 1.0)
    """
    # Convert to grayscale
    gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    
    # Calculate absolute difference
    diff = cv2.absdiff(gray1, gray2)
    
    # Normalize difference
    norm_diff = np.sum(diff) / (diff.shape[0] * diff.shape[1] * 255)
    
    return norm_diff

def format_timestamp(seconds: float) -> str:
    """
    Format timestamp in HH:MM:SS format.
    
    Args:
        seconds (float): Timestamp in seconds
        
    Returns:
        str: Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def extract_images_from_content(
    content: Dict[str, Any],
    max_images: int = 5
) -> List[Dict[str, Any]]:
    """
    Extract images from content based on source type.
    
    Args:
        content (Dict[str, Any]): Content to extract images from
        max_images (int): Maximum number of images to extract
        
    Returns:
        List[Dict[str, Any]]: List of extracted images with metadata
    """
    # Get source type and path
    source_type = content.get("source_type", "")
    source_path = content.get("source_path", "")
    
    # Skip if no source path
    if not source_path:
        logger.warning("No source path provided")
        return []
    
    # Extract images based on source type
    if source_type == "video" or source_type == "youtube":
        return extract_images_from_video(
            source_path,
            max_images=max_images,
            detect_slides=True
        )
    elif source_type == "pdf":
        return extract_images_from_pdf(
            source_path,
            max_images=max_images
        )
    else:
        logger.warning(f"Unsupported source type for image extraction: {source_type}")
        return []