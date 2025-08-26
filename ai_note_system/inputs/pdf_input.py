"""
PDF input module for AI Note System.
Handles extraction of text from PDF files.
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.pdf_input")

# Import text_input for processing extracted text
from . import text_input

def extract_text_from_pdf(
    pdf_path: str,
    method: str = "PyMuPDF",
    save_raw: bool = True,
    raw_dir: Optional[str] = None,
    ocr_if_needed: bool = True,
    pages: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        method (str): Method to use for extraction ('PyMuPDF' or 'pdf2image+OCR')
        save_raw (bool): Whether to save the extracted text to disk
        raw_dir (str, optional): Directory to save raw text. If None, uses default.
        ocr_if_needed (bool): Whether to fall back to OCR if text extraction fails
        pages (List[int], optional): List of page numbers to extract (0-indexed). If None, extracts all pages.
        
    Returns:
        Dict[str, Any]: Dictionary containing extracted text information
    """
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return {"error": f"PDF file not found: {pdf_path}"}
    
    # Extract text based on the specified method
    if method.lower() == "pymupdf":
        text, page_count = extract_with_pymupdf(pdf_path, pages)
    elif method.lower() == "pdf2image+ocr":
        text, page_count = extract_with_ocr(pdf_path, pages)
    else:
        logger.error(f"Unsupported extraction method: {method}")
        return {"error": f"Unsupported extraction method: {method}"}
    
    # If text extraction failed and OCR fallback is enabled
    if not text and ocr_if_needed and method.lower() != "pdf2image+ocr":
        logger.warning(f"Text extraction failed, falling back to OCR")
        text, page_count = extract_with_ocr(pdf_path, pages)
    
    if not text:
        logger.error(f"Failed to extract text from PDF: {pdf_path}")
        return {"error": f"Failed to extract text from PDF: {pdf_path}"}
    
    # Generate title from filename
    filename = os.path.basename(pdf_path)
    title = os.path.splitext(filename)[0].replace('_', ' ')
    
    # Process the extracted text
    result = text_input.process_text(
        text=text,
        title=title,
        tags=["pdf"],
        save_raw=save_raw,
        raw_dir=raw_dir
    )
    
    # Add PDF-specific metadata
    result["source_type"] = "pdf"
    result["source_path"] = pdf_path
    result["page_count"] = page_count
    
    logger.debug(f"PDF processed: {title} ({result['word_count']} words, {page_count} pages)")
    return result

def extract_with_pymupdf(pdf_path: str, pages: Optional[List[int]] = None) -> Tuple[str, int]:
    """
    Extract text from a PDF using PyMuPDF (fitz).
    
    Args:
        pdf_path (str): Path to the PDF file
        pages (List[int], optional): List of page numbers to extract (0-indexed). If None, extracts all pages.
        
    Returns:
        Tuple[str, int]: Extracted text and page count
    """
    try:
        import fitz  # PyMuPDF
        
        logger.debug(f"Opening PDF with PyMuPDF: {pdf_path}")
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        
        # Extract text from specified pages or all pages
        text_parts = []
        page_range = pages if pages is not None else range(page_count)
        
        for page_num in page_range:
            if 0 <= page_num < page_count:
                page = doc[page_num]
                text_parts.append(page.get_text())
        
        doc.close()
        
        # Combine text from all pages
        text = "\n\n".join(text_parts)
        
        logger.debug(f"Extracted {len(text)} characters from {len(page_range)} pages")
        return text, page_count
        
    except ImportError:
        logger.error("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
        return "", 0
        
    except Exception as e:
        logger.error(f"Error extracting text with PyMuPDF: {e}")
        return "", 0

def extract_with_ocr(pdf_path: str, pages: Optional[List[int]] = None) -> Tuple[str, int]:
    """
    Extract text from a PDF using pdf2image and OCR.
    
    Args:
        pdf_path (str): Path to the PDF file
        pages (List[int], optional): List of page numbers to extract (0-indexed). If None, extracts all pages.
        
    Returns:
        Tuple[str, int]: Extracted text and page count
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
        from PIL import Image
        
        logger.debug(f"Converting PDF to images: {pdf_path}")
        
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        page_count = len(images)
        
        # Extract text from specified pages or all pages
        text_parts = []
        page_range = pages if pages is not None else range(page_count)
        
        for i, page_num in enumerate(page_range):
            if 0 <= page_num < page_count:
                logger.debug(f"OCR processing page {page_num+1}/{page_count}")
                image = images[page_num]
                text = pytesseract.image_to_string(image)
                text_parts.append(text)
        
        # Combine text from all pages
        text = "\n\n".join(text_parts)
        
        logger.debug(f"Extracted {len(text)} characters from {len(page_range)} pages using OCR")
        return text, page_count
        
    except ImportError as e:
        logger.error(f"Required packages not installed: {e}. Install with: pip install pdf2image pytesseract")
        return "", 0
        
    except Exception as e:
        logger.error(f"Error extracting text with OCR: {e}")
        return "", 0

def extract_images_from_pdf(
    pdf_path: str,
    output_dir: Optional[str] = None,
    min_width: int = 100,
    min_height: int = 100
) -> List[str]:
    """
    Extract images from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str, optional): Directory to save extracted images. If None, uses a temp directory.
        min_width (int): Minimum width for extracted images
        min_height (int): Minimum height for extracted images
        
    Returns:
        List[str]: List of paths to extracted images
    """
    try:
        import fitz  # PyMuPDF
        
        logger.info(f"Extracting images from PDF: {pdf_path}")
        
        # Create output directory if not specified
        if not output_dir:
            output_dir = tempfile.mkdtemp(prefix="pdf_images_")
        else:
            os.makedirs(output_dir, exist_ok=True)
        
        # Open the PDF
        doc = fitz.open(pdf_path)
        image_paths = []
        
        # Iterate through pages
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                
                # Extract image
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # Get image dimensions
                width = base_image.get("width", 0)
                height = base_image.get("height", 0)
                
                # Skip small images
                if width < min_width or height < min_height:
                    continue
                
                # Save image to file
                image_filename = f"page{page_num+1}_img{img_index+1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)
                
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                
                image_paths.append(image_path)
                logger.debug(f"Extracted image: {image_path} ({width}x{height})")
        
        logger.info(f"Extracted {len(image_paths)} images from PDF")
        return image_paths
        
    except ImportError:
        logger.error("PyMuPDF (fitz) not installed. Install with: pip install PyMuPDF")
        return []
        
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {e}")
        return []