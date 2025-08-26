"""
Multilingual processor module for AI Note System.
Handles language detection and translation for cross-language summarization.
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
import json

# Setup logging
logger = logging.getLogger("ai_note_system.processing.multilingual_processor")

def detect_language(
    text: str,
    use_llm: bool = False,
    confidence_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Detect the language of a text.
    
    Args:
        text (str): The text to detect language for
        use_llm (bool): Whether to use LLM for language detection
        confidence_threshold (float): Minimum confidence threshold for detection
        
    Returns:
        Dict[str, Any]: Dictionary containing language code, name, and confidence
    """
    logger.info("Detecting language of text")
    
    if not text:
        logger.warning("Empty text provided for language detection")
        return {"language_code": "en", "language_name": "English", "confidence": 0.0, "error": "Empty text provided"}
    
    # Try different detection methods in order of preference
    
    # 1. Use langdetect if available (fast and lightweight)
    try:
        from langdetect import detect, detect_langs, LangDetectException
        
        # Get language with confidence
        try:
            # Get all language probabilities
            langs = detect_langs(text[:1000])  # Use first 1000 chars for efficiency
            
            if langs:
                # Get the most probable language
                top_lang = langs[0]
                lang_code = top_lang.lang
                confidence = top_lang.prob
                
                # Get language name
                lang_name = get_language_name(lang_code)
                
                logger.debug(f"Language detected: {lang_name} ({lang_code}) with confidence {confidence:.2f}")
                
                # Check confidence threshold
                if confidence < confidence_threshold and use_llm:
                    # Fallback to LLM if confidence is low
                    logger.debug(f"Low confidence ({confidence:.2f}), falling back to LLM")
                    return detect_language_with_llm(text)
                
                return {
                    "language_code": lang_code,
                    "language_name": lang_name,
                    "confidence": confidence
                }
            
        except LangDetectException as e:
            logger.warning(f"Error with langdetect: {str(e)}")
    
    except ImportError:
        logger.warning("langdetect package not installed. Install with: pip install langdetect")
    
    # 2. Use LLM if requested or as fallback
    if use_llm:
        return detect_language_with_llm(text)
    
    # 3. Fallback to simple heuristics
    return detect_language_heuristic(text)

