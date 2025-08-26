"""
Math formula processor module for AI Note System.
Provides OCR for math formulas, semantic linking, and practice problem generation.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import re
import base64
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.processing.math_formula_processor")

def process_math_formulas(
    content: Dict[str, Any],
    ocr_math: bool = True,
    link_explanations: bool = True,
    generate_practice: bool = True
) -> Dict[str, Any]:
    """
    Process math formulas in content.
    
    Args:
        content (Dict[str, Any]): The content to process
        ocr_math (bool): Whether to perform OCR on math formulas
        link_explanations (bool): Whether to link formulas to explanations
        generate_practice (bool): Whether to generate practice problems
        
    Returns:
        Dict[str, Any]: Processed content with math formulas
    """
    logger.info("Processing math formulas in content")
    
    # Create a copy of the content to avoid modifying the original
    processed_content = content.copy()
    
    # Extract images from content
    images = extract_images_from_content(content)
    
    # Detect math formulas in images
    if ocr_math and images:
        formulas = []
        
        for image in images:
            image_path = image.get("path")
            if not image_path or not os.path.exists(image_path):
                continue
                
            # Detect math formulas in image
            detected_formulas = detect_math_formulas(image_path)
            
            if detected_formulas:
                # Add image info to formulas
                for formula in detected_formulas:
                    formula["image_path"] = image_path
                    formula["page"] = image.get("page")
                    formula["timestamp"] = image.get("timestamp")
                    
                formulas.extend(detected_formulas)
        
        # Add formulas to content
        if formulas:
            processed_content["math_formulas"] = formulas
    
    # Link formulas to explanations in text
    if link_explanations and "math_formulas" in processed_content:
        link_formulas_to_explanations(processed_content)
    
    # Generate practice problems
    if generate_practice and "math_formulas" in processed_content:
        practice_problems = generate_practice_problems(processed_content)
        if practice_problems:
            processed_content["math_practice"] = practice_problems
    
    return processed_content

def extract_images_from_content(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract images from content.
    
    Args:
        content (Dict[str, Any]): The content to extract images from
        
    Returns:
        List[Dict[str, Any]]: List of images
    """
    # Get images from content
    images = content.get("images", [])
    
    # If no images in content, try to extract them
    if not images:
        try:
            from ai_note_system.processing.image_extractor import extract_images_from_content
            images = extract_images_from_content(content)
        except ImportError:
            logger.warning("Image extractor module not available")
        except Exception as e:
            logger.error(f"Error extracting images: {str(e)}")
    
    return images

