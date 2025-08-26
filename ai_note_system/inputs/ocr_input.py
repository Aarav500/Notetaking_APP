"""
OCR input module for AI Note System.
Handles extraction of text from images using OCR.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.ocr_input")

# Import text_input for processing extracted text
from . import text_input

def extract_text_from_image(
    image_path: str,
    engine: str = "pytesseract",
    save_raw: bool = True,
    raw_dir: Optional[str] = None,
    lang: str = "eng",
    preprocess: bool = True
) -> Dict[str, Any]:
    """
    Extract text from an image using OCR.
    
    Args:
        image_path (str): Path to the image file
        engine (str): OCR engine to use ('pytesseract' or 'easyocr')
        save_raw (bool): Whether to save the extracted text to disk
        raw_dir (str, optional): Directory to save raw text. If None, uses default.
        lang (str): Language code for OCR (default: 'eng')
        preprocess (bool): Whether to preprocess the image for better OCR results
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted text information
    """
    logger.info(f"Extracting text from image: {image_path}")
    
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        return {"error": f"Image file not found: {image_path}"}
    
    # Extract text based on the specified engine
    if engine.lower() == "pytesseract":
        text = extract_with_pytesseract(image_path, lang, preprocess)
    elif engine.lower() == "easyocr":
        text = extract_with_easyocr(image_path, lang)
    else:
        logger.error(f"Unsupported OCR engine: {engine}")
        return {"error": f"Unsupported OCR engine: {engine}"}
    
    if not text:
        logger.error(f"Failed to extract text from image: {image_path}")
        return {"error": f"Failed to extract text from image: {image_path}"}
    
    # Generate title from filename
    filename = os.path.basename(image_path)
    title = os.path.splitext(filename)[0].replace('_', ' ')
    
    # Process the extracted text
    result = text_input.process_text(
        text=text,
        title=title,
        tags=["image", "ocr"],
        save_raw=save_raw,
        raw_dir=raw_dir
    )
    
    # Add image-specific metadata
    result["source_type"] = "image"
    result["source_path"] = image_path
    
    logger.debug(f"Image processed: {title} ({result['word_count']} words)")
    return result

def extract_with_pytesseract(
    image_path: str,
    lang: str = "eng",
    preprocess: bool = True
) -> str:
    """
    Extract text from an image using pytesseract.
    
    Args:
        image_path (str): Path to the image file
        lang (str): Language code for OCR
        preprocess (bool): Whether to preprocess the image for better OCR results
        
    Returns:
        str: Extracted text
    """
    try:
        import pytesseract
        from PIL import Image, ImageEnhance, ImageFilter
        import cv2
        import numpy as np
        
        logger.debug(f"Opening image with pytesseract: {image_path}")
        
        # Load image
        if preprocess:
            # Use OpenCV for preprocessing
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get black and white image
            _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            # Noise removal
            denoised = cv2.medianBlur(binary, 3)
            
            # Convert back to PIL Image
            pil_image = Image.fromarray(denoised)
        else:
            # Use PIL directly
            pil_image = Image.open(image_path)
        
        # Extract text
        text = pytesseract.image_to_string(pil_image, lang=lang)
        
        logger.debug(f"Extracted {len(text)} characters from image")
        return text
        
    except ImportError as e:
        logger.error(f"Required packages not installed: {e}. Install with: pip install pytesseract pillow opencv-python")
        return ""
        
    except Exception as e:
        logger.error(f"Error extracting text with pytesseract: {e}")
        return ""

def extract_with_easyocr(
    image_path: str,
    lang: str = "en"
) -> str:
    """
    Extract text from an image using EasyOCR.
    
    Args:
        image_path (str): Path to the image file
        lang (str): Language code for OCR
        
    Returns:
        str: Extracted text
    """
    try:
        import easyocr
        
        logger.debug(f"Opening image with EasyOCR: {image_path}")
        
        # Initialize reader
        reader = easyocr.Reader([lang])
        
        # Extract text
        results = reader.readtext(image_path)
        
        # Combine results
        text_parts = [result[1] for result in results]
        text = "\n".join(text_parts)
        
        logger.debug(f"Extracted {len(text)} characters from image using EasyOCR")
        return text
        
    except ImportError:
        logger.error("EasyOCR not installed. Install with: pip install easyocr")
        return ""
        
    except Exception as e:
        logger.error(f"Error extracting text with EasyOCR: {e}")
        return ""

def batch_process_images(
    image_dir: str,
    output_dir: Optional[str] = None,
    engine: str = "pytesseract",
    lang: str = "eng",
    preprocess: bool = True
) -> List[Dict[str, Any]]:
    """
    Process multiple images in a directory.
    
    Args:
        image_dir (str): Directory containing images
        output_dir (str, optional): Directory to save extracted text. If None, uses default.
        engine (str): OCR engine to use
        lang (str): Language code for OCR
        preprocess (bool): Whether to preprocess images
        
    Returns:
        List[Dict[str, Any]]: List of results for each processed image
    """
    logger.info(f"Batch processing images in directory: {image_dir}")
    
    if not os.path.exists(image_dir) or not os.path.isdir(image_dir):
        logger.error(f"Image directory not found: {image_dir}")
        return [{"error": f"Image directory not found: {image_dir}"}]
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(list(Path(image_dir).glob(f"*{ext}")))
        image_files.extend(list(Path(image_dir).glob(f"*{ext.upper()}")))
    
    if not image_files:
        logger.warning(f"No image files found in directory: {image_dir}")
        return [{"error": f"No image files found in directory: {image_dir}"}]
    
    # Process each image
    results = []
    for image_file in image_files:
        result = extract_text_from_image(
            str(image_file),
            engine=engine,
            save_raw=True,
            raw_dir=output_dir,
            lang=lang,
            preprocess=preprocess
        )
        results.append(result)
    
    logger.info(f"Processed {len(results)} images")
    return results