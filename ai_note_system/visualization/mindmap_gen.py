"""
Mind map generator module for AI Note System.
Generates mind maps from text using Mermaid.
"""

import os
import logging
import subprocess
import tempfile
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.mindmap_gen")

def generate_mindmap(
    text: str,
    output_format: str = "png",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    theme: str = "default",
    include_code: bool = True
) -> Dict[str, Any]:
    """
    Generate a mind map from text.
    
    Args:
        text (str): The text to generate a mind map from
        output_format (str): The output format (png, svg, pdf)
        output_path (str, optional): Path to save the output file
        title (str, optional): Title for the mind map
        theme (str): Theme for the mind map
        include_code (bool): Whether to include the generated code in the result
        
    Returns:
        Dict[str, Any]: Dictionary containing the mind map information
    """
    logger.info("Generating mind map")
    
    # Generate Mermaid code from text
    mermaid_code = extract_mindmap_from_text(text, title)
    
    # Create result dictionary
    result = {
        "title": title or "Mind Map",
        "format": output_format
    }
    
    if include_code:
        result["code"] = mermaid_code
    
    # If output path is provided, render the mind map
    if output_path:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save Mermaid code to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", delete=False) as f:
                f.write(mermaid_code)
                temp_file = f.name
            
            # Use mmdc (Mermaid CLI) to render the mind map
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
            logger.debug(f"Mind map saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error rendering mind map: {e}")
            result["error"] = f"Error rendering mind map: {e}"
    
    return result

def extract_mindmap_from_text(
    text: str,
    title: Optional[str] = None
) -> str:
    """
    Extract a mind map from text.
    
    Args:
        text (str): The text to extract a mind map from
        title (str, optional): Title for the mind map
        
    Returns:
        str: Mermaid mind map code
    """
    # This is a simplified version that extracts topics and subtopics
    # In a real implementation, this would use an LLM to generate a more complex mind map
    
    # Extract topics and subtopics from text
    topics = extract_hierarchical_topics(text)
    
    # Generate Mermaid code
    mermaid_code = ["mindmap"]
    
    if title:
        # In Mermaid, the root node serves as the title
        root_id = "root"
        mermaid_code.append(f"  {root_id}[{title}]")
    else:
        # If no title is provided, use the first sentence as the root
        first_sentence = text.split(".")[0].strip()
        if len(first_sentence) > 50:
            first_sentence = first_sentence[:47] + "..."
        root_id = "root"
        mermaid_code.append(f"  {root_id}[{first_sentence}]")
    
    # Add topics and subtopics
    for i, (topic, subtopics) in enumerate(topics.items()):
        topic_id = f"topic{i+1}"
        mermaid_code.append(f"    {root_id} --> {topic_id}[{topic}]")
        
        for j, subtopic in enumerate(subtopics):
            subtopic_id = f"topic{i+1}_{j+1}"
            mermaid_code.append(f"      {topic_id} --> {subtopic_id}[{subtopic}]")
    
    return "\n".join(mermaid_code)

def extract_hierarchical_topics(text: str) -> Dict[str, List[str]]:
    """
    Extract hierarchical topics from text.
    
    Args:
        text (str): The text to extract topics from
        
    Returns:
        Dict[str, List[str]]: Dictionary of topics and their subtopics
    """
    # This is a simplified implementation that looks for patterns in the text
    # In a real implementation, this would use an LLM to extract topics more intelligently
    
    topics = {}
    current_topic = None
    
    # Split text into paragraphs
    paragraphs = text.split("\n\n")
    
    # Process each paragraph
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # Check if paragraph starts with a heading-like pattern
        if re.match(r"^[A-Z].*:$", paragraph.split("\n")[0]) or paragraph.isupper():
            # This looks like a heading/topic
            current_topic = paragraph.split("\n")[0].strip().rstrip(":")
            topics[current_topic] = []
        elif current_topic:
            # This is content for the current topic
            # Extract key phrases as subtopics
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            for sentence in sentences:
                if len(sentence) > 10:
                    # Extract a simplified version of the sentence as a subtopic
                    subtopic = simplify_sentence(sentence)
                    if subtopic and subtopic not in topics[current_topic]:
                        topics[current_topic].append(subtopic)
    
    # If no topics were found using the heading pattern, try another approach
    if not topics:
        # Use sentences as topics and extract key phrases as subtopics
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Use the first few sentences as topics
        for i, sentence in enumerate(sentences[:5]):
            if len(sentence) > 10:
                topic = simplify_sentence(sentence)
                if topic:
                    topics[topic] = []
                    
                    # Look for related sentences to use as subtopics
                    for j, other_sentence in enumerate(sentences):
                        if i != j and len(other_sentence) > 10:
                            if are_sentences_related(sentence, other_sentence):
                                subtopic = simplify_sentence(other_sentence)
                                if subtopic and subtopic not in topics[topic]:
                                    topics[topic].append(subtopic)
    
    # Ensure we have at least one topic
    if not topics:
        topics["Main Topic"] = ["Subtopic 1", "Subtopic 2"]
    
    # Limit the number of subtopics for readability
    for topic in topics:
        topics[topic] = topics[topic][:5]
    
    return topics

