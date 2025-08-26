"""
Notion uploader module for AI Note System.
Handles syncing notes with Notion using the Notion API.
"""

import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.notion_uploader")

try:
    from notion_client import Client
    NOTION_AVAILABLE = True
except ImportError:
    logger.warning("notion-client package not installed. Notion integration will not be available.")
    NOTION_AVAILABLE = False

def upload_to_notion(
    content: Dict[str, Any],
    database_id: Optional[str] = None,
    notion_token: Optional[str] = None,
    update_existing: bool = True
) -> Dict[str, Any]:
    """
    Upload content to Notion.
    
    Args:
        content (Dict[str, Any]): The content to upload
        database_id (str, optional): The Notion database ID
        notion_token (str, optional): The Notion API token
        update_existing (bool): Whether to update existing pages with the same title
        
    Returns:
        Dict[str, Any]: Result of the upload operation
    """
    logger.info("Uploading content to Notion")
    
    if not NOTION_AVAILABLE:
        error_msg = "notion-client package not installed. Cannot upload to Notion."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Get Notion token from environment or config
    if not notion_token:
        notion_token = os.environ.get("NOTION_TOKEN")
    
    if not notion_token:
        error_msg = "Notion token not provided and not found in environment variables."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Get database ID from environment or config
    if not database_id:
        database_id = os.environ.get("NOTION_DATABASE_ID")
    
    if not database_id:
        error_msg = "Notion database ID not provided and not found in environment variables."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    
    try:
        # Initialize Notion client
        notion = Client(auth=notion_token)
        
        # Check if we need to update an existing page
        page_id = None
        if update_existing and "title" in content:
            page_id = find_page_by_title(notion, database_id, content["title"])
        
        if page_id:
            # Update existing page
            result = update_notion_page(notion, page_id, content)
            logger.info(f"Updated existing Notion page: {content.get('title', 'Untitled')}")
            return {"success": True, "page_id": page_id, "updated": True}
        else:
            # Create new page
            page = create_notion_page(notion, database_id, content)
            page_id = page["id"]
            logger.info(f"Created new Notion page: {content.get('title', 'Untitled')}")
            return {"success": True, "page_id": page_id, "updated": False}
            
    except Exception as e:
        error_msg = f"Error uploading to Notion: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def find_page_by_title(
    notion: Any,
    database_id: str,
    title: str
) -> Optional[str]:
    """
    Find a Notion page by title.
    
    Args:
        notion: Notion client
        database_id (str): The Notion database ID
        title (str): The title to search for
        
    Returns:
        Optional[str]: Page ID if found, None otherwise
    """
    try:
        # Query the database for pages with the given title
        response = notion.databases.query(
            database_id=database_id,
            filter={
                "property": "title",
                "title": {
                    "equals": title
                }
            }
        )
        
        # Return the ID of the first matching page, if any
        if response["results"]:
            return response["results"][0]["id"]
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding page by title: {str(e)}")
        return None

def create_notion_page(
    notion: Any,
    database_id: str,
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new Notion page.
    
    Args:
        notion: Notion client
        database_id (str): The Notion database ID
        content (Dict[str, Any]): The content to upload
        
    Returns:
        Dict[str, Any]: The created page
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
    
    # Create page properties
    properties = {
        "title": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        },
        "Source Type": {
            "select": {
                "name": source_type
            }
        },
        "Created": {
            "date": {
                "start": datetime.now().isoformat()
            }
        }
    }
    
    # Add tags if provided
    if tags:
        properties["Tags"] = {
            "multi_select": [{"name": tag} for tag in tags]
        }
    
    # Create page content blocks
    children = []
    
    # Add summary if available
    if summary:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": summary}}]
                }
            }
        ])
    
    # Add key points if available
    if keypoints:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Key Points"}}]
                }
            }
        ])
        
        # Add each key point as a bulleted list item
        for point in keypoints:
            if isinstance(point, dict) and "content" in point:
                point_text = point["content"]
            else:
                point_text = str(point)
                
            children.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": point_text}}]
                }
            })
    
    # Add glossary if available
    if glossary:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Glossary"}}]
                }
            }
        ])
        
        # Add each glossary term as a toggle block
        for term in glossary:
            if isinstance(term, dict):
                term_name = term.get("term", "")
                definition = term.get("definition", "")
            else:
                # If it's not a dict, we can't extract term and definition
                continue
                
            children.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": term_name}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": definition}}]
                            }
                        }
                    ]
                }
            })
    
    # Add questions if available
    if questions:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Questions"}}]
                }
            }
        ])
        
        # Add each question as a toggle block
        for question in questions:
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
            else:
                # If it's not a dict, we can't extract question and answer
                continue
                
            children.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": q_text}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": answer}}]
                            }
                        }
                    ]
                }
            })
    
    # Add MCQs if available
    if mcqs:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Multiple Choice Questions"}}]
                }
            }
        ])
        
        # Add each MCQ as a toggle block with options as a bulleted list
        for mcq in mcqs:
            if isinstance(mcq, dict):
                q_text = mcq.get("question", "")
                options = mcq.get("options", [])
                answer = mcq.get("answer", "")
                
                # Create toggle block for the question
                toggle_block = {
                    "object": "block",
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [{"type": "text", "text": {"content": q_text}}],
                        "children": []
                    }
                }
                
                # Add options as bulleted list
                for option in options:
                    toggle_block["toggle"]["children"].append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": option}}]
                        }
                    })
                
                # Add answer
                toggle_block["toggle"]["children"].append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Answer: "}},
                            {"type": "text", "text": {"content": answer}, "annotations": {"bold": True}}
                        ]
                    }
                })
                
                children.append(toggle_block)
    
    # Add fill-in-the-blanks if available
    if fill_blanks:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Fill in the Blanks"}}]
                }
            }
        ])
        
        # Add each fill-in-the-blank as a toggle block
        for blank in fill_blanks:
            if isinstance(blank, dict):
                q_text = blank.get("text", "")
                answer = blank.get("answer", "")
                
                children.append({
                    "object": "block",
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [{"type": "text", "text": {"content": q_text}}],
                        "children": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [
                                        {"type": "text", "text": {"content": "Answer: "}},
                                        {"type": "text", "text": {"content": answer}, "annotations": {"bold": True}}
                                    ]
                                }
                            }
                        ]
                    }
                })
    
    # Add original text if available
    if text:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Original Text"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            }
        ])
    
    # Create the page
    page = notion.pages.create(
        parent={"database_id": database_id},
        properties=properties,
        children=children
    )
    
    return page

