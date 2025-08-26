"""
Markdown export module for AI Note System.
Handles exporting notes to Markdown format.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.export_markdown")

def export_to_markdown(
    content: Dict[str, Any],
    output_path: Optional[str] = None,
    include_metadata: bool = True,
    include_original_text: bool = True,
    template: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export content to Markdown format.
    
    Args:
        content (Dict[str, Any]): The content to export
        output_path (str, optional): Path to save the Markdown file
        include_metadata (bool): Whether to include metadata in the output
        include_original_text (bool): Whether to include the original text
        template (str, optional): Path to a custom Markdown template
        
    Returns:
        Dict[str, Any]: Result of the export operation
    """
    logger.info("Exporting content to Markdown")
    
    try:
        # Generate Markdown content
        markdown = generate_markdown(
            content, 
            include_metadata=include_metadata,
            include_original_text=include_original_text,
            template=template
        )
        
        # Create result dictionary
        result = {
            "success": True,
            "markdown": markdown
        }
        
        # Save to file if output path is provided
        if output_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            result["output_path"] = output_path
            logger.info(f"Markdown saved to {output_path}")
        
        return result
        
    except Exception as e:
        error_msg = f"Error exporting to Markdown: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def generate_markdown(
    content: Dict[str, Any],
    include_metadata: bool = True,
    include_original_text: bool = True,
    template: Optional[str] = None
) -> str:
    """
    Generate Markdown content from the provided data.
    
    Args:
        content (Dict[str, Any]): The content to convert to Markdown
        include_metadata (bool): Whether to include metadata in the output
        include_original_text (bool): Whether to include the original text
        template (str, optional): Path to a custom Markdown template
        
    Returns:
        str: Markdown content
    """
    # Extract content fields
    title = content.get("title", "Untitled")
    text = content.get("text", "")
    summary = content.get("summary", "")
    keypoints = content.get("keypoints", [])
    glossary = content.get("glossary", [])
    questions = content.get("questions", [])
    mcqs = content.get("mcqs", [])
    fill_blanks = content.get("fill_blanks", [])
    tags = content.get("tags", [])
    source_type = content.get("source_type", "text")
    timestamp = content.get("timestamp", datetime.now().isoformat())
    
    # Use custom template if provided
    if template and os.path.exists(template):
        return apply_template(template, content)
    
    # Generate Markdown content
    markdown_lines = []
    
    # Add title
    markdown_lines.append(f"# {title}")
    markdown_lines.append("")
    
    # Add metadata if requested
    if include_metadata:
        markdown_lines.append("## Metadata")
        markdown_lines.append("")
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_timestamp = timestamp
        
        markdown_lines.append(f"- **Created**: {formatted_timestamp}")
        markdown_lines.append(f"- **Source Type**: {source_type}")
        
        # Add tags if available
        if tags:
            tag_str = ", ".join([f"`{tag}`" for tag in tags])
            markdown_lines.append(f"- **Tags**: {tag_str}")
        
        markdown_lines.append("")
    
    # Add summary if available
    if summary:
        markdown_lines.append("## Summary")
        markdown_lines.append("")
        markdown_lines.append(summary)
        markdown_lines.append("")
    
    # Add key points if available
    if keypoints:
        markdown_lines.append("## Key Points")
        markdown_lines.append("")
        
        for point in keypoints:
            if isinstance(point, dict) and "content" in point:
                point_text = point["content"]
            else:
                point_text = str(point)
            
            markdown_lines.append(f"- {point_text}")
        
        markdown_lines.append("")
    
    # Add glossary if available
    if glossary:
        markdown_lines.append("## Glossary")
        markdown_lines.append("")
        
        for term in glossary:
            if isinstance(term, dict):
                term_name = term.get("term", "")
                definition = term.get("definition", "")
                
                markdown_lines.append(f"**{term_name}**: {definition}")
                markdown_lines.append("")
            else:
                # If it's not a dict, we can't extract term and definition
                continue
    
    # Add questions if available
    if questions:
        markdown_lines.append("## Questions")
        markdown_lines.append("")
        
        for i, question in enumerate(questions, 1):
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
                
                markdown_lines.append(f"### Question {i}")
                markdown_lines.append("")
                markdown_lines.append(q_text)
                markdown_lines.append("")
                markdown_lines.append("<details>")
                markdown_lines.append("<summary>Answer</summary>")
                markdown_lines.append("")
                markdown_lines.append(answer)
                markdown_lines.append("")
                markdown_lines.append("</details>")
                markdown_lines.append("")
            else:
                # If it's not a dict, we can't extract question and answer
                continue
    
    # Add MCQs if available
    if mcqs:
        markdown_lines.append("## Multiple Choice Questions")
        markdown_lines.append("")
        
        for i, mcq in enumerate(mcqs, 1):
            if isinstance(mcq, dict):
                q_text = mcq.get("question", "")
                options = mcq.get("options", [])
                answer = mcq.get("answer", "")
                
                markdown_lines.append(f"### MCQ {i}")
                markdown_lines.append("")
                markdown_lines.append(q_text)
                markdown_lines.append("")
                
                # Add options
                for j, option in enumerate(options):
                    markdown_lines.append(f"{j+1}. {option}")
                
                markdown_lines.append("")
                markdown_lines.append("<details>")
                markdown_lines.append("<summary>Answer</summary>")
                markdown_lines.append("")
                markdown_lines.append(f"**{answer}**")
                markdown_lines.append("")
                markdown_lines.append("</details>")
                markdown_lines.append("")
            else:
                # If it's not a dict, we can't extract question and answer
                continue
    
    # Add fill-in-the-blanks if available
    if fill_blanks:
        markdown_lines.append("## Fill in the Blanks")
        markdown_lines.append("")
        
        for i, blank in enumerate(fill_blanks, 1):
            if isinstance(blank, dict):
                q_text = blank.get("text", "")
                answer = blank.get("answer", "")
                
                markdown_lines.append(f"### Fill-in-the-Blank {i}")
                markdown_lines.append("")
                markdown_lines.append(q_text)
                markdown_lines.append("")
                markdown_lines.append("<details>")
                markdown_lines.append("<summary>Answer</summary>")
                markdown_lines.append("")
                markdown_lines.append(f"**{answer}**")
                markdown_lines.append("")
                markdown_lines.append("</details>")
                markdown_lines.append("")
            else:
                # If it's not a dict, we can't extract question and answer
                continue
    
    # Add original text if requested
    if include_original_text and text:
        markdown_lines.append("## Original Text")
        markdown_lines.append("")
        markdown_lines.append(text)
        markdown_lines.append("")
    
    return "\n".join(markdown_lines)

