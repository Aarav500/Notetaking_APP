"""
Timeline generator module for AI Note System.
Generates timelines from text using Mermaid.
"""

import os
import logging
import subprocess
import tempfile
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.timeline_gen")

def generate_timeline(
    text: str,
    output_format: str = "png",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    theme: str = "default",
    include_code: bool = True
) -> Dict[str, Any]:
    """
    Generate a timeline from text.
    
    Args:
        text (str): The text to generate a timeline from
        output_format (str): The output format (png, svg, pdf)
        output_path (str, optional): Path to save the output file
        title (str, optional): Title for the timeline
        theme (str): Theme for the timeline
        include_code (bool): Whether to include the generated code in the result
        
    Returns:
        Dict[str, Any]: Dictionary containing the timeline information
    """
    logger.info("Generating timeline")
    
    # Generate Mermaid code from text
    mermaid_code = extract_timeline_from_text(text, title)
    
    # Create result dictionary
    result = {
        "title": title or "Timeline",
        "format": output_format
    }
    
    if include_code:
        result["code"] = mermaid_code
    
    # If output path is provided, render the timeline
    if output_path:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save Mermaid code to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", delete=False) as f:
                f.write(mermaid_code)
                temp_file = f.name
            
            # Use mmdc (Mermaid CLI) to render the timeline
            # Note: This requires mmdc to be installed
            cmd = [
                "mmdc",
                "-i", temp_file,
                "-o", output_path,
                "-t", theme,
                "-b", "transparent"
            ]
            
            if output_format:
                cmd.extend(["-f", output_format])
            
            subprocess.run(cmd, check=True)
            
            # Clean up temporary file
            os.unlink(temp_file)
            
            result["output_path"] = output_path
            logger.debug(f"Timeline saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error rendering timeline: {e}")
            result["error"] = f"Error rendering timeline: {e}"
    
    return result

def extract_timeline_from_text(
    text: str,
    title: Optional[str] = None
) -> str:
    """
    Extract a timeline from text.
    
    Args:
        text (str): The text to extract a timeline from
        title (str, optional): Title for the timeline
        
    Returns:
        str: Mermaid timeline code
    """
    # Extract events with dates from text
    events = extract_events_with_dates(text)
    
    # Generate Mermaid code
    mermaid_code = ["timeline"]
    
    if title:
        mermaid_code.append(f"    title {title}")
    
    # Sort events by date
    events.sort(key=lambda x: x["date"] if x["date"] else "")
    
    # Group events by section (year or period)
    sections = {}
    for event in events:
        date_str = event["date"]
        if date_str:
            # Try to extract year
            year_match = re.search(r'\b(1\d{3}|20\d{2})\b', date_str)
            if year_match:
                section = year_match.group(1)
            else:
                # Use the first part of the date string as section
                section = date_str.split()[0]
        else:
            section = "Unknown Date"
        
        if section not in sections:
            sections[section] = []
        
        sections[section].append(event)
    
    # Add sections and events to timeline
    for section, section_events in sections.items():
        mermaid_code.append(f"    section {section}")
        
        for event in section_events:
            description = event["description"]
            date_detail = event["date"] if section != event["date"] else ""
            
            if date_detail:
                mermaid_code.append(f"        {description} : {date_detail}")
            else:
                mermaid_code.append(f"        {description} :")
    
    return "\n".join(mermaid_code)

def extract_events_with_dates(text: str) -> List[Dict[str, str]]:
    """
    Extract events with dates from text.
    
    Args:
        text (str): The text to extract events from
        
    Returns:
        List[Dict[str, str]]: List of events with dates
    """
    # This is a simplified implementation that looks for date patterns in the text
    # In a real implementation, this would use an LLM to extract events more intelligently
    
    events = []
    
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Date patterns to look for
    date_patterns = [
        # Year only: 1995, 2020
        r'\b(1\d{3}|20\d{2})\b',
        
        # Month and year: January 1995, Jan 2020
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(1\d{3}|20\d{2})\b',
        
        # Full date: January 15, 1995, 15 Jan 2020
        r'\b(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})(st|nd|rd|th)?,\s+(1\d{3}|20\d{2})\b',
        r'\b(\d{1,2})(st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(1\d{3}|20\d{2})\b',
        
        # Decades and centuries: 1990s, 19th century
        r'\b(1\d{3}|20\d{2})s\b',
        r'\b(1\d|20)(st|nd|rd|th)\s+century\b',
        
        # Time periods: Early 1990s, Late 19th century
        r'\b(Early|Mid|Late)\s+(1\d{3}|20\d{2})s\b',
        r'\b(Early|Mid|Late)\s+(1\d|20)(st|nd|rd|th)\s+century\b',
        
        # BC/AD dates
        r'\b\d+\s+(BC|BCE|AD|CE)\b'
    ]
    
    # Process each sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Look for date patterns
        date_found = False
        for pattern in date_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                date_str = match.group(0)
                
                # Extract the event description (the sentence without the date)
                description = sentence.replace(date_str, "").strip()
                description = re.sub(r'[,.;:]\s*$', '', description)  # Remove trailing punctuation
                
                if description:
                    events.append({
                        "date": date_str,
                        "description": description
                    })
                    date_found = True
                    break
        
        # If no date pattern was found but the sentence contains words that suggest a timeline event
        if not date_found:
            timeline_keywords = ["before", "after", "during", "when", "while", "following", "prior to", "subsequently"]
            for keyword in timeline_keywords:
                if re.search(r'\b' + keyword + r'\b', sentence, re.IGNORECASE):
                    events.append({
                        "date": "",
                        "description": sentence
                    })
                    break
    
    # If no events were found, try to create some based on the text structure
    if not events:
        # Look for numbered lists or bullet points
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line and (line.startswith("- ") or line.startswith("* ") or 
                        (line[0].isdigit() and line[1:3] in [". ", ") "])):
                # Remove leading markers
                description = line[2:] if line.startswith(("- ", "* ")) else line[line.index(" ")+1:]
                events.append({
                    "date": "",
                    "description": description
                })
    
    # If still no events, create some from sentences
    if not events:
        for i, sentence in enumerate(sentences[:10]):
            if len(sentence) > 10:
                events.append({
                    "date": "",
                    "description": sentence
                })
    
    # If we have events without dates, assign some placeholder dates
    if events and all(not event["date"] for event in events):
        # Create a sequence of dates starting from today and going backward
        today = datetime.now()
        for i, event in enumerate(events):
            date = today - timedelta(days=i*365)  # One year intervals
            event["date"] = date.strftime("%Y")
    
    return events

def generate_timeline_from_llm(
    text: str,
    model: str = "gpt-4",
    title: Optional[str] = None
) -> str:
    """
    Generate a timeline from text using an LLM.
    
    Args:
        text (str): The text to generate a timeline from
        model (str): The LLM model to use
        title (str, optional): Title for the timeline
        
    Returns:
        str: Mermaid timeline code
    """
    # This would use an LLM to generate the timeline code
    # For now, we'll use the simpler extraction method
    
    return extract_timeline_from_text(text, title)