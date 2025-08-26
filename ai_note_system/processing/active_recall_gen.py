"""
Active Recall Generator module for AI Note System.
Handles generation of active recall elements like questions, MCQs, and fill-in-the-blanks.
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union

# Setup logging
logger = logging.getLogger("ai_note_system.processing.active_recall_gen")

def generate_questions(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    question_type: str = "open_ended",
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate questions from text for active recall.
    
    Args:
        text (str): The text to generate questions from
        model (str): The LLM model to use
        count (int): Number of questions to generate
        question_type (str): Type of questions ('open_ended', 'socratic', 'reverse')
        difficulty (str): Difficulty level ('easy', 'medium', 'hard')
        focus_areas (List[str], optional): Specific areas to focus on
        
    Returns:
        Dict[str, Any]: Dictionary containing the questions and metadata
    """
    logger.info(f"Generating {question_type} questions using {model} model")
    
    if not text:
        logger.warning("Empty text provided for question generation")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate generation method based on the model
    if model.startswith("gpt-"):
        questions = generate_questions_with_openai(text, model, count, question_type, difficulty, focus_areas)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        questions = generate_questions_with_huggingface(text, model, count, question_type, difficulty, focus_areas)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not questions:
        logger.error(f"Failed to generate questions")
        return {"error": "Failed to generate questions"}
    
    # Create result dictionary
    result = {
        "questions": questions,
        "count": len(questions),
        "model": model,
        "question_type": question_type,
        "difficulty": difficulty
    }
    
    # Add focus areas if provided
    if focus_areas:
        result["focus_areas"] = focus_areas
    
    logger.debug(f"Questions generated: {result['count']} questions")
    return result