def apply_template(template_path: str, content: Dict[str, Any]) -> str:
    """
    Apply a custom Markdown template.
    
    Args:
        template_path (str): Path to the template file
        content (Dict[str, Any]): The content to insert into the template
        
    Returns:
        str: Markdown content with template applied
    """
    try:
        # Read template file
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Extract content fields
        title = content.get("title", "Untitled")
        text = content.get("text", "")
        summary = content.get("summary", "")
        timestamp = content.get("timestamp", datetime.now().isoformat())
        source_type = content.get("source_type", "text")
        tags = content.get("tags", [])
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            formatted_timestamp = timestamp
        
        # Format tags
        tags_str = ", ".join([f"`{tag}`" for tag in tags])
        
        # Format key points
        keypoints = content.get("keypoints", [])
        keypoints_str = ""
        for point in keypoints:
            if isinstance(point, dict) and "content" in point:
                point_text = point["content"]
            else:
                point_text = str(point)
            
            keypoints_str += f"- {point_text}\n"
        
        # Format glossary
        glossary = content.get("glossary", [])
        glossary_str = ""
        for term in glossary:
            if isinstance(term, dict):
                term_name = term.get("term", "")
                definition = term.get("definition", "")
                
                glossary_str += f"**{term_name}**: {definition}\n\n"
        
        # Format questions
        questions = content.get("questions", [])
        questions_str = ""
        for i, question in enumerate(questions, 1):
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
                
                questions_str += f"### Question {i}\n\n"
                questions_str += f"{q_text}\n\n"
                questions_str += "<details>\n"
                questions_str += "<summary>Answer</summary>\n\n"
                questions_str += f"{answer}\n\n"
                questions_str += "</details>\n\n"
        
        # Replace placeholders in template
        result = template
        result = result.replace("{{title}}", title)
        result = result.replace("{{timestamp}}", formatted_timestamp)
        result = result.replace("{{source_type}}", source_type)
        result = result.replace("{{tags}}", tags_str)
        result = result.replace("{{summary}}", summary)
        result = result.replace("{{keypoints}}", keypoints_str)
        result = result.replace("{{glossary}}", glossary_str)
        result = result.replace("{{questions}}", questions_str)
        result = result.replace("{{text}}", text)
        
        # Replace any other custom fields
        for key, value in content.items():
            if isinstance(value, str):
                result = result.replace(f"{{{{{key}}}}}", value)
        
        return result
        
    except Exception as e:
        logger.error(f"Error applying template: {str(e)}")
        # Fall back to standard format
        return generate_markdown(content)

def create_markdown_template(output_path: str) -> Dict[str, Any]:
    """
    Create a sample Markdown template file.
    
    Args:
        output_path (str): Path to save the template file
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    template = """# {{title}}

## Metadata

- **Created**: {{timestamp}}
- **Source Type**: {{source_type}}
- **Tags**: {{tags}}

## Summary

{{summary}}

## Key Points

{{keypoints}}

## Glossary

{{glossary}}

## Questions

{{questions}}

## Original Text

{{text}}
"""
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write template to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        logger.info(f"Markdown template saved to {output_path}")
        return {"success": True, "output_path": output_path}
        
    except Exception as e:
        error_msg = f"Error creating Markdown template: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}