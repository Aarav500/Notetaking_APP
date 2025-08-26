"""
Misconception Checker module for AI Note System.
Handles detection and correction of misconceptions in text.
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union

# Setup logging
logger = logging.getLogger("ai_note_system.processing.misconception_checker")

def check_misconceptions(
    text: str,
    domain: str,
    model: str = "gpt-4",
    max_misconceptions: int = 5,
    provide_corrections: bool = True,
    reference_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check for misconceptions in text.
    
    Args:
        text (str): The text to check for misconceptions
        domain (str): The domain/field of the text (e.g., "computer science", "physics")
        model (str): The LLM model to use
        max_misconceptions (int): Maximum number of misconceptions to identify
        provide_corrections (bool): Whether to provide corrections for misconceptions
        reference_text (str, optional): Reference text to compare against
        
    Returns:
        Dict[str, Any]: Dictionary containing the misconceptions and metadata
    """
    logger.info(f"Checking for misconceptions in {domain} text using {model} model")
    
    if not text:
        logger.warning("Empty text provided for misconception checking")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate checking method based on the model
    if model.startswith("gpt-"):
        misconceptions = check_misconceptions_with_openai(
            text, domain, model, max_misconceptions, provide_corrections, reference_text
        )
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        misconceptions = check_misconceptions_with_huggingface(
            text, domain, model, max_misconceptions, provide_corrections, reference_text
        )
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not misconceptions:
        logger.info("No misconceptions found")
        return {
            "misconceptions": [],
            "count": 0,
            "domain": domain,
            "has_misconceptions": False
        }
    
    # Create result dictionary
    result = {
        "misconceptions": misconceptions,
        "count": len(misconceptions),
        "domain": domain,
        "has_misconceptions": len(misconceptions) > 0,
        "model": model
    }
    
    logger.debug(f"Misconceptions found: {result['count']} misconceptions")
    return result

