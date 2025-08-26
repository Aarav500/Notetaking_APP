"""
Simplifier module for AI Note System.
Handles simplification of complex text into more understandable language.
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union

# Setup logging
logger = logging.getLogger("ai_note_system.processing.simplifier")

def simplify_text(
    text: str,
    model: str = "gpt-4",
    target_level: str = "beginner",
    domain: str = "general",
    preserve_key_terms: bool = True,
    max_length: Optional[int] = None
) -> Dict[str, Any]:
    """
    Simplify complex text to make it more understandable.
    
    Args:
        text (str): The text to simplify
        model (str): The LLM model to use
        target_level (str): Target audience level ('beginner', 'intermediate', 'advanced')
        domain (str): The domain/field of the text
        preserve_key_terms (bool): Whether to preserve key technical terms
        max_length (int, optional): Maximum length of the simplified text in words
        
    Returns:
        Dict[str, Any]: Dictionary containing the simplified text and metadata
    """
    logger.info(f"Simplifying text to {target_level} level using {model} model")
    
    if not text:
        logger.warning("Empty text provided for simplification")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate simplification method based on the model
    if model.startswith("gpt-"):
        simplified_text = simplify_with_openai(text, model, target_level, domain, preserve_key_terms, max_length)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        simplified_text = simplify_with_huggingface(text, model, target_level, domain, preserve_key_terms, max_length)
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
        "original_length": len(text.split()),
        "simplified_length": len(simplified_text.split()),
        "model": model
    }
    
    logger.debug(f"Text simplified: {result['original_length']} → {result['simplified_length']} words")
    return result

def simplify_with_openai(
    text: str,
    model: str = "gpt-4",
    target_level: str = "beginner",
    domain: str = "general",
    preserve_key_terms: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Simplify text using OpenAI API.
    
    Args:
        text (str): The text to simplify
        model (str): The OpenAI model to use
        target_level (str): Target audience level
        domain (str): The domain/field of the text
        preserve_key_terms (bool): Whether to preserve key technical terms
        max_length (int, optional): Maximum length of the simplified text in words
        
    Returns:
        str: The simplified text
    """
    try:
        import openai
        
        # Create prompt
        prompt = _create_simplification_prompt(text, target_level, domain, preserve_key_terms, max_length)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are an expert in {domain} who can explain complex concepts in simple terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500 if not max_length else min(1500, max_length * 2)
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
    domain: str = "general",
    preserve_key_terms: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Simplify text using Hugging Face models.
    
    Args:
        text (str): The text to simplify
        model (str): The Hugging Face model to use
        target_level (str): Target audience level
        domain (str): The domain/field of the text
        preserve_key_terms (bool): Whether to preserve key technical terms
        max_length (int, optional): Maximum length of the simplified text in words
        
    Returns:
        str: The simplified text
    """
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_simplification_prompt(text, target_level, domain, preserve_key_terms, max_length)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1000 if not max_length else min(1000, max_length * 2),
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

def explain_concept(
    concept: str,
    model: str = "gpt-4",
    target_level: str = "beginner",
    domain: str = "general",
    use_analogies: bool = True,
    max_length: Optional[int] = None
) -> Dict[str, Any]:
    """
    Explain a concept in simple terms.
    
    Args:
        concept (str): The concept to explain
        model (str): The LLM model to use
        target_level (str): Target audience level ('beginner', 'intermediate', 'advanced')
        domain (str): The domain/field of the concept
        use_analogies (bool): Whether to use analogies in the explanation
        max_length (int, optional): Maximum length of the explanation in words
        
    Returns:
        Dict[str, Any]: Dictionary containing the explanation and metadata
    """
    logger.info(f"Explaining concept '{concept}' at {target_level} level using {model} model")
    
    if not concept:
        logger.warning("Empty concept provided for explanation")
        return {"error": "Empty concept provided"}
    
    # Determine the appropriate explanation method based on the model
    if model.startswith("gpt-"):
        explanation = explain_with_openai(concept, model, target_level, domain, use_analogies, max_length)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        explanation = explain_with_huggingface(concept, model, target_level, domain, use_analogies, max_length)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not explanation:
        logger.error(f"Failed to explain concept")
        return {"error": "Failed to explain concept"}
    
    # Create result dictionary
    result = {
        "concept": concept,
        "explanation": explanation,
        "target_level": target_level,
        "domain": domain,
        "model": model
    }
    
    logger.debug(f"Concept explained: {len(explanation.split())} words")
    return result

def explain_with_openai(
    concept: str,
    model: str = "gpt-4",
    target_level: str = "beginner",
    domain: str = "general",
    use_analogies: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Explain a concept using OpenAI API.
    
    Args:
        concept (str): The concept to explain
        model (str): The OpenAI model to use
        target_level (str): Target audience level
        domain (str): The domain/field of the concept
        use_analogies (bool): Whether to use analogies in the explanation
        max_length (int, optional): Maximum length of the explanation in words
        
    Returns:
        str: The explanation
    """
    try:
        import openai
        
        # Create prompt
        prompt = _create_explanation_prompt(concept, target_level, domain, use_analogies, max_length)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are an expert in {domain} who can explain complex concepts in simple terms."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000 if not max_length else min(1000, max_length * 2)
        )
        
        # Extract the explanation
        explanation = response.choices[0].message.content.strip()
        
        return explanation
    except Exception as e:
        logger.error(f"Error explaining with OpenAI: {e}")
        return ""

