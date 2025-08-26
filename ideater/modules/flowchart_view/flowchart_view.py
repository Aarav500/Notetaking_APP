"""
Flowchart & UX Ideation View module for the Ideater application.

This module provides functionality for generating and visualizing flowcharts,
sequence diagrams, state machine diagrams, and component diagrams.
"""

import os
import json
import logging
import subprocess
import tempfile
from enum import Enum
from typing import List, Dict, Any, Optional, Union, Tuple

try:
    import openai
except ImportError:
    openai = None

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for when pydantic is not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(**kwargs):
        return None

from .config import config

# Set up logging
logger = logging.getLogger("ideater.modules.flowchart_view")

class DiagramType(str, Enum):
    """Enum for diagram types."""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    STATE_MACHINE = "stateDiagram"
    COMPONENT = "classDiagram"  # Using class diagram for components

class DiagramNode(BaseModel):
    """Model for a diagram node."""
    id: str
    label: str
    type: Optional[str] = None
    style: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, float]] = None

class DiagramEdge(BaseModel):
    """Model for a diagram edge."""
    source: str
    target: str
    label: Optional[str] = None
    style: Optional[Dict[str, Any]] = None

class FlowchartRequest(BaseModel):
    """Request model for generating a flowchart."""
    description: str
    title: Optional[str] = None
    node_types: Optional[List[str]] = None
    include_explanation: bool = True

class FlowchartResult(BaseModel):
    """Result model for a generated flowchart."""
    mermaid_code: str
    nodes: List[DiagramNode]
    edges: List[DiagramEdge]
    explanation: Optional[str] = None
    svg_data: Optional[str] = None

class SequenceDiagramRequest(BaseModel):
    """Request model for generating a sequence diagram."""
    description: str
    title: Optional[str] = None
    actors: Optional[List[str]] = None
    include_explanation: bool = True

class SequenceDiagramResult(BaseModel):
    """Result model for a generated sequence diagram."""
    mermaid_code: str
    actors: List[str]
    messages: List[Dict[str, Any]]
    explanation: Optional[str] = None
    svg_data: Optional[str] = None

class StateMachineDiagramRequest(BaseModel):
    """Request model for generating a state machine diagram."""
    description: str
    title: Optional[str] = None
    initial_state: Optional[str] = None
    include_explanation: bool = True

class StateMachineDiagramResult(BaseModel):
    """Result model for a generated state machine diagram."""
    mermaid_code: str
    states: List[str]
    transitions: List[Dict[str, Any]]
    explanation: Optional[str] = None
    svg_data: Optional[str] = None

class ComponentDiagramRequest(BaseModel):
    """Request model for generating a component diagram."""
    description: str
    title: Optional[str] = None
    components: Optional[List[str]] = None
    include_explanation: bool = True

class ComponentDiagramResult(BaseModel):
    """Result model for a generated component diagram."""
    mermaid_code: str
    components: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    explanation: Optional[str] = None
    svg_data: Optional[str] = None

