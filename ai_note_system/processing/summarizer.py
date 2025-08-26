"""
Summarizer module for AI Note System.
Handles text summarization using various LLM models.
Supports cross-language summarization.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple

# Setup logging
logger = logging.getLogger("ai_note_system.processing.summarizer")

def summarize_text(
    text: str,
    model: str = "gpt-4",
    max_length: Optional[int] = None,
    format: str = "paragraph",
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None,
    source_language: Optional[str] = None,
    target_language: str = "en",
    translate: bool = True,
    translation_provider: str = "auto"
) -> Dict[str, Any]:
    """
    Summarize text using an LLM.
    
    Args:
        text (str): The text to summarize
        model (str): The LLM model to use
        max_length (int, optional): Maximum length of the summary in words
        format (str): Format of the summary ('paragraph', 'bullet_points', 'numbered_list')
        focus_areas (List[str], optional): Specific areas to focus on in the summary
        title (str, optional): Title of the text, to provide context
        source_language (str, optional): Source language code (auto-detect if None)
        target_language (str): Target language code for the summary
        translate (bool): Whether to translate non-English content
        translation_provider (str): Translation provider ("google", "deepl", "llm", "auto")
        
    Returns:
        Dict[str, Any]: Dictionary containing the summary and metadata
    """
    logger.info(f"Summarizing text using {model} model")
    
    if not text:
        logger.warning("Empty text provided for summarization")
        return {"error": "Empty text provided"}
    
    # Process multilingual text if needed
    processed_text = text
    language_info = {}
    
    if translate:
        try:
            from ai_note_system.processing.multilingual_processor import process_multilingual_text
            
            # Process text with multilingual processor
            multilingual_result = process_multilingual_text(
                text=text,
                target_language="en",  # Always summarize in English first
                detect_source=source_language is None,
                translation_provider=translation_provider
            )
            
            # Use processed text for summarization
            processed_text = multilingual_result.get("processed_text", text)
            
            # Store language information
            language_info = {
                "source_language": multilingual_result.get("source_language"),
                "source_language_name": multilingual_result.get("source_language_name"),
                "detection_confidence": multilingual_result.get("detection_confidence"),
                "translated": multilingual_result.get("translated", False),
                "translation_provider": multilingual_result.get("translation_provider")
            }
            
            logger.debug(f"Processed multilingual text: {language_info.get('source_language_name')} -> English")
            
        except ImportError:
            logger.warning("Multilingual processor not available. Proceeding with original text.")
        except Exception as e:
            logger.error(f"Error processing multilingual text: {str(e)}")
    
    # Determine the appropriate summarization method based on the model
    if model.startswith("gpt-"):
        summary = summarize_with_openai(processed_text, model, max_length, format, focus_areas, title)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        summary = summarize_with_huggingface(processed_text, model, max_length, format, focus_areas, title)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not summary:
        logger.error(f"Failed to generate summary")
        return {"error": "Failed to generate summary"}
    
    # Translate summary to target language if needed
    if target_language != "en" and summary:
        try:
            from ai_note_system.processing.multilingual_processor import translate_text
            
            # Translate summary to target language
            translation_result = translate_text(
                text=summary,
                source_language="en",
                target_language=target_language,
                provider=translation_provider
            )
            
            # Use translated summary
            if "translated_text" in translation_result and translation_result["translated_text"]:
                summary = translation_result["translated_text"]
                language_info["summary_language"] = target_language
                language_info["summary_language_name"] = translation_result.get("target_language_name", 
                                                                              get_language_name(target_language))
                language_info["summary_translation_provider"] = translation_result.get("provider")
                
                logger.debug(f"Translated summary to {language_info.get('summary_language_name')}")
                
        except ImportError:
            logger.warning("Multilingual processor not available. Keeping summary in English.")
        except Exception as e:
            logger.error(f"Error translating summary: {str(e)}")
    
    # Create result dictionary
    result = {
        "summary": summary,
        "original_length": len(text.split()),
        "summary_length": len(summary.split()),
        "model": model,
        "format": format
    }
    
    # Add focus areas if provided
    if focus_areas:
        result["focus_areas"] = focus_areas
    
    # Add language information if available
    if language_info:
        result["language_info"] = language_info
    
    logger.debug(f"Summary generated: {result['summary_length']} words")
    return result

def get_language_name(language_code: str) -> str:
    """
    Get the full name of a language from its ISO 639-1 code.
    
    Args:
        language_code (str): ISO 639-1 language code
        
    Returns:
        str: Full name of the language in English
    """
    try:
        from ai_note_system.processing.multilingual_processor import get_language_name as get_name
        return get_name(language_code)
    except ImportError:
        # Fallback to basic mapping
        language_map = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
            "ru": "Russian",
            "ar": "Arabic"
        }
        return language_map.get(language_code, f"Unknown ({language_code})")

def summarize_with_openai(
    text: str,
    model: str = "gpt-4",
    max_length: Optional[int] = None,
    format: str = "paragraph",
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> str:
    """
    Summarize text using OpenAI's API.
    
    Args:
        text (str): The text to summarize
        model (str): The OpenAI model to use
        max_length (int, optional): Maximum length of the summary in words
        format (str): Format of the summary
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text
        
    Returns:
        str: The generated summary
    """
    try:
        import openai
        
        logger.debug(f"Using OpenAI {model} for summarization")
        
        # Prepare the prompt
        prompt = _create_summarization_prompt(text, max_length, format, focus_areas, title)
        
        # Call the OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert summarizer. Your task is to create concise, accurate summaries that capture the key points of the text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000 if not max_length else min(1000, max_length * 2)
        )
        
        # Extract the summary from the response
        summary = response.choices[0].message.content.strip()
        
        logger.debug(f"OpenAI summary generated: {len(summary.split())} words")
        return summary
        
    except ImportError:
        logger.error("OpenAI package not installed. Install with: pip install openai")
        return ""
        
    except Exception as e:
        logger.error(f"Error summarizing with OpenAI: {e}")
        return ""

def summarize_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    max_length: Optional[int] = None,
    format: str = "paragraph",
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> str:
    """
    Summarize text using Hugging Face models.
    
    Args:
        text (str): The text to summarize
        model (str): The Hugging Face model to use
        max_length (int, optional): Maximum length of the summary in words
        format (str): Format of the summary
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text
        
    Returns:
        str: The generated summary
    """
    try:
        from transformers import pipeline
        
        logger.debug(f"Using Hugging Face {model} for summarization")
        
        # Prepare the prompt
        prompt = _create_summarization_prompt(text, max_length, format, focus_areas, title)
        
        # Initialize the pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            device_map="auto"
        )
        
        # Generate the summary
        response = pipe(
            prompt,
            max_new_tokens=500 if not max_length else min(500, max_length * 2),
            temperature=0.3,
            top_p=0.95,
            do_sample=True
        )
        
        # Extract the summary from the response
        generated_text = response[0]["generated_text"]
        
        # Remove the prompt from the generated text
        summary = generated_text[len(prompt):].strip()
        
        # Clean up the summary (remove any trailing instructions or artifacts)
        summary = _clean_generated_summary(summary)
        
        logger.debug(f"Hugging Face summary generated: {len(summary.split())} words")
        return summary
        
    except ImportError:
        logger.error("Transformers package not installed. Install with: pip install transformers")
        return ""
        
    except Exception as e:
        logger.error(f"Error summarizing with Hugging Face: {e}")
        return ""

def _create_summarization_prompt(
    text: str,
    max_length: Optional[int] = None,
    format: str = "paragraph",
    focus_areas: Optional[List[str]] = None,
    title: Optional[str] = None
) -> str:
    """
    Create a prompt for summarization.
    
    Args:
        text (str): The text to summarize
        max_length (int, optional): Maximum length of the summary in words
        format (str): Format of the summary
        focus_areas (List[str], optional): Specific areas to focus on
        title (str, optional): Title of the text
        
    Returns:
        str: The generated prompt
    """
    # Start with the basic instruction
    prompt = "Please summarize the following text"
    
    # Add title context if provided
    if title:
        prompt += f" titled '{title}'"
    
    # Add length constraint if provided
    if max_length:
        prompt += f" in {max_length} words or less"
    
    # Add format instruction
    if format == "bullet_points":
        prompt += " as a bullet point list"
    elif format == "numbered_list":
        prompt += " as a numbered list"
    else:  # paragraph format
        prompt += " in paragraph form"
    
    # Add focus areas if provided
    if focus_areas and len(focus_areas) > 0:
        focus_str = ", ".join(focus_areas[:-1])
        if len(focus_areas) > 1:
            focus_str += f", and {focus_areas[-1]}"
        else:
            focus_str = focus_areas[0]
        prompt += f". Focus on aspects related to {focus_str}"
    
    # Add the text to summarize
    prompt += ":\n\n" + text
    
    return prompt

def _clean_generated_summary(summary: str) -> str:
    """
    Clean up a generated summary by removing artifacts.
    
    Args:
        summary (str): The raw generated summary
        
    Returns:
        str: The cleaned summary
    """
    # Remove any "Summary:" prefix
    if summary.lower().startswith("summary:"):
        summary = summary[len("summary:"):].strip()
    
    # Remove any trailing quotes
    summary = summary.strip('"\'')
    
    # Remove any trailing instructions or artifacts
    end_markers = [
        "\n\nIs there anything else",
        "\n\nDo you want me to",
        "\n\nWould you like me to",
        "\n\nIs this summary",
        "\n\nHope this helps"
    ]
    
    for marker in end_markers:
        if marker.lower() in summary.lower():
            summary = summary[:summary.lower().find(marker.lower())].strip()
    
    return summary