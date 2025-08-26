"""
Image Mind Map generator module for AI Note System.
Generates interactive mind maps with images using HTML and JavaScript.
"""

import os
import logging
import json
import tempfile
import base64
import re
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.image_mindmap")

def generate_image_mindmap(
    text: str,
    images: List[Dict[str, Any]],
    output_path: str,
    title: Optional[str] = None,
    theme: str = "default",
    include_code: bool = True,
    open_browser: bool = False
) -> Dict[str, Any]:
    """
    Generate an interactive mind map with images.
    
    Args:
        text (str): The text to generate a mind map from
        images (List[Dict[str, Any]]): List of images to include in the mind map
        output_path (str): Path to save the HTML file
        title (str, optional): Title for the mind map
        theme (str): Theme for the mind map
        include_code (bool): Whether to include the generated code in the result
        open_browser (bool): Whether to open the mind map in a browser
        
    Returns:
        Dict[str, Any]: Dictionary containing the mind map information
    """
    logger.info("Generating image mind map")
    
    # Extract topics and subtopics from text
    topics = extract_hierarchical_topics(text)
    
    # Match images to topics and subtopics
    topics_with_images = match_images_to_topics(topics, images)
    
    # Generate HTML and JavaScript code
    html_code = generate_html_mindmap(topics_with_images, title, theme)
    
    # Create result dictionary
    result = {
        "title": title or "Image Mind Map",
        "format": "html"
    }
    
    if include_code:
        result["code"] = html_code
    
    # Save the HTML file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write HTML to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_code)
        
        result["output_path"] = output_path
        logger.debug(f"Image mind map saved to {output_path}")
        
        # Open in browser if requested
        if open_browser:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(output_path)}")
            logger.debug("Opened image mind map in browser")
        
    except Exception as e:
        logger.error(f"Error saving image mind map: {e}")
        result["error"] = f"Error saving image mind map: {e}"
    
    return result

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

