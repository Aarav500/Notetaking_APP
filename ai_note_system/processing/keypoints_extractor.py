"""
Key Points Extractor module for AI Note System.
Handles extraction of key points and glossary terms from text.
"""

import os
import re
import logging
import json
from typing import Dict, Any, Optional, List, Tuple

# Setup logging
logger = logging.getLogger("ai_note_system.processing.keypoints_extractor")

def extract_keypoints(
    text: str,
    model: str = "gpt-4",
    max_points: int = 10,
    hierarchical: bool = False,
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract key points from text.
    
    Args:
        text (str): The text to extract key points from
        model (str): The LLM model to use
        max_points (int): Maximum number of key points to extract
        hierarchical (bool): Whether to organize key points hierarchically
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text, to provide context
        
    Returns:
        Dict[str, Any]: Dictionary containing the key points and metadata
    """
    logger.info(f"Extracting key points using {model} model")
    
    if not text:
        logger.warning("Empty text provided for key point extraction")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate extraction method based on the model
    if model.startswith("gpt-"):
        key_points = extract_keypoints_with_openai(text, model, max_points, hierarchical, focus_areas, title)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        key_points = extract_keypoints_with_huggingface(text, model, max_points, hierarchical, focus_areas, title)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not key_points:
        logger.error(f"Failed to extract key points")
        return {"error": "Failed to extract key points"}
    
    # Create result dictionary
    result = {
        "key_points": key_points,
        "count": len(key_points) if not hierarchical else _count_hierarchical_points(key_points),
        "model": model,
        "hierarchical": hierarchical
    }
    
    # Add focus areas if provided
    if focus_areas:
        result["focus_areas"] = focus_areas
    
    logger.debug(f"Key points extracted: {result['count']} points")
    return result

def extract_glossary(
    text: str,
    model: str = "gpt-4",
    max_terms: int = 15,
    include_definitions: bool = True,
    domain: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract glossary terms from text.
    
    Args:
        text (str): The text to extract glossary terms from
        model (str): The LLM model to use
        max_terms (int): Maximum number of glossary terms to extract
        include_definitions (bool): Whether to include definitions for terms
        domain (str, optional): Domain/field to focus on (e.g., "computer science")
        title (str, optional): Title of the text, to provide context
        
    Returns:
        Dict[str, Any]: Dictionary containing the glossary terms and metadata
    """
    logger.info(f"Extracting glossary terms using {model} model")
    
    if not text:
        logger.warning("Empty text provided for glossary extraction")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate extraction method based on the model
    if model.startswith("gpt-"):
        glossary = extract_glossary_with_openai(text, model, max_terms, include_definitions, domain, title)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        glossary = extract_glossary_with_huggingface(text, model, max_terms, include_definitions, domain, title)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not glossary:
        logger.error(f"Failed to extract glossary terms")
        return {"error": "Failed to extract glossary terms"}
    
    # Create result dictionary
    result = {
        "glossary": glossary,
        "count": len(glossary),
        "model": model,
        "include_definitions": include_definitions
    }
    
    # Add domain if provided
    if domain:
        result["domain"] = domain
    
    logger.debug(f"Glossary terms extracted: {result['count']} terms")
    return result

def extract_keypoints_with_openai(
    text: str,
    model: str = "gpt-4",
    max_points: int = 10,
    hierarchical: bool = False,
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> List[Any]:
    """
    Extract key points from text using OpenAI's API.
    
    Args:
        text (str): The text to extract key points from
        model (str): The OpenAI model to use
        max_points (int): Maximum number of key points to extract
        hierarchical (bool): Whether to organize key points hierarchically
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text
        
    Returns:
        List[Any]: The extracted key points (list of strings or hierarchical dict)
    """
    try:
        import openai
        
        logger.debug(f"Using OpenAI {model} for key point extraction")
        
        # Prepare the prompt
        prompt = _create_keypoints_prompt(text, max_points, hierarchical, focus_areas, title)
        
        # Call the OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at extracting key points from text. Your task is to identify the most important concepts, ideas, and information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
            response_format={"type": "json_object"} if hierarchical else None
        )
        
        # Extract the key points from the response
        content = response.choices[0].message.content.strip()
        
        # Parse the response based on format
        if hierarchical:
            try:
                # Parse JSON response
                result = json.loads(content)
                key_points = result.get("key_points", [])
            except json.JSONDecodeError:
                logger.error("Failed to parse hierarchical key points JSON")
                return []
        else:
            # Parse list response
            key_points = _parse_list_response(content)
        
        logger.debug(f"OpenAI key points extracted: {len(key_points) if not hierarchical else _count_hierarchical_points(key_points)} points")
        return key_points
        
    except ImportError:
        logger.error("OpenAI package not installed. Install with: pip install openai")
        return []
        
    except Exception as e:
        logger.error(f"Error extracting key points with OpenAI: {e}")
        return []

def extract_keypoints_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    max_points: int = 10,
    hierarchical: bool = False,
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> List[Any]:
    """
    Extract key points from text using Hugging Face models.
    
    Args:
        text (str): The text to extract key points from
        model (str): The Hugging Face model to use
        max_points (int): Maximum number of key points to extract
        hierarchical (bool): Whether to organize key points hierarchically
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text
        
    Returns:
        List[Any]: The extracted key points (list of strings or hierarchical dict)
    """
    try:
        from transformers import pipeline
        
        logger.debug(f"Using Hugging Face {model} for key point extraction")
        
        # Prepare the prompt
        prompt = _create_keypoints_prompt(text, max_points, hierarchical, focus_areas, title)
        
        # Initialize the pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            device_map="auto"
        )
        
        # Generate the key points
        response = pipe(
            prompt,
            max_new_tokens=800,
            temperature=0.2,
            top_p=0.95,
            do_sample=True
        )
        
        # Extract the generated text
        generated_text = response[0]["generated_text"]
        
        # Remove the prompt from the generated text
        content = generated_text[len(prompt):].strip()
        
        # Parse the response based on format
        if hierarchical:
            try:
                # Try to extract JSON from the response
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                else:
                    # Try to find JSON object directly
                    json_str = re.search(r'(\{.*\})', content, re.DOTALL)
                    if json_str:
                        json_str = json_str.group(1)
                    else:
                        json_str = content
                
                result = json.loads(json_str)
                key_points = result.get("key_points", [])
            except (json.JSONDecodeError, AttributeError):
                logger.error("Failed to parse hierarchical key points JSON")
                return []
        else:
            # Parse list response
            key_points = _parse_list_response(content)
        
        logger.debug(f"Hugging Face key points extracted: {len(key_points) if not hierarchical else _count_hierarchical_points(key_points)} points")
        return key_points
        
    except ImportError:
        logger.error("Transformers package not installed. Install with: pip install transformers")
        return []
        
    except Exception as e:
        logger.error(f"Error extracting key points with Hugging Face: {e}")
        return []

