"""
Knowledge Graph Generator module for AI Note System.
Generates hierarchical knowledge graphs from notes using Graphviz.
"""

import os
import logging
import subprocess
import tempfile
import re
import json
import webbrowser
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.knowledge_graph_gen")

def generate_knowledge_graph(
    db_manager,
    output_format: str = "svg",
    output_path: Optional[str] = None,
    title: str = "Knowledge Graph",
    layout: str = "fdp",
    include_code: bool = True,
    is_3d: bool = True,
    max_nodes: int = 100,
    similarity_threshold: float = 0.5,
    tags: Optional[List[str]] = None,
    open_browser: bool = False,
    include_reasoning: bool = True
) -> Dict[str, Any]:
    """
    Generate a hierarchical knowledge graph from notes.
    
    Args:
        db_manager: Database manager instance
        output_format (str): The output format (svg, png, pdf)
        output_path (str, optional): Path to save the output file
        title (str): Title for the knowledge graph
        layout (str): Graphviz layout engine (fdp, neato, dot, sfdp, twopi, circo)
        include_code (bool): Whether to include the generated code in the result
        is_3d (bool): Whether to generate a 3D-like graph
        max_nodes (int): Maximum number of nodes to include
        similarity_threshold (float): Minimum similarity threshold for related notes
        tags (List[str], optional): Filter notes by tags
        open_browser (bool): Whether to open the output file in a browser
        include_reasoning (bool): Whether to include reasoning paths between concepts
        
    Returns:
        Dict[str, Any]: Dictionary containing the knowledge graph information
    """
    logger.info(f"Generating knowledge graph using {layout} layout with reasoning={include_reasoning}")
    
    # Extract notes and relationships from database
    graph_data = extract_graph_data_from_db(
        db_manager, 
        max_nodes=max_nodes, 
        similarity_threshold=similarity_threshold,
        tags=tags,
        include_reasoning=include_reasoning
    )
    
    # Generate DOT code from graph data
    dot_code = generate_dot_code_from_graph_data(graph_data, title, is_3d, layout)
    
    # Create result dictionary
    result = {
        "title": title,
        "format": output_format,
        "layout": layout,
        "is_3d": is_3d,
        "node_count": len(graph_data["nodes"]),
        "edge_count": len(graph_data["edges"])
    }
    
    # Add reasoning paths if included
    if include_reasoning and "reasoning_paths" in graph_data:
        result["reasoning_path_count"] = len(graph_data["reasoning_paths"])
        result["reasoning_paths"] = graph_data["reasoning_paths"]
    
    if include_code:
        result["code"] = dot_code
    
    # If output path is provided, render the knowledge graph
    if output_path:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save DOT code to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".dot", mode="w", delete=False) as f:
                f.write(dot_code)
                temp_file = f.name
            
            # Use Graphviz to render the knowledge graph
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
            logger.debug(f"Knowledge graph saved to {output_path}")
            
            # Open in browser if requested
            if open_browser and output_format == "svg":
                try:
                    webbrowser.open(f"file://{os.path.abspath(output_path)}")
                    logger.info(f"Opened knowledge graph in browser")
                except Exception as e:
                    logger.error(f"Error opening knowledge graph in browser: {e}")
            
        except Exception as e:
            logger.error(f"Error rendering knowledge graph: {e}")
            result["error"] = f"Error rendering knowledge graph: {e}"
    
    return result

