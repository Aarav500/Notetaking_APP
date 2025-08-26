"""
Multimodal Reasoning Tasks module for AI Note System.
Handles generating connections and explanations from multiple input types (diagrams, research papers, questions).
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime
import base64

# Setup logging
logger = logging.getLogger("ai_note_system.processing.multimodal_reasoning")

def process_multimodal_inputs(
    inputs: List[str],
    input_types: Optional[List[str]] = None,
    question: Optional[str] = None,
    output_dir: Optional[str] = None,
    generate_connections: bool = True,
    generate_explanation: bool = True,
    generate_qa: bool = False,
    export_format: Optional[str] = None,
    export_path: Optional[str] = None,
    model: str = "gpt-4-vision-preview"
) -> Dict[str, Any]:
    """
    Process multiple inputs together to generate connections, explanations, and Q&A.
    
    Args:
        inputs (List[str]): List of input file paths
        input_types (List[str], optional): List of input types (diagram, paper, text, image)
        question (str, optional): Question to answer using the inputs
        output_dir (str, optional): Directory to save output files
        generate_connections (bool): Whether to generate connections between inputs
        generate_explanation (bool): Whether to generate explanations
        generate_qa (bool): Whether to generate Q&A from inputs
        export_format (str, optional): Format to export results (markdown, json)
        export_path (str, optional): Path to save exported results
        model (str): LLM model to use for processing
        
    Returns:
        Dict[str, Any]: Processing results
    """
    logger.info(f"Processing {len(inputs)} multimodal inputs")
    
    # Create output directory if not provided
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(tempfile.gettempdir(), f"multimodal_reasoning_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Determine input types if not provided
    if not input_types:
        input_types = [_determine_input_type(input_path) for input_path in inputs]
    
    # Validate inputs
    if len(inputs) != len(input_types):
        error_msg = f"Number of inputs ({len(inputs)}) does not match number of input types ({len(input_types)})"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    
    # Process each input
    processed_inputs = []
    for i, (input_path, input_type) in enumerate(zip(inputs, input_types)):
        processed_input = _process_single_input(input_path, input_type)
        if processed_input:
            processed_inputs.append(processed_input)
        else:
            logger.warning(f"Failed to process input {i+1}: {input_path}")
    
    if not processed_inputs:
        error_msg = "Failed to process any inputs"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }
    
    # Initialize result
    result = {
        "status": "success",
        "message": "Multimodal reasoning completed",
        "inputs": processed_inputs
    }
    
    # Generate connections if requested
    if generate_connections:
        logger.info("Generating connections between inputs")
        connections = generate_input_connections(processed_inputs, model)
        result["connections"] = connections
        
        # Save connections to file
        connections_path = os.path.join(output_dir, "connections.json")
        with open(connections_path, "w", encoding="utf-8") as f:
            json.dump(connections, f, ensure_ascii=False, indent=2)
        
        result["connections_path"] = connections_path
    
    # Generate explanation if requested
    if generate_explanation:
        logger.info("Generating explanation from inputs")
        explanation = generate_multimodal_explanation(processed_inputs, model)
        result["explanation"] = explanation
        
        # Save explanation to file
        explanation_path = os.path.join(output_dir, "explanation.txt")
        with open(explanation_path, "w", encoding="utf-8") as f:
            f.write(explanation)
        
        result["explanation_path"] = explanation_path
    
    # Generate Q&A if requested
    if generate_qa:
        logger.info("Generating Q&A from inputs")
        qa_pairs = generate_multimodal_qa(processed_inputs, question, model)
        result["qa_pairs"] = qa_pairs
        
        # Save Q&A to file
        qa_path = os.path.join(output_dir, "qa_pairs.json")
        with open(qa_path, "w", encoding="utf-8") as f:
            json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
        
        result["qa_path"] = qa_path
    
    # Export results if requested
    if export_format and export_path:
        logger.info(f"Exporting results to {export_format}: {export_path}")
        export_result = export_multimodal_results(result, export_format, export_path)
        result["export_result"] = export_result
    
    return result

def _determine_input_type(input_path: str) -> str:
    """
    Determine the type of input based on file extension.
    
    Args:
        input_path (str): Path to the input file
        
    Returns:
        str: Input type (diagram, paper, text, image)
    """
    # Get file extension
    _, ext = os.path.splitext(input_path.lower())
    
    # Determine input type based on extension
    if ext in ['.pdf']:
        return "paper"
    elif ext in ['.txt', '.md', '.doc', '.docx']:
        return "text"
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return "image"
    elif ext in ['.svg', '.drawio', '.vsdx', '.dia']:
        return "diagram"
    else:
        # Default to image for unknown extensions
        return "image"

def _process_single_input(input_path: str, input_type: str) -> Optional[Dict[str, Any]]:
    """
    Process a single input file.
    
    Args:
        input_path (str): Path to the input file
        input_type (str): Type of input (diagram, paper, text, image)
        
    Returns:
        Optional[Dict[str, Any]]: Processed input or None if processing failed
    """
    logger.info(f"Processing {input_type}: {input_path}")
    
    try:
        # Check if file exists
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return None
        
        # Initialize result
        result = {
            "path": input_path,
            "type": input_type,
            "filename": os.path.basename(input_path)
        }
        
        # Process based on input type
        if input_type == "text":
            # Read text file
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            result["content"] = content
            result["content_type"] = "text"
        
        elif input_type == "paper":
            # Extract text from PDF
            try:
                import fitz  # PyMuPDF
                
                # Open PDF
                pdf = fitz.open(input_path)
                
                # Extract text
                content = ""
                for page_num in range(len(pdf)):
                    page = pdf[page_num]
                    content += page.get_text()
                
                # Extract metadata
                metadata = pdf.metadata
                
                result["content"] = content
                result["content_type"] = "text"
                result["metadata"] = {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "keywords": metadata.get("keywords", ""),
                    "page_count": len(pdf)
                }
                
            except ImportError:
                logger.warning("PyMuPDF not installed, using basic text extraction")
                result["content"] = f"PDF file: {input_path}"
                result["content_type"] = "text"
        
        elif input_type in ["image", "diagram"]:
            # Read image file as base64
            with open(input_path, "rb") as f:
                image_data = f.read()
            
            # Convert to base64
            base64_image = base64.b64encode(image_data).decode("utf-8")
            
            result["content"] = base64_image
            result["content_type"] = "image"
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing input {input_path}: {e}")
        return None

def generate_input_connections(
    processed_inputs: List[Dict[str, Any]],
    model: str = "gpt-4-vision-preview"
) -> List[Dict[str, Any]]:
    """
    Generate connections between inputs.
    
    Args:
        processed_inputs (List[Dict[str, Any]]): List of processed inputs
        model (str): LLM model to use
        
    Returns:
        List[Dict[str, Any]]: List of connections between inputs
    """
    logger.info("Generating connections between inputs")
    
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Check if we have at least 2 inputs
    if len(processed_inputs) < 2:
        logger.warning("Need at least 2 inputs to generate connections")
        return []
    
    # Prepare inputs for the model
    model_inputs = []
    
    for input_data in processed_inputs:
        if input_data["content_type"] == "text":
            # Add text content
            model_inputs.append({
                "type": "text",
                "text": f"Input ({input_data['type']}): {input_data['filename']}\n\n{input_data['content'][:2000]}..."
            })
        elif input_data["content_type"] == "image":
            # Add image content
            model_inputs.append({
                "type": "text",
                "text": f"Input ({input_data['type']}): {input_data['filename']}"
            })
            model_inputs.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{input_data['content']}"
                }
            })
    
    # Create prompt
    prompt = """
    Analyze the provided inputs and identify meaningful connections between them.
    For each connection, explain:
    1. What concepts or elements are connected
    2. How they are related
    3. Why this connection is significant
    
    Format your response as a JSON array of connection objects with the following fields:
    - "input1": Index of the first input (0-based)
    - "input2": Index of the second input (0-based)
    - "connection_type": Type of connection (e.g., "conceptual", "visual", "complementary", "contradictory")
    - "description": Detailed description of the connection
    - "significance": Why this connection is important or insightful
    
    Focus on the most meaningful and non-obvious connections.
    """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai", model=model)
        
        # Generate connections
        if model.endswith("-vision"):
            # Use vision model
            response = llm.generate_chat_response(
                messages=[
                    {"role": "user", "content": model_inputs + [{"type": "text", "text": prompt}]}
                ],
                response_format={"type": "json_object"}
            )
        else:
            # Use text-only model
            text_inputs = "\n\n".join([
                input_data["content"][:1000] + "..." 
                for input_data in processed_inputs 
                if input_data["content_type"] == "text"
            ])
            
            text_prompt = f"""
            Analyze the following inputs and identify meaningful connections between them.
            
            {text_inputs}
            
            {prompt}
            """
            
            response = llm.generate_text(text_prompt)
        
        # Parse response
        try:
            connections = json.loads(response)
            if isinstance(connections, dict) and "connections" in connections:
                connections = connections["connections"]
            
            # Validate connections
            valid_connections = []
            for conn in connections:
                if isinstance(conn, dict) and "input1" in conn and "input2" in conn:
                    valid_connections.append(conn)
            
            return valid_connections
        except json.JSONDecodeError:
            logger.error(f"Error parsing connections response: {response}")
            return []
        
    except Exception as e:
        logger.error(f"Error generating connections: {e}")
        return []

def generate_multimodal_explanation(
    processed_inputs: List[Dict[str, Any]],
    model: str = "gpt-4-vision-preview"
) -> str:
    """
    Generate an explanation from multiple inputs.
    
    Args:
        processed_inputs (List[Dict[str, Any]]): List of processed inputs
        model (str): LLM model to use
        
    Returns:
        str: Generated explanation
    """
    logger.info("Generating explanation from inputs")
    
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Prepare inputs for the model
    model_inputs = []
    
    for input_data in processed_inputs:
        if input_data["content_type"] == "text":
            # Add text content
            model_inputs.append({
                "type": "text",
                "text": f"Input ({input_data['type']}): {input_data['filename']}\n\n{input_data['content'][:2000]}..."
            })
        elif input_data["content_type"] == "image":
            # Add image content
            model_inputs.append({
                "type": "text",
                "text": f"Input ({input_data['type']}): {input_data['filename']}"
            })
            model_inputs.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{input_data['content']}"
                }
            })
    
    # Create prompt
    prompt = """
    Generate a comprehensive explanation that integrates information from all the provided inputs.
    Your explanation should:
    1. Synthesize the key concepts and information from each input
    2. Explain how these concepts relate to each other
    3. Provide a coherent narrative that helps understand the overall topic
    4. Highlight any important insights that emerge from considering all inputs together
    
    Your explanation should be educational, clear, and insightful, making connections that might not be obvious when looking at each input individually.
    """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai", model=model)
        
        # Generate explanation
        if model.endswith("-vision"):
            # Use vision model
            response = llm.generate_chat_response(
                messages=[
                    {"role": "user", "content": model_inputs + [{"type": "text", "text": prompt}]}
                ]
            )
        else:
            # Use text-only model
            text_inputs = "\n\n".join([
                input_data["content"][:1000] + "..." 
                for input_data in processed_inputs 
                if input_data["content_type"] == "text"
            ])
            
            text_prompt = f"""
            Generate a comprehensive explanation that integrates information from all the following inputs.
            
            {text_inputs}
            
            {prompt}
            """
            
            response = llm.generate_text(text_prompt)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        return f"Error generating explanation: {e}"

def generate_multimodal_qa(
    processed_inputs: List[Dict[str, Any]],
    question: Optional[str] = None,
    model: str = "gpt-4-vision-preview"
) -> List[Dict[str, str]]:
    """
    Generate Q&A pairs from multiple inputs.
    
    Args:
        processed_inputs (List[Dict[str, Any]]): List of processed inputs
        question (str, optional): Specific question to answer
        model (str): LLM model to use
        
    Returns:
        List[Dict[str, str]]: List of Q&A pairs
    """
    logger.info("Generating Q&A from inputs")
    
    from ai_note_system.api.llm_interface import get_llm_interface
    
    # Prepare inputs for the model
    model_inputs = []
    
    for input_data in processed_inputs:
        if input_data["content_type"] == "text":
            # Add text content
            model_inputs.append({
                "type": "text",
                "text": f"Input ({input_data['type']}): {input_data['filename']}\n\n{input_data['content'][:2000]}..."
            })
        elif input_data["content_type"] == "image":
            # Add image content
            model_inputs.append({
                "type": "text",
                "text": f"Input ({input_data['type']}): {input_data['filename']}"
            })
            model_inputs.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{input_data['content']}"
                }
            })
    
    # Create prompt
    if question:
        # Answer specific question
        prompt = f"""
        Answer the following question based on the provided inputs:
        
        Question: {question}
        
        Your answer should:
        1. Be comprehensive and accurate
        2. Draw information from all relevant inputs
        3. Explain your reasoning clearly
        4. Cite specific inputs where appropriate
        
        Format your response as a JSON object with "question" and "answer" fields.
        """
    else:
        # Generate Q&A pairs
        prompt = """
        Generate a set of educational question-answer pairs based on the provided inputs.
        
        For each Q&A pair:
        1. Create an insightful question that requires understanding multiple inputs
        2. Provide a comprehensive answer that draws from the relevant inputs
        3. Ensure the question tests understanding of important concepts
        
        Format your response as a JSON array of objects, each with "question" and "answer" fields.
        Generate at least 5 Q&A pairs that cover the most important concepts from the inputs.
        """
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai", model=model)
        
        # Generate Q&A
        if model.endswith("-vision"):
            # Use vision model
            response = llm.generate_chat_response(
                messages=[
                    {"role": "user", "content": model_inputs + [{"type": "text", "text": prompt}]}
                ],
                response_format={"type": "json_object"}
            )
        else:
            # Use text-only model
            text_inputs = "\n\n".join([
                input_data["content"][:1000] + "..." 
                for input_data in processed_inputs 
                if input_data["content_type"] == "text"
            ])
            
            text_prompt = f"""
            {prompt}
            
            Inputs:
            {text_inputs}
            """
            
            response = llm.generate_text(text_prompt)
        
        # Parse response
        try:
            qa_data = json.loads(response)
            
            # Handle both single Q&A and multiple Q&A formats
            if isinstance(qa_data, dict) and "question" in qa_data and "answer" in qa_data:
                # Single Q&A
                return [qa_data]
            elif isinstance(qa_data, list):
                # Multiple Q&A pairs
                return qa_data
            elif isinstance(qa_data, dict) and "qa_pairs" in qa_data:
                # Q&A pairs in a nested field
                return qa_data["qa_pairs"]
            else:
                logger.error(f"Unexpected Q&A response format: {qa_data}")
                return []
                
        except json.JSONDecodeError:
            logger.error(f"Error parsing Q&A response: {response}")
            return []
        
    except Exception as e:
        logger.error(f"Error generating Q&A: {e}")
        return []

def export_multimodal_results(
    result: Dict[str, Any],
    export_format: str,
    export_path: str
) -> Dict[str, Any]:
    """
    Export multimodal reasoning results to the specified format.
    
    Args:
        result (Dict[str, Any]): Processing results
        export_format (str): Format to export (markdown, json)
        export_path (str): Path to save exported results
        
    Returns:
        Dict[str, Any]: Export result
    """
    logger.info(f"Exporting multimodal reasoning results to {export_format}: {export_path}")
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(export_path)), exist_ok=True)
        
        if export_format.lower() == "json":
            # Export as JSON
            with open(export_path, "w", encoding="utf-8") as f:
                # Create a copy of the result without the base64 image content to reduce file size
                export_result = result.copy()
                
                # Remove base64 content from inputs
                if "inputs" in export_result:
                    for input_data in export_result["inputs"]:
                        if input_data.get("content_type") == "image":
                            input_data["content"] = "[BASE64_IMAGE_DATA_REMOVED]"
                
                json.dump(export_result, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "message": f"Results exported to JSON: {export_path}",
                "export_path": export_path
            }
        
        elif export_format.lower() == "markdown":
            # Export as Markdown
            md_content = []
            
            # Add title
            md_content.append("# Multimodal Reasoning Results")
            md_content.append("")
            
            # Add inputs
            md_content.append("## Inputs")
            md_content.append("")
            
            inputs = result.get("inputs", [])
            for i, input_data in enumerate(inputs):
                md_content.append(f"### Input {i+1}: {input_data.get('filename')}")
                md_content.append("")
                md_content.append(f"- **Type:** {input_data.get('type')}")
                md_content.append(f"- **Path:** {input_data.get('path')}")
                md_content.append("")
                
                # Add metadata for papers
                if input_data.get("type") == "paper" and "metadata" in input_data:
                    metadata = input_data["metadata"]
                    md_content.append("#### Metadata")
                    md_content.append("")
                    md_content.append(f"- **Title:** {metadata.get('title', 'N/A')}")
                    md_content.append(f"- **Author:** {metadata.get('author', 'N/A')}")
                    md_content.append(f"- **Subject:** {metadata.get('subject', 'N/A')}")
                    md_content.append(f"- **Pages:** {metadata.get('page_count', 'N/A')}")
                    md_content.append("")
            
            # Add connections
            connections = result.get("connections", [])
            if connections:
                md_content.append("## Connections")
                md_content.append("")
                
                for i, connection in enumerate(connections):
                    input1_idx = connection.get("input1", 0)
                    input2_idx = connection.get("input2", 0)
                    
                    input1_name = inputs[input1_idx]["filename"] if input1_idx < len(inputs) else f"Input {input1_idx+1}"
                    input2_name = inputs[input2_idx]["filename"] if input2_idx < len(inputs) else f"Input {input2_idx+1}"
                    
                    md_content.append(f"### Connection {i+1}: {input1_name} ↔ {input2_name}")
                    md_content.append("")
                    md_content.append(f"- **Type:** {connection.get('connection_type', 'N/A')}")
                    md_content.append("")
                    md_content.append(f"**Description:** {connection.get('description', '')}")
                    md_content.append("")
                    md_content.append(f"**Significance:** {connection.get('significance', '')}")
                    md_content.append("")
            
            # Add explanation
            explanation = result.get("explanation", "")
            if explanation:
                md_content.append("## Explanation")
                md_content.append("")
                md_content.append(explanation)
                md_content.append("")
            
            # Add Q&A
            qa_pairs = result.get("qa_pairs", [])
            if qa_pairs:
                md_content.append("## Q&A")
                md_content.append("")
                
                for i, qa in enumerate(qa_pairs):
                    md_content.append(f"### Q{i+1}: {qa.get('question', '')}")
                    md_content.append("")
                    md_content.append(qa.get("answer", ""))
                    md_content.append("")
            
            # Write Markdown content to file
            with open(export_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_content))
            
            return {
                "status": "success",
                "message": f"Results exported to Markdown: {export_path}",
                "export_path": export_path
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unsupported export format: {export_format}",
                "export_path": None
            }
    
    except Exception as e:
        logger.error(f"Error exporting multimodal reasoning results: {e}")
        return {
            "status": "error",
            "message": f"Error exporting multimodal reasoning results: {e}",
            "export_path": None
        }