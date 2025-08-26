"""
Input pipeline package for AI Note System.
Contains modules for handling different types of input (text, PDF, OCR, speech).
"""

# Import modules to make them available when importing the package
from . import text_input
from . import pdf_input
from . import ocr_input
from . import speech_input

# Export key functions for easier access
from .text_input import process_text, load_text_from_file
from .pdf_input import extract_text_from_pdf, extract_images_from_pdf
from .ocr_input import extract_text_from_image, batch_process_images
from .speech_input import transcribe_audio, record_audio

__all__ = [
    'text_input',
    'pdf_input',
    'ocr_input',
    'speech_input',
    'process_text',
    'load_text_from_file',
    'extract_text_from_pdf',
    'extract_images_from_pdf',
    'extract_text_from_image',
    'batch_process_images',
    'transcribe_audio',
    'record_audio'
]