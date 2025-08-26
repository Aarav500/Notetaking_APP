"""
Tree graph generator module for AI Note System.
Generates 3D tree graphs from text using Graphviz.
"""

import os
import logging
import subprocess
import tempfile
import re
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.treegraph_gen")

def generate_treegraph(
    text: str,
    output_format: str = "png",
    output_path: Optional[str] = None,
    title: Optional[str] = None,
    layout: str = "dot",
    include_code: bool = True,
    is_3d: bool = True
) -> Dict[str, Any]:
    """
    Generate a tree graph from text.
    
    Args:
        text (str): The text to generate a tree graph from
        output_format (str): The output format (png, svg, pdf)
        output_path (str, optional): Path to save the output file
        title (str, optional): Title for the tree graph
        layout (str): Graphviz layout engine (dot, neato, fdp, sfdp, twopi, circo)
        include_code (bool): Whether to include the generated code in the result
        is_3d (bool): Whether to generate a 3D-like tree graph
        
    Returns:
        Dict[str, Any]: Dictionary containing the tree graph information
    """
    logger.info(f"Generating tree graph using {layout} layout")
    
    # Generate DOT code from text
    dot_code = extract_treegraph_from_text(text, title, is_3d)
    
    # Create result dictionary
    result = {
        "title": title or "Tree Graph",
        "format": output_format,
        "layout": layout,
        "is_3d": is_3d
    }
    
    if include_code:
        result["code"] = dot_code
    
    # If output path is provided, render the tree graph
    if output_path:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save DOT code to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
                f.write(dot_code)
                temp_file = f.name
            
            # Use Graphviz to render the tree graph
            cmd = [
                layout,
                "-T" + output_format,
                "-o", output_path,
                temp_file
            ]
            
            subprocess.run(cmd, check=True)
            
            # Clean up temporary file
            os.unlink(temp_file)
            
            result["output_path"] = output_path
            logger.debug(f"Tree graph saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error rendering tree graph: {e}")
            result["error"] = f"Error rendering tree graph: {e}"
    
    return result

def extract_treegraph_from_text(
    text: str,
    title: Optional[str] = None,
    is_3d: bool = True
) -> str:
    """
    Extract a tree graph from text.
    
    Args:
        text (str): The text to extract a tree graph from
        title (str, optional): Title for the tree graph
        is_3d (bool): Whether to generate a 3D-like tree graph
        
    Returns:
        str: Graphviz DOT code
    """
    # Extract hierarchical structure from text
    tree_structure = extract_hierarchical_structure(text)
    
    # Generate DOT code
    dot_code = ["digraph G {"]
    
    # Add graph attributes
    dot_code.append("    // Graph attributes")
    dot_code.append('    graph [rankdir="TB", splines="ortho", nodesep=0.8, ranksep=1.0, fontname="Arial"];')
    
    if is_3d:
        dot_code.append('    node [shape="box", style="filled,rounded", fillcolor="#E8E8E8", gradientangle="315", color="#AAAAAA", fontname="Arial", fontsize=12, margin=0.2];')
        dot_code.append('    edge [color="#777777", penwidth=2.0, arrowsize=0.8];')
    else:
        dot_code.append('    node [shape="box", style="filled", fillcolor="#E8E8E8", color="#333333", fontname="Arial", fontsize=12];')
        dot_code.append('    edge [color="#555555", penwidth=1.0];')
    
    # Add title as a label if provided
    if title:
        dot_code.append(f'    labelloc="t";')
        dot_code.append(f'    label="{title}";')
    
    # Add nodes and edges
    dot_code.append("\n    // Nodes and edges")
    
    # Create a unique ID for each node
    node_ids = {}
    node_counter = 0
    
    def add_node_and_children(node: Dict[str, Any], parent_id: Optional[str] = None, depth: int = 0) -> str:
        nonlocal node_counter
        
        # Create a unique ID for this node
        node_id = f"node{node_counter}"
        node_counter += 1
        
        # Store the ID for this node
        node_ids[node["name"]] = node_id
        
        # Add node with 3D-like styling if requested
        label = node["name"].replace('"', '\\"')
        
        if is_3d:
            # Calculate color based on depth
            hue = (depth * 40) % 360
            saturation = 30 + (depth * 10) % 50
            lightness = 80 - (depth * 5) % 30
            fillcolor = f"\"#{hsl_to_hex(hue, saturation, lightness)}\""
            
            # Add 3D-like node
            dot_code.append(f'    {node_id} [label="{label}", fillcolor={fillcolor}, gradientangle="{(45 + depth * 30) % 360}"];')
        else:
            # Simple node
            dot_code.append(f'    {node_id} [label="{label}"];')
        
        # Add edge from parent if this is not the root
        if parent_id:
            if is_3d:
                # 3D-like edge
                dot_code.append(f'    {parent_id} -> {node_id} [penwidth="{max(0.5, 2.0 - depth * 0.3)}", arrowsize="{max(0.3, 0.8 - depth * 0.1)}"];')
            else:
                # Simple edge
                dot_code.append(f'    {parent_id} -> {node_id};')
        
        # Process children
        for child in node.get("children", []):
            add_node_and_children(child, node_id, depth + 1)
        
        return node_id
    
    # Add all nodes starting from the root
    if tree_structure:
        add_node_and_children(tree_structure)
    
    dot_code.append("}")
    
    return "\n".join(dot_code)