def match_images_to_topics(
    topics: Dict[str, List[str]],
    images: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Match images to topics and subtopics based on relevance.
    
    Args:
        topics (Dict[str, List[str]]): Dictionary of topics and their subtopics
        images (List[Dict[str, Any]]): List of images to match
        
    Returns:
        Dict[str, Dict[str, Any]]: Topics with matched images
    """
    # Initialize result dictionary
    result = {}
    
    # Process each topic
    for topic, subtopics in topics.items():
        result[topic] = {
            "subtopics": [],
            "image": None
        }
        
        # Find the most relevant image for this topic
        topic_image = find_relevant_image(topic, images)
        if topic_image:
            result[topic]["image"] = topic_image
            # Remove the image from the list to avoid duplicates
            images = [img for img in images if img["path"] != topic_image["path"]]
        
        # Process subtopics
        for subtopic in subtopics:
            subtopic_data = {
                "text": subtopic,
                "image": None
            }
            
            # Find the most relevant image for this subtopic
            subtopic_image = find_relevant_image(subtopic, images)
            if subtopic_image:
                subtopic_data["image"] = subtopic_image
                # Remove the image from the list to avoid duplicates
                images = [img for img in images if img["path"] != subtopic_image["path"]]
            
            result[topic]["subtopics"].append(subtopic_data)
    
    return result

def find_relevant_image(
    text: str,
    images: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Find the most relevant image for a given text.
    
    Args:
        text (str): The text to find a relevant image for
        images (List[Dict[str, Any]]): List of images to search
        
    Returns:
        Optional[Dict[str, Any]]: The most relevant image, or None if no relevant image is found
    """
    # This is a simplified implementation
    # In a real implementation, this would use image captions, OCR, or vision-language models
    
    # If no images, return None
    if not images:
        return None
    
    # Extract keywords from text
    keywords = extract_keywords(text)
    
    # Score each image based on filename and metadata
    scored_images = []
    for image in images:
        score = 0
        
        # Check filename for keywords
        filename = image.get("filename", "").lower()
        for keyword in keywords:
            if keyword in filename:
                score += 2
        
        # Check page/slide number
        if "page" in image or "slide" in image:
            score += 1
        
        # Prefer larger images
        width = image.get("width", 0)
        height = image.get("height", 0)
        if width > 300 and height > 300:
            score += 1
        
        scored_images.append((score, image))
    
    # Sort by score (descending)
    scored_images.sort(key=lambda x: x[0], reverse=True)
    
    # Return the highest-scoring image, or None if no images
    return scored_images[0][1] if scored_images else None

def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text (str): The text to extract keywords from
        
    Returns:
        List[str]: List of keywords
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    
    # Split into words
    words = text.split()
    
    # Remove common stop words
    stop_words = ["the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be", "been", "being", "in", "on", "at", "to", "for", "with", "by", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "from", "up", "down", "of", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Return unique keywords
    return list(set(keywords))

def generate_html_mindmap(
    topics_with_images: Dict[str, Dict[str, Any]],
    title: Optional[str] = None,
    theme: str = "default"
) -> str:
    """
    Generate HTML and JavaScript code for an interactive mind map with images.
    
    Args:
        topics_with_images (Dict[str, Dict[str, Any]]): Topics with matched images
        title (str, optional): Title for the mind map
        theme (str): Theme for the mind map
        
    Returns:
        str: HTML code for the mind map
    """
    # Set title
    if not title:
        title = "Interactive Mind Map with Images"
    
    # Convert topics to JSON for JavaScript
    topics_json = json.dumps(topics_with_images)
    
    # Choose theme colors
    if theme == "dark":
        bg_color = "#2c3e50"
        text_color = "#ecf0f1"
        node_color = "#3498db"
        line_color = "#7f8c8d"
    elif theme == "light":
        bg_color = "#ecf0f1"
        text_color = "#2c3e50"
        node_color = "#3498db"
        line_color = "#bdc3c7"
    elif theme == "nature":
        bg_color = "#f1f8e9"
        text_color = "#33691e"
        node_color = "#7cb342"
        line_color = "#aed581"
    else:  # default
        bg_color = "#ffffff"
        text_color = "#333333"
        node_color = "#4285f4"
        line_color = "#cccccc"
    
    # Generate HTML code
    html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: {bg_color};
            color: {text_color};
        }}
        #mindmap-container {{
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            fill: {node_color};
            stroke: {text_color};
            stroke-width: 1.5px;
        }}
        .node text {{
            font-size: 14px;
            fill: {text_color};
        }}
        .link {{
            fill: none;
            stroke: {line_color};
            stroke-width: 1.5px;
        }}
        .image-container {{
            position: absolute;
            border: 2px solid {node_color};
            border-radius: 5px;
            background-color: white;
            padding: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        .image-container img {{
            max-width: 200px;
            max-height: 150px;
        }}
        .controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        .controls button {{
            margin: 0 5px;
            padding: 5px 10px;
            background-color: {node_color};
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
        }}
        .controls button:hover {{
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="controls">
        <h2>{title}</h2>
        <button id="zoom-in">Zoom In</button>
        <button id="zoom-out">Zoom Out</button>
        <button id="reset">Reset</button>
    </div>
    <div id="mindmap-container"></div>
    <div id="image-container" class="image-container"></div>
    
    <script>
        // Mind map data
        const topicsData = {topics_json};
        
        // Set up the SVG
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#mindmap-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Create a group for the mind map
        const g = svg.append("g")
            .attr("transform", `translate(${{width / 2}}, ${{height / 2}})`);
        
        // Set up zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Create hierarchical data structure
        const root = {{
            name: "{title}",
            children: []
        }};
        
        // Add topics and subtopics
        for (const [topic, data] of Object.entries(topicsData)) {{
            const topicNode = {{
                name: topic,
                image: data.image,
                children: []
            }};
            
            // Add subtopics
            for (const subtopic of data.subtopics) {{
                topicNode.children.push({{
                    name: subtopic.text,
                    image: subtopic.image
                }});
            }}
            
            root.children.push(topicNode);
        }}
        
        // Create tree layout
        const treeLayout = d3.tree()
            .size([2 * Math.PI, Math.min(width, height) / 3])
            .separation((a, b) => (a.parent === b.parent ? 1 : 2) / a.depth);
        
        // Convert data to hierarchy
        const hierarchy = d3.hierarchy(root);
        
        // Apply layout
        const nodes = treeLayout(hierarchy);
        
        // Create links
        const links = g.append("g")
            .selectAll("path")
            .data(nodes.links())
            .enter()
            .append("path")
            .attr("class", "link")
            .attr("d", d3.linkRadial()
                .angle(d => d.x)
                .radius(d => d.y));
        
        // Create nodes
        const nodeGroups = g.append("g")
            .selectAll(".node")
            .data(nodes.descendants())
            .enter()
            .append("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${{d.y * Math.sin(d.x)}}, ${{d.y * Math.cos(d.x)}})`);
        
        // Add circles to nodes
        nodeGroups.append("circle")
            .attr("r", 5)
            .on("mouseover", showImage)
            .on("mouseout", hideImage);
        
        // Add text to nodes
        nodeGroups.append("text")
            .attr("dy", ".31em")
            .attr("x", d => d.x < Math.PI ? 8 : -8)
            .attr("text-anchor", d => d.x < Math.PI ? "start" : "end")
            .attr("transform", d => d.x < Math.PI ? null : "rotate(180)")
            .text(d => d.data.name)
            .on("mouseover", showImage)
            .on("mouseout", hideImage);
        
        // Image container
        const imageContainer = d3.select("#image-container");
        
        // Function to show image
        function showImage(event, d) {{
            if (d.data.image) {{
                const image = d.data.image;
                const imagePath = image.path;
                
                // Create image HTML
                let html = `<img src="file://${{imagePath}}" alt="Mind Map Image">`;
                
                // Add metadata if available
                if (image.page) {{
                    html += `<div>Page: ${{image.page}}</div>`;
                }} else if (image.slide) {{
                    html += `<div>Slide: ${{image.slide}}</div>`;
                }} else if (image.timestamp_str) {{
                    html += `<div>Timestamp: ${{image.timestamp_str}}</div>`;
                }}
                
                // Set container content and position
                imageContainer
                    .html(html)
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY + 10) + "px")
                    .style("opacity", 1);
            }}
        }}
        
        // Function to hide image
        function hideImage() {{
            imageContainer.style("opacity", 0);
        }}
        
        // Zoom controls
        d3.select("#zoom-in").on("click", () => {{
            svg.transition().call(zoom.scaleBy, 1.5);
        }});
        
        d3.select("#zoom-out").on("click", () => {{
            svg.transition().call(zoom.scaleBy, 0.75);
        }});
        
        d3.select("#reset").on("click", () => {{
            svg.transition().call(zoom.transform, d3.zoomIdentity);
        }});
    </script>
</body>
</html>
"""
    
    return html_code

def process_source_for_image_mindmap(
    source_path: str,
    source_type: str,
    content: Dict[str, Any],
    output_path: str,
    title: Optional[str] = None,
    theme: str = "default",
    open_browser: bool = False
) -> Dict[str, Any]:
    """
    Process a source file to generate an image mind map.
    
    Args:
        source_path (str): Path to the source file
        source_type (str): Type of source (pdf, slides, video)
        content (Dict[str, Any]): Content data (text, summary, etc.)
        output_path (str): Path to save the HTML file
        title (str, optional): Title for the mind map
        theme (str): Theme for the mind map
        open_browser (bool): Whether to open the mind map in a browser
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    logger.info(f"Processing {source_type} source for image mind map: {source_path}")
    
    try:
        # Create temporary directory for extracted images
        temp_dir = tempfile.mkdtemp()
        
        # Extract images based on source type
        images = []
        
        if source_type.lower() == "pdf":
            from ..processing.image_flashcards import extract_images_from_pdf
            images = extract_images_from_pdf(source_path, temp_dir)
        elif source_type.lower() in ["slides", "pptx", "powerpoint"]:
            from ..processing.image_flashcards import extract_images_from_slides
            images = extract_images_from_slides(source_path, temp_dir)
        elif source_type.lower() in ["video", "mp4", "youtube"]:
            from ..processing.image_flashcards import extract_images_from_video
            images = extract_images_from_video(source_path, temp_dir)
        else:
            return {
                "success": False,
                "error": f"Unsupported source type: {source_type}"
            }
        
        # Check if images were extracted
        if not images:
            return {
                "success": False,
                "error": f"No images extracted from {source_type} source"
            }
        
        # Get text from content
        text = content.get("text", "")
        summary = content.get("summary", "")
        
        # Use summary if available, otherwise use text
        content_text = summary if summary else text
        
        # Generate image mind map
        result = generate_image_mindmap(
            text=content_text,
            images=images,
            output_path=output_path,
            title=title or content.get("title", "Image Mind Map"),
            theme=theme,
            open_browser=open_browser
        )
        
        return {
            "success": True,
            "output_path": output_path,
            "result": result
        }
        
    except Exception as e:
        error_msg = f"Error processing source for image mind map: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}