class FlowchartView:
    """
    Main class for the Flowchart & UX Ideation View module.
    
    This class provides methods for generating and visualizing flowcharts,
    sequence diagrams, state machine diagrams, and component diagrams.
    """
    
    def __init__(self):
        """Initialize the FlowchartView."""
        self.openai_api_key = config.get_openai_api_key()
        self.openai_model = config.get_openai_model()
        self.temperature = config.get_temperature()
        self.max_tokens = config.get_max_tokens()
        self.mermaid_cli_path = config.get_mermaid_cli_path()
        self.graphviz_path = config.get_graphviz_path()
        
        # Initialize OpenAI client if available
        if openai and self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.client = openai.OpenAI()
        else:
            self.client = None
            logger.warning("OpenAI client not available. Some features may not work.")
    
    def generate_flowchart(self, request: FlowchartRequest) -> FlowchartResult:
        """
        Generate a flowchart based on the request.
        
        Args:
            request: The flowchart request.
            
        Returns:
            The flowchart result.
        """
        logger.info(f"Generating flowchart: {request.title or 'Untitled'}")
        
        # Generate Mermaid code using OpenAI
        mermaid_code = self._generate_mermaid_code(
            diagram_type=DiagramType.FLOWCHART,
            description=request.description,
            title=request.title,
            additional_info={"node_types": request.node_types} if request.node_types else None
        )
        
        # Parse the Mermaid code to extract nodes and edges
        nodes, edges = self._parse_flowchart_mermaid(mermaid_code)
        
        # Generate explanation if requested
        explanation = None
        if request.include_explanation:
            explanation = self._generate_explanation(
                diagram_type=DiagramType.FLOWCHART,
                mermaid_code=mermaid_code,
                title=request.title
            )
        
        # Generate SVG data
        svg_data = self._generate_svg(mermaid_code)
        
        return FlowchartResult(
            mermaid_code=mermaid_code,
            nodes=nodes,
            edges=edges,
            explanation=explanation,
            svg_data=svg_data
        )
    
    def generate_sequence_diagram(self, request: SequenceDiagramRequest) -> SequenceDiagramResult:
        """
        Generate a sequence diagram based on the request.
        
        Args:
            request: The sequence diagram request.
            
        Returns:
            The sequence diagram result.
        """
        logger.info(f"Generating sequence diagram: {request.title or 'Untitled'}")
        
        # Generate Mermaid code using OpenAI
        mermaid_code = self._generate_mermaid_code(
            diagram_type=DiagramType.SEQUENCE,
            description=request.description,
            title=request.title,
            additional_info={"actors": request.actors} if request.actors else None
        )
        
        # Parse the Mermaid code to extract actors and messages
        actors, messages = self._parse_sequence_mermaid(mermaid_code)
        
        # Generate explanation if requested
        explanation = None
        if request.include_explanation:
            explanation = self._generate_explanation(
                diagram_type=DiagramType.SEQUENCE,
                mermaid_code=mermaid_code,
                title=request.title
            )
        
        # Generate SVG data
        svg_data = self._generate_svg(mermaid_code)
        
        return SequenceDiagramResult(
            mermaid_code=mermaid_code,
            actors=actors,
            messages=messages,
            explanation=explanation,
            svg_data=svg_data
        )
    
    def generate_state_machine_diagram(self, request: StateMachineDiagramRequest) -> StateMachineDiagramResult:
        """
        Generate a state machine diagram based on the request.
        
        Args:
            request: The state machine diagram request.
            
        Returns:
            The state machine diagram result.
        """
        logger.info(f"Generating state machine diagram: {request.title or 'Untitled'}")
        
        # Generate Mermaid code using OpenAI
        mermaid_code = self._generate_mermaid_code(
            diagram_type=DiagramType.STATE_MACHINE,
            description=request.description,
            title=request.title,
            additional_info={"initial_state": request.initial_state} if request.initial_state else None
        )
        
        # Parse the Mermaid code to extract states and transitions
        states, transitions = self._parse_state_machine_mermaid(mermaid_code)
        
        # Generate explanation if requested
        explanation = None
        if request.include_explanation:
            explanation = self._generate_explanation(
                diagram_type=DiagramType.STATE_MACHINE,
                mermaid_code=mermaid_code,
                title=request.title
            )
        
        # Generate SVG data
        svg_data = self._generate_svg(mermaid_code)
        
        return StateMachineDiagramResult(
            mermaid_code=mermaid_code,
            states=states,
            transitions=transitions,
            explanation=explanation,
            svg_data=svg_data
        )
    
    def generate_component_diagram(self, request: ComponentDiagramRequest) -> ComponentDiagramResult:
        """
        Generate a component diagram based on the request.
        
        Args:
            request: The component diagram request.
            
        Returns:
            The component diagram result.
        """
        logger.info(f"Generating component diagram: {request.title or 'Untitled'}")
        
        # Generate Mermaid code using OpenAI
        mermaid_code = self._generate_mermaid_code(
            diagram_type=DiagramType.COMPONENT,
            description=request.description,
            title=request.title,
            additional_info={"components": request.components} if request.components else None
        )
        
        # Parse the Mermaid code to extract components and relationships
        components, relationships = self._parse_component_mermaid(mermaid_code)
        
        # Generate explanation if requested
        explanation = None
        if request.include_explanation:
            explanation = self._generate_explanation(
                diagram_type=DiagramType.COMPONENT,
                mermaid_code=mermaid_code,
                title=request.title
            )
        
        # Generate SVG data
        svg_data = self._generate_svg(mermaid_code)
        
        return ComponentDiagramResult(
            mermaid_code=mermaid_code,
            components=components,
            relationships=relationships,
            explanation=explanation,
            svg_data=svg_data
        )
    
    def update_diagram(self, diagram_type: DiagramType, mermaid_code: str, instructions: str) -> str:
        """
        Update a diagram based on natural language instructions.
        
        Args:
            diagram_type: The type of diagram.
            mermaid_code: The current Mermaid code.
            instructions: Natural language instructions for updating the diagram.
            
        Returns:
            The updated Mermaid code.
        """
        logger.info(f"Updating {diagram_type.value} diagram")
        
        if not self.client:
            logger.error("OpenAI client not available. Cannot update diagram.")
            return mermaid_code
        
        try:
            # Create a prompt for updating the diagram
            prompt = f"""
            You are an expert at creating and updating Mermaid diagrams. You have been given the following Mermaid code for a {diagram_type.value} diagram:
            
            ```mermaid
            {mermaid_code}
            ```
            
            Please update this diagram based on the following instructions:
            
            {instructions}
            
            Return only the updated Mermaid code without any additional text or explanation.
            """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating and updating Mermaid diagrams."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the updated Mermaid code from the response
            updated_code = response.choices[0].message.content.strip()
            
            # Remove any markdown code block markers
            updated_code = updated_code.replace("```mermaid", "").replace("```", "").strip()
            
            return updated_code
            
        except Exception as e:
            logger.error(f"Error updating diagram: {str(e)}")
            return mermaid_code
    
    def _generate_mermaid_code(
        self,
        diagram_type: DiagramType,
        description: str,
        title: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate Mermaid code using OpenAI.
        
        Args:
            diagram_type: The type of diagram.
            description: The description of the diagram.
            title: The title of the diagram.
            additional_info: Additional information for the diagram.
            
        Returns:
            The generated Mermaid code.
        """
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate Mermaid code.")
            return f"{diagram_type.value}\n    A[Start] --> B[End]"
        
        try:
            # Create a prompt for generating the diagram
            prompt = f"""
            You are an expert at creating Mermaid diagrams. Please create a {diagram_type.value} diagram based on the following description:
            
            {description}
            """
            
            if title:
                prompt += f"\n\nThe title of the diagram is: {title}"
            
            if additional_info:
                prompt += "\n\nAdditional information:"
                for key, value in additional_info.items():
                    prompt += f"\n- {key}: {value}"
            
            prompt += "\n\nPlease return only the Mermaid code without any additional text or explanation."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating Mermaid diagrams."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the Mermaid code from the response
            mermaid_code = response.choices[0].message.content.strip()
            
            # Remove any markdown code block markers
            mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
            
            return mermaid_code
            
        except Exception as e:
            logger.error(f"Error generating Mermaid code: {str(e)}")
            return f"{diagram_type.value}\n    A[Start] --> B[End]"
    
    def _generate_explanation(
        self,
        diagram_type: DiagramType,
        mermaid_code: str,
        title: Optional[str] = None
    ) -> str:
        """
        Generate an explanation for a diagram.
        
        Args:
            diagram_type: The type of diagram.
            mermaid_code: The Mermaid code.
            title: The title of the diagram.
            
        Returns:
            The generated explanation.
        """
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate explanation.")
            return "Explanation not available."
        
        try:
            # Create a prompt for generating the explanation
            prompt = f"""
            You are an expert at explaining Mermaid diagrams. Please explain the following {diagram_type.value} diagram:
            
            ```mermaid
            {mermaid_code}
            ```
            """
            
            if title:
                prompt += f"\n\nThe title of the diagram is: {title}"
            
            prompt += "\n\nPlease provide a clear and concise explanation of the diagram, including its purpose, components, and relationships."
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert at explaining Mermaid diagrams."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the explanation from the response
            explanation = response.choices[0].message.content.strip()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return "Explanation not available."
    
    def _generate_svg(self, mermaid_code: str) -> Optional[str]:
        """
        Generate SVG data from Mermaid code.
        
        Args:
            mermaid_code: The Mermaid code.
            
        Returns:
            The generated SVG data, or None if generation fails.
        """
        try:
            # Create a temporary file for the Mermaid code
            with tempfile.NamedTemporaryFile(suffix=".mmd", delete=False) as mmd_file:
                mmd_file.write(mermaid_code.encode("utf-8"))
                mmd_file_path = mmd_file.name
            
            # Create a temporary file for the SVG output
            svg_file_path = mmd_file_path + ".svg"
            
            # Run the Mermaid CLI to generate the SVG
            cmd = [self.mermaid_cli_path, "-i", mmd_file_path, "-o", svg_file_path]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Read the SVG data
            with open(svg_file_path, "r", encoding="utf-8") as svg_file:
                svg_data = svg_file.read()
            
            # Clean up temporary files
            os.remove(mmd_file_path)
            os.remove(svg_file_path)
            
            return svg_data
            
        except Exception as e:
            logger.error(f"Error generating SVG: {str(e)}")
            return None
    
    def _parse_flowchart_mermaid(self, mermaid_code: str) -> Tuple[List[DiagramNode], List[DiagramEdge]]:
        """
        Parse Mermaid flowchart code to extract nodes and edges.
        
        Args:
            mermaid_code: The Mermaid flowchart code.
            
        Returns:
            A tuple of (nodes, edges).
        """
        nodes = []
        edges = []
        
        # Simple regex-based parsing (not comprehensive)
        lines = mermaid_code.split("\n")
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and the flowchart declaration
            if not line or line.startswith("flowchart"):
                continue
            
            # Check if the line defines an edge
            if "-->" in line or "---" in line or "==>" in line:
                # Extract source and target nodes
                parts = line.split("-->") if "-->" in line else line.split("---") if "---" in line else line.split("==>")
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    
                    # Extract node IDs
                    source_id = source.split("[")[0].strip() if "[" in source else source
                    target_id = target.split("[")[0].strip() if "[" in target else target
                    
                    # Extract edge label if present
                    label = None
                    if "|" in line:
                        label_parts = line.split("|")
                        if len(label_parts) > 1:
                            label = label_parts[1].split("|")[0].strip()
                    
                    edges.append(DiagramEdge(
                        source=source_id,
                        target=target_id,
                        label=label
                    ))
            
            # Check if the line defines a node
            elif "[" in line and "]" in line:
                # Extract node ID and label
                parts = line.split("[")
                if len(parts) == 2:
                    node_id = parts[0].strip()
                    node_label = parts[1].split("]")[0].strip()
                    
                    nodes.append(DiagramNode(
                        id=node_id,
                        label=node_label
                    ))
        
        return nodes, edges
    
    def _parse_sequence_mermaid(self, mermaid_code: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Parse Mermaid sequence diagram code to extract actors and messages.
        
        Args:
            mermaid_code: The Mermaid sequence diagram code.
            
        Returns:
            A tuple of (actors, messages).
        """
        actors = []
        messages = []
        
        # Simple regex-based parsing (not comprehensive)
        lines = mermaid_code.split("\n")
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and the sequence diagram declaration
            if not line or line.startswith("sequenceDiagram"):
                continue
            
            # Check if the line defines an actor
            if line.startswith("participant") or line.startswith("actor"):
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    actor = parts[1].strip()
                    actors.append(actor)
            
            # Check if the line defines a message
            elif "->" in line or "-->>" in line:
                parts = line.split("->") if "->" in line else line.split("-->>")
                if len(parts) == 2:
                    source = parts[0].strip()
                    target_and_message = parts[1].strip()
                    
                    # Extract target and message
                    target_message_parts = target_and_message.split(":", 1)
                    target = target_message_parts[0].strip()
                    message = target_message_parts[1].strip() if len(target_message_parts) > 1 else ""
                    
                    messages.append({
                        "source": source,
                        "target": target,
                        "message": message
                    })
        
        return actors, messages
    
    def _parse_state_machine_mermaid(self, mermaid_code: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Parse Mermaid state machine diagram code to extract states and transitions.
        
        Args:
            mermaid_code: The Mermaid state machine diagram code.
            
        Returns:
            A tuple of (states, transitions).
        """
        states = []
        transitions = []
        
        # Simple regex-based parsing (not comprehensive)
        lines = mermaid_code.split("\n")
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and the state diagram declaration
            if not line or line.startswith("stateDiagram"):
                continue
            
            # Check if the line defines a state
            if "[*]" not in line and "-->" not in line and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    state = parts[0].strip()
                    if state not in states:
                        states.append(state)
            
            # Check if the line defines a transition
            elif "-->" in line:
                parts = line.split("-->")
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    
                    # Extract transition label if present
                    label = None
                    if ":" in target:
                        target_parts = target.split(":", 1)
                        target = target_parts[0].strip()
                        label = target_parts[1].strip()
                    
                    # Add states if not already added
                    if source != "[*]" and source not in states:
                        states.append(source)
                    if target != "[*]" and target not in states:
                        states.append(target)
                    
                    transitions.append({
                        "source": source,
                        "target": target,
                        "label": label
                    })
        
        return states, transitions
    
    def _parse_component_mermaid(self, mermaid_code: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parse Mermaid component diagram code to extract components and relationships.
        
        Args:
            mermaid_code: The Mermaid component diagram code.
            
        Returns:
            A tuple of (components, relationships).
        """
        components = []
        relationships = []
        
        # Simple regex-based parsing (not comprehensive)
        lines = mermaid_code.split("\n")
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and the class diagram declaration
            if not line or line.startswith("classDiagram"):
                continue
            
            # Check if the line defines a component
            if "class" in line:
                parts = line.split("class", 1)
                if len(parts) == 2:
                    component_name = parts[1].strip()
                    components.append({
                        "name": component_name,
                        "type": "component"
                    })
            
            # Check if the line defines a relationship
            elif "-->" in line or "<--" in line or "--" in line:
                relationship_type = "uses" if "-->" in line else "used by" if "<--" in line else "related to"
                separator = "-->" if "-->" in line else "<--" if "<--" in line else "--"
                parts = line.split(separator)
                if len(parts) == 2:
                    source = parts[0].strip()
                    target = parts[1].strip()
                    
                    # Extract relationship label if present
                    label = relationship_type
                    if ":" in line:
                        label_parts = line.split(":", 1)
                        if len(label_parts) > 1:
                            label = label_parts[1].strip()
                    
                    relationships.append({
                        "source": source,
                        "target": target,
                        "type": relationship_type,
                        "label": label
                    })
        
        return components, relationships