def explain_with_huggingface(
    concept: str,
    model: str = "mistral-7b-instruct",
    target_level: str = "beginner",
    domain: str = "general",
    use_analogies: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Explain a concept using Hugging Face models.
    
    Args:
        concept (str): The concept to explain
        model (str): The Hugging Face model to use
        target_level (str): Target audience level
        domain (str): The domain/field of the concept
        use_analogies (bool): Whether to use analogies in the explanation
        max_length (int, optional): Maximum length of the explanation in words
        
    Returns:
        str: The explanation
    """
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_explanation_prompt(concept, target_level, domain, use_analogies, max_length)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=800 if not max_length else min(800, max_length * 2),
            temperature=0.5,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        explanation = generated_text[len(prompt):].strip()
        
        # Clean up the explanation
        explanation = _clean_generated_text(explanation)
        
        return explanation
    except Exception as e:
        logger.error(f"Error explaining with Hugging Face: {e}")
        return ""

def _create_simplification_prompt(
    text: str,
    target_level: str = "beginner",
    domain: str = "general",
    preserve_key_terms: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Create prompt for text simplification.
    
    Args:
        text (str): The text to simplify
        target_level (str): Target audience level
        domain (str): The domain/field of the text
        preserve_key_terms (bool): Whether to preserve key technical terms
        max_length (int, optional): Maximum length of the simplified text in words
        
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
    
    # Add key terms instruction
    if preserve_key_terms:
        prompt += ". Preserve key technical terms but explain them clearly"
    
    # Add length constraint if provided
    if max_length:
        prompt += f". Keep the simplified text under {max_length} words"
    
    # Add the text to simplify
    prompt += ":\n\n" + text
    
    return prompt

def _create_explanation_prompt(
    concept: str,
    target_level: str = "beginner",
    domain: str = "general",
    use_analogies: bool = True,
    max_length: Optional[int] = None
) -> str:
    """
    Create prompt for concept explanation.
    
    Args:
        concept (str): The concept to explain
        target_level (str): Target audience level
        domain (str): The domain/field of the concept
        use_analogies (bool): Whether to use analogies in the explanation
        max_length (int, optional): Maximum length of the explanation in words
        
    Returns:
        str: The generated prompt
    """
    # Base prompt
    prompt = f"Explain the concept of '{concept}' in {domain} for a {target_level} audience"
    
    # Add specific instructions based on target level
    if target_level == "beginner":
        prompt += ". Use simple language, avoid jargon, and explain any technical terms"
    elif target_level == "intermediate":
        prompt += ". Use moderately technical language, but explain complex concepts. Assume some background knowledge"
    elif target_level == "advanced":
        prompt += ". Use precise technical language, but ensure clarity. Focus on making complex ideas accessible to experts"
    
    # Add analogy instruction
    if use_analogies:
        prompt += ". Use analogies or examples to make the concept more relatable"
    
    # Add length constraint if provided
    if max_length:
        prompt += f". Keep the explanation under {max_length} words"
    
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
        "\n\nHope this helps",
        "\n\nLet me know if"
    ]
    
    for marker in end_markers:
        if marker.lower() in text.lower():
            text = text[:text.lower().find(marker.lower())].strip()
    
    return text

def eli5(
    text: str,
    model: str = "gpt-4",
    max_length: Optional[int] = 200
) -> Dict[str, Any]:
    """
    Explain Like I'm 5 (ELI5) - Simplify text to a child's level of understanding.
    
    Args:
        text (str): The text to simplify
        model (str): The LLM model to use
        max_length (int, optional): Maximum length of the simplified text in words
        
    Returns:
        Dict[str, Any]: Dictionary containing the simplified text and metadata
    """
    logger.info(f"Generating ELI5 explanation using {model} model")
    
    if not text:
        logger.warning("Empty text provided for ELI5")
        return {"error": "Empty text provided"}
    
    # Create ELI5 prompt
    prompt = f"Explain the following text like I'm 5 years old. Use very simple language, short sentences, and familiar examples. Avoid technical terms. Keep it under {max_length if max_length else 200} words:\n\n{text}"
    
    # Determine the appropriate method based on the model
    if model.startswith("gpt-"):
        try:
            import openai
            
            # Call OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert at explaining complex topics to young children."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the explanation
            eli5_text = response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating ELI5 with OpenAI: {e}")
            return {"error": f"Error generating ELI5: {e}"}
            
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        try:
            from transformers import pipeline
            
            # Initialize pipeline
            pipe = pipeline("text-generation", model=model, device_map="auto")
            
            # Generate text
            response = pipe(
                prompt,
                max_new_tokens=500,
                temperature=0.7,
                do_sample=True
            )
            
            # Extract generated text
            generated_text = response[0]["generated_text"]
            eli5_text = generated_text[len(prompt):].strip()
            
            # Clean up the text
            eli5_text = _clean_generated_text(eli5_text)
            
        except Exception as e:
            logger.error(f"Error generating ELI5 with Hugging Face: {e}")
            return {"error": f"Error generating ELI5: {e}"}
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    # Create result dictionary
    result = {
        "original_text": text,
        "eli5_text": eli5_text,
        "original_length": len(text.split()),
        "eli5_length": len(eli5_text.split()),
        "model": model
    }
    
    logger.debug(f"ELI5 generated: {result['eli5_length']} words")
    return result