def detect_language_with_llm(text: str) -> Dict[str, Any]:
    """
    Detect language using an LLM.
    
    Args:
        text (str): The text to detect language for
        
    Returns:
        Dict[str, Any]: Dictionary containing language code, name, and confidence
    """
    try:
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # Create prompt for language detection
        prompt = f"""
        Detect the language of the following text. Respond with a JSON object containing:
        1. language_code: ISO 639-1 language code (e.g., "en" for English)
        2. language_name: Full name of the language in English
        3. confidence: Your confidence level from 0.0 to 1.0

        Text to analyze:
        {text[:500]}  # Use first 500 chars for efficiency
        
        JSON response:
        """
        
        # Generate structured output
        output_schema = {
            "type": "object",
            "properties": {
                "language_code": {"type": "string"},
                "language_name": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["language_code", "language_name", "confidence"]
        }
        
        result = llm.generate_structured_output(prompt, output_schema)
        
        if "language_code" in result and "language_name" in result and "confidence" in result:
            logger.debug(f"Language detected with LLM: {result['language_name']} ({result['language_code']}) with confidence {result['confidence']:.2f}")
            return result
        
        logger.warning("Invalid response from LLM for language detection")
        
    except Exception as e:
        logger.error(f"Error detecting language with LLM: {str(e)}")
    
    # Fallback to English if LLM detection fails
    return {"language_code": "en", "language_name": "English", "confidence": 0.5}

def detect_language_heuristic(text: str) -> Dict[str, Any]:
    """
    Detect language using simple heuristics.
    
    Args:
        text (str): The text to detect language for
        
    Returns:
        Dict[str, Any]: Dictionary containing language code, name, and confidence
    """
    # This is a very basic heuristic based on character frequency
    # In a real implementation, this would be more sophisticated
    
    # Count character frequencies
    char_count = {}
    for char in text.lower():
        if char.isalpha():
            char_count[char] = char_count.get(char, 0) + 1
    
    # Check for specific character patterns
    
    # Japanese (hiragana, katakana, kanji)
    japanese_chars = sum(1 for char in text if ord(char) >= 0x3040 and ord(char) <= 0x30FF or ord(char) >= 0x4E00 and ord(char) <= 0x9FFF)
    if japanese_chars > len(text) * 0.1:
        return {"language_code": "ja", "language_name": "Japanese", "confidence": 0.8}
    
    # Chinese (simplified and traditional)
    chinese_chars = sum(1 for char in text if ord(char) >= 0x4E00 and ord(char) <= 0x9FFF)
    if chinese_chars > len(text) * 0.1:
        return {"language_code": "zh", "language_name": "Chinese", "confidence": 0.8}
    
    # Korean (Hangul)
    korean_chars = sum(1 for char in text if ord(char) >= 0xAC00 and ord(char) <= 0xD7A3)
    if korean_chars > len(text) * 0.1:
        return {"language_code": "ko", "language_name": "Korean", "confidence": 0.8}
    
    # Russian (Cyrillic)
    cyrillic_chars = sum(1 for char in text if ord(char) >= 0x0400 and ord(char) <= 0x04FF)
    if cyrillic_chars > len(text) * 0.1:
        return {"language_code": "ru", "language_name": "Russian", "confidence": 0.7}
    
    # Arabic
    arabic_chars = sum(1 for char in text if ord(char) >= 0x0600 and ord(char) <= 0x06FF)
    if arabic_chars > len(text) * 0.1:
        return {"language_code": "ar", "language_name": "Arabic", "confidence": 0.7}
    
    # Check for common European languages
    
    # Spanish (high frequency of ñ, á, é, í, ó, ú)
    spanish_chars = sum(1 for char in text if char in "ñáéíóú")
    if spanish_chars > len(text) * 0.01:
        return {"language_code": "es", "language_name": "Spanish", "confidence": 0.6}
    
    # French (high frequency of é, è, ê, à, ç)
    french_chars = sum(1 for char in text if char in "éèêàç")
    if french_chars > len(text) * 0.01:
        return {"language_code": "fr", "language_name": "French", "confidence": 0.6}
    
    # German (high frequency of ä, ö, ü, ß)
    german_chars = sum(1 for char in text if char in "äöüß")
    if german_chars > len(text) * 0.01:
        return {"language_code": "de", "language_name": "German", "confidence": 0.6}
    
    # Default to English with low confidence
    return {"language_code": "en", "language_name": "English", "confidence": 0.5}

def translate_text(
    text: str,
    source_language: Optional[str] = None,
    target_language: str = "en",
    use_llm: bool = False,
    provider: str = "google"
) -> Dict[str, Any]:
    """
    Translate text from one language to another.
    
    Args:
        text (str): The text to translate
        source_language (str, optional): Source language code (auto-detect if None)
        target_language (str): Target language code
        use_llm (bool): Whether to use LLM for translation
        provider (str): Translation provider ("google", "deepl", "llm")
        
    Returns:
        Dict[str, Any]: Dictionary containing translated text and metadata
    """
    logger.info(f"Translating text to {target_language}")
    
    if not text:
        logger.warning("Empty text provided for translation")
        return {"translated_text": "", "error": "Empty text provided"}
    
    # Auto-detect source language if not provided
    if not source_language:
        detection_result = detect_language(text)
        source_language = detection_result.get("language_code", "en")
        
        # If source and target languages are the same, no translation needed
        if source_language == target_language:
            logger.debug(f"Source and target languages are the same ({source_language}), skipping translation")
            return {
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "none"
            }
    
    # Choose translation method based on provider
    if provider == "google" or (provider == "auto" and not use_llm):
        return translate_with_google(text, source_language, target_language)
    elif provider == "deepl" or (provider == "auto" and not use_llm):
        return translate_with_deepl(text, source_language, target_language)
    elif provider == "llm" or use_llm:
        return translate_with_llm(text, source_language, target_language)
    else:
        logger.error(f"Unsupported translation provider: {provider}")
        return {"error": f"Unsupported translation provider: {provider}"}

def translate_with_google(
    text: str,
    source_language: str,
    target_language: str
) -> Dict[str, Any]:
    """
    Translate text using Google Translate API.
    
    Args:
        text (str): The text to translate
        source_language (str): Source language code
        target_language (str): Target language code
        
    Returns:
        Dict[str, Any]: Dictionary containing translated text and metadata
    """
    try:
        from googletrans import Translator
        
        # Initialize translator
        translator = Translator()
        
        # Translate text
        result = translator.translate(
            text,
            src=source_language,
            dest=target_language
        )
        
        # Return result
        return {
            "translated_text": result.text,
            "source_language": source_language,
            "target_language": target_language,
            "provider": "google"
        }
        
    except ImportError:
        logger.warning("googletrans package not installed. Install with: pip install googletrans==4.0.0-rc1")
        # Fallback to LLM translation
        return translate_with_llm(text, source_language, target_language)
        
    except Exception as e:
        logger.error(f"Error translating with Google Translate: {str(e)}")
        # Fallback to LLM translation
        return translate_with_llm(text, source_language, target_language)

def translate_with_deepl(
    text: str,
    source_language: str,
    target_language: str
) -> Dict[str, Any]:
    """
    Translate text using DeepL API.
    
    Args:
        text (str): The text to translate
        source_language (str): Source language code
        target_language (str): Target language code
        
    Returns:
        Dict[str, Any]: Dictionary containing translated text and metadata
    """
    try:
        import deepl
        
        # Get API key from environment variable
        auth_key = os.environ.get("DEEPL_API_KEY")
        
        if not auth_key:
            logger.warning("DeepL API key not found in environment variables")
            # Fallback to LLM translation
            return translate_with_llm(text, source_language, target_language)
        
        # Initialize translator
        translator = deepl.Translator(auth_key)
        
        # Convert language codes to DeepL format
        source_lang = convert_to_deepl_language_code(source_language)
        target_lang = convert_to_deepl_language_code(target_language)
        
        # Translate text
        result = translator.translate_text(
            text,
            source_lang=source_lang,
            target_lang=target_lang
        )
        
        # Return result
        return {
            "translated_text": result.text,
            "source_language": source_language,
            "target_language": target_language,
            "provider": "deepl"
        }
        
    except ImportError:
        logger.warning("deepl package not installed. Install with: pip install deepl")
        # Fallback to LLM translation
        return translate_with_llm(text, source_language, target_language)
        
    except Exception as e:
        logger.error(f"Error translating with DeepL: {str(e)}")
        # Fallback to LLM translation
        return translate_with_llm(text, source_language, target_language)

def translate_with_llm(
    text: str,
    source_language: str,
    target_language: str
) -> Dict[str, Any]:
    """
    Translate text using an LLM.
    
    Args:
        text (str): The text to translate
        source_language (str): Source language code
        target_language (str): Target language code
        
    Returns:
        Dict[str, Any]: Dictionary containing translated text and metadata
    """
    try:
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get source and target language names
        source_lang_name = get_language_name(source_language)
        target_lang_name = get_language_name(target_language)
        
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # Create prompt for translation
        prompt = f"""
        Translate the following text from {source_lang_name} to {target_lang_name}.
        Maintain the original meaning, tone, and formatting as much as possible.
        
        Text to translate:
        {text}
        
        Translation:
        """
        
        # Generate translation
        translated_text = llm.generate_text(prompt)
        
        # Return result
        return {
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "provider": "llm"
        }
        
    except Exception as e:
        logger.error(f"Error translating with LLM: {str(e)}")
        return {"error": f"Error translating with LLM: {str(e)}"}

def get_language_name(language_code: str) -> str:
    """
    Get the full name of a language from its ISO 639-1 code.
    
    Args:
        language_code (str): ISO 639-1 language code
        
    Returns:
        str: Full name of the language in English
    """
    language_map = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "nl": "Dutch",
        "ru": "Russian",
        "zh": "Chinese",
        "ja": "Japanese",
        "ko": "Korean",
        "ar": "Arabic",
        "hi": "Hindi",
        "bn": "Bengali",
        "pa": "Punjabi",
        "te": "Telugu",
        "mr": "Marathi",
        "ta": "Tamil",
        "ur": "Urdu",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "vi": "Vietnamese",
        "th": "Thai",
        "tr": "Turkish",
        "pl": "Polish",
        "uk": "Ukrainian",
        "cs": "Czech",
        "sv": "Swedish",
        "da": "Danish",
        "fi": "Finnish",
        "no": "Norwegian",
        "el": "Greek",
        "he": "Hebrew",
        "id": "Indonesian",
        "ms": "Malay",
        "fa": "Persian",
        "sw": "Swahili"
    }
    
    return language_map.get(language_code, f"Unknown ({language_code})")

