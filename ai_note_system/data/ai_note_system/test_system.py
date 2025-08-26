"""
Test script for AI Note System.
This script tests the basic functionality of the system by processing a text input.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai_note_system.test")

# Import required modules
from inputs.text_input import process_text
from processing.summarizer import summarize_text
from processing.keypoints_extractor import extract_keypoints, extract_glossary
from processing.active_recall_gen import generate_questions
from database.db_manager import DatabaseManager

def test_text_processing():
    """Test text processing functionality."""
    logger.info("Testing text processing functionality")
    
    # Sample text for testing
    sample_text = """
    Python is a high-level, interpreted programming language known for its readability and simplicity.
    It was created by Guido van Rossum and first released in 1991. Python supports multiple programming
    paradigms, including procedural, object-oriented, and functional programming. It has a comprehensive
    standard library and a large ecosystem of third-party packages, making it suitable for a wide range
    of applications, from web development to data science and artificial intelligence.
    
    Python's syntax is designed to be readable and uses indentation to define code blocks, rather than
    curly braces or keywords. This enforces a consistent coding style and makes the code more readable.
    Python's design philosophy emphasizes code readability, with its notable use of significant whitespace.
    
    Key features of Python include:
    - Easy to learn and use
    - Interpreted language (no compilation needed)
    - Dynamically typed (no need to declare variable types)
    - Object-oriented programming support
    - Extensive standard library
    - Large community and ecosystem
    """
    
    # Process the text
    logger.info("Processing text input")
    processed_text = process_text(sample_text, title="Introduction to Python", tags=["python", "programming"])
    
    # Generate summary
    logger.info("Generating summary")
    summary_result = summarize_text(sample_text, model="gpt-4")
    
    # Extract key points
    logger.info("Extracting key points")
    keypoints_result = extract_keypoints(sample_text, model="gpt-4")
    
    # Extract glossary
    logger.info("Extracting glossary")
    glossary_result = extract_glossary(sample_text, model="gpt-4")
    
    # Generate questions
    logger.info("Generating questions")
    questions_result = generate_questions(sample_text, model="gpt-4")
    
    # Store in database
    logger.info("Storing in database")
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pansophy.db")
    
    with DatabaseManager(db_path) as db:
        # Create note data
        note_data = {
            "title": processed_text["title"],
            "text": processed_text["text"],
            "summary": summary_result.get("summary", ""),
            "source_type": processed_text["source_type"],
            "word_count": processed_text["word_count"],
            "char_count": processed_text["char_count"],
            "tags": processed_text["tags"],
            "keypoints": keypoints_result.get("key_points", []),
            "glossary": glossary_result.get("glossary", {}),
            "questions": questions_result
        }
        
        # Create note in database
        note_id = db.create_note(note_data)
        logger.info(f"Created note with ID: {note_id}")
        
        # Retrieve note from database
        note = db.get_note(note_id)
        logger.info(f"Retrieved note: {note['title']}")
        
    logger.info("Test completed successfully")

if __name__ == "__main__":
    try:
        test_text_processing()
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)