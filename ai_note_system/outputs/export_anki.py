"""
Anki export module for AI Note System.
Handles exporting notes to Anki flashcard format.
"""

import os
import logging
import json
import tempfile
import random
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.export_anki")

def export_to_anki(
    content: Dict[str, Any],
    output_path: str,
    deck_name: Optional[str] = None,
    include_metadata: bool = True,
    include_source: bool = False,
    card_types: Optional[List[str]] = None,
    include_images: bool = True
) -> Dict[str, Any]:
    """
    Export content to Anki flashcard format.
    
    Args:
        content (Dict[str, Any]): The content to export
        output_path (str): Path to save the Anki deck file (.apkg)
        deck_name (str, optional): Name of the Anki deck
        include_metadata (bool): Whether to include metadata in the cards
        include_source (bool): Whether to include source text in the cards
        card_types (List[str], optional): Types of cards to include (questions, mcqs, fill_blanks)
        
    Returns:
        Dict[str, Any]: Result of the export operation
    """
    logger.info("Exporting content to Anki")
    
    try:
        # Check if required packages are installed
        try:
            import genanki
            GENANKI_AVAILABLE = True
        except ImportError:
            error_msg = "genanki package not installed. Cannot export to Anki."
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        
        # Set default card types if not provided
        if card_types is None:
            card_types = ["questions", "mcqs", "fill_blanks"]
        
        # Set default deck name if not provided
        if deck_name is None:
            deck_name = content.get("title", "AI Note System Export")
        
        # Create Anki deck
        deck = create_anki_deck(
            content,
            deck_name=deck_name,
            include_metadata=include_metadata,
            include_source=include_source,
            card_types=card_types
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Generate package
        package = genanki.Package(deck)
        package.write_to_file(output_path)
        
        logger.info(f"Anki deck saved to {output_path}")
        return {"success": True, "output_path": output_path}
        
    except Exception as e:
        error_msg = f"Error exporting to Anki: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def create_anki_deck(
    content: Dict[str, Any],
    deck_name: str,
    include_metadata: bool = True,
    include_source: bool = False,
    card_types: List[str] = ["questions", "mcqs", "fill_blanks", "cloze", "image_cards"],
    include_images: bool = True
) -> Any:
    """
    Create an Anki deck from the provided content.
    
    Args:
        content (Dict[str, Any]): The content to export
        deck_name (str): Name of the Anki deck
        include_metadata (bool): Whether to include metadata in the cards
        include_source (bool): Whether to include source text in the cards
        card_types (List[str]): Types of cards to include
        include_images (bool): Whether to include images in the cards
        
    Returns:
        Any: Anki deck object
    """
    import genanki
    
    # Create a unique deck ID based on content title and timestamp
    title = content.get("title", "Untitled")
    timestamp = int(time.time())
    deck_id = random.randrange(1 << 30, 1 << 31)
    
    # Create the deck
    deck = genanki.Deck(deck_id, deck_name)
    
    # Create package for media files
    package = genanki.Package(deck)
    package.media_files = []
    
    # Add metadata note if requested
    if include_metadata:
        metadata_model = create_metadata_model()
        metadata_note = create_metadata_note(content, metadata_model)
        deck.add_note(metadata_note)
    
    # Add cards based on requested types
    if "questions" in card_types and "questions" in content:
        question_model = create_basic_model()
        for question in content["questions"]:
            if isinstance(question, dict) and "question" in question and "answer" in question:
                note = create_basic_note(
                    question["question"],
                    question["answer"],
                    question_model,
                    source=content.get("text", "") if include_source else None
                )
                deck.add_note(note)
    
    if "mcqs" in card_types and "mcqs" in content:
        mcq_model = create_mcq_model()
        for mcq in content["mcqs"]:
            if isinstance(mcq, dict) and "question" in mcq and "options" in mcq and "answer" in mcq:
                note = create_mcq_note(
                    mcq["question"],
                    mcq["options"],
                    mcq["answer"],
                    mcq_model,
                    source=content.get("text", "") if include_source else None
                )
                deck.add_note(note)
    
    if "fill_blanks" in card_types and "fill_blanks" in content:
        fill_blank_model = create_fill_blank_model()
        for blank in content["fill_blanks"]:
            if isinstance(blank, dict) and "text" in blank and "answer" in blank:
                note = create_fill_blank_note(
                    blank["text"],
                    blank["answer"],
                    fill_blank_model,
                    source=content.get("text", "") if include_source else None
                )
                deck.add_note(note)
    
    # Add cloze deletion cards if available
    if "cloze" in card_types and "cloze" in content:
        cloze_model = create_cloze_model()
        for cloze in content.get("cloze", []):
            if isinstance(cloze, dict) and "text" in cloze:
                note = create_cloze_note(
                    cloze["text"],
                    cloze.get("extra", ""),
                    cloze_model,
                    source=content.get("text", "") if include_source else None
                )
                deck.add_note(note)
    
    # Add image cards if available and requested
    if include_images and "image_cards" in card_types:
        image_card_model = create_image_card_model()
        
        # Process images from content
        images = content.get("images", [])
        
        # If no images in content, try to extract them
        if not images and include_images:
            try:
                from ai_note_system.processing.image_extractor import extract_images_from_content
                images = extract_images_from_content(content)
            except ImportError:
                logger.warning("Image extractor module not available")
            except Exception as e:
                logger.error(f"Error extracting images: {str(e)}")
        
        # Create image cards
        for image in images:
            if isinstance(image, dict) and "path" in image:
                # Generate question and answer if not provided
                question = image.get("question", f"Describe what you see in this image")
                answer = image.get("answer", "")
                
                # If no answer, try to generate one based on context
                if not answer and "timestamp" in image:
                    # For video images, use timestamp to find relevant content
                    timestamp = image.get("timestamp", 0)
                    time_str = image.get("time_str", "")
                    
                    # Add timestamp to question
                    if time_str:
                        question = f"{question} (at {time_str})"
                    
                    # Try to find content around this timestamp
                    segments = content.get("segments", [])
                    for segment in segments:
                        if abs(segment.get("start_time", 0) - timestamp) < 10:
                            answer = segment.get("summary", "")
                            break
                
                # Create image card
                note = create_image_card_note(
                    question,
                    image["path"],
                    answer,
                    image_card_model,
                    source=content.get("text", "") if include_source else None,
                    package=package
                )
                deck.add_note(note)
    
    # Add glossary terms if available
    if "glossary" in card_types and "glossary" in content:
        glossary_model = create_basic_model()
        for term in content["glossary"]:
            if isinstance(term, dict) and "term" in term and "definition" in term:
                note = create_basic_note(
                    term["term"],
                    term["definition"],
                    glossary_model,
                    source=content.get("text", "") if include_source else None
                )
                deck.add_note(note)
    
    return deck