def convert_to_deepl_language_code(iso_code: str) -> Optional[str]:
    """
    Convert ISO 639-1 language code to DeepL language code.
    
    Args:
        iso_code (str): ISO 639-1 language code
        
    Returns:
        Optional[str]: DeepL language code or None if not supported
    """
    # DeepL uses ISO 639-1 codes but with some differences
    deepl_map = {
        "en": "EN",  # English
        "es": "ES",  # Spanish
        "fr": "FR",  # French
        "de": "DE",  # German
        "it": "IT",  # Italian
        "pt": "PT",  # Portuguese
        "nl": "NL",  # Dutch
        "ru": "RU",  # Russian
        "zh": "ZH",  # Chinese
        "ja": "JA",  # Japanese
        "pl": "PL",  # Polish
        "sv": "SV",  # Swedish
        "da": "DA",  # Danish
        "fi": "FI",  # Finnish
        "cs": "CS",  # Czech
        "el": "EL",  # Greek
        "hu": "HU",  # Hungarian
        "ro": "RO",  # Romanian
        "sk": "SK",  # Slovak
        "bg": "BG",  # Bulgarian
        "et": "ET",  # Estonian
        "lt": "LT",  # Lithuanian
        "lv": "LV",  # Latvian
        "sl": "SL",  # Slovenian
        "id": "ID",  # Indonesian
        "ko": "KO",  # Korean
        "tr": "TR",  # Turkish
        "uk": "UK",  # Ukrainian
    }
    
    return deepl_map.get(iso_code.lower())

