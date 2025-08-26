"""
Flowchart generator module for AI Note System.
Generates flowcharts from text using Mermaid or Graphviz.
"""

import os
import logging
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.flowchart_gen")

def generate_flowchart(
    text: str,
    engine: str = "mermaid",
    output_format: str = "png",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    direction: str = "TD",
    theme: str = "default",
    include_code: bool = True
) -> Dict[str, Any]:
    """
    Generate a flowchart from text.
    
    Args:
        text (str): The text to generate a flowchart from
        engine (str): The engine to use for generation (mermaid or graphviz)
        output_format (str): The output format (png, svg, pdf)
        output_path (str, optional): Path to save the output file
        title (str, optional): Title for the flowchart
        direction (str): Direction of the flowchart (TD=top-down, LR=left-right)
        theme (str): Theme for the flowchart
        include_code (bool): Whether to include the generated code in the result
        
    Returns:
        Dict[str, Any]: Dictionary containing the flowchart information
    """
    logger.info(f"Generating flowchart using {engine}")
    
    if engine.lower() == "mermaid":
        return generate_mermaid_flowchart(
            text, output_format, output_path, title, direction, theme, include_code
        )
    elif engine.lower() == "graphviz":
        return generate_graphviz_flowchart(
            text, output_format, output_path, title, direction, theme, include_code
        )
    else:
        logger.error(f"Unsupported engine: {engine}")
        return {"error": f"Unsupported engine: {engine}"}

def generate_mermaid_flowchart(
    text: str,
    output_format: str = "png",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    direction: str = "TD",
    theme: str = "default",
    include_code: bool = True
) -> Dict[str, Any]:
    """
    Generate a flowchart using Mermaid.
    
    Args:
        text (str): The text to generate a flowchart from
        output_format (str): The output format (png, svg, pdf)
        output_path (str, optional): Path to save the output file
        title (str, optional): Title for the flowchart
        direction (str): Direction of the flowchart (TD=top-down, LR=left-right)
        theme (str): Theme for the flowchart
        include_code (bool): Whether to include the generated code in the result
        
    Returns:
        Dict[str, Any]: Dictionary containing the flowchart information
    """
    logger.info("Generating Mermaid flowchart")
    
    # Generate Mermaid code from text
    mermaid_code = extract_flowchart_from_text(text, title, direction)
    
    # Create result dictionary
    result = {
        "engine": "mermaid",
        "title": title or "Flowchart",
        "format": output_format
    }
    
    if include_code:
        result["code"] = mermaid_code
    
    # If output path is provided, render the flowchart
    if output_path:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save Mermaid code to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", delete=False) as f:
                f.write(mermaid_code)
                temp_file = f.name
            
            # Use mmdc (Mermaid CLI) to render the flowchart
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
            logger.debug(f"Flowchart saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error rendering Mermaid flowchart: {e}")
            result["error"] = f"Error rendering Mermaid flowchart: {e}"
    
    return result

def generate_graphviz_flowchart(
    text: str,
    output_format: str = "png",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    direction: str = "TD",
    theme: str = "default",
    include_code: bool = True
) -> Dict[str, Any]:
    """
    Generate a flowchart using Graphviz.
    
    Args:
        text (str): The text to generate a flowchart from
        output_format (str): The output format (png, svg, pdf)
        output_path (str, optional): Path to save the output file
        title (str, optional): Title for the flowchart
        direction (str): Direction of the flowchart (TD=top-down, LR=left-right)
        theme (str): Theme for the flowchart
        include_code (bool): Whether to include the generated code in the result
        
    Returns:
        Dict[str, Any]: Dictionary containing the flowchart information
    """
    logger.info("Generating Graphviz flowchart")
    
    # Convert direction to Graphviz format
    graphviz_direction = "TB" if direction == "TD" else direction
    
    # Generate Graphviz DOT code from text
    dot_code = extract_dot_from_text(text, title, graphviz_direction)
    
    # Create result dictionary
    result = {
        "engine": "graphviz",
        "title": title or "Flowchart",
        "format": output_format
    }
    
    if include_code:
        result["code"] = dot_code
    
    # If output path is provided, render the flowchart
    if output_path:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save DOT code to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
                f.write(dot_code)
                temp_file = f.name
            
            # Use dot to render the flowchart
            cmd = [
                "dot",
                "-T" + output_format,
                "-o", output_path,
                temp_file
            ]
            
            subprocess.run(cmd, check=True)
            
            # Clean up temporary file
            os.unlink(temp_file)
            
            result["output_path"] = output_path
            logger.debug(f"Flowchart saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error rendering Graphviz flowchart: {e}")
            result["error"] = f"Error rendering Graphviz flowchart: {e}"
    
    return result