def create_metadata_model() -> Any:
    """
    Create an Anki note model for metadata.
    
    Returns:
        Any: Anki note model
    """
    import genanki
    
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'AI Note System - Metadata',
        fields=[
            {'name': 'Title'},
            {'name': 'Metadata'},
        ],
        templates=[
            {
                'name': 'Metadata Card',
                'qfmt': '''
                <div class="card-title">{{Title}}</div>
                <div class="card-question">Note Information</div>
                ''',
                'afmt': '''
                <div class="card-title">{{Title}}</div>
                <div class="card-question">Note Information</div>
                <hr>
                <div class="card-answer">{{Metadata}}</div>
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        .card-title {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .card-question {
            font-size: 18px;
            color: #3498db;
            margin-bottom: 10px;
        }
        .card-answer {
            font-size: 16px;
            color: #333;
        }
        .metadata-item {
            margin-bottom: 5px;
        }
        .metadata-label {
            font-weight: bold;
            color: #555;
        }
        .tag {
            display: inline-block;
            background-color: #e0f7fa;
            color: #0097a7;
            padding: 2px 8px;
            border-radius: 4px;
            margin-right: 5px;
            font-size: 0.9em;
        }
        '''
    )
    
    return model

def create_basic_model() -> Any:
    """
    Create an Anki note model for basic question and answer cards.
    
    Returns:
        Any: Anki note model
    """
    import genanki
    
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'AI Note System - Basic',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Source'},
        ],
        templates=[
            {
                'name': 'Basic Card',
                'qfmt': '''
                <div class="card-question">{{Question}}</div>
                ''',
                'afmt': '''
                <div class="card-question">{{Question}}</div>
                <hr>
                <div class="card-answer">{{Answer}}</div>
                {{#Source}}
                <div class="card-source">
                    <hr>
                    <div class="source-label">Source:</div>
                    <div class="source-text">{{Source}}</div>
                </div>
                {{/Source}}
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        .card-question {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .card-answer {
            font-size: 16px;
            color: #333;
        }
        .card-source {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
        .source-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .source-text {
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        '''
    )
    
    return model

def create_mcq_model() -> Any:
    """
    Create an Anki note model for multiple choice questions.
    
    Returns:
        Any: Anki note model
    """
    import genanki
    
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'AI Note System - MCQ',
        fields=[
            {'name': 'Question'},
            {'name': 'Options'},
            {'name': 'Answer'},
            {'name': 'Source'},
        ],
        templates=[
            {
                'name': 'MCQ Card',
                'qfmt': '''
                <div class="card-question">{{Question}}</div>
                <div class="card-options">{{Options}}</div>
                ''',
                'afmt': '''
                <div class="card-question">{{Question}}</div>
                <div class="card-options">{{Options}}</div>
                <hr>
                <div class="card-answer">Correct answer: <span class="correct-answer">{{Answer}}</span></div>
                {{#Source}}
                <div class="card-source">
                    <hr>
                    <div class="source-label">Source:</div>
                    <div class="source-text">{{Source}}</div>
                </div>
                {{/Source}}
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        .card-question {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .card-options {
            margin-bottom: 15px;
        }
        .option {
            margin-bottom: 8px;
            padding: 5px;
            border-radius: 4px;
        }
        .card-answer {
            font-size: 16px;
            color: #333;
            margin-bottom: 10px;
        }
        .correct-answer {
            font-weight: bold;
            color: #27ae60;
        }
        .card-source {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
        .source-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .source-text {
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        '''
    )
    
    return model

def create_fill_blank_model() -> Any:
    """
    Create an Anki note model for fill-in-the-blank questions.
    
    Returns:
        Any: Anki note model
    """
    import genanki
    
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'AI Note System - Fill in the Blank',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'Source'},
        ],
        templates=[
            {
                'name': 'Fill in the Blank Card',
                'qfmt': '''
                <div class="card-question">{{Question}}</div>
                ''',
                'afmt': '''
                <div class="card-question">{{Question}}</div>
                <hr>
                <div class="card-answer">Answer: <span class="blank-answer">{{Answer}}</span></div>
                {{#Source}}
                <div class="card-source">
                    <hr>
                    <div class="source-label">Source:</div>
                    <div class="source-text">{{Source}}</div>
                </div>
                {{/Source}}
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        .card-question {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .card-answer {
            font-size: 16px;
            color: #333;
            margin-bottom: 10px;
        }
        .blank-answer {
            font-weight: bold;
            color: #3498db;
        }
        .card-source {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
        .source-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .source-text {
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        '''
    )
    
    return model

def create_metadata_note(content: Dict[str, Any], model: Any) -> Any:
    """
    Create an Anki note for metadata.
    
    Args:
        content (Dict[str, Any]): The content to export
        model (Any): Anki note model
        
    Returns:
        Any: Anki note
    """
    import genanki
    
    # Extract content fields
    title = content.get("title", "Untitled")
    source_type = content.get("source_type", "text")
    timestamp = content.get("timestamp", datetime.now().isoformat())
    tags = content.get("tags", [])
    
    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp)
        formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        formatted_timestamp = timestamp
    
    # Format tags
    tags_html = ""
    if tags:
        tags_html = "".join([f'<span class="tag">{tag}</span> ' for tag in tags])
    
    # Create metadata HTML
    metadata_html = f"""
    <div class="metadata-item"><span class="metadata-label">Title:</span> {title}</div>
    <div class="metadata-item"><span class="metadata-label">Source Type:</span> {source_type}</div>
    <div class="metadata-item"><span class="metadata-label">Created:</span> {formatted_timestamp}</div>
    <div class="metadata-item"><span class="metadata-label">Tags:</span> {tags_html}</div>
    """
    
    # Add summary if available
    if "summary" in content:
        metadata_html += f"""
        <div class="metadata-item"><span class="metadata-label">Summary:</span></div>
        <div>{content["summary"]}</div>
        """
    
    # Create note
    note = genanki.Note(
        model=model,
        fields=[title, metadata_html]
    )
    
    return note