def update_notion_page(
    notion: Any,
    page_id: str,
    content: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update an existing Notion page.
    
    Args:
        notion: Notion client
        page_id (str): The Notion page ID
        content (Dict[str, Any]): The content to upload
        
    Returns:
        Dict[str, Any]: The updated page
    """
    # Extract content fields
    title = content.get("title", "Untitled")
    tags = content.get("tags", [])
    
    # Update page properties
    properties = {
        "title": {
            "title": [
                {
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    }
    
    # Add tags if provided
    if tags:
        properties["Tags"] = {
            "multi_select": [{"name": tag} for tag in tags]
        }
    
    # Update the page properties
    notion.pages.update(
        page_id=page_id,
        properties=properties
    )
    
    # Get the current page content
    blocks = notion.blocks.children.list(block_id=page_id)
    
    # Delete all existing blocks
    for block in blocks.get("results", []):
        notion.blocks.delete(block_id=block["id"])
    
    # Create new page content blocks (same as in create_notion_page)
    children = []
    
    # Extract content fields
    text = content.get("text", "")
    summary = content.get("summary", "")
    keypoints = content.get("keypoints", [])
    glossary = content.get("glossary", [])
    questions = content.get("questions", [])
    mcqs = content.get("mcqs", [])
    fill_blanks = content.get("fill_blanks", [])
    
    # Add summary if available
    if summary:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Summary"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": summary}}]
                }
            }
        ])
    
    # Add key points if available
    if keypoints:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Key Points"}}]
                }
            }
        ])
        
        # Add each key point as a bulleted list item
        for point in keypoints:
            if isinstance(point, dict) and "content" in point:
                point_text = point["content"]
            else:
                point_text = str(point)
                
            children.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": point_text}}]
                }
            })
    
    # Add glossary if available
    if glossary:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Glossary"}}]
                }
            }
        ])
        
        # Add each glossary term as a toggle block
        for term in glossary:
            if isinstance(term, dict):
                term_name = term.get("term", "")
                definition = term.get("definition", "")
            else:
                # If it's not a dict, we can't extract term and definition
                continue
                
            children.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": term_name}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": definition}}]
                            }
                        }
                    ]
                }
            })
    
    # Add questions if available
    if questions:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Questions"}}]
                }
            }
        ])
        
        # Add each question as a toggle block
        for question in questions:
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
            else:
                # If it's not a dict, we can't extract question and answer
                continue
                
            children.append({
                "object": "block",
                "type": "toggle",
                "toggle": {
                    "rich_text": [{"type": "text", "text": {"content": q_text}}],
                    "children": [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": answer}}]
                            }
                        }
                    ]
                }
            })
    
    # Add MCQs if available
    if mcqs:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Multiple Choice Questions"}}]
                }
            }
        ])
        
        # Add each MCQ as a toggle block with options as a bulleted list
        for mcq in mcqs:
            if isinstance(mcq, dict):
                q_text = mcq.get("question", "")
                options = mcq.get("options", [])
                answer = mcq.get("answer", "")
                
                # Create toggle block for the question
                toggle_block = {
                    "object": "block",
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [{"type": "text", "text": {"content": q_text}}],
                        "children": []
                    }
                }
                
                # Add options as bulleted list
                for option in options:
                    toggle_block["toggle"]["children"].append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": option}}]
                        }
                    })
                
                # Add answer
                toggle_block["toggle"]["children"].append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {"type": "text", "text": {"content": "Answer: "}},
                            {"type": "text", "text": {"content": answer}, "annotations": {"bold": True}}
                        ]
                    }
                })
                
                children.append(toggle_block)
    
    # Add fill-in-the-blanks if available
    if fill_blanks:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Fill in the Blanks"}}]
                }
            }
        ])
        
        # Add each fill-in-the-blank as a toggle block
        for blank in fill_blanks:
            if isinstance(blank, dict):
                q_text = blank.get("text", "")
                answer = blank.get("answer", "")
                
                children.append({
                    "object": "block",
                    "type": "toggle",
                    "toggle": {
                        "rich_text": [{"type": "text", "text": {"content": q_text}}],
                        "children": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [
                                        {"type": "text", "text": {"content": "Answer: "}},
                                        {"type": "text", "text": {"content": answer}, "annotations": {"bold": True}}
                                    ]
                                }
                            }
                        ]
                    }
                })
    
    # Add original text if available
    if text:
        children.extend([
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Original Text"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            }
        ])
    
    # Add the new blocks to the page
    notion.blocks.children.append(
        block_id=page_id,
        children=children
    )
    
    # Get the updated page
    page = notion.pages.retrieve(page_id=page_id)
    
    return page