def extract_hierarchical_structure(text: str) -> Dict[str, Any]:
    """
    Extract hierarchical structure from text.
    
    Args:
        text (str): The text to extract structure from
        
    Returns:
        Dict[str, Any]: Hierarchical structure as a nested dictionary
    """
    # This is a simplified implementation that looks for patterns in the text
    # In a real implementation, this would use an LLM to extract structure more intelligently
    
    # Try to extract structure from markdown-like headings
    structure = extract_structure_from_headings(text)
    if structure and structure.get("children"):
        return structure
    
    # Try to extract structure from bullet points
    structure = extract_structure_from_bullets(text)
    if structure and structure.get("children"):
        return structure
    
    # Try to extract structure from paragraphs
    structure = extract_structure_from_paragraphs(text)
    if structure and structure.get("children"):
        return structure
    
    # Fallback: create a simple structure from sentences
    return extract_structure_from_sentences(text)

def extract_structure_from_headings(text: str) -> Dict[str, Any]:
    """
    Extract structure from markdown-like headings.
    
    Args:
        text (str): The text to extract structure from
        
    Returns:
        Dict[str, Any]: Hierarchical structure as a nested dictionary
    """
    lines = text.split("\n")
    
    # Look for heading patterns: # Heading, ## Subheading, etc.
    heading_pattern = re.compile(r'^(#+)\s+(.+)$')
    
    # Create root node
    root = {
        "name": "Root",
        "children": []
    }
    
    # Stack to keep track of current path in the hierarchy
    # Start with just the root
    stack = [root]
    
    current_level = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this line is a heading
        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()
            
            # Create a new node for this heading
            node = {
                "name": heading,
                "children": []
            }
            
            # Adjust the stack based on the heading level
            if level > current_level:
                # Going deeper in the hierarchy
                stack.append(stack[-1]["children"][-1] if stack[-1]["children"] else stack[-1])
            elif level < current_level:
                # Going back up in the hierarchy
                for _ in range(current_level - level):
                    if len(stack) > 1:  # Don't pop the root
                        stack.pop()
            
            # Add this node to its parent
            stack[-1]["children"].append(node)
            current_level = level
        else:
            # This is content for the current heading
            # In a more sophisticated implementation, we would parse this content
            # For now, we'll just ignore it
            pass
    
    # If we didn't find any headings, return an empty root
    if not root["children"]:
        # Try to extract a title from the first line
        if lines and lines[0].strip():
            root["name"] = lines[0].strip()
    
    return root

def extract_structure_from_bullets(text: str) -> Dict[str, Any]:
    """
    Extract structure from bullet points.
    
    Args:
        text (str): The text to extract structure from
        
    Returns:
        Dict[str, Any]: Hierarchical structure as a nested dictionary
    """
    lines = text.split("\n")
    
    # Create root node
    root = {
        "name": "Root",
        "children": []
    }
    
    # Try to extract a title from the first non-bullet line
    for line in lines:
        line = line.strip()
        if line and not line.startswith(("- ", "* ", "  ")):
            root["name"] = line
            break
    
    # Stack to keep track of current path in the hierarchy
    # Start with just the root
    stack = [root]
    
    # Keep track of indentation levels
    indentation_levels = {}
    
    for line in lines:
        # Count leading spaces to determine indentation level
        indent = len(line) - len(line.lstrip())
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Check if this line is a bullet point
        if line.startswith(("- ", "* ")):
            # Extract the content of the bullet point
            content = line[2:].strip()
            
            # Create a new node for this bullet point
            node = {
                "name": content,
                "children": []
            }
            
            # Determine the level based on indentation
            if indent not in indentation_levels:
                indentation_levels[indent] = len(indentation_levels) + 1
            level = indentation_levels[indent]
            
            # Adjust the stack based on the indentation level
            while len(stack) > level:
                stack.pop()
            
            while len(stack) < level:
                # If we're missing levels, add the node to the deepest available level
                if not stack[-1]["children"]:
                    # Add a placeholder node if needed
                    stack[-1]["children"].append({"name": "...", "children": []})
                stack.append(stack[-1]["children"][-1])
            
            # Add this node to its parent
            stack[-1]["children"].append(node)
            
            # This node becomes the new current node at its level
            stack = stack[:level]
            stack.append(node)
    
    return root