def extract_glossary_with_openai(
    text: str,
    model: str = "gpt-4",
    max_terms: int = 15,
    include_definitions: bool = True,
    domain: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, str]:
    """
    Extract glossary terms from text using OpenAI's API.
    
    Args:
        text (str): The text to extract glossary terms from
        model (str): The OpenAI model to use
        max_terms (int): Maximum number of glossary terms to extract
        include_definitions (bool): Whether to include definitions for terms
        domain (str, optional): Domain/field to focus on
        title (str, optional): Title of the text
        
    Returns:
        Dict[str, str]: Dictionary of glossary terms and their definitions
    """
    try:
        import openai
        
        logger.debug(f"Using OpenAI {model} for glossary extraction")
        
        # Prepare the prompt
        prompt = _create_glossary_prompt(text, max_terms, include_definitions, domain, title)
        
        # Call the OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at identifying technical terms and creating glossaries. Your task is to extract important terms and provide clear, concise definitions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Extract the glossary from the response
        content = response.choices[0].message.content.strip()
        
        try:
            # Parse JSON response
            result = json.loads(content)
            glossary = result.get("glossary", {})
        except json.JSONDecodeError:
            logger.error("Failed to parse glossary JSON")
            return {}
        
        logger.debug(f"OpenAI glossary terms extracted: {len(glossary)} terms")
        return glossary
        
    except ImportError:
        logger.error("OpenAI package not installed. Install with: pip install openai")
        return {}
        
    except Exception as e:
        logger.error(f"Error extracting glossary with OpenAI: {e}")
        return {}

def extract_glossary_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    max_terms: int = 15,
    include_definitions: bool = True,
    domain: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, str]:
    """
    Extract glossary terms from text using Hugging Face models.
    
    Args:
        text (str): The text to extract glossary terms from
        model (str): The Hugging Face model to use
        max_terms (int): Maximum number of glossary terms to extract
        include_definitions (bool): Whether to include definitions for terms
        domain (str, optional): Domain/field to focus on
        title (str, optional): Title of the text
        
    Returns:
        Dict[str, str]: Dictionary of glossary terms and their definitions
    """
    try:
        from transformers import pipeline
        
        logger.debug(f"Using Hugging Face {model} for glossary extraction")
        
        # Prepare the prompt
        prompt = _create_glossary_prompt(text, max_terms, include_definitions, domain, title)
        
        # Initialize the pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            device_map="auto"
        )
        
        # Generate the glossary
        response = pipe(
            prompt,
            max_new_tokens=800,
            temperature=0.2,
            top_p=0.95,
            do_sample=True
        )
        
        # Extract the generated text
        generated_text = response[0]["generated_text"]
        
        # Remove the prompt from the generated text
        content = generated_text[len(prompt):].strip()
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_str = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_str:
                    json_str = json_str.group(1)
                else:
                    json_str = content
            
            result = json.loads(json_str)
            glossary = result.get("glossary", {})
        except (json.JSONDecodeError, AttributeError):
            logger.error("Failed to parse glossary JSON")
            return {}
        
        logger.debug(f"Hugging Face glossary terms extracted: {len(glossary)} terms")
        return glossary
        
    except ImportError:
        logger.error("Transformers package not installed. Install with: pip install transformers")
        return {}
        
    except Exception as e:
        logger.error(f"Error extracting glossary with Hugging Face: {e}")
        return {}