def process_multilingual_text(
    text: str,
    target_language: str = "en",
    detect_source: bool = True,
    translation_provider: str = "auto",
    use_llm: bool = False
) -> Dict[str, Any]:
    """
    Process multilingual text by detecting language and translating if needed.
    
    Args:
        text (str): The text to process
        target_language (str): Target language code
        detect_source (bool): Whether to detect source language
        translation_provider (str): Translation provider ("google", "deepl", "llm", "auto")
        use_llm (bool): Whether to use LLM for detection and translation
        
    Returns:
        Dict[str, Any]: Dictionary containing processed text and metadata
    """
    logger.info(f"Processing multilingual text, target language: {target_language}")
    
    result = {
        "original_text": text,
        "target_language": target_language
    }
    
    # Detect source language if requested
    if detect_source:
        detection_result = detect_language(text, use_llm=use_llm)
        result["source_language"] = detection_result.get("language_code", "en")
        result["source_language_name"] = detection_result.get("language_name", "English")
        result["detection_confidence"] = detection_result.get("confidence", 0.0)
        
        # If source and target languages are the same, no translation needed
        if result["source_language"] == target_language:
            logger.debug(f"Source and target languages are the same ({target_language}), skipping translation")
            result["processed_text"] = text
            result["translated"] = False
            return result
    
    # Translate text
    translation_result = translate_text(
        text,
        source_language=result.get("source_language"),
        target_language=target_language,
        use_llm=use_llm,
        provider=translation_provider
    )
    
    # Add translation result to output
    result["processed_text"] = translation_result.get("translated_text", text)
    result["translation_provider"] = translation_result.get("provider", "none")
    result["translated"] = True
    
    # Check for errors
    if "error" in translation_result:
        result["error"] = translation_result["error"]
        result["processed_text"] = text  # Use original text if translation failed
        result["translated"] = False
    
    return result

def main():
    """
    Command-line interface for multilingual processing.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Process multilingual text")
    parser.add_argument("--text", help="Text to process")
    parser.add_argument("--file", help="File containing text to process")
    parser.add_argument("--target", default="en", help="Target language code")
    parser.add_argument("--provider", default="auto", choices=["google", "deepl", "llm", "auto"], help="Translation provider")
    parser.add_argument("--use-llm", action="store_true", help="Use LLM for detection and translation")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Get text from file or command line
    text = ""
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
    elif args.text:
        text = args.text
    else:
        print("Please provide text using --text or --file")
        return
    
    # Process text
    result = process_multilingual_text(
        text,
        target_language=args.target,
        translation_provider=args.provider,
        use_llm=args.use_llm
    )
    
    # Print or save result
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Result saved to {args.output}")
        except Exception as e:
            print(f"Error saving result: {str(e)}")
    else:
        # Print summary
        print(f"Source language: {result.get('source_language_name', 'Unknown')} (confidence: {result.get('detection_confidence', 0.0):.2f})")
        print(f"Target language: {get_language_name(result.get('target_language', 'en'))}")
        print(f"Translation provider: {result.get('translation_provider', 'none')}")
        print(f"Translated: {result.get('translated', False)}")
        print("\nProcessed text:")
        print(result.get("processed_text", ""))

if __name__ == "__main__":
    main()