def create_basic_note(question: str, answer: str, model: Any, source: Optional[str] = None) -> Any:
    """
    Create an Anki note for a basic question and answer.
    
    Args:
        question (str): The question
        answer (str): The answer
        model (Any): Anki note model
        source (str, optional): Source text
        
    Returns:
        Any: Anki note
    """
    import genanki
    
    # Truncate source if it's too long
    if source and len(source) > 1000:
        source = source[:997] + "..."
    
    # Create note
    note = genanki.Note(
        model=model,
        fields=[question, answer, source or ""]
    )
    
    return note

def create_mcq_note(question: str, options: List[str], answer: str, model: Any, source: Optional[str] = None) -> Any:
    """
    Create an Anki note for a multiple choice question.
    
    Args:
        question (str): The question
        options (List[str]): The options
        answer (str): The correct answer
        model (Any): Anki note model
        source (str, optional): Source text
        
    Returns:
        Any: Anki note
    """
    import genanki
    
    # Format options as HTML
    options_html = "<ol>\n"
    for option in options:
        options_html += f"<li class='option'>{option}</li>\n"
    options_html += "</ol>"
    
    # Truncate source if it's too long
    if source and len(source) > 1000:
        source = source[:997] + "..."
    
    # Create note
    note = genanki.Note(
        model=model,
        fields=[question, options_html, answer, source or ""]
    )
    
    return note