def extract_flowchart_from_text(
    text: str,
    title: Optional[str] = None,
    direction: str = "TD"
) -> str:
    """
    Extract a flowchart from text using AI.
    
    Args:
        text (str): The text to extract a flowchart from
        title (str, optional): Title for the flowchart
        direction (str): Direction of the flowchart (TD=top-down, LR=left-right)
        
    Returns:
        str: Mermaid flowchart code
    """
    # This is a simplified version that extracts steps and creates a linear flowchart
    # In a real implementation, this would use an LLM to generate a more complex flowchart
    
    # Extract steps from text (simple implementation)
    lines = text.split("\n")
    steps = []
    
    for line in lines:
        line = line.strip()
        if line and (line.startswith("- ") or line.startswith("* ") or 
                    (line[0].isdigit() and line[1:3] in [". ", ") "])):
            # Remove leading markers
            step = line[2:] if line.startswith(("- ", "* ")) else line[line.index(" ")+1:]
            steps.append(step)
    
    # If no steps were found, try to extract sentences
    if not steps:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        steps = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Limit to 10 steps for readability
        steps = steps[:10]
    
    # Generate Mermaid code
    mermaid_code = [f"flowchart {direction}"]
    
    if title:
        mermaid_code.append(f"    title {title}")
    
    # Add nodes and connections
    for i, step in enumerate(steps):
        node_id = f"step{i+1}"
        # Escape quotes in step text
        step_text = step.replace('"', '\\"')
        mermaid_code.append(f'    {node_id}["{step_text}"]')
    
    # Add connections between nodes
    for i in range(len(steps) - 1):
        mermaid_code.append(f"    step{i+1} --> step{i+2}")
    
    return "\n".join(mermaid_code)

def extract_dot_from_text(
    text: str,
    title: Optional[str] = None,
    direction: str = "TB"
) -> str:
    """
    Extract a DOT graph from text using AI.
    
    Args:
        text (str): The text to extract a graph from
        title (str, optional): Title for the graph
        direction (str): Direction of the graph (TB=top-bottom, LR=left-right)
        
    Returns:
        str: Graphviz DOT code
    """
    # This is a simplified version that extracts steps and creates a linear flowchart
    # In a real implementation, this would use an LLM to generate a more complex flowchart
    
    # Extract steps from text (simple implementation)
    lines = text.split("\n")
    steps = []
    
    for line in lines:
        line = line.strip()
        if line and (line.startswith("- ") or line.startswith("* ") or 
                    (line[0].isdigit() and line[1:3] in [". ", ") "])):
            # Remove leading markers
            step = line[2:] if line.startswith(("- ", "* ")) else line[line.index(" ")+1:]
            steps.append(step)
    
    # If no steps were found, try to extract sentences
    if not steps:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        steps = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Limit to 10 steps for readability
        steps = steps[:10]
    
    # Generate DOT code
    dot_code = ["digraph G {"]
    
    # Set graph direction
    dot_code.append(f"    rankdir={direction};")
    
    # Add title as a label if provided
    if title:
        dot_code.append(f'    labelloc="t";')
        dot_code.append(f'    label="{title}";')
    
    # Add nodes
    for i, step in enumerate(steps):
        node_id = f"step{i+1}"
        # Escape quotes in step text
        step_text = step.replace('"', '\\"')
        dot_code.append(f'    {node_id} [shape=box, label="{step_text}"];')
    
    # Add connections between nodes
    for i in range(len(steps) - 1):
        dot_code.append(f"    step{i+1} -> step{i+2};")
    
    dot_code.append("}")
    
    return "\n".join(dot_code)