def check_misconceptions_with_openai(
    text: str,
    domain: str,
    model: str = "gpt-4",
    max_misconceptions: int = 5,
    provide_corrections: bool = True,
    reference_text: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Check for misconceptions using OpenAI API.
    
    Args:
        text (str): The text to check for misconceptions
        domain (str): The domain/field of the text
        model (str): The OpenAI model to use
        max_misconceptions (int): Maximum number of misconceptions to identify
        provide_corrections (bool): Whether to provide corrections
        reference_text (str, optional): Reference text to compare against
        
    Returns:
        List[Dict[str, str]]: List of misconceptions
    """
    try:
        import openai
        
        # Create prompt
        prompt = _create_misconception_prompt(
            text, domain, max_misconceptions, provide_corrections, reference_text
        )
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are an expert in {domain} who can identify misconceptions and provide accurate corrections."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        misconceptions = result.get("misconceptions", [])
        
        return misconceptions
    except Exception as e:
        logger.error(f"Error checking misconceptions with OpenAI: {e}")
        return []

def check_misconceptions_with_huggingface(
    text: str,
    domain: str,
    model: str = "mistral-7b-instruct",
    max_misconceptions: int = 5,
    provide_corrections: bool = True,
    reference_text: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Check for misconceptions using Hugging Face models.
    
    Args:
        text (str): The text to check for misconceptions
        domain (str): The domain/field of the text
        model (str): The Hugging Face model to use
        max_misconceptions (int): Maximum number of misconceptions to identify
        provide_corrections (bool): Whether to provide corrections
        reference_text (str, optional): Reference text to compare against
        
    Returns:
        List[Dict[str, str]]: List of misconceptions
    """
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_misconception_prompt(
            text, domain, max_misconceptions, provide_corrections, reference_text
        )
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1000,
            temperature=0.3,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        content = generated_text[len(prompt):].strip()
        
        # Try to parse JSON
        misconceptions = _extract_json_from_text(content, "misconceptions")
        
        return misconceptions
    except Exception as e:
        logger.error(f"Error checking misconceptions with Hugging Face: {e}")
        return []

def _create_misconception_prompt(
    text: str,
    domain: str,
    max_misconceptions: int = 5,
    provide_corrections: bool = True,
    reference_text: Optional[str] = None
) -> str:
    """
    Create prompt for misconception checking.
    
    Args:
        text (str): The text to check for misconceptions
        domain (str): The domain/field of the text
        max_misconceptions (int): Maximum number of misconceptions to identify
        provide_corrections (bool): Whether to provide corrections
        reference_text (str, optional): Reference text to compare against
        
    Returns:
        str: The generated prompt
    """
    # Base prompt
    prompt = f"Analyze the following text in the field of {domain} and identify up to {max_misconceptions} potential misconceptions, inaccuracies, or factual errors"
    
    # Add reference text if provided
    if reference_text:
        prompt += ". Compare it with the provided reference text to identify discrepancies"
    
    # Add correction instruction
    if provide_corrections:
        prompt += ". For each misconception, provide a correction with accurate information"
    
    # Add format instruction
    if provide_corrections:
        prompt += ". Return the result as a JSON object with the following structure: {\"misconceptions\": [{\"statement\": \"...\", \"explanation\": \"...\", \"correction\": \"...\"}, ...]}"
    else:
        prompt += ". Return the result as a JSON object with the following structure: {\"misconceptions\": [{\"statement\": \"...\", \"explanation\": \"...\"}, ...]}"
    
    # Add the text to check
    prompt += ":\n\nText to analyze:\n" + text
    
    # Add reference text if provided
    if reference_text:
        prompt += "\n\nReference text:\n" + reference_text
    
    return prompt

def _extract_json_from_text(text: str, key: str) -> List[Any]:
    """
    Extract JSON from text generated by LLM.
    
    Args:
        text (str): The text to extract JSON from
        key (str): The key to extract from the JSON
        
    Returns:
        List[Any]: The extracted list
    """
    try:
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'(\{.*\})', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = text
        
        # Parse JSON
        result = json.loads(json_str)
        return result.get(key, [])
    except Exception as e:
        logger.error(f"Error extracting JSON from text: {e}")
        return []

def simplify_explanation(
    text: str,
    model: str = "gpt-4",
    target_level: str = "beginner",
    domain: str = "general"
) -> Dict[str, Any]:
    """
    Simplify an explanation to make it more understandable.
    
    Args:
        text (str): The text to simplify
        model (str): The LLM model to use
        target_level (str): Target audience level ('beginner', 'intermediate', 'advanced')
        domain (str): The domain/field of the text
        
    Returns:
        Dict[str, Any]: Dictionary containing the simplified text and metadata
    """
    logger.info(f"Simplifying explanation to {target_level} level using {model} model")
    
    if not text:
        logger.warning("Empty text provided for simplification")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate simplification method based on the model
    if model.startswith("gpt-"):
        simplified_text = simplify_with_openai(text, model, target_level, domain)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        simplified_text = simplify_with_huggingface(text, model, target_level, domain)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not simplified_text:
        logger.error(f"Failed to simplify text")
        return {"error": "Failed to simplify text"}
    
    # Create result dictionary
    result = {
        "original_text": text,
        "simplified_text": simplified_text,
        "target_level": target_level,
        "domain": domain,
        "model": model
    }
    
    logger.debug(f"Text simplified to {target_level} level")
    return result

def simplify_with_openai(
    text: str,
    model: str = "gpt-4",
    target_level: str = "beginner",
    domain: str = "general"
) -> str:
    """
    Simplify text using OpenAI API.
    
    Args:
        text (str): The text to simplify
        model (str): The OpenAI model to use
        target_level (str): Target audience level
        domain (str): The domain/field of the text
        
    Returns:
        str: The simplified text
    """
    try:
        import openai
        
        # Create prompt
        prompt = _create_simplification_prompt(text, target_level, domain)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are an expert in {domain} who can explain complex concepts in simple terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        # Extract the simplified text
        simplified_text = response.choices[0].message.content.strip()
        
        return simplified_text
    except Exception as e:
        logger.error(f"Error simplifying with OpenAI: {e}")
        return ""

def simplify_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    target_level: str = "beginner",
    domain: str = "general"
) -> str:
    """
    Simplify text using Hugging Face models.
    
    Args:
        text (str): The text to simplify
        model (str): The Hugging Face model to use
        target_level (str): Target audience level
        domain (str): The domain/field of the text
        
    Returns:
        str: The simplified text
    """
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_simplification_prompt(text, target_level, domain)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1000,
            temperature=0.5,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        simplified_text = generated_text[len(prompt):].strip()
        
        # Clean up the simplified text
        simplified_text = _clean_generated_text(simplified_text)
        
        return simplified_text
    except Exception as e:
        logger.error(f"Error simplifying with Hugging Face: {e}")
        return ""

def _create_simplification_prompt(
    text: str,
    target_level: str = "beginner",
    domain: str = "general"
) -> str:
    """
    Create prompt for text simplification.
    
    Args:
        text (str): The text to simplify
        target_level (str): Target audience level
        domain (str): The domain/field of the text
        
    Returns:
        str: The generated prompt
    """
    # Base prompt
    prompt = f"Rewrite the following {domain} text to make it more understandable for a {target_level} audience"
    
    # Add specific instructions based on target level
    if target_level == "beginner":
        prompt += ". Use simple language, avoid jargon, and explain technical terms. Use analogies where helpful"
    elif target_level == "intermediate":
        prompt += ". Use moderately technical language, but explain complex concepts. Assume some background knowledge"
    elif target_level == "advanced":
        prompt += ". Use precise technical language, but ensure clarity. Focus on making complex ideas accessible to experts in adjacent fields"
    
    # Add the text to simplify
    prompt += ":\n\n" + text
    
    return prompt

def _clean_generated_text(text: str) -> str:
    """
    Clean up generated text by removing artifacts.
    
    Args:
        text (str): The raw generated text
        
    Returns:
        str: The cleaned text
    """
    # Remove any trailing instructions or artifacts
    end_markers = [
        "\n\nIs there anything else",
        "\n\nDo you want me to",
        "\n\nWould you like me to",
        "\n\nHope this helps"
    ]
    
    for marker in end_markers:
        if marker.lower() in text.lower():
            text = text[:text.lower().find(marker.lower())].strip()
    
    return text