"""
Diagram generator module for AI Note System.
Automatically generates various types of diagrams from text.
"""

import os
import logging
import json
import tempfile
import subprocess
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.diagram_generator")

# Import required modules
from ..api.llm_interface import get_llm_interface
from .flowchart_gen import generate_flowchart

class DiagramGenerator:
    """
    Generates various types of diagrams from text.
    Supports entity-relationship diagrams, architecture diagrams, algorithm flowcharts, etc.
    """
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Diagram Generator.
        
        Args:
            llm_provider (str): LLM provider to use for diagram generation
            llm_model (str): LLM model to use for diagram generation
            output_dir (str, optional): Directory to save generated diagrams
        """
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Diagram Generator with {llm_provider} {llm_model}")
    
    def generate_diagram(
        self,
        text: str,
        diagram_type: str,
        output_format: str = "png",
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        editable: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a diagram from text.
        
        Args:
            text (str): Text to generate diagram from
            diagram_type (str): Type of diagram to generate (er, architecture, algorithm, etc.)
            output_format (str): Output format (png, svg, pdf)
            output_path (str, optional): Path to save the output file
            title (str, optional): Title for the diagram
            editable (bool): Whether to include editable layers
            
        Returns:
            Dict[str, Any]: Generated diagram information
        """
        logger.info(f"Generating {diagram_type} diagram")
        
        # Determine the appropriate diagram generator based on type
        if diagram_type.lower() in ["er", "entity-relationship", "erd"]:
            return self.generate_er_diagram(text, output_format, output_path, title, editable)
        elif diagram_type.lower() in ["architecture", "arch"]:
            return self.generate_architecture_diagram(text, output_format, output_path, title, editable)
        elif diagram_type.lower() in ["algorithm", "algo", "flowchart"]:
            return self.generate_algorithm_flowchart(text, output_format, output_path, title, editable)
        else:
            logger.error(f"Unsupported diagram type: {diagram_type}")
            return {"error": f"Unsupported diagram type: {diagram_type}"}
    
    def generate_er_diagram(
        self,
        text: str,
        output_format: str = "png",
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        editable: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an entity-relationship diagram from text.
        
        Args:
            text (str): Text to generate diagram from
            output_format (str): Output format (png, svg, pdf)
            output_path (str, optional): Path to save the output file
            title (str, optional): Title for the diagram
            editable (bool): Whether to include editable layers
            
        Returns:
            Dict[str, Any]: Generated diagram information
        """
        logger.info("Generating entity-relationship diagram")
        
        # Generate ER diagram code using LLM
        er_code = self._generate_er_code(text, title)
        
        # Create result dictionary
        result = {
            "diagram_type": "entity-relationship",
            "title": title or "Entity-Relationship Diagram",
            "format": output_format,
            "code": er_code
        }
        
        # If output path is provided, render the diagram
        if output_path:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Save diagram code to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".mmd", mode="w", delete=False) as f:
                    f.write(er_code)
                    temp_file = f.name
                
                # Use mmdc (Mermaid CLI) to render the diagram
                cmd = [
                    "mmdc",
                    "-i", temp_file,
                    "-o", output_path,
                    "-t", "default",
                    "-b", "transparent"
                ]
                
                if output_format:
                    cmd.extend(["-f", output_format])
                
                subprocess.run(cmd, check=True)
                
                # Clean up temporary file
                os.unlink(temp_file)
                
                result["output_path"] = output_path
                logger.debug(f"ER diagram saved to {output_path}")
                
                # If editable, save the source code
                if editable:
                    code_path = os.path.splitext(output_path)[0] + ".mmd"
                    with open(code_path, "w") as f:
                        f.write(er_code)
                    result["code_path"] = code_path
                
            except Exception as e:
                logger.error(f"Error rendering ER diagram: {e}")
                result["error"] = f"Error rendering ER diagram: {e}"
        
        return result
    
    def generate_architecture_diagram(
        self,
        text: str,
        output_format: str = "png",
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        editable: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an architecture diagram from text.
        
        Args:
            text (str): Text to generate diagram from
            output_format (str): Output format (png, svg, pdf)
            output_path (str, optional): Path to save the output file
            title (str, optional): Title for the diagram
            editable (bool): Whether to include editable layers
            
        Returns:
            Dict[str, Any]: Generated diagram information
        """
        logger.info("Generating architecture diagram")
        
        # Generate architecture diagram code using LLM
        arch_code = self._generate_architecture_code(text, title)
        
        # Create result dictionary
        result = {
            "diagram_type": "architecture",
            "title": title or "Architecture Diagram",
            "format": output_format,
            "code": arch_code
        }
        
        # If output path is provided, render the diagram
        if output_path:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                
                # Save diagram code to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
                    f.write(arch_code)
                    temp_file = f.name
                
                # Use dot to render the diagram
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
                logger.debug(f"Architecture diagram saved to {output_path}")
                
                # If editable, save the source code
                if editable:
                    code_path = os.path.splitext(output_path)[0] + ".dot"
                    with open(code_path, "w") as f:
                        f.write(arch_code)
                    result["code_path"] = code_path
                
            except Exception as e:
                logger.error(f"Error rendering architecture diagram: {e}")
                result["error"] = f"Error rendering architecture diagram: {e}"
        
        return result
    
    def generate_algorithm_flowchart(
        self,
        text: str,
        output_format: str = "png",
        output_path: Optional[str] = None,
        title: Optional[str] = None,
        editable: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an algorithm flowchart from text.
        
        Args:
            text (str): Text to generate diagram from
            output_format (str): Output format (png, svg, pdf)
            output_path (str, optional): Path to save the output file
            title (str, optional): Title for the diagram
            editable (bool): Whether to include editable layers
            
        Returns:
            Dict[str, Any]: Generated diagram information
        """
        logger.info("Generating algorithm flowchart")
        
        # Use the existing flowchart generator
        result = generate_flowchart(
            text=text,
            engine="mermaid",
            output_format=output_format,
            output_path=output_path,
            title=title,
            direction="TD",
            theme="default",
            include_code=True
        )
        
        # Update result with additional information
        result["diagram_type"] = "algorithm"
        
        # If editable and output path is provided, save the source code
        if editable and output_path and "code" in result and "error" not in result:
            code_path = os.path.splitext(output_path)[0] + ".mmd"
            with open(code_path, "w") as f:
                f.write(result["code"])
            result["code_path"] = code_path
        
        return result
    
    def _generate_er_code(
        self,
        text: str,
        title: Optional[str] = None
    ) -> str:
        """
        Generate entity-relationship diagram code from text using LLM.
        
        Args:
            text (str): Text to generate diagram from
            title (str, optional): Title for the diagram
            
        Returns:
            str: Mermaid code for the ER diagram
        """
        # Define the prompt for ER diagram generation
        prompt = f"""
        Generate a Mermaid entity-relationship diagram from the following text description of a database schema.
        Extract entities, attributes, and relationships from the text.
        
        Text:
        {text}
        
        Use the following Mermaid syntax for ER diagrams:
        ```mermaid
        erDiagram
            CUSTOMER ||--o{{ ORDER : places
            ORDER ||--|{{ LINE-ITEM : contains
            CUSTOMER {{{{
                string name
                string email
                string address
            }}}}
            ORDER {{{{
                int order_id
                date created_at
                float total_amount
            }}}}
            LINE-ITEM {{{{
                int line_item_id
                int product_id
                int quantity
                float price
            }}}}
        ```
        
        Make sure to:
        1. Identify all entities from the text
        2. Include relevant attributes for each entity
        3. Define relationships between entities with proper cardinality
        4. Use clear and concise naming
        
        Return only the Mermaid code without any additional text or explanation.
        """
        
        try:
            # Generate ER diagram code using LLM
            response = self.llm.generate_text(prompt=prompt, temperature=0.2)
            
            # Extract code block if present
            import re
            code_match = re.search(r'```(?:mermaid)?\s*(erDiagram[\s\S]*?)```', response, re.IGNORECASE)
            
            if code_match:
                er_code = code_match.group(1).strip()
            else:
                # If no code block is found, use the entire response
                er_code = response.strip()
            
            # Add title if provided
            if title and "title" not in er_code.lower():
                er_code = f"erDiagram\n    title {title}\n" + er_code[len("erDiagram"):]
            
            return er_code
            
        except Exception as e:
            logger.error(f"Error generating ER diagram code: {e}")
            
            # Return a simple ER diagram as fallback
            fallback_code = "erDiagram\n"
            if title:
                fallback_code += f"    title {title}\n"
            fallback_code += "    ENTITY1 ||--o{ ENTITY2 : relates_to\n"
            fallback_code += "    ENTITY1 {\n        string id\n        string name\n    }\n"
            fallback_code += "    ENTITY2 {\n        string id\n        string description\n    }"
            
            return fallback_code
    
    def _generate_architecture_code(
        self,
        text: str,
        title: Optional[str] = None
    ) -> str:
        """
        Generate architecture diagram code from text using LLM.
        
        Args:
            text (str): Text to generate diagram from
            title (str, optional): Title for the diagram
            
        Returns:
            str: Graphviz DOT code for the architecture diagram
        """
        # Define the prompt for architecture diagram generation
        prompt = f"""
        Generate a Graphviz DOT diagram from the following text description of a system architecture.
        Extract components, connections, and hierarchies from the text.
        
        Text:
        {text}
        
        Use the following Graphviz DOT syntax for architecture diagrams:
        ```dot
        digraph G {{{{
            rankdir=TB;
            node [shape=box, style=filled, fillcolor=lightblue];
            
            subgraph cluster_frontend {{{{
                label = "Frontend";
                UI [label="User Interface"];
                API_Client [label="API Client"];
            }}}}
            
            subgraph cluster_backend {{{{
                label = "Backend";
                API [label="API Server"];
                Auth [label="Authentication"];
                DB [label="Database", shape=cylinder, fillcolor=lightgrey];
            }}}}
            
            UI -> API_Client;
            API_Client -> API;
            API -> Auth;
            API -> DB;
        }}}}
        ```
        
        Make sure to:
        1. Identify all components from the text
        2. Group related components into clusters/subgraphs
        3. Define connections between components with proper direction
        4. Use appropriate shapes and styles for different types of components
        
        Return only the DOT code without any additional text or explanation.
        """
        
        try:
            # Generate architecture diagram code using LLM
            response = self.llm.generate_text(prompt=prompt, temperature=0.2)
            
            # Extract code block if present
            import re
            code_match = re.search(r'```(?:dot)?\s*(digraph[\s\S]*?)```', response, re.IGNORECASE)
            
            if code_match:
                arch_code = code_match.group(1).strip()
            else:
                # If no code block is found, use the entire response
                arch_code = response.strip()
            
            # Add title if provided
            if title and "label" not in arch_code.lower():
                # Find the opening brace
                open_brace_idx = arch_code.find("{")
                if open_brace_idx != -1:
                    # Insert title after the opening brace
                    arch_code = arch_code[:open_brace_idx+1] + f'\n    label="{title}";\n' + arch_code[open_brace_idx+1:]
            
            return arch_code
            
        except Exception as e:
            logger.error(f"Error generating architecture diagram code: {e}")
            
            # Return a simple architecture diagram as fallback
            fallback_code = "digraph G {\n"
            if title:
                fallback_code += f'    label="{title}";\n'
            fallback_code += "    rankdir=TB;\n"
            fallback_code += "    node [shape=box, style=filled, fillcolor=lightblue];\n"
            fallback_code += "    Component1 -> Component2;\n"
            fallback_code += "    Component2 -> Component3;\n"
            fallback_code += "}"
            
            return fallback_code
    
    def create_editable_layers(
        self,
        diagram_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create editable layers for an existing diagram.
        
        Args:
            diagram_path (str): Path to the diagram file
            output_dir (str, optional): Directory to save the editable layers
            
        Returns:
            Dict[str, Any]: Information about the editable layers
        """
        logger.info(f"Creating editable layers for diagram: {diagram_path}")
        
        try:
            # Determine diagram type from file extension
            file_ext = os.path.splitext(diagram_path)[1].lower()
            
            # Set output directory
            if not output_dir:
                output_dir = os.path.dirname(diagram_path)
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(diagram_path))[0]
            
            # Create editable layers based on diagram type
            if file_ext in [".png", ".jpg", ".jpeg", ".svg", ".pdf"]:
                # For image diagrams, create an SVG overlay
                svg_path = os.path.join(output_dir, f"{base_name}_editable.svg")
                
                # Create a simple SVG overlay
                svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
                     width="800" height="600" viewBox="0 0 800 600">
                  <image xlink:href="{os.path.abspath(diagram_path)}" x="0" y="0" width="800" height="600"/>
                  <g id="editable-layer">
                    <!-- Editable elements will be added here -->
                  </g>
                </svg>
                """
                
                with open(svg_path, "w") as f:
                    f.write(svg_content)
                
                return {
                    "original_diagram": diagram_path,
                    "editable_layers": [
                        {
                            "name": "overlay",
                            "path": svg_path,
                            "format": "svg"
                        }
                    ]
                }
            
            elif file_ext in [".mmd", ".dot"]:
                # For source code diagrams, create a copy for editing
                editable_path = os.path.join(output_dir, f"{base_name}_editable{file_ext}")
                
                # Copy the source code
                with open(diagram_path, "r") as src, open(editable_path, "w") as dst:
                    dst.write(src.read())
                
                return {
                    "original_diagram": diagram_path,
                    "editable_layers": [
                        {
                            "name": "source",
                            "path": editable_path,
                            "format": file_ext[1:]  # Remove the dot
                        }
                    ]
                }
            
            else:
                return {
                    "error": f"Unsupported diagram format: {file_ext}",
                    "original_diagram": diagram_path
                }
            
        except Exception as e:
            logger.error(f"Error creating editable layers: {e}")
            return {
                "error": f"Error creating editable layers: {e}",
                "original_diagram": diagram_path
            }


def main():
    """
    Command-line interface for the Diagram Generator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Automatic Diagram Generator")
    parser.add_argument("--text", help="Text to generate diagram from")
    parser.add_argument("--file", help="File containing text to generate diagram from")
    parser.add_argument("--type", required=True, choices=["er", "architecture", "algorithm"], help="Type of diagram to generate")
    parser.add_argument("--output", required=True, help="Output file path")
    parser.add_argument("--format", default="png", choices=["png", "svg", "pdf"], help="Output format")
    parser.add_argument("--title", help="Title for the diagram")
    parser.add_argument("--editable", action="store_true", help="Include editable layers")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Get text from file or command line
    if args.file:
        with open(args.file, "r") as f:
            text = f.read()
    elif args.text:
        text = args.text
    else:
        print("Error: Either --text or --file must be provided")
        return
    
    # Initialize generator
    generator = DiagramGenerator(
        llm_provider=args.llm,
        llm_model=args.model,
        output_dir=os.path.dirname(args.output)
    )
    
    # Generate diagram
    result = generator.generate_diagram(
        text=text,
        diagram_type=args.type,
        output_format=args.format,
        output_path=args.output,
        title=args.title,
        editable=args.editable
    )
    
    # Check for errors
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Generated {result['diagram_type']} diagram: {result.get('output_path', '')}")
    if args.editable and "code_path" in result:
        print(f"Editable source code: {result['code_path']}")


if __name__ == "__main__":
    main()