def generate_flowchart_from_llm(
    text: str,
    model: str = "gpt-4",
    engine: str = "mermaid",
    direction: str = "TD",
    title: Optional[str] = None
) -> str:
    """
    Generate a flowchart from text using an LLM.
    
    Args:
        text (str): The text to generate a flowchart from
        model (str): The LLM model to use
        engine (str): The flowchart engine (mermaid or graphviz)
        direction (str): Direction of the flowchart
        title (str, optional): Title for the flowchart
        
    Returns:
        str: Flowchart code (Mermaid or DOT)
    """
    logger.info(f"Generating flowchart using LLM model: {model}")
    
    # Determine which LLM to use based on the model name
    if model.startswith("gpt-"):
        flowchart_code = _generate_flowchart_with_openai(text, model, engine, direction, title)
    elif model.startswith("mistral-") or model.startswith("llama-") or model.startswith("phi-"):
        flowchart_code = _generate_flowchart_with_huggingface(text, model, engine, direction, title)
    else:
        logger.warning(f"Unsupported model: {model}, falling back to simple extraction")
        # Fall back to simpler extraction methods
        if engine.lower() == "mermaid":
            flowchart_code = extract_flowchart_from_text(text, title, direction)
        else:
            flowchart_code = extract_dot_from_text(text, title, direction)
    
    return flowchart_code

def _generate_flowchart_with_openai(
    text: str,
    model: str = "gpt-4",
    engine: str = "mermaid",
    direction: str = "TD",
    title: Optional[str] = None
) -> str:
    """
    Generate a flowchart from text using OpenAI's API.
    
    Args:
        text (str): The text to generate a flowchart from
        model (str): The OpenAI model to use
        engine (str): The flowchart engine (mermaid or graphviz)
        direction (str): Direction of the flowchart
        title (str, optional): Title for the flowchart
        
    Returns:
        str: Flowchart code (Mermaid or DOT)
    """
    try:
        import openai
        
        logger.debug(f"Using OpenAI {model} for flowchart generation")
        
        # Prepare the prompt
        prompt = _create_flowchart_prompt(text, engine, direction, title)
        
        # Call the OpenAI API
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert at creating flowcharts from text. Your task is to analyze the text and create a clear, logical flowchart that represents the process or concept described."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        
        # Extract the flowchart code from the response
        content = response.choices[0].message.content.strip()
        
        # Extract code block if present
        import re
        if engine.lower() == "mermaid":
            code_match = re.search(r'```(?:mermaid)?\s*(flowchart[\s\S]*?)```', content, re.IGNORECASE)
        else:  # graphviz
            code_match = re.search(r'```(?:dot|graphviz)?\s*(digraph[\s\S]*?)```', content, re.IGNORECASE)
        
        if code_match:
            flowchart_code = code_match.group(1).strip()
        else:
            # If no code block is found, use the entire response
            flowchart_code = content
        
        logger.debug("Successfully generated flowchart with OpenAI")
        return flowchart_code
        
    except ImportError:
        logger.error("OpenAI package not installed. Install with: pip install openai")
        # Fall back to simpler extraction
        if engine.lower() == "mermaid":
            return extract_flowchart_from_text(text, title, direction)
        else:
            return extract_dot_from_text(text, title, direction)
        
    except Exception as e:
        logger.error(f"Error generating flowchart with OpenAI: {e}")
        # Fall back to simpler extraction
        if engine.lower() == "mermaid":
            return extract_flowchart_from_text(text, title, direction)
        else:
            return extract_dot_from_text(text, title, direction)