def create_fill_blank_note(question: str, answer: str, model: Any, source: Optional[str] = None) -> Any:
    """
    Create an Anki note for a fill-in-the-blank question.
    
    Args:
        question (str): The question with blanks
        answer (str): The answer
        model (Any): Anki note model
        source (str, optional): Source text
        
    Returns:
        Any: Anki note
    """
    import genanki
    
    # Highlight blanks in the question
    highlighted_question = question.replace("_____", "<span style='color: #e74c3c; font-weight: bold;'>_____</span>")
    
    # Truncate source if it's too long
    if source and len(source) > 1000:
        source = source[:997] + "..."
    
    # Create note
    note = genanki.Note(
        model=model,
        fields=[highlighted_question, answer, source or ""]
    )
    
    return note

def create_image_card_model() -> Any:
    """
    Create an Anki note model for cards with images.
    
    Returns:
        Any: Anki note model
    """
    import genanki
    
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'AI Note System - Image Card',
        fields=[
            {'name': 'Question'},
            {'name': 'Image'},
            {'name': 'Answer'},
            {'name': 'Source'},
        ],
        templates=[
            {
                'name': 'Image Card',
                'qfmt': '''
                <div class="card-question">{{Question}}</div>
                <div class="card-image">{{Image}}</div>
                ''',
                'afmt': '''
                <div class="card-question">{{Question}}</div>
                <div class="card-image">{{Image}}</div>
                <hr>
                <div class="card-answer">{{Answer}}</div>
                {{#Source}}
                <div class="card-source">
                    <hr>
                    <div class="source-label">Source:</div>
                    <div class="source-text">{{Source}}</div>
                </div>
                {{/Source}}
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        .card-question {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .card-image {
            margin-bottom: 15px;
            text-align: center;
        }
        .card-image img {
            max-width: 100%;
            max-height: 300px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .card-answer {
            font-size: 16px;
            color: #333;
            margin-bottom: 10px;
        }
        .card-source {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
        .source-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .source-text {
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        '''
    )
    
    return model

def create_cloze_model() -> Any:
    """
    Create an Anki note model for cloze deletion cards.
    
    Returns:
        Any: Anki note model
    """
    import genanki
    
    model_id = random.randrange(1 << 30, 1 << 31)
    
    model = genanki.Model(
        model_id,
        'AI Note System - Cloze',
        fields=[
            {'name': 'Text'},
            {'name': 'Extra'},
            {'name': 'Source'},
        ],
        templates=[
            {
                'name': 'Cloze Card',
                'qfmt': '''
                <div class="card-text">{{cloze:Text}}</div>
                ''',
                'afmt': '''
                <div class="card-text">{{cloze:Text}}</div>
                {{#Extra}}
                <hr>
                <div class="card-extra">{{Extra}}</div>
                {{/Extra}}
                {{#Source}}
                <div class="card-source">
                    <hr>
                    <div class="source-label">Source:</div>
                    <div class="source-text">{{Source}}</div>
                </div>
                {{/Source}}
                ''',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 16px;
            text-align: left;
            color: #333;
            background-color: #f9f9f9;
            padding: 20px;
        }
        .card-text {
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        .cloze {
            font-weight: bold;
            color: #3498db;
        }
        .card-extra {
            font-size: 16px;
            color: #333;
            margin-bottom: 10px;
            font-style: italic;
        }
        .card-source {
            margin-top: 20px;
            font-size: 12px;
            color: #777;
        }
        .source-label {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .source-text {
            white-space: pre-wrap;
            max-height: 200px;
            overflow-y: auto;
        }
        ''',
        model_type=genanki.Model.CLOZE
    )
    
    return model

def create_image_card_note(
    question: str,
    image_path: str,
    answer: str,
    model: Any,
    source: Optional[str] = None,
    package: Optional[Any] = None
) -> Any:
    """
    Create an Anki note for a card with an image.
    
    Args:
        question (str): The question
        image_path (str): Path to the image file
        answer (str): The answer
        model (Any): Anki note model
        source (str, optional): Source text
        package (Any, optional): Anki package to add media to
        
    Returns:
        Any: Anki note
    """
    import genanki
    import os
    
    # Truncate source if it's too long
    if source and len(source) > 1000:
        source = source[:997] + "..."
    
    # Format image as HTML
    image_filename = os.path.basename(image_path)
    image_html = f'<img src="{image_filename}">'
    
    # Add image to package if provided
    if package is not None and os.path.exists(image_path):
        package.media_files.append(image_path)
    
    # Create note
    note = genanki.Note(
        model=model,
        fields=[question, image_html, answer, source or ""]
    )
    
    return note

def create_cloze_note(
    text: str,
    extra: str,
    model: Any,
    source: Optional[str] = None
) -> Any:
    """
    Create an Anki note for a cloze deletion card.
    
    Args:
        text (str): The text with cloze deletions (e.g., "The capital of France is {{c1::Paris}}.")
        extra (str): Extra information to show on the back of the card
        model (Any): Anki note model
        source (str, optional): Source text
        
    Returns:
        Any: Anki note
    """
    import genanki
    
    # Truncate source if it's too long
    if source and len(source) > 1000:
        source = source[:997] + "..."
    
    # Create note
    note = genanki.Note(
        model=model,
        fields=[text, extra, source or ""]
    )
    
    return note