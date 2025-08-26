"""
Podcast & Audiobook Processing module for AI Note System.
Handles ingesting podcasts and audiobooks by transcribing, summarizing, and generating flashcards and structured notes.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from datetime import datetime

# Import speech input module for transcription
from .speech_input import transcribe_audio

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.process_audio")

def process_audio_content(
    input_path: str,
    content_type: str = "podcast",
    output_dir: Optional[str] = None,
    transcribe_only: bool = False,
    summarize: bool = True,
    generate_notes: bool = True,
    generate_flashcards: bool = False,
    export_format: Optional[str] = None,
    export_path: Optional[str] = None,
    model: str = "gpt-4",
    language: str = "en"
) -> Dict[str, Any]:
    """
    Process audio content (podcast or audiobook) by transcribing, summarizing, and generating structured notes.
    
    Args:
        input_path (str): Path to the audio file
        content_type (str): Type of content ("podcast" or "audiobook")
        output_dir (str, optional): Directory to save output files
        transcribe_only (bool): Whether to only transcribe without further processing
        summarize (bool): Whether to generate a summary
        generate_notes (bool): Whether to generate structured notes
        generate_flashcards (bool): Whether to generate flashcards
        export_format (str, optional): Format to export results (markdown, json)
        export_path (str, optional): Path to save exported results
        model (str): LLM model to use for processing
        language (str): Language of the audio content
        
    Returns:
        Dict[str, Any]: Processing results
    """
    logger.info(f"Processing {content_type}: {input_path}")
    
    # Create output directory if not provided
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(tempfile.gettempdir(), f"audio_processing_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Transcribe audio
    logger.info("Transcribing audio...")
    transcription_result = transcribe_audio(
        audio_path=input_path,
        engine="whisper",  # Use Whisper for better quality
        language=language,
        model_size="medium"  # Use medium model for balance of speed and accuracy
    )
    
    if "error" in transcription_result:
        logger.error(f"Error transcribing audio: {transcription_result['error']}")
        return {
            "status": "error",
            "message": f"Error transcribing audio: {transcription_result['error']}",
            "input_path": input_path
        }
    
    # Extract transcription text
    transcription_text = transcription_result.get("text", "")
    
    if not transcription_text:
        logger.error("No transcription text generated")
        return {
            "status": "error",
            "message": "No transcription text generated",
            "input_path": input_path
        }
    
    # Save transcription to file
    transcription_path = os.path.join(output_dir, "transcription.txt")
    with open(transcription_path, "w", encoding="utf-8") as f:
        f.write(transcription_text)
    
    # If transcribe_only, return early
    if transcribe_only:
        logger.info("Transcription completed (transcribe_only mode)")
        return {
            "status": "success",
            "message": "Audio transcription completed",
            "input_path": input_path,
            "transcription_path": transcription_path,
            "transcription_text": transcription_text
        }
    
    # Step 2: Process transcription based on content type
    if content_type == "podcast":
        processing_result = process_podcast_transcription(
            transcription_text=transcription_text,
            output_dir=output_dir,
            summarize=summarize,
            generate_notes=generate_notes,
            generate_flashcards=generate_flashcards,
            model=model
        )
    else:  # audiobook
        processing_result = process_audiobook_transcription(
            transcription_text=transcription_text,
            output_dir=output_dir,
            summarize=summarize,
            generate_notes=generate_notes,
            generate_flashcards=generate_flashcards,
            model=model
        )
    
    # Add transcription info to result
    processing_result["input_path"] = input_path
    processing_result["transcription_path"] = transcription_path
    
    # Step 3: Export results if requested
    if export_format and export_path:
        export_result = export_processing_results(
            processing_result=processing_result,
            export_format=export_format,
            export_path=export_path
        )
        processing_result["export_result"] = export_result
    
    return processing_result

def process_podcast_transcription(
    transcription_text: str,
    output_dir: str,
    summarize: bool = True,
    generate_notes: bool = True,
    generate_flashcards: bool = False,
    model: str = "gpt-4"
) -> Dict[str, Any]:
    """
    Process podcast transcription to generate summary, notes, and flashcards.
    
    Args:
        transcription_text (str): Transcribed text
        output_dir (str): Directory to save output files
        summarize (bool): Whether to generate a summary
        generate_notes (bool): Whether to generate structured notes
        generate_flashcards (bool): Whether to generate flashcards
        model (str): LLM model to use
        
    Returns:
        Dict[str, Any]: Processing results
    """
    logger.info("Processing podcast transcription")
    
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Initialize result
    result = {
        "status": "success",
        "message": "Podcast processing completed",
        "content_type": "podcast"
    }
    
    # Get LLM interface
    llm = get_llm_interface("openai", model=model)
    
    # Step 1: Extract podcast metadata
    logger.info("Extracting podcast metadata")
    metadata_prompt = f"""
    Extract metadata from the following podcast transcription.
    Identify the podcast title, host(s), guest(s) if any, and main topics discussed.
    
    Transcription:
    {transcription_text[:2000]}...
    
    Format your response as a JSON object with the following fields:
    - title: The podcast title
    - hosts: Array of host names
    - guests: Array of guest names (empty if none)
    - topics: Array of main topics discussed
    - estimated_duration_minutes: Estimated duration in minutes based on the transcription length
    """
    
    metadata_response = llm.generate_text(metadata_prompt)
    
    try:
        metadata = json.loads(metadata_response)
        result["metadata"] = metadata
        
        # Save metadata to file
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        result["metadata_path"] = metadata_path
    except json.JSONDecodeError:
        logger.error(f"Error parsing metadata response: {metadata_response}")
        result["metadata"] = {
            "title": "Unknown Podcast",
            "hosts": [],
            "guests": [],
            "topics": []
        }
    
    # Step 2: Generate summary if requested
    if summarize:
        logger.info("Generating podcast summary")
        summary_prompt = f"""
        Summarize the following podcast transcription.
        Provide a concise summary that captures the main points, key insights, and important discussions.
        
        Transcription:
        {transcription_text}
        
        Your summary should be comprehensive yet concise, highlighting the most valuable information from the podcast.
        """
        
        summary = llm.generate_text(summary_prompt)
        result["summary"] = summary
        
        # Save summary to file
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        
        result["summary_path"] = summary_path
    
    # Step 3: Generate structured notes if requested
    if generate_notes:
        logger.info("Generating structured notes")
        notes_prompt = f"""
        Create structured notes from the following podcast transcription.
        Organize the content into sections with headings, key points, and important quotes.
        
        Transcription:
        {transcription_text}
        
        Format your response as a JSON object with the following structure:
        {{
            "sections": [
                {{
                    "title": "Section title",
                    "key_points": ["Key point 1", "Key point 2", ...],
                    "quotes": ["Quote 1", "Quote 2", ...],
                    "additional_notes": "Any additional information"
                }},
                ...
            ],
            "key_takeaways": ["Takeaway 1", "Takeaway 2", ...],
            "resources_mentioned": ["Resource 1", "Resource 2", ...]
        }}
        """
        
        notes_response = llm.generate_text(notes_prompt)
        
        try:
            structured_notes = json.loads(notes_response)
            result["structured_notes"] = structured_notes
            
            # Save structured notes to file
            notes_path = os.path.join(output_dir, "structured_notes.json")
            with open(notes_path, "w", encoding="utf-8") as f:
                json.dump(structured_notes, f, ensure_ascii=False, indent=2)
            
            result["structured_notes_path"] = notes_path
        except json.JSONDecodeError:
            logger.error(f"Error parsing structured notes response: {notes_response}")
            result["structured_notes"] = {"error": "Failed to parse structured notes"}
    
    # Step 4: Generate flashcards if requested
    if generate_flashcards:
        logger.info("Generating flashcards")
        flashcards_prompt = f"""
        Create educational flashcards from the following podcast transcription.
        Generate question-answer pairs that test understanding of the key concepts discussed.
        
        Transcription:
        {transcription_text}
        
        Format your response as a JSON array of objects with "question" and "answer" fields.
        Create at least 10 flashcards that cover the most important concepts from the podcast.
        """
        
        flashcards_response = llm.generate_text(flashcards_prompt)
        
        try:
            flashcards = json.loads(flashcards_response)
            result["flashcards"] = flashcards
            
            # Save flashcards to file
            flashcards_path = os.path.join(output_dir, "flashcards.json")
            with open(flashcards_path, "w", encoding="utf-8") as f:
                json.dump(flashcards, f, ensure_ascii=False, indent=2)
            
            result["flashcards_path"] = flashcards_path
        except json.JSONDecodeError:
            logger.error(f"Error parsing flashcards response: {flashcards_response}")
            result["flashcards"] = {"error": "Failed to parse flashcards"}
    
    return result

def process_audiobook_transcription(
    transcription_text: str,
    output_dir: str,
    summarize: bool = True,
    generate_notes: bool = True,
    generate_flashcards: bool = False,
    model: str = "gpt-4"
) -> Dict[str, Any]:
    """
    Process audiobook transcription to generate summary, notes, and flashcards.
    
    Args:
        transcription_text (str): Transcribed text
        output_dir (str): Directory to save output files
        summarize (bool): Whether to generate a summary
        generate_notes (bool): Whether to generate structured notes
        generate_flashcards (bool): Whether to generate flashcards
        model (str): LLM model to use
        
    Returns:
        Dict[str, Any]: Processing results
    """
    logger.info("Processing audiobook transcription")
    
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Initialize result
    result = {
        "status": "success",
        "message": "Audiobook processing completed",
        "content_type": "audiobook"
    }
    
    # Get LLM interface
    llm = get_llm_interface("openai", model=model)
    
    # Step 1: Extract audiobook metadata
    logger.info("Extracting audiobook metadata")
    metadata_prompt = f"""
    Extract metadata from the following audiobook transcription.
    Identify the book title, author, narrator, genre, and main themes.
    
    Transcription (beginning):
    {transcription_text[:2000]}...
    
    Format your response as a JSON object with the following fields:
    - title: The book title
    - author: The book author
    - narrator: The audiobook narrator (if identifiable)
    - genre: The book genre
    - themes: Array of main themes
    - estimated_duration_minutes: Estimated duration in minutes based on the transcription length
    """
    
    metadata_response = llm.generate_text(metadata_prompt)
    
    try:
        metadata = json.loads(metadata_response)
        result["metadata"] = metadata
        
        # Save metadata to file
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        result["metadata_path"] = metadata_path
    except json.JSONDecodeError:
        logger.error(f"Error parsing metadata response: {metadata_response}")
        result["metadata"] = {
            "title": "Unknown Audiobook",
            "author": "Unknown Author",
            "narrator": "Unknown Narrator",
            "genre": "Unknown",
            "themes": []
        }
    
    # Step 2: Generate chapter segmentation
    logger.info("Generating chapter segmentation")
    segmentation_prompt = f"""
    Analyze the following audiobook transcription and identify chapter breaks or major sections.
    
    Transcription (sample):
    {transcription_text[:5000]}...
    
    Format your response as a JSON array of objects with "title" and "indicators" fields.
    The "indicators" field should contain phrases or patterns that indicate the start of this chapter or section.
    """
    
    segmentation_response = llm.generate_text(segmentation_prompt)
    
    try:
        chapters = json.loads(segmentation_response)
        result["chapters"] = chapters
        
        # Save chapters to file
        chapters_path = os.path.join(output_dir, "chapters.json")
        with open(chapters_path, "w", encoding="utf-8") as f:
            json.dump(chapters, f, ensure_ascii=False, indent=2)
        
        result["chapters_path"] = chapters_path
    except json.JSONDecodeError:
        logger.error(f"Error parsing chapter segmentation response: {segmentation_response}")
        result["chapters"] = [{"title": "Full Audiobook", "indicators": []}]
    
    # Step 3: Generate summary if requested
    if summarize:
        logger.info("Generating audiobook summary")
        summary_prompt = f"""
        Summarize the following audiobook transcription.
        Provide a concise summary that captures the main plot, key characters, and important themes.
        
        Transcription:
        {transcription_text}
        
        Your summary should be comprehensive yet concise, highlighting the most important elements of the audiobook.
        """
        
        summary = llm.generate_text(summary_prompt)
        result["summary"] = summary
        
        # Save summary to file
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)
        
        result["summary_path"] = summary_path
    
    # Step 4: Generate structured notes if requested
    if generate_notes:
        logger.info("Generating structured notes")
        notes_prompt = f"""
        Create structured notes from the following audiobook transcription.
        Organize the content into sections with chapter summaries, character descriptions, key themes, and important quotes.
        
        Transcription:
        {transcription_text}
        
        Format your response as a JSON object with the following structure:
        {{
            "chapter_summaries": [
                {{
                    "title": "Chapter title",
                    "summary": "Chapter summary",
                    "key_events": ["Event 1", "Event 2", ...],
                    "quotes": ["Quote 1", "Quote 2", ...]
                }},
                ...
            ],
            "characters": [
                {{
                    "name": "Character name",
                    "description": "Character description",
                    "role": "Character role"
                }},
                ...
            ],
            "themes": [
                {{
                    "theme": "Theme name",
                    "description": "Theme description",
                    "examples": ["Example 1", "Example 2", ...]
                }},
                ...
            ],
            "key_takeaways": ["Takeaway 1", "Takeaway 2", ...]
        }}
        """
        
        notes_response = llm.generate_text(notes_prompt)
        
        try:
            structured_notes = json.loads(notes_response)
            result["structured_notes"] = structured_notes
            
            # Save structured notes to file
            notes_path = os.path.join(output_dir, "structured_notes.json")
            with open(notes_path, "w", encoding="utf-8") as f:
                json.dump(structured_notes, f, ensure_ascii=False, indent=2)
            
            result["structured_notes_path"] = notes_path
        except json.JSONDecodeError:
            logger.error(f"Error parsing structured notes response: {notes_response}")
            result["structured_notes"] = {"error": "Failed to parse structured notes"}
    
    # Step 5: Generate flashcards if requested
    if generate_flashcards:
        logger.info("Generating flashcards")
        flashcards_prompt = f"""
        Create educational flashcards from the following audiobook transcription.
        Generate question-answer pairs that test understanding of the key concepts, characters, plot points, and themes.
        
        Transcription:
        {transcription_text}
        
        Format your response as a JSON array of objects with "question" and "answer" fields.
        Create at least 15 flashcards that cover the most important elements of the audiobook.
        """
        
        flashcards_response = llm.generate_text(flashcards_prompt)
        
        try:
            flashcards = json.loads(flashcards_response)
            result["flashcards"] = flashcards
            
            # Save flashcards to file
            flashcards_path = os.path.join(output_dir, "flashcards.json")
            with open(flashcards_path, "w", encoding="utf-8") as f:
                json.dump(flashcards, f, ensure_ascii=False, indent=2)
            
            result["flashcards_path"] = flashcards_path
        except json.JSONDecodeError:
            logger.error(f"Error parsing flashcards response: {flashcards_response}")
            result["flashcards"] = {"error": "Failed to parse flashcards"}
    
    return result

def export_processing_results(
    processing_result: Dict[str, Any],
    export_format: str,
    export_path: str
) -> Dict[str, Any]:
    """
    Export processing results to the specified format.
    
    Args:
        processing_result (Dict[str, Any]): Processing results
        export_format (str): Format to export (markdown, json)
        export_path (str): Path to save exported results
        
    Returns:
        Dict[str, Any]: Export result
    """
    logger.info(f"Exporting processing results to {export_format}: {export_path}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
        
        if export_format.lower() == "json":
            # Export as JSON
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(processing_result, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": f"Results exported to JSON: {export_path}",
                "export_path": export_path
            }
        
        elif export_format.lower() == "markdown":
            # Export as Markdown
            content_type = processing_result.get("content_type", "audio")
            metadata = processing_result.get("metadata", {})
            summary = processing_result.get("summary", "")
            
            # Create Markdown content
            md_content = []
            
            # Add title and metadata
            if content_type == "podcast":
                title = metadata.get("title", "Podcast Transcription")
                md_content.append(f"# {title}")
                md_content.append("")
                
                # Add metadata
                md_content.append("## Metadata")
                md_content.append("")
                md_content.append(f"- **Hosts:** {', '.join(metadata.get('hosts', []))}")
                
                if metadata.get("guests"):
                    md_content.append(f"- **Guests:** {', '.join(metadata.get('guests', []))}")
                
                md_content.append(f"- **Topics:** {', '.join(metadata.get('topics', []))}")
                md_content.append(f"- **Duration:** {metadata.get('estimated_duration_minutes', 'Unknown')} minutes")
                md_content.append("")
            
            else:  # audiobook
                title = metadata.get("title", "Audiobook Transcription")
                md_content.append(f"# {title}")
                md_content.append("")
                
                # Add metadata
                md_content.append("## Metadata")
                md_content.append("")
                md_content.append(f"- **Author:** {metadata.get('author', 'Unknown')}")
                md_content.append(f"- **Narrator:** {metadata.get('narrator', 'Unknown')}")
                md_content.append(f"- **Genre:** {metadata.get('genre', 'Unknown')}")
                md_content.append(f"- **Themes:** {', '.join(metadata.get('themes', []))}")
                md_content.append(f"- **Duration:** {metadata.get('estimated_duration_minutes', 'Unknown')} minutes")
                md_content.append("")
            
            # Add summary
            if summary:
                md_content.append("## Summary")
                md_content.append("")
                md_content.append(summary)
                md_content.append("")
            
            # Add structured notes
            structured_notes = processing_result.get("structured_notes", {})
            if structured_notes and not isinstance(structured_notes, str) and "error" not in structured_notes:
                if content_type == "podcast":
                    # Add sections
                    sections = structured_notes.get("sections", [])
                    if sections:
                        md_content.append("## Notes")
                        md_content.append("")
                        
                        for section in sections:
                            md_content.append(f"### {section.get('title', 'Section')}")
                            md_content.append("")
                            
                            # Add key points
                            key_points = section.get("key_points", [])
                            if key_points:
                                md_content.append("#### Key Points")
                                md_content.append("")
                                for point in key_points:
                                    md_content.append(f"- {point}")
                                md_content.append("")
                            
                            # Add quotes
                            quotes = section.get("quotes", [])
                            if quotes:
                                md_content.append("#### Quotes")
                                md_content.append("")
                                for quote in quotes:
                                    md_content.append(f"> {quote}")
                                    md_content.append("")
                            
                            # Add additional notes
                            additional_notes = section.get("additional_notes")
                            if additional_notes:
                                md_content.append("#### Additional Notes")
                                md_content.append("")
                                md_content.append(additional_notes)
                                md_content.append("")
                    
                    # Add key takeaways
                    key_takeaways = structured_notes.get("key_takeaways", [])
                    if key_takeaways:
                        md_content.append("## Key Takeaways")
                        md_content.append("")
                        for takeaway in key_takeaways:
                            md_content.append(f"- {takeaway}")
                        md_content.append("")
                    
                    # Add resources mentioned
                    resources = structured_notes.get("resources_mentioned", [])
                    if resources:
                        md_content.append("## Resources Mentioned")
                        md_content.append("")
                        for resource in resources:
                            md_content.append(f"- {resource}")
                        md_content.append("")
                
                else:  # audiobook
                    # Add chapter summaries
                    chapter_summaries = structured_notes.get("chapter_summaries", [])
                    if chapter_summaries:
                        md_content.append("## Chapter Summaries")
                        md_content.append("")
                        
                        for chapter in chapter_summaries:
                            md_content.append(f"### {chapter.get('title', 'Chapter')}")
                            md_content.append("")
                            md_content.append(chapter.get("summary", ""))
                            md_content.append("")
                            
                            # Add key events
                            key_events = chapter.get("key_events", [])
                            if key_events:
                                md_content.append("#### Key Events")
                                md_content.append("")
                                for event in key_events:
                                    md_content.append(f"- {event}")
                                md_content.append("")
                            
                            # Add quotes
                            quotes = chapter.get("quotes", [])
                            if quotes:
                                md_content.append("#### Quotes")
                                md_content.append("")
                                for quote in quotes:
                                    md_content.append(f"> {quote}")
                                    md_content.append("")
                    
                    # Add characters
                    characters = structured_notes.get("characters", [])
                    if characters:
                        md_content.append("## Characters")
                        md_content.append("")
                        
                        for character in characters:
                            md_content.append(f"### {character.get('name', 'Character')}")
                            md_content.append("")
                            md_content.append(f"**Role:** {character.get('role', 'Unknown')}")
                            md_content.append("")
                            md_content.append(character.get("description", ""))
                            md_content.append("")
                    
                    # Add themes
                    themes = structured_notes.get("themes", [])
                    if themes:
                        md_content.append("## Themes")
                        md_content.append("")
                        
                        for theme in themes:
                            md_content.append(f"### {theme.get('theme', 'Theme')}")
                            md_content.append("")
                            md_content.append(theme.get("description", ""))
                            md_content.append("")
                            
                            # Add examples
                            examples = theme.get("examples", [])
                            if examples:
                                md_content.append("#### Examples")
                                md_content.append("")
                                for example in examples:
                                    md_content.append(f"- {example}")
                                md_content.append("")
                    
                    # Add key takeaways
                    key_takeaways = structured_notes.get("key_takeaways", [])
                    if key_takeaways:
                        md_content.append("## Key Takeaways")
                        md_content.append("")
                        for takeaway in key_takeaways:
                            md_content.append(f"- {takeaway}")
                        md_content.append("")
            
            # Add flashcards
            flashcards = processing_result.get("flashcards", [])
            if flashcards and not isinstance(flashcards, dict) and "error" not in flashcards:
                md_content.append("## Flashcards")
                md_content.append("")
                
                for i, card in enumerate(flashcards, 1):
                    md_content.append(f"### Card {i}")
                    md_content.append("")
                    md_content.append(f"**Q:** {card.get('question', '')}")
                    md_content.append("")
                    md_content.append(f"**A:** {card.get('answer', '')}")
                    md_content.append("")
            
            # Add transcription info
            md_content.append("## Transcription")
            md_content.append("")
            md_content.append(f"Full transcription saved to: {processing_result.get('transcription_path', 'Unknown')}")
            md_content.append("")
            
            # Write Markdown content to file
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_content))
            
            return {
                "status": "success",
                "message": f"Results exported to Markdown: {export_path}",
                "export_path": export_path
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unsupported export format: {export_format}",
                "export_path": None
            }
    
    except Exception as e:
        logger.error(f"Error exporting processing results: {e}")
        return {
            "status": "error",
            "message": f"Error exporting processing results: {e}",
            "export_path": None
        }