def _create_keypoints_prompt(
    text: str,
    max_points: int = 10,
    hierarchical: bool = False,
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> str:
    """
    Create a prompt for key point extraction.
    
    Args:
        text (str): The text to extract key points from
        max_points (int): Maximum number of key points to extract
        hierarchical (bool): Whether to organize key points hierarchically
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text
        
    Returns:
        str: The generated prompt
    """
    # Start with the basic instruction
    prompt = f"Extract the {max_points} most important key points from the following text"
    
    # Add title context if provided
    if title:
        prompt += f" titled '{title}'"
    
    # Add focus areas if provided
    if focus_areas and len(focus_areas) > 0:
        focus_str = ", ".join(focus_areas[:-1])
        if len(focus_areas) > 1:
            focus_str += f", and {focus_areas[-1]}"
        else:
            focus_str = focus_areas[0]
        prompt += f". Focus on aspects related to {focus_str}"
    
    # Add format instruction
    if hierarchical:
        prompt += ". Organize the key points hierarchically with main points and sub-points. Return the result as a JSON object with the following structure: {\"key_points\": [{\"main_point\": \"Main point 1\", \"sub_points\": [\"Sub-point 1.1\", \"Sub-point 1.2\"]}, ...]}"
    else:
        prompt += ". Return the key points as a numbered list"
    
    # Add the text to extract key points from
    prompt += ":\n\n" + text
    
    return prompt

def _create_glossary_prompt(
    text: str,
    max_terms: int = 15,
    include_definitions: bool = True,
    domain: Optional[str] = None,
    title: Optional[str] = None
) -> str:
    """
    Create a prompt for glossary extraction.
    
    Args:
        text (str): The text to extract glossary terms from
        max_terms (int): Maximum number of glossary terms to extract
        include_definitions (bool): Whether to include definitions for terms
        domain (str, optional): Domain/field to focus on
        title (str, optional): Title of the text
        
    Returns:
        str: The generated prompt
    """
    # Start with the basic instruction
    prompt = f"Extract up to {max_terms} important technical terms or concepts from the following text"
    
    # Add title context if provided
    if title:
        prompt += f" titled '{title}'"
    
    # Add domain if provided
    if domain:
        prompt += f" in the field of {domain}"
    
    # Add definition instruction
    if include_definitions:
        prompt += ". For each term, provide a clear, concise definition based on the context"
    else:
        prompt += ". Only extract the terms without definitions"
    
    # Add format instruction
    if include_definitions:
        prompt += ". Return the result as a JSON object with the following structure: {\"glossary\": {\"term1\": \"definition1\", \"term2\": \"definition2\", ...}}"
    else:
        prompt += ". Return the result as a JSON object with the following structure: {\"glossary\": {\"term1\": \"\", \"term2\": \"\", ...}}"
    
    # Add the text to extract glossary terms from
    prompt += ":\n\n" + text
    
    return prompt

def _parse_list_response(response: str) -> List[str]:
    """
    Parse a list response from an LLM.
    
    Args:
        response (str): The response to parse
        
    Returns:
        List[str]: The parsed list
    """
    # Try to extract numbered list items
    numbered_pattern = r'^\s*(\d+)[.)\]]\s*(.+)$'
    numbered_matches = re.findall(numbered_pattern, response, re.MULTILINE)
    
    if numbered_matches:
        return [match[1].strip() for match in numbered_matches]
    
    # Try to extract bullet list items
    bullet_pattern = r'^\s*[-•*]\s*(.+)$'
    bullet_matches = re.findall(bullet_pattern, response, re.MULTILINE)
    
    if bullet_matches:
        return [match.strip() for match in bullet_matches]
    
    # If no list format is detected, split by newlines and filter empty lines
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    return lines

def _count_hierarchical_points(key_points: List[Dict[str, Any]]) -> int:
    """
    Count the total number of points in a hierarchical key points structure.
    
    Args:
        key_points (List[Dict[str, Any]]): The hierarchical key points
        
    Returns:
        int: The total number of points
    """
    count = 0
    
    for point in key_points:
        # Count the main point
        count += 1
        
        # Count sub-points if present
        sub_points = point.get("sub_points", [])
        count += len(sub_points)
    
    return count