def simplify_sentence(sentence: str) -> str:
    """
    Simplify a sentence to extract the main concept.
    
    Args:
        sentence (str): The sentence to simplify
        
    Returns:
        str: Simplified sentence
    """
    sentence = sentence.strip()
    
    # Remove common filler words
    filler_words = ["the", "a", "an", "and", "or", "but", "so", "because", "however", "therefore"]
    for word in filler_words:
        sentence = re.sub(r'\b' + word + r'\b', '', sentence, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    sentence = re.sub(r'\s+', ' ', sentence).strip()
    
    # Truncate if too long
    if len(sentence) > 40:
        sentence = sentence[:37] + "..."
    
    return sentence

def are_sentences_related(sentence1: str, sentence2: str) -> bool:
    """
    Check if two sentences are related.
    
    Args:
        sentence1 (str): First sentence
        sentence2 (str): Second sentence
        
    Returns:
        bool: True if sentences are related, False otherwise
    """
    # This is a very simplified implementation
    # In a real implementation, this would use embeddings or an LLM
    
    # Convert to lowercase and tokenize
    words1 = set(re.findall(r'\b\w+\b', sentence1.lower()))
    words2 = set(re.findall(r'\b\w+\b', sentence2.lower()))
    
    # Calculate overlap
    common_words = words1.intersection(words2)
    
    # Consider related if they share at least 2 significant words
    return len(common_words) >= 2

def generate_mindmap_from_llm(
    text: str,
    model: str = "gpt-4",
    title: Optional[str] = None
) -> str:
    """
    Generate a mind map from text using an LLM.
    
    Args:
        text (str): The text to generate a mind map from
        model (str): The LLM model to use
        title (str, optional): Title for the mind map
        
    Returns:
        str: Mermaid mind map code
    """
    logger.info(f"Generating mind map using LLM model: {model}")
    
    # Determine which LLM to use based on the model name
    if model.startswith("gpt-"):
        mindmap_code = _generate_mindmap_with_openai(text, model, title)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        mindmap_code = _generate_mindmap_with_huggingface(text, model, title)
    else:
        logger.warning(f"Unsupported model: {model}, falling back to simple extraction")
        # Fall back to simpler extraction method
        mindmap_code = extract_mindmap_from_text(text, title)
    
    return mindmap_code

def _generate_mindmap_with_openai(
    text: str,
    model: str = "gpt-4",
    title: Optional[str] = None
) -> str:
    """
    Generate a mind map from text using OpenAI's API.
    
    Args:
        text (str): The text to generate a mind map from
        model (str): The OpenAI model to use
        title (str, optional): Title for the mind map
        
    Returns:
        str: Mermaid mind map code
    """
    try:
        import openai
        
        logger.debug(f"Using OpenAI {model} for mind map generation")
        
        # Prepare the prompt
        prompt = _create_mindmap_prompt(text, title)
        
        # Call the OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at creating mind maps from text. Your task is to analyze the text and create a clear, hierarchical mind map that represents the main concepts and their relationships."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        # Extract the mind map code from the response
        content = response.choices[0].message.content.strip()
        
        # Extract code block if present
        import re
        code_match = re.search(r'```(?:mermaid)?\s*(mindmap[\s\S]*?)```', content, re.IGNORECASE)
        
        if code_match:
            mindmap_code = code_match.group(1).strip()
        else:
            # If no code block is found, use the entire response
            mindmap_code = content
        
        logger.debug("Successfully generated mind map with OpenAI")
        return mindmap_code
        
    except ImportError:
        logger.error("OpenAI package not installed. Install with: pip install openai")
        # Fall back to simpler extraction
        return extract_mindmap_from_text(text, title)
        
    except Exception as e:
        logger.error(f"Error generating mind map with OpenAI: {e}")
        # Fall back to simpler extraction
        return extract_mindmap_from_text(text, title)

def _generate_mindmap_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    title: Optional[str] = None
) -> str:
    """
    Generate a mind map from text using Hugging Face models.
    
    Args:
        text (str): The text to generate a mind map from
        model (str): The Hugging Face model to use
        title (str, optional): Title for the mind map
        
    Returns:
        str: Mermaid mind map code
    """
    try:
        from transformers import pipeline
        
        logger.debug(f"Using Hugging Face {model} for mind map generation")
        
        # Prepare the prompt
        prompt = _create_mindmap_prompt(text, title)
        
        # Initialize the pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            device_map="auto"
        )
        
        # Generate the mind map
        response = pipe(
            prompt,
            max_new_tokens=1000,
            temperature=0.2,
            top_p=0.95,
            do_sample=True
        )
        
        # Extract the generated text
        generated_text = response[0]["generated_text"]
        
        # Remove the prompt from the generated text
        content = generated_text[len(prompt):].strip()
        
        # Extract code block if present
        import re
        code_match = re.search(r'```(?:mermaid)?\s*(mindmap[\s\S]*?)```', content, re.IGNORECASE)
        
        if code_match:
            mindmap_code = code_match.group(1).strip()
        else:
            # If no code block is found, try to extract the relevant part
            mindmap_match = re.search(r'(mindmap[\s\S]*)', content)
            if mindmap_match:
                mindmap_code = mindmap_match.group(1).strip()
            else:
                # Fall back to simpler extraction
                mindmap_code = extract_mindmap_from_text(text, title)
        
        logger.debug("Successfully generated mind map with Hugging Face")
        return mindmap_code
        
    except ImportError:
        logger.error("Transformers package not installed. Install with: pip install transformers")
        # Fall back to simpler extraction
        return extract_mindmap_from_text(text, title)
        
    except Exception as e:
        logger.error(f"Error generating mind map with Hugging Face: {e}")
        # Fall back to simpler extraction
        return extract_mindmap_from_text(text, title)