def generate_mcqs(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    options_per_question: int = 4,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate multiple-choice questions from text.
    
    Args:
        text (str): The text to generate MCQs from
        model (str): The LLM model to use
        count (int): Number of MCQs to generate
        options_per_question (int): Number of options per question
        difficulty (str): Difficulty level ('easy', 'medium', 'hard')
        focus_areas (List[str], optional): Specific areas to focus on
        
    Returns:
        Dict[str, Any]: Dictionary containing the MCQs and metadata
    """
    logger.info(f"Generating MCQs using {model} model")
    
    if not text:
        logger.warning("Empty text provided for MCQ generation")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate generation method based on the model
    if model.startswith("gpt-"):
        mcqs = generate_mcqs_with_openai(text, model, count, options_per_question, difficulty, focus_areas)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        mcqs = generate_mcqs_with_huggingface(text, model, count, options_per_question, difficulty, focus_areas)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not mcqs:
        logger.error(f"Failed to generate MCQs")
        return {"error": "Failed to generate MCQs"}
    
    # Create result dictionary
    result = {
        "mcqs": mcqs,
        "count": len(mcqs),
        "model": model,
        "options_per_question": options_per_question,
        "difficulty": difficulty
    }
    
    # Add focus areas if provided
    if focus_areas:
        result["focus_areas"] = focus_areas
    
    logger.debug(f"MCQs generated: {result['count']} questions")
    return result

def generate_fill_blanks(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate fill-in-the-blanks questions from text.
    
    Args:
        text (str): The text to generate fill-in-the-blanks from
        model (str): The LLM model to use
        count (int): Number of fill-in-the-blanks to generate
        difficulty (str): Difficulty level ('easy', 'medium', 'hard')
        focus_areas (List[str], optional): Specific areas to focus on
        
    Returns:
        Dict[str, Any]: Dictionary containing the fill-in-the-blanks and metadata
    """
    logger.info(f"Generating fill-in-the-blanks using {model} model")
    
    if not text:
        logger.warning("Empty text provided for fill-in-the-blanks generation")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate generation method based on the model
    if model.startswith("gpt-"):
        fill_blanks = generate_fill_blanks_with_openai(text, model, count, difficulty, focus_areas)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        fill_blanks = generate_fill_blanks_with_huggingface(text, model, count, difficulty, focus_areas)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not fill_blanks:
        logger.error(f"Failed to generate fill-in-the-blanks")
        return {"error": "Failed to generate fill-in-the-blanks"}
    
    # Create result dictionary
    result = {
        "fill_blanks": fill_blanks,
        "count": len(fill_blanks),
        "model": model,
        "difficulty": difficulty
    }
    
    # Add focus areas if provided
    if focus_areas:
        result["focus_areas"] = focus_areas
    
    logger.debug(f"Fill-in-the-blanks generated: {result['count']} questions")
    return result

def generate_cloze_deletions(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None,
    include_context: bool = True
) -> Dict[str, Any]:
    """
    Generate cloze deletion cards from text.
    
    Args:
        text (str): The text to generate cloze deletions from
        model (str): The LLM model to use
        count (int): Number of cloze deletions to generate
        difficulty (str): Difficulty level ('easy', 'medium', 'hard')
        focus_areas (List[str], optional): Specific areas to focus on
        include_context (bool): Whether to include additional context in the extra field
        
    Returns:
        Dict[str, Any]: Dictionary containing the cloze deletions and metadata
    """
    logger.info(f"Generating cloze deletions using {model} model")
    
    if not text:
        logger.warning("Empty text provided for cloze deletion generation")
        return {"error": "Empty text provided"}
    
    # Determine the appropriate generation method based on the model
    if model.startswith("gpt-"):
        cloze_deletions = generate_cloze_with_openai(text, model, count, difficulty, focus_areas, include_context)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        cloze_deletions = generate_cloze_with_huggingface(text, model, count, difficulty, focus_areas, include_context)
    else:
        logger.error(f"Unsupported model: {model}")
        return {"error": f"Unsupported model: {model}"}
    
    if not cloze_deletions:
        logger.error(f"Failed to generate cloze deletions")
        return {"error": "Failed to generate cloze deletions"}
    
    # Create result dictionary
    result = {
        "cloze": cloze_deletions,
        "count": len(cloze_deletions),
        "model": model,
        "difficulty": difficulty
    }
    
    # Add focus areas if provided
    if focus_areas:
        result["focus_areas"] = focus_areas
    
    logger.debug(f"Cloze deletions generated: {result['count']} cards")
    return result

# Helper functions for OpenAI API
def generate_questions_with_openai(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    question_type: str = "open_ended",
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """Generate questions using OpenAI API"""
    try:
        import openai
        
        # Create prompt based on question type
        prompt = _create_questions_prompt(text, count, question_type, difficulty, focus_areas)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator who creates high-quality questions for active recall learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        questions = result.get("questions", [])
        
        return questions
    except Exception as e:
        logger.error(f"Error generating questions with OpenAI: {e}")
        return []

def generate_mcqs_with_openai(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    options_per_question: int = 4,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Generate MCQs using OpenAI API"""
    try:
        import openai
        
        # Create prompt
        prompt = _create_mcqs_prompt(text, count, options_per_question, difficulty, focus_areas)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator who creates high-quality multiple-choice questions for active recall learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        mcqs = result.get("mcqs", [])
        
        return mcqs
    except Exception as e:
        logger.error(f"Error generating MCQs with OpenAI: {e}")
        return []

def generate_fill_blanks_with_openai(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """Generate fill-in-the-blanks using OpenAI API"""
    try:
        import openai
        
        # Create prompt
        prompt = _create_fill_blanks_prompt(text, count, difficulty, focus_areas)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator who creates high-quality fill-in-the-blanks exercises for active recall learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        fill_blanks = result.get("fill_blanks", [])
        
        return fill_blanks
    except Exception as e:
        logger.error(f"Error generating fill-in-the-blanks with OpenAI: {e}")
        return []

# Helper functions for Hugging Face models
def generate_questions_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    count: int = 5,
    question_type: str = "open_ended",
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """Generate questions using Hugging Face models"""
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_questions_prompt(text, count, question_type, difficulty, focus_areas)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1000,
            temperature=0.7,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        content = generated_text[len(prompt):].strip()
        
        # Try to parse JSON
        questions = _extract_json_from_text(content, "questions")
        
        return questions
    except Exception as e:
        logger.error(f"Error generating questions with Hugging Face: {e}")
        return []

def generate_mcqs_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    count: int = 5,
    options_per_question: int = 4,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Generate MCQs using Hugging Face models"""
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_mcqs_prompt(text, count, options_per_question, difficulty, focus_areas)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1500,
            temperature=0.7,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        content = generated_text[len(prompt):].strip()
        
        # Try to parse JSON
        mcqs = _extract_json_from_text(content, "mcqs")
        
        return mcqs
    except Exception as e:
        logger.error(f"Error generating MCQs with Hugging Face: {e}")
        return []

def generate_fill_blanks_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """Generate fill-in-the-blanks using Hugging Face models"""
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_fill_blanks_prompt(text, count, difficulty, focus_areas)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1000,
            temperature=0.7,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        content = generated_text[len(prompt):].strip()
        
        # Try to parse JSON
        fill_blanks = _extract_json_from_text(content, "fill_blanks")
        
        return fill_blanks
    except Exception as e:
        logger.error(f"Error generating fill-in-the-blanks with Hugging Face: {e}")
        return []

# Helper functions for prompt creation
def _create_questions_prompt(
    text: str,
    count: int = 5,
    question_type: str = "open_ended",
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> str:
    """Create prompt for question generation"""
    # Base prompt
    prompt = f"Generate {count} {difficulty} {question_type} questions based on the following text"
    
    # Add focus areas if provided
    if focus_areas and len(focus_areas) > 0:
        focus_str = ", ".join(focus_areas[:-1])
        if len(focus_areas) > 1:
            focus_str += f", and {focus_areas[-1]}"
        else:
            focus_str = focus_areas[0]
        prompt += f". Focus on aspects related to {focus_str}"
    
    # Add specific instructions based on question type
    if question_type == "open_ended":
        prompt += ". Include both the question and a model answer"
    elif question_type == "socratic":
        prompt += ". Create Socratic questions that encourage deeper thinking and don't have simple answers"
    elif question_type == "reverse":
        prompt += ". Create reverse questions where the answer is given and the student must formulate the question"
    
    # Add format instruction
    prompt += ". Return the result as a JSON object with the following structure: {\"questions\": [{\"question\": \"...\", \"answer\": \"...\"}, ...]}"
    
    # Add the text
    prompt += ":\n\n" + text
    
    return prompt

def _create_mcqs_prompt(
    text: str,
    count: int = 5,
    options_per_question: int = 4,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> str:
    """Create prompt for MCQ generation"""
    # Base prompt
    prompt = f"Generate {count} {difficulty} multiple-choice questions with {options_per_question} options each based on the following text"
    
    # Add focus areas if provided
    if focus_areas and len(focus_areas) > 0:
        focus_str = ", ".join(focus_areas[:-1])
        if len(focus_areas) > 1:
            focus_str += f", and {focus_areas[-1]}"
        else:
            focus_str = focus_areas[0]
        prompt += f". Focus on aspects related to {focus_str}"
    
    # Add format instruction
    prompt += ". Return the result as a JSON object with the following structure: {\"mcqs\": [{\"question\": \"...\", \"options\": [\"A. ...\", \"B. ...\", ...], \"correct_answer\": \"A\", \"explanation\": \"...\"}, ...]}"
    
    # Add the text
    prompt += ":\n\n" + text
    
    return prompt

def _create_fill_blanks_prompt(
    text: str,
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None
) -> str:
    """Create prompt for fill-in-the-blanks generation"""
    # Base prompt
    prompt = f"Generate {count} {difficulty} fill-in-the-blanks exercises based on the following text"
    
    # Add focus areas if provided
    if focus_areas and len(focus_areas) > 0:
        focus_str = ", ".join(focus_areas[:-1])
        if len(focus_areas) > 1:
            focus_str += f", and {focus_areas[-1]}"
        else:
            focus_str = focus_areas[0]
        prompt += f". Focus on aspects related to {focus_str}"
    
    # Add format instruction
    prompt += ". Return the result as a JSON object with the following structure: {\"fill_blanks\": [{\"sentence\": \"... ___ ...\", \"answer\": \"...\", \"context\": \"...\"}, ...]}"
    
    # Add the text
    prompt += ":\n\n" + text
    
    return prompt

def generate_cloze_with_openai(
    text: str,
    model: str = "gpt-4",
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None,
    include_context: bool = True
) -> List[Dict[str, Any]]:
    """Generate cloze deletions using OpenAI API"""
    try:
        import openai
        
        # Create prompt
        prompt = _create_cloze_prompt(text, count, difficulty, focus_areas, include_context)
        
        # Call OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert educator who creates high-quality cloze deletion cards for spaced repetition learning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        result = json.loads(content)
        cloze_deletions = result.get("cloze", [])
        
        return cloze_deletions
    except Exception as e:
        logger.error(f"Error generating cloze deletions with OpenAI: {e}")
        return []

def generate_cloze_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None,
    include_context: bool = True
) -> List[Dict[str, Any]]:
    """Generate cloze deletions using Hugging Face models"""
    try:
        from transformers import pipeline
        
        # Create prompt
        prompt = _create_cloze_prompt(text, count, difficulty, focus_areas, include_context)
        
        # Initialize pipeline
        pipe = pipeline("text-generation", model=model, device_map="auto")
        
        # Generate text
        response = pipe(
            prompt,
            max_new_tokens=1500,
            temperature=0.7,
            do_sample=True
        )
        
        # Extract generated text
        generated_text = response[0]["generated_text"]
        content = generated_text[len(prompt):].strip()
        
        # Try to parse JSON
        cloze_deletions = _extract_json_from_text(content, "cloze")
        
        return cloze_deletions
    except Exception as e:
        logger.error(f"Error generating cloze deletions with Hugging Face: {e}")
        return []

def _create_cloze_prompt(
    text: str,
    count: int = 5,
    difficulty: str = "medium",
    focus_areas: Optional[List[str]] = None,
    include_context: bool = True
) -> str:
    """Create prompt for cloze deletion generation"""
    # Base prompt
    prompt = f"Generate {count} {difficulty} cloze deletion cards based on the following text"
    
    # Add focus areas if provided
    if focus_areas and len(focus_areas) > 0:
        focus_str = ", ".join(focus_areas[:-1])
        if len(focus_areas) > 1:
            focus_str += f", and {focus_areas[-1]}"
        else:
            focus_str = focus_areas[0]
        prompt += f". Focus on aspects related to {focus_str}"
    
    # Add context instruction
    if include_context:
        prompt += ". Include additional context in the 'extra' field to help understand the cloze deletion"
    
    # Add format instruction
    prompt += ". Format each cloze deletion using {{c1::term}} syntax for the first term to be deleted, {{c2::term}} for the second, etc."
    prompt += " Return the result as a JSON object with the following structure: {\"cloze\": [{\"text\": \"This is a {{c1::cloze deletion}} example\", \"extra\": \"Additional context\"}, ...]}"
    
    # Add the text
    prompt += ":\n\n" + text
    
    return prompt

def _extract_json_from_text(text: str, key: str) -> List[Any]:
    """Extract JSON from text generated by LLM"""
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