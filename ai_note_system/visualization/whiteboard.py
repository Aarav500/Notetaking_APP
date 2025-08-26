"""
Integrated Whiteboard Reasoning & Note Mapping

This module provides functionality for creating and managing interactive whiteboards
with mind maps and diagrams. It supports manual sketching and AI-assisted features
like auto-labeling and conversion to structured notes.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import uuid
import base64
import re

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class WhiteboardElement:
    """Base class for whiteboard elements"""
    def __init__(self, element_id: str, element_type: str, 
                 position: Tuple[float, float], 
                 properties: Dict[str, Any] = None):
        self.id = element_id or str(uuid.uuid4())
        self.type = element_type
        self.position = position
        self.properties = properties or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'position': self.position,
            'properties': self.properties,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WhiteboardElement':
        """Create from dictionary"""
        element = cls(
            element_id=data.get('id'),
            element_type=data.get('type'),
            position=data.get('position'),
            properties=data.get('properties')
        )
        element.created_at = data.get('created_at', element.created_at)
        element.updated_at = data.get('updated_at', element.updated_at)
        return element

class Whiteboard:
    """
    Integrated Whiteboard for Reasoning & Note Mapping
    
    Features:
    - Create and manage interactive whiteboards
    - Sketch mind maps and diagrams
    - Link to notes automatically
    - AI auto-labeling of sketches
    - Convert diagrams to structured markdown notes
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None):
        """Initialize the whiteboard"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create whiteboards table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS whiteboards (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            width INTEGER NOT NULL DEFAULT 1920,
            height INTEGER NOT NULL DEFAULT 1080,
            background_color TEXT DEFAULT '#FFFFFF',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create whiteboard elements table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS whiteboard_elements (
            id TEXT PRIMARY KEY,
            whiteboard_id INTEGER NOT NULL,
            element_type TEXT NOT NULL,
            position_x REAL NOT NULL,
            position_y REAL NOT NULL,
            properties TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (whiteboard_id) REFERENCES whiteboards(id)
        )
        ''')
        
        # Create whiteboard links table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS whiteboard_links (
            id INTEGER PRIMARY KEY,
            whiteboard_id INTEGER NOT NULL,
            source_element_id TEXT NOT NULL,
            target_element_id TEXT NOT NULL,
            link_type TEXT NOT NULL,
            properties TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (whiteboard_id) REFERENCES whiteboards(id),
            FOREIGN KEY (source_element_id) REFERENCES whiteboard_elements(id),
            FOREIGN KEY (target_element_id) REFERENCES whiteboard_elements(id)
        )
        ''')
        
        # Create whiteboard note links table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS whiteboard_note_links (
            id INTEGER PRIMARY KEY,
            whiteboard_id INTEGER NOT NULL,
            element_id TEXT NOT NULL,
            note_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (whiteboard_id) REFERENCES whiteboards(id),
            FOREIGN KEY (element_id) REFERENCES whiteboard_elements(id),
            FOREIGN KEY (note_id) REFERENCES notes(id)
        )
        ''')
        
        conn.commit()
    
    def create_whiteboard(self, user_id: int, title: str, 
                         description: Optional[str] = None,
                         width: int = 1920, height: int = 1080,
                         background_color: str = '#FFFFFF') -> int:
        """
        Create a new whiteboard
        
        Args:
            user_id: The ID of the user
            title: The title of the whiteboard
            description: Optional description of the whiteboard
            width: Width of the whiteboard canvas
            height: Height of the whiteboard canvas
            background_color: Background color of the whiteboard
            
        Returns:
            The ID of the created whiteboard
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO whiteboards (user_id, title, description, created_at, updated_at, width, height, background_color)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, description, now, now, width, height, background_color))
        
        whiteboard_id = cursor.lastrowid
        conn.commit()
        
        return whiteboard_id
    
    def get_whiteboard(self, whiteboard_id: int) -> Dict[str, Any]:
        """
        Get a whiteboard by ID
        
        Args:
            whiteboard_id: The ID of the whiteboard
            
        Returns:
            Dictionary with whiteboard details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, title, description, created_at, updated_at, width, height, background_color
        FROM whiteboards
        WHERE id = ?
        ''', (whiteboard_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        whiteboard = {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'description': row[3],
            'created_at': row[4],
            'updated_at': row[5],
            'width': row[6],
            'height': row[7],
            'background_color': row[8],
            'elements': self.get_whiteboard_elements(row[0]),
            'links': self.get_whiteboard_links(row[0]),
            'note_links': self.get_whiteboard_note_links(row[0])
        }
        
        return whiteboard
    
    def get_user_whiteboards(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get whiteboards for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of whiteboards to return
            
        Returns:
            List of whiteboard summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, description, created_at, updated_at
        FROM whiteboards
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        whiteboards = []
        for row in cursor.fetchall():
            whiteboard = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'created_at': row[3],
                'updated_at': row[4]
            }
            whiteboards.append(whiteboard)
        
        return whiteboards
    
    def add_element(self, whiteboard_id: int, element_type: str,
                  position: Tuple[float, float],
                  properties: Dict[str, Any] = None) -> str:
        """
        Add an element to a whiteboard
        
        Args:
            whiteboard_id: The ID of the whiteboard
            element_type: The type of element (text, shape, image, etc.)
            position: The (x, y) position of the element
            properties: Additional properties of the element
            
        Returns:
            The ID of the created element
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        element_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO whiteboard_elements (id, whiteboard_id, element_type, position_x, position_y, properties, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (element_id, whiteboard_id, element_type, position[0], position[1], json.dumps(properties or {}), now, now))
        
        # Update the whiteboard's updated_at timestamp
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        return element_id
    
    def update_element(self, element_id: str, position: Optional[Tuple[float, float]] = None,
                     properties: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an element on a whiteboard
        
        Args:
            element_id: The ID of the element
            position: Optional new position of the element
            properties: Optional new properties of the element
            
        Returns:
            True if the element was updated, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get the current element data
        cursor.execute('''
        SELECT whiteboard_id, element_type, position_x, position_y, properties
        FROM whiteboard_elements
        WHERE id = ?
        ''', (element_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return False
        
        whiteboard_id, element_type, current_x, current_y, current_properties_json = row
        
        # Update the element
        now = datetime.now().isoformat()
        
        if position is not None:
            new_x, new_y = position
        else:
            new_x, new_y = current_x, current_y
        
        if properties is not None:
            new_properties = properties
        else:
            new_properties = json.loads(current_properties_json)
        
        cursor.execute('''
        UPDATE whiteboard_elements
        SET position_x = ?, position_y = ?, properties = ?, updated_at = ?
        WHERE id = ?
        ''', (new_x, new_y, json.dumps(new_properties), now, element_id))
        
        # Update the whiteboard's updated_at timestamp
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        return True
    
    def delete_element(self, element_id: str) -> bool:
        """
        Delete an element from a whiteboard
        
        Args:
            element_id: The ID of the element
            
        Returns:
            True if the element was deleted, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get the whiteboard ID
        cursor.execute('''
        SELECT whiteboard_id FROM whiteboard_elements
        WHERE id = ?
        ''', (element_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return False
        
        whiteboard_id = row[0]
        
        # Delete any links involving this element
        cursor.execute('''
        DELETE FROM whiteboard_links
        WHERE source_element_id = ? OR target_element_id = ?
        ''', (element_id, element_id))
        
        # Delete any note links involving this element
        cursor.execute('''
        DELETE FROM whiteboard_note_links
        WHERE element_id = ?
        ''', (element_id,))
        
        # Delete the element
        cursor.execute('''
        DELETE FROM whiteboard_elements
        WHERE id = ?
        ''', (element_id,))
        
        # Update the whiteboard's updated_at timestamp
        now = datetime.now().isoformat()
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        return True
    
    def add_link(self, whiteboard_id: int, source_element_id: str,
               target_element_id: str, link_type: str = 'default',
               properties: Dict[str, Any] = None) -> int:
        """
        Add a link between elements on a whiteboard
        
        Args:
            whiteboard_id: The ID of the whiteboard
            source_element_id: The ID of the source element
            target_element_id: The ID of the target element
            link_type: The type of link
            properties: Additional properties of the link
            
        Returns:
            The ID of the created link
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO whiteboard_links (whiteboard_id, source_element_id, target_element_id, link_type, properties, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (whiteboard_id, source_element_id, target_element_id, link_type, json.dumps(properties or {}), now))
        
        link_id = cursor.lastrowid
        
        # Update the whiteboard's updated_at timestamp
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        return link_id
    
    def delete_link(self, link_id: int) -> bool:
        """
        Delete a link from a whiteboard
        
        Args:
            link_id: The ID of the link
            
        Returns:
            True if the link was deleted, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get the whiteboard ID
        cursor.execute('''
        SELECT whiteboard_id FROM whiteboard_links
        WHERE id = ?
        ''', (link_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return False
        
        whiteboard_id = row[0]
        
        # Delete the link
        cursor.execute('''
        DELETE FROM whiteboard_links
        WHERE id = ?
        ''', (link_id,))
        
        # Update the whiteboard's updated_at timestamp
        now = datetime.now().isoformat()
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        return True
    
    def link_to_note(self, whiteboard_id: int, element_id: str, note_id: int) -> int:
        """
        Link a whiteboard element to a note
        
        Args:
            whiteboard_id: The ID of the whiteboard
            element_id: The ID of the element
            note_id: The ID of the note
            
        Returns:
            The ID of the created link
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO whiteboard_note_links (whiteboard_id, element_id, note_id, created_at)
        VALUES (?, ?, ?, ?)
        ''', (whiteboard_id, element_id, note_id, now))
        
        link_id = cursor.lastrowid
        
        # Update the whiteboard's updated_at timestamp
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        return link_id
    
    def get_whiteboard_elements(self, whiteboard_id: int) -> List[Dict[str, Any]]:
        """
        Get elements for a whiteboard
        
        Args:
            whiteboard_id: The ID of the whiteboard
            
        Returns:
            List of elements
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, element_type, position_x, position_y, properties, created_at, updated_at
        FROM whiteboard_elements
        WHERE whiteboard_id = ?
        ''', (whiteboard_id,))
        
        elements = []
        for row in cursor.fetchall():
            element = {
                'id': row[0],
                'type': row[1],
                'position': (row[2], row[3]),
                'properties': json.loads(row[4]),
                'created_at': row[5],
                'updated_at': row[6]
            }
            elements.append(element)
        
        return elements
    
    def get_whiteboard_links(self, whiteboard_id: int) -> List[Dict[str, Any]]:
        """
        Get links for a whiteboard
        
        Args:
            whiteboard_id: The ID of the whiteboard
            
        Returns:
            List of links
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, source_element_id, target_element_id, link_type, properties, created_at
        FROM whiteboard_links
        WHERE whiteboard_id = ?
        ''', (whiteboard_id,))
        
        links = []
        for row in cursor.fetchall():
            link = {
                'id': row[0],
                'source_id': row[1],
                'target_id': row[2],
                'type': row[3],
                'properties': json.loads(row[4]) if row[4] else {},
                'created_at': row[5]
            }
            links.append(link)
        
        return links
    
    def get_whiteboard_note_links(self, whiteboard_id: int) -> List[Dict[str, Any]]:
        """
        Get note links for a whiteboard
        
        Args:
            whiteboard_id: The ID of the whiteboard
            
        Returns:
            List of note links
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT wnl.id, wnl.element_id, wnl.note_id, wnl.created_at, n.title
        FROM whiteboard_note_links wnl
        JOIN notes n ON wnl.note_id = n.id
        WHERE wnl.whiteboard_id = ?
        ''', (whiteboard_id,))
        
        note_links = []
        for row in cursor.fetchall():
            note_link = {
                'id': row[0],
                'element_id': row[1],
                'note_id': row[2],
                'created_at': row[3],
                'note_title': row[4]
            }
            note_links.append(note_link)
        
        return note_links
    
    def auto_label_sketch(self, whiteboard_id: int, element_id: str) -> Dict[str, Any]:
        """
        Automatically label a sketch using AI
        
        Args:
            whiteboard_id: The ID of the whiteboard
            element_id: The ID of the element to label
            
        Returns:
            Dictionary with the updated element
        """
        # Get the element
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT element_type, properties
        FROM whiteboard_elements
        WHERE id = ? AND whiteboard_id = ?
        ''', (element_id, whiteboard_id))
        
        row = cursor.fetchone()
        
        if not row:
            return {'error': 'Element not found'}
        
        element_type, properties_json = row
        properties = json.loads(properties_json)
        
        # Only process sketch elements
        if element_type != 'sketch' and element_type != 'drawing':
            return {'error': 'Element is not a sketch or drawing'}
        
        # Get the sketch data
        sketch_data = properties.get('data', '')
        
        if not sketch_data:
            return {'error': 'No sketch data found'}
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an AI assistant that can recognize and label hand-drawn sketches.
        
        I have a sketch that I need you to identify and label. The sketch is represented as a series of strokes.
        
        Based on the sketch data, what do you think this sketch represents? Provide a concise label and a brief description.
        
        Format your response as JSON:
        ```json
        {{
          "label": "Concise label for the sketch",
          "description": "Brief description of what the sketch appears to represent",
          "confidence": 0.85  // Your confidence level from 0.0 to 1.0
        }}
        ```
        """
        
        # Generate label using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=300)
        
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without the markdown code block
            json_match = re.search(r'\{\s*"label".*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return {'error': 'Failed to extract label from AI response'}
        
        try:
            label_data = json.loads(json_str)
        except json.JSONDecodeError:
            return {'error': 'Failed to parse label data from AI response'}
        
        # Update the element properties with the label
        properties['label'] = label_data.get('label', 'Unknown')
        properties['description'] = label_data.get('description', '')
        properties['ai_labeled'] = True
        properties['label_confidence'] = label_data.get('confidence', 0.0)
        
        # Update the element in the database
        now = datetime.now().isoformat()
        cursor.execute('''
        UPDATE whiteboard_elements
        SET properties = ?, updated_at = ?
        WHERE id = ?
        ''', (json.dumps(properties), now, element_id))
        
        # Update the whiteboard's updated_at timestamp
        cursor.execute('''
        UPDATE whiteboards
        SET updated_at = ?
        WHERE id = ?
        ''', (now, whiteboard_id))
        
        conn.commit()
        
        # Return the updated element
        return {
            'id': element_id,
            'type': element_type,
            'properties': properties,
            'label': label_data.get('label', 'Unknown'),
            'description': label_data.get('description', ''),
            'confidence': label_data.get('confidence', 0.0)
        }
    
    def convert_to_markdown(self, whiteboard_id: int) -> Dict[str, Any]:
        """
        Convert a whiteboard to structured markdown notes
        
        Args:
            whiteboard_id: The ID of the whiteboard
            
        Returns:
            Dictionary with the generated markdown
        """
        # Get the whiteboard
        whiteboard = self.get_whiteboard(whiteboard_id)
        
        if not whiteboard:
            return {'error': 'Whiteboard not found'}
        
        # Get elements and links
        elements = whiteboard.get('elements', [])
        links = whiteboard.get('links', [])
        
        # Prepare data for conversion
        elements_by_id = {element['id']: element for element in elements}
        
        # Build a graph of connected elements
        graph = {}
        for link in links:
            source_id = link['source_id']
            target_id = link['target_id']
            
            if source_id not in graph:
                graph[source_id] = []
            
            graph[source_id].append({
                'target_id': target_id,
                'link_type': link['type'],
                'properties': link['properties']
            })
        
        # Prepare prompt for LLM
        elements_text = ""
        for element in elements:
            elements_text += f"Element ID: {element['id']}\n"
            elements_text += f"Type: {element['type']}\n"
            
            if 'label' in element['properties']:
                elements_text += f"Label: {element['properties']['label']}\n"
            
            if 'text' in element['properties']:
                elements_text += f"Text: {element['properties']['text']}\n"
            
            if 'description' in element['properties']:
                elements_text += f"Description: {element['properties']['description']}\n"
            
            elements_text += "\n"
        
        links_text = ""
        for link in links:
            source_element = elements_by_id.get(link['source_id'], {})
            target_element = elements_by_id.get(link['target_id'], {})
            
            source_label = source_element.get('properties', {}).get('label', source_element.get('id', 'Unknown'))
            target_label = target_element.get('properties', {}).get('label', target_element.get('id', 'Unknown'))
            
            links_text += f"Link: {source_label} -> {target_label}\n"
            links_text += f"Type: {link['type']}\n\n"
        
        prompt = f"""
        You are an AI assistant that can convert whiteboard diagrams to structured markdown notes.
        
        I have a whiteboard with the following elements and links:
        
        Whiteboard Title: {whiteboard['title']}
        Description: {whiteboard.get('description', 'No description')}
        
        Elements:
        {elements_text}
        
        Links:
        {links_text}
        
        Please convert this whiteboard into a well-structured markdown document that captures the relationships and hierarchy between elements.
        
        The markdown should include:
        1. A title and introduction
        2. Sections based on the main elements
        3. Proper hierarchy and relationships based on the links
        4. Any additional context or explanations that would make the notes more useful
        
        Format your response as markdown with proper headings, lists, and formatting.
        """
        
        # Generate markdown using LLM
        markdown = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        return {
            'whiteboard_id': whiteboard_id,
            'title': whiteboard['title'],
            'markdown': markdown
        }
    
    def convert_to_diagram(self, whiteboard_id: int, format: str = 'mermaid') -> Dict[str, Any]:
        """
        Convert a whiteboard to a diagram format
        
        Args:
            whiteboard_id: The ID of the whiteboard
            format: The diagram format (mermaid, plantuml, etc.)
            
        Returns:
            Dictionary with the generated diagram code
        """
        # Get the whiteboard
        whiteboard = self.get_whiteboard(whiteboard_id)
        
        if not whiteboard:
            return {'error': 'Whiteboard not found'}
        
        # Get elements and links
        elements = whiteboard.get('elements', [])
        links = whiteboard.get('links', [])
        
        # Prepare data for conversion
        elements_by_id = {element['id']: element for element in elements}
        
        # Prepare prompt for LLM
        elements_text = ""
        for element in elements:
            elements_text += f"Element ID: {element['id']}\n"
            elements_text += f"Type: {element['type']}\n"
            
            if 'label' in element['properties']:
                elements_text += f"Label: {element['properties']['label']}\n"
            
            if 'text' in element['properties']:
                elements_text += f"Text: {element['properties']['text']}\n"
            
            if 'description' in element['properties']:
                elements_text += f"Description: {element['properties']['description']}\n"
            
            elements_text += "\n"
        
        links_text = ""
        for link in links:
            source_element = elements_by_id.get(link['source_id'], {})
            target_element = elements_by_id.get(link['target_id'], {})
            
            source_label = source_element.get('properties', {}).get('label', source_element.get('id', 'Unknown'))
            target_label = target_element.get('properties', {}).get('label', target_element.get('id', 'Unknown'))
            
            links_text += f"Link: {source_label} -> {target_label}\n"
            links_text += f"Type: {link['type']}\n\n"
        
        prompt = f"""
        You are an AI assistant that can convert whiteboard diagrams to code in various diagram formats.
        
        I have a whiteboard with the following elements and links:
        
        Whiteboard Title: {whiteboard['title']}
        Description: {whiteboard.get('description', 'No description')}
        
        Elements:
        {elements_text}
        
        Links:
        {links_text}
        
        Please convert this whiteboard into a {format} diagram that accurately represents the elements and their relationships.
        
        Format your response as a code block with the appropriate {format} syntax.
        ```{format}
        // Your {format} code here
        ```
        """
        
        # Generate diagram code using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
        # Extract code from response
        code_match = re.search(f'```{format}\s*(.*?)\s*```', response, re.DOTALL)
        if code_match:
            diagram_code = code_match.group(1)
        else:
            # Try to find code without the markdown code block
            diagram_code = response
        
        return {
            'whiteboard_id': whiteboard_id,
            'title': whiteboard['title'],
            'format': format,
            'diagram_code': diagram_code
        }

# Helper functions for easier access to whiteboard functionality

def create_whiteboard(db_manager, user_id: int, title: str, 
                     description: Optional[str] = None) -> int:
    """
    Create a new whiteboard
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        title: The title of the whiteboard
        description: Optional description of the whiteboard
        
    Returns:
        The ID of the created whiteboard
    """
    whiteboard = Whiteboard(db_manager)
    return whiteboard.create_whiteboard(user_id, title, description)

def auto_label_sketch(db_manager, whiteboard_id: int, element_id: str) -> Dict[str, Any]:
    """
    Automatically label a sketch using AI
    
    Args:
        db_manager: Database manager instance
        whiteboard_id: The ID of the whiteboard
        element_id: The ID of the element to label
        
    Returns:
        Dictionary with the updated element
    """
    whiteboard = Whiteboard(db_manager)
    return whiteboard.auto_label_sketch(whiteboard_id, element_id)

def convert_to_markdown(db_manager, whiteboard_id: int) -> Dict[str, Any]:
    """
    Convert a whiteboard to structured markdown notes
    
    Args:
        db_manager: Database manager instance
        whiteboard_id: The ID of the whiteboard
        
    Returns:
        Dictionary with the generated markdown
    """
    whiteboard = Whiteboard(db_manager)
    return whiteboard.convert_to_markdown(whiteboard_id)

def convert_to_diagram(db_manager, whiteboard_id: int, format: str = 'mermaid') -> Dict[str, Any]:
    """
    Convert a whiteboard to a diagram format
    
    Args:
        db_manager: Database manager instance
        whiteboard_id: The ID of the whiteboard
        format: The diagram format (mermaid, plantuml, etc.)
        
    Returns:
        Dictionary with the generated diagram code
    """
    whiteboard = Whiteboard(db_manager)
    return whiteboard.convert_to_diagram(whiteboard_id, format)