def extract_graph_data_from_db(
    db_manager,
    max_nodes: int = 100,
    similarity_threshold: float = 0.5,
    tags: Optional[List[str]] = None,
    include_reasoning: bool = False
) -> Dict[str, Any]:
    """
    Extract graph data from the database.
    
    Args:
        db_manager: Database manager instance
        max_nodes (int): Maximum number of nodes to include
        similarity_threshold (float): Minimum similarity threshold for related notes
        tags (List[str], optional): Filter notes by tags
        include_reasoning (bool): Whether to include reasoning paths between concepts
        
    Returns:
        Dict[str, Any]: Dictionary containing nodes, edges, and reasoning paths
    """
    logger.info(f"Extracting graph data from database (max_nodes={max_nodes}, threshold={similarity_threshold}, include_reasoning={include_reasoning})")
    
    # Get notes from database
    if tags:
        notes = db_manager.search_notes(tags=tags, limit=max_nodes)
    else:
        notes = db_manager.search_notes(limit=max_nodes)
    
    # Create nodes and edges
    nodes = []
    edges = []
    reasoning_paths = []
    node_ids = set()
    
    # Add nodes
    for note in notes:
        node_ids.add(note["id"])
        
        # Format timestamp
        timestamp = note.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(timestamp)
            formatted_date = dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            formatted_date = "Unknown date"
        
        # Extract key concepts from the note
        key_concepts = []
        if note.get("keypoints"):
            for keypoint in note.get("keypoints", []):
                if isinstance(keypoint, dict) and "text" in keypoint:
                    key_concepts.append(keypoint["text"])
                elif isinstance(keypoint, str):
                    key_concepts.append(keypoint)
        
        # Create node
        node = {
            "id": note["id"],
            "title": note["title"],
            "summary": note.get("summary", ""),
            "tags": note.get("tags", []),
            "date": formatted_date,
            "source_type": note.get("source_type", "text"),
            "key_concepts": key_concepts,
            "is_prerequisite": any(tag.lower() in ["prerequisite", "fundamental", "basic"] for tag in note.get("tags", [])),
            "is_advanced": any(tag.lower() in ["advanced", "expert", "complex"] for tag in note.get("tags", []))
        }
        
        nodes.append(node)
    
    # Add edges (relationships between notes)
    for note in notes:
        note_id = note["id"]
        
        # Get related notes
        related_notes = db_manager.get_related_notes(note_id)
        
        for related_note in related_notes:
            related_id = related_note["id"]
            similarity = related_note.get("similarity", 0.0)
            
            # Only include edges above the similarity threshold
            if similarity >= similarity_threshold and related_id in node_ids:
                # Determine relationship type
                relationship_type = "related"
                
                # Check if this is a prerequisite relationship
                source_note = next((n for n in nodes if n["id"] == note_id), None)
                target_note = next((n for n in nodes if n["id"] == related_id), None)
                
                if source_note and target_note:
                    # Check for prerequisite relationship based on tags
                    if source_note.get("is_prerequisite") and target_note.get("is_advanced"):
                        relationship_type = "prerequisite"
                    elif target_note.get("is_prerequisite") and source_note.get("is_advanced"):
                        relationship_type = "builds_on"
                    
                    # Check for temporal relationship based on dates
                    if source_note.get("date") < target_note.get("date"):
                        relationship_type = "precedes" if relationship_type == "related" else relationship_type
                
                edge = {
                    "source": note_id,
                    "target": related_id,
                    "similarity": similarity,
                    "relationship_type": relationship_type
                }
                
                edges.append(edge)
    
    # Generate reasoning paths if requested
    if include_reasoning:
        reasoning_paths = generate_reasoning_paths(nodes, edges)
    
    logger.info(f"Extracted {len(nodes)} nodes, {len(edges)} edges, and {len(reasoning_paths)} reasoning paths")
    
    return {
        "nodes": nodes,
        "edges": edges,
        "reasoning_paths": reasoning_paths
    }