def _generate_flowchart_with_huggingface(
    text: str,
    model: str = "mistral-7b-instruct",
    engine: str = "mermaid",
    direction: str = "TD",
    title: Optional[str] = None
) -> str:
    """
    Generate a flowchart from text using Hugging Face models.
    
    Args:
        text (str): The text to generate a flowchart from
        model (str): The Hugging Face model to use
        engine (str): The flowchart engine (mermaid or graphviz)
        direction (str): Direction of the flowchart
        title (str, optional): Title for the flowchart
        
    Returns:
        str: Flowchart code (Mermaid or DOT)
    """
    try:
        from transformers import pipeline
        
        logger.debug(f"Using Hugging Face {model} for flowchart generation")
        
        # Prepare the prompt
        prompt = _create_flowchart_prompt(text, engine, direction, title)
        
        # Initialize the pipeline
        pipe = pipeline(
            "text-generation",
            model=model,
            device_map="auto"
        )
        
        # Generate the flowchart
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
        if engine.lower() == "mermaid":
            code_match = re.search(r'```(?:mermaid)?\s*(flowchart[\s\S]*?)```', content, re.IGNORECASE)
        else:  # graphviz
            code_match = re.search(r'```(?:dot|graphviz)?\s*(digraph[\s\S]*?)```', content, re.IGNORECASE)
        
        if code_match:
            flowchart_code = code_match.group(1).strip()
        else:
            # If no code block is found, try to extract the relevant part
            if engine.lower() == "mermaid":
                flowchart_match = re.search(r'(flowchart\s+[A-Z]+[\s\S]*)', content)
                if flowchart_match:
                    flowchart_code = flowchart_match.group(1).strip()
                else:
                    # Fall back to simpler extraction
                    flowchart_code = extract_flowchart_from_text(text, title, direction)
            else:  # graphviz
                digraph_match = re.search(r'(digraph\s+\w+\s*\{[\s\S]*\})', content)
                if digraph_match:
                    flowchart_code = digraph_match.group(1).strip()
                else:
                    # Fall back to simpler extraction
                    flowchart_code = extract_dot_from_text(text, title, direction)
        
        logger.debug("Successfully generated flowchart with Hugging Face")
        return flowchart_code
        
    except ImportError:
        logger.error("Transformers package not installed. Install with: pip install transformers")
        # Fall back to simpler extraction
        if engine.lower() == "mermaid":
            return extract_flowchart_from_text(text, title, direction)
        else:
            return extract_dot_from_text(text, title, direction)
        
    except Exception as e:
        logger.error(f"Error generating flowchart with Hugging Face: {e}")
        # Fall back to simpler extraction
        if engine.lower() == "mermaid":
            return extract_flowchart_from_text(text, title, direction)
        else:
            return extract_dot_from_text(text, title, direction)

def _create_flowchart_prompt(
    text: str,
    engine: str = "mermaid",
    direction: str = "TD",
    title: Optional[str] = None
) -> str:
    """
    Create a prompt for flowchart generation.
    
    Args:
        text (str): The text to generate a flowchart from
        engine (str): The flowchart engine (mermaid or graphviz)
        direction (str): Direction of the flowchart
        title (str, optional): Title for the flowchart
        
    Returns:
        str: The generated prompt
    """
    # Start with the basic instruction
    if engine.lower() == "mermaid":
        prompt = f"Create a Mermaid flowchart from the following text. The flowchart should be in {direction} direction"
        if title:
            prompt += f" with the title '{title}'"
        prompt += ". Extract the key steps, decisions, and processes from the text and represent them in a logical flow."
        prompt += "\n\nUse the following Mermaid syntax:\n```mermaid\nflowchart TD\n    A[Start] --> B{Decision}\n    B -->|Yes| C[Process]\n    B -->|No| D[End]\n```"
        prompt += "\n\nMake sure to:\n- Use appropriate node shapes ([] for process, {} for decision, () for input/output)\n- Label connections clearly\n- Keep the flowchart focused on the main process\n- Include only the most important steps\n- Use proper Mermaid syntax"
    else:  # graphviz
        prompt = f"Create a Graphviz DOT flowchart from the following text. The flowchart should be in {direction} direction"
        if title:
            prompt += f" with the title '{title}'"
        prompt += ". Extract the key steps, decisions, and processes from the text and represent them in a logical flow."
        prompt += "\n\nUse the following DOT syntax:\n```dot\ndigraph G {\n    rankdir=TB;\n    A [label=\"Start\", shape=box];\n    B [label=\"Decision\", shape=diamond];\n    C [label=\"Process\", shape=box];\n    D [label=\"End\", shape=box];\n    A -> B;\n    B -> C [label=\"Yes\"];\n    B -> D [label=\"No\"];\n}\n```"
        prompt += "\n\nMake sure to:\n- Use appropriate node shapes (box for process, diamond for decision)\n- Label connections clearly\n- Keep the flowchart focused on the main process\n- Include only the most important steps\n- Use proper DOT syntax"
    
    # Add the text to generate a flowchart from
    prompt += "\n\nText to convert to flowchart:\n\n" + text
    
    # Add final instruction
    prompt += "\n\nPlease provide only the flowchart code in a code block."
    
    return prompt