def detect_math_formulas(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect math formulas in an image.
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        List[Dict[str, Any]]: List of detected formulas
    """
    logger.info(f"Detecting math formulas in image: {image_path}")
    
    formulas = []
    
    try:
        # Try different OCR methods in order of preference
        
        # 1. Try Mathpix OCR
        try:
            formulas = detect_math_with_mathpix(image_path)
            if formulas:
                return formulas
        except ImportError:
            logger.warning("Mathpix SDK not installed. Trying next OCR method.")
        except Exception as e:
            logger.warning(f"Error using Mathpix: {str(e)}. Trying next OCR method.")
        
        # 2. Try Azure Computer Vision Read API
        try:
            formulas = detect_math_with_azure(image_path)
            if formulas:
                return formulas
        except ImportError:
            logger.warning("Azure SDK not installed. Trying next OCR method.")
        except Exception as e:
            logger.warning(f"Error using Azure: {str(e)}. Trying next OCR method.")
        
        # 3. Try Tesseract OCR with math formula detection
        try:
            formulas = detect_math_with_tesseract(image_path)
            if formulas:
                return formulas
        except ImportError:
            logger.warning("Tesseract not installed. No more OCR methods to try.")
        except Exception as e:
            logger.warning(f"Error using Tesseract: {str(e)}. No more OCR methods to try.")
        
        # If all methods fail, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error detecting math formulas: {str(e)}")
        return []

def detect_math_with_mathpix(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect math formulas using Mathpix OCR.
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        List[Dict[str, Any]]: List of detected formulas
    """
    import requests
    
    # Get API credentials from environment variables
    app_id = os.environ.get("MATHPIX_APP_ID")
    app_key = os.environ.get("MATHPIX_APP_KEY")
    
    if not app_id or not app_key:
        logger.warning("Mathpix API credentials not found in environment variables")
        return []
    
    # Read image file
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Encode image as base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    
    # Make API request with enhanced options for better math detection
    response = requests.post(
        "https://api.mathpix.com/v3/text",
        json={
            "src": f"data:image/jpeg;base64,{image_base64}",
            "formats": ["text", "latex", "mathml", "data"],
            "data_options": {
                "include_asciimath": True,
                "include_latex": True,
                "include_svg": True,
                "include_table_data": True,
                "include_mathml": True,
                "include_detected_alphabets": True,
                "include_line_data": True,
                "include_word_data": True,
                "include_smiles": True,  # For chemical formulas
                "include_inchi": True,   # For chemical formulas
                "include_tsv": True      # For tabular data
            },
            "ocr_options": {
                "detect_tables": True,
                "detect_formulas": True,
                "detect_diagrams": True,
                "math_inline_delimiters": ["$", "$"],
                "math_display_delimiters": ["$$", "$$"],
                "enable_spell_check": False,  # Disable spell check for math formulas
                "enable_markdown": True,
                "enable_matrix_recognition": True,
                "enable_handwriting_recognition": True
            }
        },
        headers={
            "app_id": app_id,
            "app_key": app_key,
            "Content-type": "application/json"
        }
    )
    
    # Check response
    if response.status_code != 200:
        logger.error(f"Mathpix API error: {response.text}")
        return []
    
    # Parse response
    result = response.json()
    
    # Extract formulas
    formulas = []
    
    # Process latex_styled content
    if "latex_styled" in result:
        latex = result["latex_styled"]
        
        # Extract formulas using regex - improved pattern to catch more formula types
        formula_patterns = [
            r'\$(.*?)\$',                  # Inline math
            r'\$\$(.*?)\$\$',              # Display math
            r'\\\[(.*?)\\\]',              # Display math
            r'\\\((.*?)\\\)',              # Inline math
            r'\\begin\{equation\}(.*?)\\end\{equation\}',  # Equation environment
            r'\\begin\{align\}(.*?)\\end\{align\}',        # Align environment
            r'\\begin\{eqnarray\}(.*?)\\end\{eqnarray\}',  # Eqnarray environment
            r'\\begin\{matrix\}(.*?)\\end\{matrix\}',      # Matrix environment
            r'\\begin\{pmatrix\}(.*?)\\end\{pmatrix\}',    # Parenthesis matrix
            r'\\begin\{bmatrix\}(.*?)\\end\{bmatrix\}'     # Bracket matrix
        ]
        
        for pattern in formula_patterns:
            formula_matches = re.finditer(pattern, latex, re.DOTALL)
            for match in formula_matches:
                formula_text = match.group(1)
                if formula_text and formula_text.strip():
                    formulas.append({
                        "latex": formula_text.strip(),
                        "confidence": result.get("confidence", 0.0),
                        "source": "mathpix",
                        "type": "formula"
                    })
    
    # Process data field for more structured information
    if "data" in result:
        data = result["data"]
        
        # Extract math formulas from data
        if "math_formulas" in data:
            for formula in data.get("math_formulas", []):
                latex = formula.get("latex", "")
                if latex:
                    formulas.append({
                        "latex": latex,
                        "confidence": formula.get("confidence", 0.0),
                        "source": "mathpix",
                        "type": "formula",
                        "position": formula.get("position", {})
                    })
        
        # Extract chemical formulas if available
        if "chemical_formulas" in data:
            for formula in data.get("chemical_formulas", []):
                smiles = formula.get("smiles", "")
                if smiles:
                    formulas.append({
                        "latex": smiles,
                        "confidence": formula.get("confidence", 0.0),
                        "source": "mathpix",
                        "type": "chemical",
                        "smiles": smiles,
                        "inchi": formula.get("inchi", "")
                    })
    
    # Deduplicate formulas
    unique_formulas = []
    seen_latex = set()
    
    for formula in formulas:
        latex = formula.get("latex", "")
        if latex and latex not in seen_latex:
            seen_latex.add(latex)
            unique_formulas.append(formula)
    
    return unique_formulas

def detect_math_with_azure(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect math formulas using Azure Computer Vision Read API.
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        List[Dict[str, Any]]: List of detected formulas
    """
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
    from msrest.authentication import CognitiveServicesCredentials
    
    # Get API credentials from environment variables
    subscription_key = os.environ.get("AZURE_VISION_KEY")
    endpoint = os.environ.get("AZURE_VISION_ENDPOINT")
    
    if not subscription_key or not endpoint:
        logger.warning("Azure Vision API credentials not found in environment variables")
        return []
    
    # Create client
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
    
    # Read image file
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # Call API
    read_response = client.read_in_stream(image_data, raw=True)
    
    # Get operation location (URL with ID)
    operation_location = read_response.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]
    
    # Wait for operation to complete
    import time
    while True:
        read_result = client.get_read_result(operation_id)
        if read_result.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
            break
        time.sleep(1)
    
    # Check result
    if read_result.status != OperationStatusCodes.succeeded:
        logger.error(f"Azure Vision API error: {read_result.status}")
        return []
    
    # Extract text
    text = ""
    for text_result in read_result.analyze_result.read_results:
        for line in text_result.lines:
            text += line.text + "\n"
    
    # Extract formulas using regex
    formulas = []
    
    # Look for common math patterns
    patterns = [
        r'\\frac\{.*?\}\{.*?\}',  # Fractions
        r'\\sum_\{.*?\}\^\{.*?\}',  # Summations
        r'\\int_\{.*?\}\^\{.*?\}',  # Integrals
        r'\\sqrt\{.*?\}',  # Square roots
        r'[a-zA-Z]_\{[a-zA-Z0-9]+\}',  # Subscripts
        r'[a-zA-Z]\^\{[a-zA-Z0-9]+\}',  # Superscripts
        r'\\alpha|\\beta|\\gamma|\\delta|\\epsilon|\\zeta|\\eta|\\theta|\\iota|\\kappa|\\lambda|\\mu|\\nu|\\xi|\\pi|\\rho|\\sigma|\\tau|\\upsilon|\\phi|\\chi|\\psi|\\omega',  # Greek letters
        r'\\sum|\\prod|\\int|\\oint|\\partial|\\nabla|\\infty|\\approx|\\neq|\\geq|\\leq|\\times|\\div|\\pm|\\mp',  # Math symbols
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            formula_text = match.group(0)
            formulas.append({
                "latex": formula_text,
                "confidence": 0.7,  # Arbitrary confidence
                "source": "azure"
            })
    
    return formulas

def detect_math_with_tesseract(image_path: str) -> List[Dict[str, Any]]:
    """
    Detect math formulas using Tesseract OCR.
    
    Args:
        image_path (str): Path to the image
        
    Returns:
        List[Dict[str, Any]]: List of detected formulas
    """
    import pytesseract
    from PIL import Image
    
    # Open image
    image = Image.open(image_path)
    
    # Perform OCR
    text = pytesseract.image_to_string(image, config='--psm 6')
    
    # Extract formulas using regex
    formulas = []
    
    # Look for common math patterns
    patterns = [
        r'[a-zA-Z]=.+',  # Equations
        r'[a-zA-Z]\([a-zA-Z]\)=.+',  # Functions
        r'[a-zA-Z]_[0-9]+',  # Subscripts
        r'[a-zA-Z]\^[0-9]+',  # Superscripts
        r'\\frac\{.*?\}\{.*?\}',  # Fractions
        r'\\sum_\{.*?\}\^\{.*?\}',  # Summations
        r'\\int_\{.*?\}\^\{.*?\}',  # Integrals
        r'\\sqrt\{.*?\}',  # Square roots
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            formula_text = match.group(0)
            
            # Convert to LaTeX (simple conversion)
            latex = formula_text
            latex = re.sub(r'([a-zA-Z])_([0-9]+)', r'\1_{\2}', latex)  # Fix subscripts
            latex = re.sub(r'([a-zA-Z])\^([0-9]+)', r'\1^{\2}', latex)  # Fix superscripts
            
            formulas.append({
                "latex": latex,
                "text": formula_text,
                "confidence": 0.5,  # Lower confidence for Tesseract
                "source": "tesseract"
            })
    
    return formulas

def link_formulas_to_explanations(content: Dict[str, Any]) -> None:
    """
    Link formulas to explanations in text.
    
    Args:
        content (Dict[str, Any]): The content with formulas
    """
    logger.info("Linking formulas to explanations")
    
    # Get formulas and text
    formulas = content.get("math_formulas", [])
    text = content.get("text", "")
    
    if not formulas or not text:
        return
    
    # Process each formula
    for formula in formulas:
        latex = formula.get("latex", "")
        if not latex:
            continue
        
        # Find explanation for this formula
        explanation = find_explanation_for_formula(latex, text)
        
        if explanation:
            formula["explanation"] = explanation

def find_explanation_for_formula(latex: str, text: str) -> Optional[Dict[str, Any]]:
    """
    Find explanation for a formula in text with enhanced semantic understanding.
    
    Args:
        latex (str): LaTeX formula
        text (str): Text to search for explanation
        
    Returns:
        Optional[Dict[str, Any]]: Explanation data if found, None otherwise
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # First, try to identify the formula's meaning and components
        formula_analysis_prompt = f"""
        Analyze the following mathematical formula in LaTeX format:
        
        {latex}
        
        Please provide:
        1. A brief description of what this formula represents
        2. The key variables or symbols in the formula and what they represent
        3. The mathematical domain this formula belongs to (e.g., calculus, linear algebra, statistics)
        
        Format your response as a JSON object with the following structure:
        {{
            "description": "Brief description of the formula",
            "variables": [
                {{"symbol": "x", "meaning": "What x represents"}},
                {{"symbol": "y", "meaning": "What y represents"}}
            ],
            "domain": "Mathematical domain"
        }}
        """
        
        # Generate formula analysis
        formula_analysis_json = llm.generate_structured_output(
            prompt=formula_analysis_prompt,
            output_schema={
                "description": str,
                "variables": [{"symbol": str, "meaning": str}],
                "domain": str
            }
        )
        
        # Now, search for explanations with enhanced context
        explanation_prompt = f"""
        I have the following mathematical formula in LaTeX format:
        
        {latex}
        
        This formula appears to represent: {formula_analysis_json.get('description', 'unknown concept')}
        It belongs to the domain of: {formula_analysis_json.get('domain', 'mathematics')}
        
        And I have the following text that might contain an explanation for this formula:
        
        {text}
        
        Please:
        1. Extract the sentence or paragraph that best explains this formula
        2. Identify any examples that demonstrate the formula's application
        3. Find any related formulas mentioned in the text
        4. Determine if there are any prerequisites needed to understand this formula
        
        Format your response as a JSON object with the following structure:
        {{
            "explanation": "The extracted explanation",
            "examples": ["Example 1", "Example 2"],
            "related_formulas": ["Related formula 1", "Related formula 2"],
            "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
        }}
        
        If no explanation is found, set "explanation" to null and provide empty arrays for the other fields.
        """
        
        # Generate explanation with structured output
        explanation_json = llm.generate_structured_output(
            prompt=explanation_prompt,
            output_schema={
                "explanation": str,
                "examples": [str],
                "related_formulas": [str],
                "prerequisites": [str]
            }
        )
        
        # Check if explanation was found
        if explanation_json and explanation_json.get("explanation"):
            # Combine formula analysis with explanation
            result = {
                "explanation": explanation_json.get("explanation", ""),
                "examples": explanation_json.get("examples", []),
                "related_formulas": explanation_json.get("related_formulas", []),
                "prerequisites": explanation_json.get("prerequisites", []),
                "formula_analysis": formula_analysis_json
            }
            return result
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding explanation: {str(e)}")
        return None

def generate_practice_problems(content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate practice problems for math formulas.
    
    Args:
        content (Dict[str, Any]): The content with formulas
        
    Returns:
        List[Dict[str, Any]]: List of practice problems
    """
    logger.info("Generating practice problems for math formulas")
    
    # Get formulas
    formulas = content.get("math_formulas", [])
    
    if not formulas:
        return []
    
    # Generate practice problems
    practice_problems = []
    
    for formula in formulas:
        latex = formula.get("latex", "")
        explanation = formula.get("explanation", "")
        
        if not latex:
            continue
        
        # Generate practice problems for this formula
        problems = generate_problems_for_formula(latex, explanation)
        
        if problems:
            practice_problems.extend(problems)
    
    return practice_problems

def generate_problems_for_formula(latex: str, explanation: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate practice problems for a formula with enhanced context and structure.
    
    Args:
        latex (str): LaTeX formula
        explanation (Union[str, Dict[str, Any]]): Explanation of the formula, either as a string or a structured dictionary
        
    Returns:
        List[Dict[str, Any]]: List of practice problems
    """
    from ai_note_system.api.llm_interface import get_llm_interface
    
    try:
        # Get LLM interface
        llm = get_llm_interface("openai")  # Use default provider, can be configured
        
        # Extract structured information if explanation is a dictionary
        formula_description = ""
        formula_variables = []
        formula_domain = ""
        formula_examples = []
        formula_prerequisites = []
        
        if isinstance(explanation, dict):
            formula_description = explanation.get("explanation", "")
            formula_examples = explanation.get("examples", [])
            formula_prerequisites = explanation.get("prerequisites", [])
            
            # Get formula analysis if available
            formula_analysis = explanation.get("formula_analysis", {})
            if formula_analysis:
                formula_description = formula_analysis.get("description", formula_description)
                formula_variables = formula_analysis.get("variables", [])
                formula_domain = formula_analysis.get("domain", "")
        else:
            formula_description = explanation
        
        # Create a more detailed prompt for generating practice problems
        prompt = f"""
        I need to generate practice problems for the following mathematical formula:
        
        LaTeX: {latex}
        
        Description: {formula_description}
        
        Domain: {formula_domain if formula_domain else "Mathematics"}
        
        """
        
        # Add variables if available
        if formula_variables:
            prompt += "Variables:\n"
            for var in formula_variables:
                prompt += f"- {var.get('symbol', '')}: {var.get('meaning', '')}\n"
            prompt += "\n"
        
        # Add examples if available
        if formula_examples:
            prompt += "Examples:\n"
            for example in formula_examples:
                prompt += f"- {example}\n"
            prompt += "\n"
        
        # Add prerequisites if available
        if formula_prerequisites:
            prompt += "Prerequisites:\n"
            for prereq in formula_prerequisites:
                prompt += f"- {prereq}\n"
            prompt += "\n"
        
        # Add instructions for problem generation
        prompt += """
        Please generate 5 practice problems based on this formula, with the following difficulty distribution:
        - 1 Easy problem (basic application of the formula)
        - 2 Medium problems (requiring some manipulation or multiple steps)
        - 1 Hard problem (requiring deeper understanding or combination with other concepts)
        - 1 Challenge problem (requiring creative application or extension of the formula)
        
        For each problem, provide:
        1. A clear problem statement
        2. A step-by-step solution with explanations
        3. The difficulty level
        4. A hint that could help a student who is stuck
        5. Key concepts tested by the problem
        
        Format your response as a JSON array with objects containing the following fields:
        - "problem": The problem statement
        - "solution": The step-by-step solution
        - "difficulty": The difficulty level ("easy", "medium", "hard", "challenge")
        - "hint": A helpful hint
        - "concepts": An array of key concepts tested
        """
        
        # Generate practice problems with structured output
        problems = llm.generate_structured_output(
            prompt=prompt,
            output_schema=[{
                "problem": str,
                "solution": str,
                "difficulty": str,
                "hint": str,
                "concepts": [str]
            }]
        )
        
        # Add formula reference and timestamp to each problem
        current_time = datetime.now().isoformat()
        for problem in problems:
            problem["formula"] = latex
            problem["generated_at"] = current_time
            
            # Add domain if available
            if formula_domain:
                problem["domain"] = formula_domain
        
        return problems
            
    except Exception as e:
        logger.error(f"Error generating practice problems: {str(e)}")
        return []

def render_formula_as_image(
    latex: str,
    output_path: Optional[str] = None,
    dpi: int = 300,
    fontsize: int = 12,
    color: str = "black",
    transparent: bool = True
) -> Optional[str]:
    """
    Render a LaTeX formula as an image.
    
    Args:
        latex (str): LaTeX formula
        output_path (str, optional): Path to save the image
        dpi (int): DPI for the image
        fontsize (int): Font size
        color (str): Text color
        transparent (bool): Whether to use transparent background
        
    Returns:
        Optional[str]: Path to the rendered image if successful, None otherwise
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        
        # Set up matplotlib
        rcParams['text.usetex'] = True
        rcParams['font.size'] = fontsize
        rcParams['text.latex.preamble'] = r'\usepackage{amsmath,amssymb,amsfonts}'
        
        # Create figure
        fig = plt.figure(figsize=(6, 1))
        plt.axis('off')
        
        # Render formula
        plt.text(0.5, 0.5, f"${latex}$", size=fontsize, ha='center', va='center', color=color)
        
        # Create output path if not provided
        if output_path is None:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            output_path = temp_file.name
            temp_file.close()
        
        # Save figure
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0.1, transparent=transparent)
        plt.close(fig)
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error rendering formula: {str(e)}")
        return None

def main():
    """
    Command-line interface for processing math formulas.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Process math formulas in content")
    parser.add_argument("--input", required=True, help="Input file (JSON) or image")
    parser.add_argument("--output", help="Output file (JSON)")
    parser.add_argument("--no-ocr", action="store_true", help="Skip OCR")
    parser.add_argument("--no-link", action="store_true", help="Skip linking")
    parser.add_argument("--no-practice", action="store_true", help="Skip practice problem generation")
    
    args = parser.parse_args()
    
    # Check if input is a file
    input_path = args.input
    
    if not os.path.isfile(input_path):
        print(f"Input file not found: {input_path}")
        return
    
    # Process input
    if input_path.lower().endswith((".json")):
        # Process JSON file
        try:
            with open(input_path, "r") as f:
                content = json.load(f)
            
            # Process math formulas
            processed_content = process_math_formulas(
                content,
                ocr_math=not args.no_ocr,
                link_explanations=not args.no_link,
                generate_practice=not args.no_practice
            )
            
            # Save processed content
            output_path = args.output
            if not output_path:
                output_path = f"{os.path.splitext(input_path)[0]}_math.json"
            
            with open(output_path, "w") as f:
                json.dump(processed_content, f, indent=2)
            
            print(f"Processed content saved to {output_path}")
            
        except Exception as e:
            print(f"Error processing JSON file: {str(e)}")
            
    else:
        # Process image file
        try:
            # Detect math formulas in image
            formulas = detect_math_formulas(input_path)
            
            if not formulas:
                print("No math formulas detected in the image")
                return
            
            # Save formulas
            output_path = args.output
            if not output_path:
                output_path = f"{os.path.splitext(input_path)[0]}_formulas.json"
            
            with open(output_path, "w") as f:
                json.dump({"math_formulas": formulas}, f, indent=2)
            
            print(f"Detected formulas saved to {output_path}")
            
        except Exception as e:
            print(f"Error processing image file: {str(e)}")

if __name__ == "__main__":
    main()