def _create_mindmap_prompt(
    text: str,
    title: Optional[str] = None
) -> str:
    """
    Create a prompt for mind map generation.
    
    Args:
        text (str): The text to generate a mind map from
        title (str, optional): Title for the mind map
        
    Returns:
        str: The generated prompt
    """
    # Start with the basic instruction
    prompt = "Create a Mermaid mind map from the following text"
    if title:
        prompt += f" with the root node titled '{title}'"
    prompt += ". Extract the main concepts and their relationships, organizing them hierarchically."
    
    prompt += "\n\nUse the following Mermaid syntax:\n```mermaid\nmindmap\n  root((Main Topic))\n    A[Topic A]\n      A1(Subtopic A1)\n      A2(Subtopic A2)\n    B[Topic B]\n      B1(Subtopic B1)\n      B2(Subtopic B2)\n```"
    
    prompt += "\n\nMake sure to:\n- Identify the main concepts and their subconcepts\n- Organize them in a hierarchical structure\n- Use appropriate node shapes\n- Keep the mind map focused on the main concepts\n- Use proper Mermaid mindmap syntax"
    
    # Add the text to generate a mind map from
    prompt += "\n\nText to convert to mind map:\n\n" + text
    
    # Add final instruction
    prompt += "\n\nPlease provide only the mind map code in a code block."
    
    return prompt