def generate_reasoning_paths(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate reasoning paths between concepts.
    
    Args:
        nodes (List[Dict[str, Any]]): List of nodes
        edges (List[Dict[str, Any]]): List of edges
        
    Returns:
        List[Dict[str, Any]]: List of reasoning paths
    """
    reasoning_paths = []
    
    # Create a graph representation for path finding
    graph = {}
    for node in nodes:
        graph[node["id"]] = []
    
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        relationship_type = edge.get("relationship_type", "related")
        
        if source in graph:
            graph[source].append((target, relationship_type))
        if target in graph:  # Add reverse direction for non-directional relationships
            if relationship_type == "related":
                graph[target].append((source, relationship_type))
    
    # Find paths between nodes that have prerequisite relationships
    prerequisite_edges = [edge for edge in edges if edge.get("relationship_type") == "prerequisite"]
    
    for edge in prerequisite_edges:
        source_id = edge["source"]
        target_id = edge["target"]
        
        source_node = next((n for n in nodes if n["id"] == source_id), None)
        target_node = next((n for n in nodes if n["id"] == target_id), None)
        
        if source_node and target_node:
            # Create a reasoning path explaining the prerequisite relationship
            path = {
                "source_id": source_id,
                "target_id": target_id,
                "source_title": source_node["title"],
                "target_title": target_node["title"],
                "path_type": "prerequisite",
                "explanation": f"{source_node['title']} is a prerequisite for understanding {target_node['title']}. "
                              f"You should master the concepts in {source_node['title']} before moving on to {target_node['title']}."
            }
            
            reasoning_paths.append(path)
    
    # Find paths between nodes that have causal relationships
    for i, node1 in enumerate(nodes):
        for j, node2 in enumerate(nodes):
            if i != j:
                # Check if there's a potential causal relationship based on key concepts
                common_concepts = set(node1.get("key_concepts", [])) & set(node2.get("key_concepts", []))
                
                if common_concepts and any(edge["source"] == node1["id"] and edge["target"] == node2["id"] for edge in edges):
                    # Create a reasoning path explaining the causal relationship
                    path = {
                        "source_id": node1["id"],
                        "target_id": node2["id"],
                        "source_title": node1["title"],
                        "target_title": node2["title"],
                        "path_type": "causal",
                        "common_concepts": list(common_concepts),
                        "explanation": f"{node1['title']} and {node2['title']} are causally related through concepts: {', '.join(common_concepts)}."
                    }
                    
                    reasoning_paths.append(path)
    
    return reasoning_paths

def generate_dot_code_from_graph_data(
    graph_data: Dict[str, Any],
    title: str,
    is_3d: bool = True,
    layout: str = "fdp"
) -> str:
    """
    Generate Graphviz DOT code from graph data.
    
    Args:
        graph_data (Dict[str, Any]): Dictionary containing nodes and edges
        title (str): Title for the knowledge graph
        is_3d (bool): Whether to generate a 3D-like graph
        layout (str): Graphviz layout engine
        
    Returns:
        str: Graphviz DOT code
    """
    nodes = graph_data["nodes"]
    edges = graph_data["edges"]
    
    # Generate DOT code
    dot_code = ["digraph G {"]
    
    # Add graph attributes
    dot_code.append("    // Graph attributes")
    
    if layout == "dot":
        dot_code.append('    graph [rankdir="TB", splines="ortho", nodesep=0.8, ranksep=1.0, fontname="Arial", overlap=false, K=0.6];')
    else:
        dot_code.append(f'    graph [layout="{layout}", splines="spline", overlap=false, fontname="Arial", K=0.6, sep="+25"];')
    
    if is_3d:
        dot_code.append('    node [shape="box", style="filled,rounded", fillcolor="#E8E8E8", gradientangle="315", color="#AAAAAA", fontname="Arial", fontsize=12, margin=0.2];')
        dot_code.append('    edge [color="#777777", penwidth=2.0, arrowsize=0.8];')
    else:
        dot_code.append('    node [shape="box", style="filled", fillcolor="#E8E8E8", color="#333333", fontname="Arial", fontsize=12];')
        dot_code.append('    edge [color="#555555", penwidth=1.0];')
    
    # Add title as a label
    dot_code.append(f'    labelloc="t";')
    dot_code.append(f'    label="{title}";')
    
    # Add nodes
    dot_code.append("\n    // Nodes")
    
    for node in nodes:
        node_id = f"node_{node['id']}"
        title = node["title"].replace('"', '\\"')
        
        # Create tooltip with summary and tags
        tooltip = title
        if node.get("summary"):
            summary = node["summary"].replace('"', '\\"')
            if len(summary) > 100:
                summary = summary[:97] + "..."
            tooltip += "\\n\\n" + summary
        
        if node.get("tags"):
            tags_str = ", ".join(node["tags"])
            tooltip += f"\\n\\nTags: {tags_str}"
        
        tooltip += f"\\n\\nDate: {node['date']}"
        tooltip += f"\\n\\nType: {node['source_type']}"
        
        # Create URL for clickable nodes
        url = f"javascript:alert('Opening note {node['id']}: {title}');"
        
        # Determine node color based on source type
        source_type = node.get("source_type", "text").lower()
        if source_type == "pdf":
            hue = 0  # Red
        elif source_type == "youtube":
            hue = 200  # Blue
        elif source_type == "image":
            hue = 120  # Green
        elif source_type == "speech":
            hue = 270  # Purple
        else:  # text
            hue = 40  # Yellow/Orange
        
        # Add tags to hue calculation
        for tag in node.get("tags", []):
            # Use hash of tag to influence hue
            tag_hash = sum(ord(c) for c in tag)
            hue = (hue + tag_hash) % 360
        
        saturation = 30
        lightness = 85
        
        if is_3d:
            fillcolor = f"\"#{hsl_to_hex(hue, saturation, lightness)}\""
            dot_code.append(f'    {node_id} [label="{title}", tooltip="{tooltip}", URL="{url}", fillcolor={fillcolor}, gradientangle="315"];')
        else:
            fillcolor = f"\"#{hsl_to_hex(hue, saturation, lightness)}\""
            dot_code.append(f'    {node_id} [label="{title}", tooltip="{tooltip}", URL="{url}", fillcolor={fillcolor}];')
    
    # Add edges
    dot_code.append("\n    // Edges")
    
    for edge in edges:
        source_id = f"node_{edge['source']}"
        target_id = f"node_{edge['target']}"
        similarity = edge["similarity"]
        
        # Scale edge properties based on similarity
        penwidth = max(0.5, min(3.0, similarity * 3.0))
        opacity = max(0.3, min(1.0, similarity))
        
        if is_3d:
            # 3D-like edge with similarity as tooltip
            dot_code.append(f'    {source_id} -> {target_id} [penwidth="{penwidth}", color="#777777{int(opacity*255):02x}", tooltip="Similarity: {similarity:.2f}"];')
        else:
            # Simple edge
            dot_code.append(f'    {source_id} -> {target_id} [penwidth="{penwidth}", color="#555555{int(opacity*255):02x}", tooltip="Similarity: {similarity:.2f}"];')
    
    dot_code.append("}")
    
    return "\n".join(dot_code)

def generate_html_knowledge_graph(
    graph_data: Dict[str, Any],
    output_path: str,
    title: str = "Knowledge Graph",
    open_browser: bool = False
) -> Dict[str, Any]:
    """
    Generate an interactive HTML knowledge graph using D3.js.
    
    Args:
        graph_data (Dict[str, Any]): Dictionary containing nodes and edges
        output_path (str): Path to save the HTML file
        title (str): Title for the knowledge graph
        open_browser (bool): Whether to open the output file in a browser
        
    Returns:
        Dict[str, Any]: Dictionary containing the knowledge graph information
    """
    logger.info(f"Generating HTML knowledge graph")
    
    # Convert graph data to D3.js format
    d3_data = {
        "nodes": [],
        "links": []
    }
    
    # Add nodes
    for node in graph_data["nodes"]:
        d3_node = {
            "id": f"node_{node['id']}",
            "note_id": node["id"],
            "title": node["title"],
            "summary": node.get("summary", ""),
            "tags": node.get("tags", []),
            "date": node.get("date", ""),
            "source_type": node.get("source_type", "text")
        }
        
        d3_data["nodes"].append(d3_node)
    
    # Add links
    for edge in graph_data["edges"]:
        d3_link = {
            "source": f"node_{edge['source']}",
            "target": f"node_{edge['target']}",
            "similarity": edge["similarity"]
        }
        
        d3_data["links"].append(d3_link)
    
    # Create HTML template
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        #graph-container {{
            width: 100%;
            height: 100vh;
            overflow: hidden;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            stroke: #aaa;
            stroke-width: 1.5px;
        }}
        .node text {{
            font-size: 12px;
            pointer-events: none;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
        }}
        #tooltip {{
            position: absolute;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 300px;
            display: none;
            z-index: 1000;
        }}
        #tooltip h3 {{
            margin-top: 0;
            margin-bottom: 5px;
        }}
        #tooltip p {{
            margin: 5px 0;
        }}
        #tooltip .tags {{
            margin-top: 8px;
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
        }}
        #tooltip .tag {{
            background-color: #eee;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 11px;
        }}
        #controls {{
            position: absolute;
            top: 10px;
            left: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        #search {{
            margin-bottom: 10px;
        }}
        #search input {{
            padding: 5px;
            width: 200px;
        }}
        #filters {{
            margin-bottom: 10px;
        }}
        #filters select {{
            padding: 5px;
            width: 200px;
        }}
    </style>
</head>
<body>
    <div id="controls">
        <h2>{title}</h2>
        <div id="search">
            <input type="text" id="search-input" placeholder="Search nodes...">
        </div>
        <div id="filters">
            <select id="source-type-filter">
                <option value="all">All Source Types</option>
                <option value="text">Text</option>
                <option value="pdf">PDF</option>
                <option value="youtube">YouTube</option>
                <option value="image">Image</option>
                <option value="speech">Speech</option>
            </select>
        </div>
        <div>
            <button id="zoom-in">Zoom In</button>
            <button id="zoom-out">Zoom Out</button>
            <button id="reset">Reset</button>
        </div>
    </div>
    <div id="tooltip"></div>
    <div id="graph-container"></div>
    
    <script>
        // Graph data
        const graphData = {json.dumps(d3_data)};
        
        // Set up the SVG
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
        
        // Create a group for the graph
        const g = svg.append("g");
        
        // Set up zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        // Create a force simulation
        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(50));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter()
            .append("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.max(1, d.similarity * 3))
            .attr("stroke-opacity", d => Math.max(0.3, d.similarity));
        
        // Create nodes
        const node = g.append("g")
            .selectAll(".node")
            .data(graphData.nodes)
            .enter()
            .append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add circles to nodes
        node.append("circle")
            .attr("r", 10)
            .attr("fill", d => getNodeColor(d.source_type))
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip)
            .on("click", openNote);
        
        // Add labels to nodes
        node.append("text")
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(d => d.title.length > 20 ? d.title.substring(0, 17) + "..." : d.title);
        
        // Set up the simulation tick function
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});
        
        // Function to get node color based on source type
        function getNodeColor(sourceType) {{
            switch(sourceType.toLowerCase()) {{
                case "pdf": return "#ff7f7f"; // Red
                case "youtube": return "#7f7fff"; // Blue
                case "image": return "#7fff7f"; // Green
                case "speech": return "#bf7fff"; // Purple
                default: return "#ffbf7f"; // Yellow/Orange (text)
            }}
        }}
        
        // Tooltip functions
        function showTooltip(event, d) {{
            const tooltip = d3.select("#tooltip");
            
            // Create tooltip content
            let content = `<h3>${{d.title}}</h3>`;
            
            if (d.summary) {{
                content += `<p>${{d.summary.length > 150 ? d.summary.substring(0, 147) + "..." : d.summary}}</p>`;
            }}
            
            content += `<p><strong>Date:</strong> ${{d.date}}</p>`;
            content += `<p><strong>Type:</strong> ${{d.source_type}}</p>`;
            
            if (d.tags && d.tags.length > 0) {{
                content += `<div class="tags">`;
                d.tags.forEach(tag => {{
                    content += `<span class="tag">${{tag}}</span>`;
                }});
                content += `</div>`;
            }}
            
            tooltip.html(content)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY + 10) + "px")
                .style("display", "block");
        }}
        
        function hideTooltip() {{
            d3.select("#tooltip").style("display", "none");
        }}
        
        // Open note function
        function openNote(event, d) {{
            alert(`Opening note ${{d.note_id}}: ${{d.title}}`);
            // In a real implementation, this would open the note in the application
        }}
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Search functionality
        d3.select("#search-input").on("input", function() {{
            const searchTerm = this.value.toLowerCase();
            
            node.each(function(d) {{
                const element = d3.select(this);
                const isMatch = d.title.toLowerCase().includes(searchTerm) || 
                               (d.summary && d.summary.toLowerCase().includes(searchTerm)) ||
                               (d.tags && d.tags.some(tag => tag.toLowerCase().includes(searchTerm)));
                
                element.style("opacity", isMatch || searchTerm === "" ? 1 : 0.2);
            }});
            
            link.style("opacity", searchTerm === "" ? null : 0.1);
        }});
        
        // Source type filter
        d3.select("#source-type-filter").on("change", function() {{
            const selectedType = this.value;
            
            node.each(function(d) {{
                const element = d3.select(this);
                const isMatch = selectedType === "all" || d.source_type.toLowerCase() === selectedType;
                
                element.style("opacity", isMatch ? 1 : 0.2);
            }});
        }});
        
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
    
    # Save HTML file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write HTML file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        logger.info(f"HTML knowledge graph saved to {output_path}")
        
        # Open in browser if requested
        if open_browser:
            try:
                webbrowser.open(f"file://{os.path.abspath(output_path)}")
                logger.info(f"Opened HTML knowledge graph in browser")
            except Exception as e:
                logger.error(f"Error opening HTML knowledge graph in browser: {e}")
        
        return {
            "title": title,
            "output_path": output_path,
            "node_count": len(graph_data["nodes"]),
            "edge_count": len(graph_data["edges"])
        }
        
    except Exception as e:
        logger.error(f"Error generating HTML knowledge graph: {e}")
        return {
            "error": f"Error generating HTML knowledge graph: {e}"
        }

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
def query_knowledge_graph(
    db_manager,
    query: str,
    max_nodes: int = 100,
    similarity_threshold: float = 0.5,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Query the knowledge graph for specific relationships.
    
    Args:
        db_manager: Database manager instance
        query (str): The query to search for (e.g., "prerequisites for CNN backpropagation")
        max_nodes (int): Maximum number of nodes to include
        similarity_threshold (float): Minimum similarity threshold for related notes
        tags (List[str], optional): Filter notes by tags
        
    Returns:
        Dict[str, Any]: Dictionary containing the query results
    """
    logger.info(f"Querying knowledge graph: {query}")
    
    # Extract graph data with reasoning paths
    graph_data = extract_graph_data_from_db(
        db_manager, 
        max_nodes=max_nodes, 
        similarity_threshold=similarity_threshold,
        tags=tags,
        include_reasoning=True
    )
    
    # Parse the query to determine the type of relationship to look for
    query_lower = query.lower()
    
    # Initialize result
    result = {
        "query": query,
        "matches": [],
        "explanation": ""
    }
    
    # Check for prerequisite queries
    if any(term in query_lower for term in ["prerequisite", "prerequisites", "before", "prior"]):
        # Extract the concept from the query
        # This is a simple approach; in a real implementation, you would use NLP techniques
        concept = query_lower.split("for ")[-1].split("understanding ")[-1].strip()
        
        # Find nodes that match the concept
        matching_nodes = []
        for node in graph_data["nodes"]:
            node_title = node["title"].lower()
            if concept in node_title or any(concept in kc.lower() for kc in node.get("key_concepts", [])):
                matching_nodes.append(node)
        
        if matching_nodes:
            # Find prerequisites for the matching nodes
            prerequisites = []
            for node in matching_nodes:
                # Look for prerequisite relationships in reasoning paths
                for path in graph_data.get("reasoning_paths", []):
                    if path.get("path_type") == "prerequisite" and path.get("target_id") == node["id"]:
                        prerequisites.append({
                            "prerequisite": path.get("source_title"),
                            "for_concept": path.get("target_title"),
                            "explanation": path.get("explanation")
                        })
            
            if prerequisites:
                result["matches"] = prerequisites
                result["explanation"] = f"Found {len(prerequisites)} prerequisites for {concept}."
            else:
                result["explanation"] = f"No explicit prerequisites found for {concept}."
        else:
            result["explanation"] = f"Could not find any concepts matching '{concept}' in the knowledge graph."
    
    # Check for causal relationship queries
    elif any(term in query_lower for term in ["cause", "effect", "leads to", "results in", "causal"]):
        # Extract the concept from the query
        parts = re.split(r"cause|effect|leads to|results in|causal", query_lower)
        concept = parts[-1].strip() if len(parts) > 1 else parts[0].strip()
        
        # Find nodes that match the concept
        matching_nodes = []
        for node in graph_data["nodes"]:
            node_title = node["title"].lower()
            if concept in node_title or any(concept in kc.lower() for kc in node.get("key_concepts", [])):
                matching_nodes.append(node)
        
        if matching_nodes:
            # Find causal relationships for the matching nodes
            causal_relations = []
            for node in matching_nodes:
                # Look for causal relationships in reasoning paths
                for path in graph_data.get("reasoning_paths", []):
                    if path.get("path_type") == "causal" and (path.get("source_id") == node["id"] or path.get("target_id") == node["id"]):
                        causal_relations.append({
                            "source": path.get("source_title"),
                            "target": path.get("target_title"),
                            "common_concepts": path.get("common_concepts", []),
                            "explanation": path.get("explanation")
                        })
            
            if causal_relations:
                result["matches"] = causal_relations
                result["explanation"] = f"Found {len(causal_relations)} causal relationships involving {concept}."
            else:
                result["explanation"] = f"No explicit causal relationships found for {concept}."
        else:
            result["explanation"] = f"Could not find any concepts matching '{concept}' in the knowledge graph."
    
    # Check for dependency queries
    elif any(term in query_lower for term in ["depend", "dependency", "dependencies", "relies on"]):
        # Extract the concept from the query
        concept = query_lower.split("for ")[-1].split("of ")[-1].strip()
        
        # Find nodes that match the concept
        matching_nodes = []
        for node in graph_data["nodes"]:
            node_title = node["title"].lower()
            if concept in node_title or any(concept in kc.lower() for kc in node.get("key_concepts", [])):
                matching_nodes.append(node)
        
        if matching_nodes:
            # Find dependencies for the matching nodes
            dependencies = []
            for node in matching_nodes:
                # Look for dependency relationships in edges
                for edge in graph_data["edges"]:
                    if edge.get("target_id") == node["id"] and edge.get("relationship_type") in ["prerequisite", "builds_on"]:
                        source_node = next((n for n in graph_data["nodes"] if n["id"] == edge.get("source")), None)
                        if source_node:
                            dependencies.append({
                                "dependency": source_node.get("title"),
                                "for_concept": node["title"],
                                "relationship_type": edge.get("relationship_type")
                            })
            
            if dependencies:
                result["matches"] = dependencies
                result["explanation"] = f"Found {len(dependencies)} dependencies for {concept}."
            else:
                result["explanation"] = f"No explicit dependencies found for {concept}."
        else:
            result["explanation"] = f"Could not find any concepts matching '{concept}' in the knowledge graph."
    
    # General relationship query
    else:
        # Extract concepts from the query
        # This is a simple approach; in a real implementation, you would use NLP techniques
        words = query_lower.split()
        potential_concepts = [w for w in words if len(w) > 3 and w not in ["what", "show", "tell", "about", "between", "relationship"]]
        
        # Find relationships between potential concepts
        relationships = []
        for concept in potential_concepts:
            for node in graph_data["nodes"]:
                node_title = node["title"].lower()
                if concept in node_title or any(concept in kc.lower() for kc in node.get("key_concepts", [])):
                    # Look for relationships in reasoning paths
                    for path in graph_data.get("reasoning_paths", []):
                        if path.get("source_id") == node["id"] or path.get("target_id") == node["id"]:
                            relationships.append({
                                "source": path.get("source_title"),
                                "target": path.get("target_title"),
                                "path_type": path.get("path_type"),
                                "explanation": path.get("explanation")
                            })
        
        if relationships:
            result["matches"] = relationships
            result["explanation"] = f"Found {len(relationships)} relationships related to your query."
        else:
            result["explanation"] = "Could not find any relevant relationships in the knowledge graph."
    
    return result