def extract_structure_from_paragraphs(text: str) -> Dict[str, Any]:
    """
    Extract structure from paragraphs.
    
    Args:
        text (str): The text to extract structure from
        
    Returns:
        Dict[str, Any]: Hierarchical structure as a nested dictionary
    """
    # Split text into paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    
    # Create root node
    root = {
        "name": "Root",
        "children": []
    }
    
    # Try to extract a title from the first paragraph
    if paragraphs:
        root["name"] = paragraphs[0].strip().split(".")[0]
        
        # Process remaining paragraphs
        for paragraph in paragraphs[1:]:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Use the first sentence as the node name
            sentences = re.split(r'(?<=[.!?])\s+', paragraph)
            if sentences:
                node_name = sentences[0].strip()
                if len(node_name) > 50:
                    node_name = node_name[:47] + "..."
                
                # Create a node for this paragraph
                node = {
                    "name": node_name,
                    "children": []
                }
                
                # Add child nodes for additional sentences
                for sentence in sentences[1:]:
                    sentence = sentence.strip()
                    if len(sentence) > 10:
                        child_name = sentence
                        if len(child_name) > 50:
                            child_name = child_name[:47] + "..."
                        
                        node["children"].append({
                            "name": child_name,
                            "children": []
                        })
                
                # Add this node to the root
                root["children"].append(node)
    
    return root

def extract_structure_from_sentences(text: str) -> Dict[str, Any]:
    """
    Extract structure from sentences as a fallback.
    
    Args:
        text (str): The text to extract structure from
        
    Returns:
        Dict[str, Any]: Hierarchical structure as a nested dictionary
    """
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Create root node
    root = {
        "name": "Root",
        "children": []
    }
    
    # Try to extract a title from the first sentence
    if sentences:
        root["name"] = sentences[0].strip()
        
        # Group sentences into topics
        current_topic = None
        current_children = []
        
        for sentence in sentences[1:]:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if this sentence looks like a new topic
            if len(sentence) < 40 and sentence.endswith((":", ".")):
                # Save the previous topic if it exists
                if current_topic and current_children:
                    node = {
                        "name": current_topic,
                        "children": current_children
                    }
                    root["children"].append(node)
                
                # Start a new topic
                current_topic = sentence.rstrip(":.")
                current_children = []
            elif current_topic:
                # Add this sentence as a child of the current topic
                if len(sentence) > 50:
                    sentence = sentence[:47] + "..."
                
                current_children.append({
                    "name": sentence,
                    "children": []
                })
            else:
                # No topic yet, add directly to root
                if len(sentence) > 50:
                    sentence = sentence[:47] + "..."
                
                root["children"].append({
                    "name": sentence,
                    "children": []
                })
        
        # Add the last topic if it exists
        if current_topic and current_children:
            node = {
                "name": current_topic,
                "children": current_children
            }
            root["children"].append(node)
    
    return root

def hsl_to_hex(h: float, s: float, l: float) -> str:
    """
    Convert HSL color to hex color code.
    
    Args:
        h (float): Hue (0-360)
        s (float): Saturation (0-100)
        l (float): Lightness (0-100)
        
    Returns:
        str: Hex color code
    """
    h /= 360
    s /= 100
    l /= 100
    
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0:
                t += 1
            if t > 1:
                t -= 1
            if t < 1/6:
                return p + (q - p) * 6 * t
            if t < 1/2:
                return q
            if t < 2/3:
                return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    
    return f"{r:02x}{g:02x}{b:02x}"

def generate_treegraph_from_llm(
    text: str,
    model: str = "gpt-4",
    title: Optional[str] = None,
    is_3d: bool = True
) -> str:
    """
    Generate a tree graph from text using an LLM.
    
    Args:
        text (str): The text to generate a tree graph from
        model (str): The LLM model to use
        title (str, optional): Title for the tree graph
        is_3d (bool): Whether to generate a 3D-like tree graph
        
    Returns:
        str: Graphviz DOT code
    """
    # This would use an LLM to generate the tree graph code
    # For now, we'll use the simpler extraction method
    
    return extract_treegraph_from_text(text, title, is_3d)