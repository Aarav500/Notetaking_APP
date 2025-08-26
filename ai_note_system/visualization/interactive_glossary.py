"""
Interactive Visual Glossary module for AI Note System.
Creates clickable, interactive term maps with definitions, diagrams, examples, and references.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import re
import html

# Setup logging
logger = logging.getLogger("ai_note_system.visualization.interactive_glossary")

# Import required modules
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import get_llm_interface
from ..api.embedding_interface import get_embedding_interface

class InteractiveGlossary:
    """
    Creates and manages interactive glossaries with clickable terms.
    Links terms to definitions, diagrams, examples, and references in notes.
    """
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        embedding_provider: str = "openai",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Interactive Glossary.
        
        Args:
            db_manager (DatabaseManager, optional): Database manager instance
            llm_provider (str): LLM provider to use for content generation
            llm_model (str): LLM model to use for content generation
            embedding_provider (str): Provider for embedding generation
            output_dir (str, optional): Directory to save generated glossaries
        """
        self.db_manager = db_manager
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Initialize embedding interface for semantic search
        self.embedder = get_embedding_interface(embedding_provider)
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Interactive Glossary with {llm_provider} {llm_model}")
        
        # Initialize database tables if needed
        if self.db_manager:
            self._init_database()
    
    def _init_database(self) -> None:
        """
        Initialize database tables for glossary terms.
        """
        try:
            # Create glossary_terms table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS glossary_terms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL UNIQUE,
                definition TEXT NOT NULL,
                category TEXT,
                importance INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            ''')
            
            # Create term_examples table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS term_examples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                example_text TEXT NOT NULL,
                source TEXT,
                FOREIGN KEY (term_id) REFERENCES glossary_terms (id) ON DELETE CASCADE
            )
            ''')
            
            # Create term_diagrams table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS term_diagrams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                diagram_path TEXT NOT NULL,
                diagram_type TEXT,
                caption TEXT,
                FOREIGN KEY (term_id) REFERENCES glossary_terms (id) ON DELETE CASCADE
            )
            ''')
            
            # Create term_references table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS term_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id INTEGER NOT NULL,
                note_id INTEGER NOT NULL,
                context TEXT,
                location TEXT,
                FOREIGN KEY (term_id) REFERENCES glossary_terms (id) ON DELETE CASCADE,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Create term_relationships table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS term_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term1_id INTEGER NOT NULL,
                term2_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (term1_id) REFERENCES glossary_terms (id) ON DELETE CASCADE,
                FOREIGN KEY (term2_id) REFERENCES glossary_terms (id) ON DELETE CASCADE
            )
            ''')
            
            self.db_manager.conn.commit()
            logger.debug("Glossary database tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database tables: {e}")
    
    def add_term(
        self,
        term: str,
        definition: str,
        category: Optional[str] = None,
        importance: int = 1,
        examples: Optional[List[Dict[str, str]]] = None,
        diagrams: Optional[List[Dict[str, str]]] = None,
        related_terms: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Add a term to the glossary.
        
        Args:
            term (str): The term to add
            definition (str): Definition of the term
            category (str, optional): Category of the term
            importance (int): Importance level (1-5)
            examples (List[Dict[str, str]], optional): Examples of the term
            diagrams (List[Dict[str, str]], optional): Diagrams for the term
            related_terms (List[Dict[str, Any]], optional): Related terms
            
        Returns:
            Dict[str, Any]: The added term data
        """
        # Validate inputs
        term = term.strip()
        if not term or not definition:
            logger.error("Term and definition are required")
            return {"error": "Term and definition are required"}
        
        importance = max(1, min(5, importance))
        
        # Check if term already exists
        existing_term = self.get_term(term)
        if existing_term and "id" in existing_term:
            logger.info(f"Term '{term}' already exists, updating")
            return self.update_term(
                term_id=existing_term["id"],
                definition=definition,
                category=category,
                importance=importance,
                examples=examples,
                diagrams=diagrams,
                related_terms=related_terms
            )
        
        # Create term in database
        term_id = -1
        if self.db_manager:
            try:
                timestamp = datetime.now().isoformat()
                
                self.db_manager.cursor.execute('''
                INSERT INTO glossary_terms (term, definition, category, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (term, definition, category, importance, timestamp, timestamp))
                
                term_id = self.db_manager.cursor.lastrowid
                
                # Add examples if provided
                if examples:
                    for example in examples:
                        self.db_manager.cursor.execute('''
                        INSERT INTO term_examples (term_id, example_text, source)
                        VALUES (?, ?, ?)
                        ''', (term_id, example.get("text", ""), example.get("source", "")))
                
                # Add diagrams if provided
                if diagrams:
                    for diagram in diagrams:
                        self.db_manager.cursor.execute('''
                        INSERT INTO term_diagrams (term_id, diagram_path, diagram_type, caption)
                        VALUES (?, ?, ?, ?)
                        ''', (
                            term_id,
                            diagram.get("path", ""),
                            diagram.get("type", ""),
                            diagram.get("caption", "")
                        ))
                
                # Add related terms if provided
                if related_terms:
                    for related in related_terms:
                        related_term = related.get("term", "")
                        relationship_type = related.get("relationship_type", "related")
                        description = related.get("description", "")
                        
                        # Get or create related term
                        related_term_data = self.get_term(related_term)
                        if not related_term_data:
                            # Create a placeholder for the related term
                            related_term_data = self.add_term(
                                term=related_term,
                                definition=f"Related to {term}. Definition pending.",
                                category=category
                            )
                        
                        related_term_id = related_term_data.get("id", -1)
                        if related_term_id > 0:
                            self.db_manager.cursor.execute('''
                            INSERT INTO term_relationships (term1_id, term2_id, relationship_type, description)
                            VALUES (?, ?, ?, ?)
                            ''', (term_id, related_term_id, relationship_type, description))
                
                self.db_manager.conn.commit()
                logger.info(f"Added term '{term}' with ID {term_id}")
                
            except Exception as e:
                self.db_manager.conn.rollback()
                logger.error(f"Error adding term '{term}': {e}")
                return {"error": f"Error adding term: {e}"}
        
        # Create term data
        term_data = {
            "id": term_id,
            "term": term,
            "definition": definition,
            "category": category,
            "importance": importance,
            "examples": examples or [],
            "diagrams": diagrams or [],
            "related_terms": related_terms or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save to file if database not available or output_dir is specified
        if term_id < 0 or self.output_dir:
            self._save_to_file(term_data)
        
        return term_data
    
    def update_term(
        self,
        term_id: int,
        definition: Optional[str] = None,
        category: Optional[str] = None,
        importance: Optional[int] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        diagrams: Optional[List[Dict[str, str]]] = None,
        related_terms: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing term in the glossary.
        
        Args:
            term_id (int): ID of the term to update
            definition (str, optional): New definition
            category (str, optional): New category
            importance (int, optional): New importance level
            examples (List[Dict[str, str]], optional): New examples
            diagrams (List[Dict[str, str]], optional): New diagrams
            related_terms (List[Dict[str, Any]], optional): New related terms
            
        Returns:
            Dict[str, Any]: The updated term data
        """
        if not self.db_manager:
            logger.error("Database manager is required to update terms")
            return {"error": "Database manager is required to update terms"}
        
        try:
            # Get current term data
            self.db_manager.cursor.execute('''
            SELECT * FROM glossary_terms WHERE id = ?
            ''', (term_id,))
            
            row = self.db_manager.cursor.fetchone()
            if not row:
                logger.error(f"Term with ID {term_id} not found")
                return {"error": f"Term with ID {term_id} not found"}
            
            term_data = dict(row)
            
            # Update fields if provided
            updates = []
            params = []
            
            if definition is not None:
                updates.append("definition = ?")
                params.append(definition)
            
            if category is not None:
                updates.append("category = ?")
                params.append(category)
            
            if importance is not None:
                importance = max(1, min(5, importance))
                updates.append("importance = ?")
                params.append(importance)
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            
            # Execute update if there are changes
            if updates:
                query = f"UPDATE glossary_terms SET {', '.join(updates)} WHERE id = ?"
                params.append(term_id)
                
                self.db_manager.cursor.execute(query, params)
            
            # Update examples if provided
            if examples is not None:
                # Remove existing examples
                self.db_manager.cursor.execute('''
                DELETE FROM term_examples WHERE term_id = ?
                ''', (term_id,))
                
                # Add new examples
                for example in examples:
                    self.db_manager.cursor.execute('''
                    INSERT INTO term_examples (term_id, example_text, source)
                    VALUES (?, ?, ?)
                    ''', (term_id, example.get("text", ""), example.get("source", "")))
            
            # Update diagrams if provided
            if diagrams is not None:
                # Remove existing diagrams
                self.db_manager.cursor.execute('''
                DELETE FROM term_diagrams WHERE term_id = ?
                ''', (term_id,))
                
                # Add new diagrams
                for diagram in diagrams:
                    self.db_manager.cursor.execute('''
                    INSERT INTO term_diagrams (term_id, diagram_path, diagram_type, caption)
                    VALUES (?, ?, ?, ?)
                    ''', (
                        term_id,
                        diagram.get("path", ""),
                        diagram.get("type", ""),
                        diagram.get("caption", "")
                    ))
            
            # Update related terms if provided
            if related_terms is not None:
                # Remove existing relationships
                self.db_manager.cursor.execute('''
                DELETE FROM term_relationships WHERE term1_id = ?
                ''', (term_id,))
                
                # Add new relationships
                for related in related_terms:
                    related_term = related.get("term", "")
                    relationship_type = related.get("relationship_type", "related")
                    description = related.get("description", "")
                    
                    # Get or create related term
                    related_term_data = self.get_term(related_term)
                    if not related_term_data:
                        # Create a placeholder for the related term
                        related_term_data = self.add_term(
                            term=related_term,
                            definition=f"Related to {term_data['term']}. Definition pending.",
                            category=term_data.get("category")
                        )
                    
                    related_term_id = related_term_data.get("id", -1)
                    if related_term_id > 0:
                        self.db_manager.cursor.execute('''
                        INSERT INTO term_relationships (term1_id, term2_id, relationship_type, description)
                        VALUES (?, ?, ?, ?)
                        ''', (term_id, related_term_id, relationship_type, description))
            
            self.db_manager.conn.commit()
            logger.info(f"Updated term with ID {term_id}")
            
            # Get updated term data
            return self.get_term_by_id(term_id)
            
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Error updating term with ID {term_id}: {e}")
            return {"error": f"Error updating term: {e}"}
    
    def get_term(self, term: str) -> Optional[Dict[str, Any]]:
        """
        Get a term by name.
        
        Args:
            term (str): Name of the term
            
        Returns:
            Optional[Dict[str, Any]]: Term data or None if not found
        """
        if not self.db_manager:
            logger.error("Database manager is required to get terms")
            return None
        
        try:
            # Get term data
            self.db_manager.cursor.execute('''
            SELECT * FROM glossary_terms WHERE term = ?
            ''', (term,))
            
            row = self.db_manager.cursor.fetchone()
            if not row:
                return None
            
            term_data = dict(row)
            term_id = term_data["id"]
            
            # Get examples
            self.db_manager.cursor.execute('''
            SELECT * FROM term_examples WHERE term_id = ?
            ''', (term_id,))
            
            examples = []
            for example_row in self.db_manager.cursor.fetchall():
                examples.append({
                    "id": example_row["id"],
                    "text": example_row["example_text"],
                    "source": example_row["source"]
                })
            
            term_data["examples"] = examples
            
            # Get diagrams
            self.db_manager.cursor.execute('''
            SELECT * FROM term_diagrams WHERE term_id = ?
            ''', (term_id,))
            
            diagrams = []
            for diagram_row in self.db_manager.cursor.fetchall():
                diagrams.append({
                    "id": diagram_row["id"],
                    "path": diagram_row["diagram_path"],
                    "type": diagram_row["diagram_type"],
                    "caption": diagram_row["caption"]
                })
            
            term_data["diagrams"] = diagrams
            
            # Get related terms
            self.db_manager.cursor.execute('''
            SELECT r.*, t.term
            FROM term_relationships r
            JOIN glossary_terms t ON r.term2_id = t.id
            WHERE r.term1_id = ?
            ''', (term_id,))
            
            related_terms = []
            for rel_row in self.db_manager.cursor.fetchall():
                related_terms.append({
                    "id": rel_row["id"],
                    "term": rel_row["term"],
                    "term_id": rel_row["term2_id"],
                    "relationship_type": rel_row["relationship_type"],
                    "description": rel_row["description"]
                })
            
            term_data["related_terms"] = related_terms
            
            # Get note references
            self.db_manager.cursor.execute('''
            SELECT * FROM term_references WHERE term_id = ?
            ''', (term_id,))
            
            references = []
            for ref_row in self.db_manager.cursor.fetchall():
                references.append({
                    "id": ref_row["id"],
                    "note_id": ref_row["note_id"],
                    "context": ref_row["context"],
                    "location": ref_row["location"]
                })
            
            term_data["references"] = references
            
            return term_data
            
        except Exception as e:
            logger.error(f"Error getting term '{term}': {e}")
            return None
    
    def get_term_by_id(self, term_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a term by ID.
        
        Args:
            term_id (int): ID of the term
            
        Returns:
            Optional[Dict[str, Any]]: Term data or None if not found
        """
        if not self.db_manager:
            logger.error("Database manager is required to get terms by ID")
            return None
        
        try:
            # Get term data
            self.db_manager.cursor.execute('''
            SELECT * FROM glossary_terms WHERE id = ?
            ''', (term_id,))
            
            row = self.db_manager.cursor.fetchone()
            if not row:
                return None
            
            term = row["term"]
            return self.get_term(term)
            
        except Exception as e:
            logger.error(f"Error getting term with ID {term_id}: {e}")
            return None
    
    def _save_to_file(self, term_data: Dict[str, Any]) -> str:
        """
        Save term data to file.
        
        Args:
            term_data (Dict[str, Any]): Term data to save
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Create filename
            term_slug = re.sub(r'[^\w\s-]', '', term_data["term"]).strip().lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"glossary_term_{term_slug}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(term_data, f, indent=2)
            
            logger.debug(f"Saved term data to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving term data to file: {e}")
            return ""
    
    def search_terms(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
        semantic_search: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for terms in the glossary.
        
        Args:
            query (str): Search query
            category (str, optional): Filter by category
            limit (int): Maximum number of results to return
            semantic_search (bool): Whether to use semantic search
            
        Returns:
            List[Dict[str, Any]]: Matching terms
        """
        if not self.db_manager:
            logger.error("Database manager is required to search terms")
            return []
        
        try:
            if semantic_search and self.embedder:
                # Get all terms
                self.db_manager.cursor.execute('''
                SELECT id, term, definition, category FROM glossary_terms
                ''')
                
                all_terms = []
                for row in self.db_manager.cursor.fetchall():
                    all_terms.append(dict(row))
                
                # Generate query embedding
                query_embedding = self.embedder.get_embedding(query)
                
                # Generate embeddings for terms and definitions
                results_with_scores = []
                for term_data in all_terms:
                    # Create text to embed (term + definition)
                    text = f"{term_data['term']} {term_data['definition']}"
                    
                    # Filter by category if specified
                    if category and term_data.get("category") != category:
                        continue
                    
                    # Get embedding
                    embedding = self.embedder.get_embedding(text)
                    
                    # Calculate similarity
                    similarity = self.embedder.calculate_similarity(query_embedding, embedding)
                    
                    # Add to results if similarity is above threshold
                    if similarity > 0.7:  # Adjust threshold as needed
                        results_with_scores.append((term_data, similarity))
                
                # Sort by similarity (highest first)
                results_with_scores.sort(key=lambda x: x[1], reverse=True)
                
                # Get top results
                top_results = [item[0] for item in results_with_scores[:limit]]
                
                # Fetch full data for each term
                return [self.get_term_by_id(term["id"]) for term in top_results if term["id"]]
            else:
                # Use simple text search
                query_pattern = f"%{query}%"
                
                # Build query
                sql_query = '''
                SELECT id FROM glossary_terms 
                WHERE (term LIKE ? OR definition LIKE ?)
                '''
                params = [query_pattern, query_pattern]
                
                if category:
                    sql_query += " AND category = ?"
                    params.append(category)
                
                sql_query += " LIMIT ?"
                params.append(limit)
                
                # Execute query
                self.db_manager.cursor.execute(sql_query, params)
                
                # Fetch results
                results = []
                for row in self.db_manager.cursor.fetchall():
                    term_data = self.get_term_by_id(row["id"])
                    if term_data:
                        results.append(term_data)
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching terms: {e}")
            return []
    
    def add_note_reference(
        self,
        term_id: int,
        note_id: int,
        context: Optional[str] = None,
        location: Optional[str] = None
    ) -> bool:
        """
        Add a reference to a note where the term appears.
        
        Args:
            term_id (int): ID of the term
            note_id (int): ID of the note
            context (str, optional): Context where the term appears
            location (str, optional): Location in the note (e.g., paragraph number)
            
        Returns:
            bool: Whether the reference was added successfully
        """
        if not self.db_manager:
            logger.error("Database manager is required to add note references")
            return False
        
        try:
            # Check if term exists
            self.db_manager.cursor.execute('''
            SELECT id FROM glossary_terms WHERE id = ?
            ''', (term_id,))
            
            if not self.db_manager.cursor.fetchone():
                logger.error(f"Term with ID {term_id} not found")
                return False
            
            # Check if note exists
            self.db_manager.cursor.execute('''
            SELECT id FROM notes WHERE id = ?
            ''', (note_id,))
            
            if not self.db_manager.cursor.fetchone():
                logger.error(f"Note with ID {note_id} not found")
                return False
            
            # Add reference
            self.db_manager.cursor.execute('''
            INSERT INTO term_references (term_id, note_id, context, location)
            VALUES (?, ?, ?, ?)
            ''', (term_id, note_id, context, location))
            
            self.db_manager.conn.commit()
            logger.info(f"Added note reference for term {term_id} to note {note_id}")
            
            return True
            
        except Exception as e:
            self.db_manager.conn.rollback()
            logger.error(f"Error adding note reference: {e}")
            return False
    
    def scan_note_for_terms(
        self,
        note_id: int,
        note_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan a note for terms in the glossary and add references.
        
        Args:
            note_id (int): ID of the note
            note_text (str, optional): Text of the note (if not provided, will be fetched from database)
            
        Returns:
            List[Dict[str, Any]]: Terms found in the note with their references
        """
        if not self.db_manager:
            logger.error("Database manager is required to scan notes for terms")
            return []
        
        try:
            # Get note text if not provided
            if not note_text:
                self.db_manager.cursor.execute('''
                SELECT text FROM notes WHERE id = ?
                ''', (note_id,))
                
                row = self.db_manager.cursor.fetchone()
                if not row:
                    logger.error(f"Note with ID {note_id} not found")
                    return []
                
                note_text = row["text"]
            
            # Get all terms
            self.db_manager.cursor.execute('''
            SELECT id, term FROM glossary_terms
            ''')
            
            all_terms = []
            for row in self.db_manager.cursor.fetchall():
                all_terms.append(dict(row))
            
            # Find terms in note
            found_terms = []
            for term_data in all_terms:
                term = term_data["term"]
                term_id = term_data["id"]
                
                # Simple search for exact term
                term_pattern = r'\b' + re.escape(term) + r'\b'
                matches = list(re.finditer(term_pattern, note_text, re.IGNORECASE))
                
                if matches:
                    # Add reference for each match
                    for match in matches:
                        # Get context (text around the match)
                        start = max(0, match.start() - 50)
                        end = min(len(note_text), match.end() + 50)
                        context = note_text[start:end]
                        
                        # Add reference
                        self.add_note_reference(
                            term_id=term_id,
                            note_id=note_id,
                            context=context,
                            location=f"position:{match.start()}"
                        )
                    
                    # Get full term data
                    full_term = self.get_term_by_id(term_id)
                    if full_term:
                        found_terms.append(full_term)
            
            return found_terms
            
        except Exception as e:
            logger.error(f"Error scanning note for terms: {e}")
            return []
    
    def generate_clickable_interface(
        self,
        terms: List[Dict[str, Any]],
        format_type: str = "html",
        include_definitions: bool = True,
        include_examples: bool = True,
        include_diagrams: bool = True,
        include_references: bool = False
    ) -> str:
        """
        Generate a clickable interface for a list of terms.
        
        Args:
            terms (List[Dict[str, Any]]): List of terms to include
            format_type (str): Output format (html, markdown, text)
            include_definitions (bool): Whether to include definitions
            include_examples (bool): Whether to include examples
            include_diagrams (bool): Whether to include diagrams
            include_references (bool): Whether to include note references
            
        Returns:
            str: Clickable interface in the specified format
        """
        if format_type == "html":
            return self._generate_html_interface(
                terms, include_definitions, include_examples, include_diagrams, include_references
            )
        elif format_type == "markdown":
            return self._generate_markdown_interface(
                terms, include_definitions, include_examples, include_diagrams, include_references
            )
        else:  # text
            return self._generate_text_interface(
                terms, include_definitions, include_examples, include_diagrams, include_references
            )
    
    def _generate_html_interface(
        self,
        terms: List[Dict[str, Any]],
        include_definitions: bool,
        include_examples: bool,
        include_diagrams: bool,
        include_references: bool
    ) -> str:
        """
        Generate an HTML clickable interface for terms.
        
        Args:
            terms (List[Dict[str, Any]]): List of terms to include
            include_definitions (bool): Whether to include definitions
            include_examples (bool): Whether to include examples
            include_diagrams (bool): Whether to include diagrams
            include_references (bool): Whether to include note references
            
        Returns:
            str: HTML interface
        """
        # Start with HTML header
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Interactive Glossary</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .glossary-container { display: flex; }
        .terms-list { width: 30%; padding-right: 20px; }
        .term-details { width: 70%; border-left: 1px solid #ccc; padding-left: 20px; }
        .term-item { cursor: pointer; padding: 8px; margin: 4px 0; border-radius: 4px; }
        .term-item:hover { background-color: #f0f0f0; }
        .term-item.active { background-color: #e0e0e0; font-weight: bold; }
        .term-category { color: #666; font-size: 0.9em; }
        .term-definition { margin-bottom: 15px; }
        .term-examples { margin-bottom: 15px; }
        .term-example { background-color: #f9f9f9; padding: 10px; margin-bottom: 10px; border-left: 3px solid #ddd; }
        .term-diagrams { margin-bottom: 15px; }
        .term-diagram { margin-bottom: 10px; }
        .term-diagram img { max-width: 100%; border: 1px solid #ddd; }
        .term-references { margin-bottom: 15px; }
        .term-reference { background-color: #f5f5f5; padding: 8px; margin-bottom: 8px; font-size: 0.9em; }
        .term-related { margin-bottom: 15px; }
        .term-related-item { display: inline-block; margin-right: 10px; margin-bottom: 5px; background-color: #eef; padding: 3px 8px; border-radius: 12px; cursor: pointer; }
        .term-related-item:hover { background-color: #ddf; }
        .hidden { display: none; }
        h1 { color: #333; }
        h2 { color: #444; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        h3 { color: #555; }
    </style>
    <script>
        function showTerm(termId) {
            // Hide all term details
            var details = document.getElementsByClassName('term-detail');
            for (var i = 0; i < details.length; i++) {
                details[i].classList.add('hidden');
            }
            
            // Show selected term details
            document.getElementById('term-' + termId).classList.remove('hidden');
            
            // Update active term in list
            var items = document.getElementsByClassName('term-item');
            for (var i = 0; i < items.length; i++) {
                items[i].classList.remove('active');
            }
            document.getElementById('term-item-' + termId).classList.add('active');
            
            // Update URL hash
            window.location.hash = 'term-' + termId;
        }
        
        window.onload = function() {
            // Show first term by default, or term from URL hash
            var hash = window.location.hash;
            if (hash && hash.startsWith('#term-')) {
                var termId = hash.substring(6);
                showTerm(termId);
            } else if (document.getElementsByClassName('term-item').length > 0) {
                var firstTermId = document.getElementsByClassName('term-item')[0].getAttribute('data-term-id');
                showTerm(firstTermId);
            }
        };
    </script>
</head>
<body>
    <h1>Interactive Glossary</h1>
    <div class="glossary-container">
        <div class="terms-list">
            <h2>Terms</h2>
"""
        
        # Add terms list
        for term in terms:
            term_id = term.get("id", 0)
            term_name = html.escape(term.get("term", ""))
            category = html.escape(term.get("category", ""))
            
            html += f'            <div id="term-item-{term_id}" class="term-item" data-term-id="{term_id}" onclick="showTerm({term_id})">\n'
            html += f'                {term_name}\n'
            if category:
                html += f'                <div class="term-category">{category}</div>\n'
            html += f'            </div>\n'
        
        # Start term details section
        html += """        </div>
        <div class="term-details">
            <h2>Details</h2>
"""
        
        # Add term details
        for term in terms:
            term_id = term.get("id", 0)
            term_name = html.escape(term.get("term", ""))
            definition = html.escape(term.get("definition", ""))
            category = html.escape(term.get("category", ""))
            importance = term.get("importance", 1)
            examples = term.get("examples", [])
            diagrams = term.get("diagrams", [])
            references = term.get("references", [])
            related_terms = term.get("related_terms", [])
            
            html += f'            <div id="term-{term_id}" class="term-detail hidden">\n'
            html += f'                <h3>{term_name}</h3>\n'
            
            if category:
                html += f'                <div class="term-category">Category: {category} | Importance: {importance}/5</div>\n'
            
            if include_definitions:
                html += f'                <div class="term-definition">{definition}</div>\n'
            
            if include_examples and examples:
                html += f'                <h4>Examples</h4>\n'
                html += f'                <div class="term-examples">\n'
                for example in examples:
                    example_text = html.escape(example.get("text", ""))
                    example_source = html.escape(example.get("source", ""))
                    html += f'                    <div class="term-example">\n'
                    html += f'                        {example_text}\n'
                    if example_source:
                        html += f'                        <div class="example-source">Source: {example_source}</div>\n'
                    html += f'                    </div>\n'
                html += f'                </div>\n'
            
            if include_diagrams and diagrams:
                html += f'                <h4>Diagrams</h4>\n'
                html += f'                <div class="term-diagrams">\n'
                for diagram in diagrams:
                    diagram_path = html.escape(diagram.get("path", ""))
                    diagram_caption = html.escape(diagram.get("caption", ""))
                    if diagram_path:
                        html += f'                    <div class="term-diagram">\n'
                        html += f'                        <img src="{diagram_path}" alt="{term_name} diagram">\n'
                        if diagram_caption:
                            html += f'                        <div class="diagram-caption">{diagram_caption}</div>\n'
                        html += f'                    </div>\n'
                html += f'                </div>\n'
            
            if include_references and references:
                html += f'                <h4>References in Notes</h4>\n'
                html += f'                <div class="term-references">\n'
                for reference in references:
                    note_id = reference.get("note_id", 0)
                    context = html.escape(reference.get("context", ""))
                    html += f'                    <div class="term-reference">\n'
                    html += f'                        <a href="#note-{note_id}">Note #{note_id}</a>\n'
                    if context:
                        html += f'                        <div class="reference-context">"{context}"</div>\n'
                    html += f'                    </div>\n'
                html += f'                </div>\n'
            
            if related_terms:
                html += f'                <h4>Related Terms</h4>\n'
                html += f'                <div class="term-related">\n'
                for related in related_terms:
                    related_id = related.get("term_id", 0)
                    related_name = html.escape(related.get("term", ""))
                    relationship = html.escape(related.get("relationship_type", "related"))
                    html += f'                    <span class="term-related-item" onclick="showTerm({related_id})" title="{relationship}">{related_name}</span>\n'
                html += f'                </div>\n'
            
            html += f'            </div>\n'
        
        # Close HTML
        html += """        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_markdown_interface(
        self,
        terms: List[Dict[str, Any]],
        include_definitions: bool,
        include_examples: bool,
        include_diagrams: bool,
        include_references: bool
    ) -> str:
        """
        Generate a Markdown clickable interface for terms.
        
        Args:
            terms (List[Dict[str, Any]]): List of terms to include
            include_definitions (bool): Whether to include definitions
            include_examples (bool): Whether to include examples
            include_diagrams (bool): Whether to include diagrams
            include_references (bool): Whether to include note references
            
        Returns:
            str: Markdown interface
        """
        # Start with title
        md = "# Interactive Glossary\n\n"
        
        # Add table of contents
        md += "## Table of Contents\n\n"
        for term in terms:
            term_id = term.get("id", 0)
            term_name = term.get("term", "")
            md += f"- [{term_name}](#{term_id}-{term_name.lower().replace(' ', '-')})\n"
        
        md += "\n---\n\n"
        
        # Add term details
        for term in terms:
            term_id = term.get("id", 0)
            term_name = term.get("term", "")
            definition = term.get("definition", "")
            category = term.get("category", "")
            importance = term.get("importance", 1)
            examples = term.get("examples", [])
            diagrams = term.get("diagrams", [])
            references = term.get("references", [])
            related_terms = term.get("related_terms", [])
            
            # Create anchor for linking
            anchor = f"{term_id}-{term_name.lower().replace(' ', '-')}"
            md += f"## {term_name} <a id='{anchor}'></a>\n\n"
            
            if category:
                md += f"**Category:** {category} | **Importance:** {importance}/5\n\n"
            
            if include_definitions:
                md += f"{definition}\n\n"
            
            if include_examples and examples:
                md += "### Examples\n\n"
                for example in examples:
                    example_text = example.get("text", "")
                    example_source = example.get("source", "")
                    md += f"> {example_text}\n"
                    if example_source:
                        md += f"> \n> Source: *{example_source}*\n"
                    md += "\n"
            
            if include_diagrams and diagrams:
                md += "### Diagrams\n\n"
                for diagram in diagrams:
                    diagram_path = diagram.get("path", "")
                    diagram_caption = diagram.get("caption", "")
                    if diagram_path:
                        md += f"![{term_name} diagram]({diagram_path})\n"
                        if diagram_caption:
                            md += f"*{diagram_caption}*\n"
                        md += "\n"
            
            if include_references and references:
                md += "### References in Notes\n\n"
                for reference in references:
                    note_id = reference.get("note_id", 0)
                    context = reference.get("context", "")
                    md += f"- Note #{note_id}\n"
                    if context:
                        md += f"  > \"{context}\"\n"
                md += "\n"
            
            if related_terms:
                md += "### Related Terms\n\n"
                for related in related_terms:
                    related_id = related.get("term_id", 0)
                    related_name = related.get("term", "")
                    relationship = related.get("relationship_type", "related")
                    related_anchor = f"{related_id}-{related_name.lower().replace(' ', '-')}"
                    md += f"- [{related_name}](#{related_anchor}) ({relationship})\n"
                md += "\n"
            
            md += "---\n\n"
        
        return md
    
    def _generate_text_interface(
        self,
        terms: List[Dict[str, Any]],
        include_definitions: bool,
        include_examples: bool,
        include_diagrams: bool,
        include_references: bool
    ) -> str:
        """
        Generate a text interface for terms.
        
        Args:
            terms (List[Dict[str, Any]]): List of terms to include
            include_definitions (bool): Whether to include definitions
            include_examples (bool): Whether to include examples
            include_diagrams (bool): Whether to include diagrams
            include_references (bool): Whether to include note references
            
        Returns:
            str: Text interface
        """
        # Start with title
        text = "INTERACTIVE GLOSSARY\n"
        text += "=" * 50 + "\n\n"
        
        # Add term details
        for term in terms:
            term_name = term.get("term", "")
            definition = term.get("definition", "")
            category = term.get("category", "")
            importance = term.get("importance", 1)
            examples = term.get("examples", [])
            diagrams = term.get("diagrams", [])
            references = term.get("references", [])
            related_terms = term.get("related_terms", [])
            
            text += f"{term_name.upper()}\n"
            text += "-" * len(term_name) + "\n\n"
            
            if category:
                text += f"Category: {category} | Importance: {importance}/5\n\n"
            
            if include_definitions:
                text += f"{definition}\n\n"
            
            if include_examples and examples:
                text += "Examples:\n"
                for example in examples:
                    example_text = example.get("text", "")
                    example_source = example.get("source", "")
                    text += f"* {example_text}\n"
                    if example_source:
                        text += f"  Source: {example_source}\n"
                text += "\n"
            
            if include_diagrams and diagrams:
                text += "Diagrams:\n"
                for diagram in diagrams:
                    diagram_path = diagram.get("path", "")
                    diagram_caption = diagram.get("caption", "")
                    if diagram_path:
                        text += f"* {diagram_path}\n"
                        if diagram_caption:
                            text += f"  Caption: {diagram_caption}\n"
                text += "\n"
            
            if include_references and references:
                text += "References in Notes:\n"
                for reference in references:
                    note_id = reference.get("note_id", 0)
                    context = reference.get("context", "")
                    text += f"* Note #{note_id}\n"
                    if context:
                        text += f"  \"{context}\"\n"
                text += "\n"
            
            if related_terms:
                text += "Related Terms:\n"
                for related in related_terms:
                    related_name = related.get("term", "")
                    relationship = related.get("relationship_type", "related")
                    text += f"* {related_name} ({relationship})\n"
                text += "\n"
            
            text += "=" * 50 + "\n\n"
        
        return text


def main():
    """
    Command-line interface for the Interactive Glossary.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Interactive Visual Glossary")
    parser.add_argument("--action", choices=["add", "update", "get", "search", "scan", "generate"], 
                        required=True, help="Action to perform")
    parser.add_argument("--term", help="Term name (for add, update, get actions)")
    parser.add_argument("--definition", help="Term definition (for add, update actions)")
    parser.add_argument("--category", help="Term category (for add, update actions)")
    parser.add_argument("--importance", type=int, choices=[1, 2, 3, 4, 5], 
                        help="Term importance (1-5, for add, update actions)")
    parser.add_argument("--term-id", type=int, help="Term ID (for update action)")
    parser.add_argument("--note-id", type=int, help="Note ID (for scan action)")
    parser.add_argument("--note-text", help="Note text (for scan action)")
    parser.add_argument("--query", help="Search query (for search action)")
    parser.add_argument("--semantic", action="store_true", help="Use semantic search (for search action)")
    parser.add_argument("--format", choices=["html", "markdown", "text"], default="text", 
                        help="Output format (for generate action)")
    parser.add_argument("--output", help="Output file path (for generate action)")
    parser.add_argument("--no-definitions", action="store_true", help="Exclude definitions (for generate action)")
    parser.add_argument("--no-examples", action="store_true", help="Exclude examples (for generate action)")
    parser.add_argument("--no-diagrams", action="store_true", help="Exclude diagrams (for generate action)")
    parser.add_argument("--include-references", action="store_true", 
                        help="Include note references (for generate action)")
    parser.add_argument("--db-path", help="Path to the database file")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    parser.add_argument("--embedding", default="openai", help="Embedding provider")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Initialize database manager if db_path is provided
    db_manager = None
    if args.db_path:
        from ..database.db_manager import DatabaseManager
        db_manager = DatabaseManager(args.db_path)
    
    # Initialize glossary
    glossary = InteractiveGlossary(
        db_manager=db_manager,
        llm_provider=args.llm,
        llm_model=args.model,
        embedding_provider=args.embedding,
        output_dir=args.output_dir
    )
    
    # Perform action
    if args.action == "add":
        if not args.term or not args.definition:
            print("Error: term and definition are required for add action")
            return
        
        result = glossary.add_term(
            term=args.term,
            definition=args.definition,
            category=args.category,
            importance=args.importance or 1
        )
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Added term '{result['term']}' with ID {result['id']}")
        
    elif args.action == "update":
        if not args.term_id:
            print("Error: term-id is required for update action")
            return
        
        result = glossary.update_term(
            term_id=args.term_id,
            definition=args.definition,
            category=args.category,
            importance=args.importance
        )
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Updated term '{result['term']}' with ID {result['id']}")
        
    elif args.action == "get":
        if not args.term and not args.term_id:
            print("Error: either term or term-id is required for get action")
            return
        
        if args.term_id:
            result = glossary.get_term_by_id(args.term_id)
        else:
            result = glossary.get_term(args.term)
        
        if not result:
            print(f"Term not found")
            return
        
        # Display term details
        print(f"\n{result['term'].upper()}")
        print("-" * len(result['term']))
        
        if result.get("category"):
            print(f"Category: {result['category']} | Importance: {result['importance']}/5")
        
        print(f"\n{result['definition']}\n")
        
        if result.get("examples"):
            print("Examples:")
            for example in result["examples"]:
                print(f"* {example['text']}")
                if example.get("source"):
                    print(f"  Source: {example['source']}")
            print()
        
        if result.get("related_terms"):
            print("Related Terms:")
            for related in result["related_terms"]:
                print(f"* {related['term']} ({related['relationship_type']})")
            print()
        
    elif args.action == "search":
        if not args.query:
            print("Error: query is required for search action")
            return
        
        results = glossary.search_terms(
            query=args.query,
            category=args.category,
            semantic_search=args.semantic
        )
        
        if not results:
            print(f"No terms found matching '{args.query}'")
            return
        
        print(f"\nFound {len(results)} terms matching '{args.query}':")
        
        for i, term in enumerate(results, 1):
            print(f"\n{i}. {term['term']}")
            if term.get("category"):
                print(f"   Category: {term['category']}")
            print(f"   {term['definition'][:100]}...")
        
    elif args.action == "scan":
        if not args.note_id and not args.note_text:
            print("Error: either note-id or note-text is required for scan action")
            return
        
        if args.note_text:
            if not args.note_id:
                print("Error: note-id is required when providing note-text")
                return
            
            results = glossary.scan_note_for_terms(
                note_id=args.note_id,
                note_text=args.note_text
            )
        else:
            results = glossary.scan_note_for_terms(note_id=args.note_id)
        
        if not results:
            print(f"No glossary terms found in note #{args.note_id}")
            return
        
        print(f"\nFound {len(results)} glossary terms in note #{args.note_id}:")
        
        for i, term in enumerate(results, 1):
            print(f"\n{i}. {term['term']}")
            if term.get("category"):
                print(f"   Category: {term['category']}")
            print(f"   {term['definition'][:100]}...")
        
    elif args.action == "generate":
        # Get all terms if no specific term is provided
        if args.term:
            term_data = glossary.get_term(args.term)
            if not term_data:
                print(f"Term '{args.term}' not found")
                return
            terms = [term_data]
        elif args.term_id:
            term_data = glossary.get_term_by_id(args.term_id)
            if not term_data:
                print(f"Term with ID {args.term_id} not found")
                return
            terms = [term_data]
        else:
            # Get all terms
            if not db_manager:
                print("Error: database is required to get all terms")
                return
            
            db_manager.cursor.execute("SELECT id FROM glossary_terms")
            term_ids = [row["id"] for row in db_manager.cursor.fetchall()]
            
            terms = []
            for term_id in term_ids:
                term_data = glossary.get_term_by_id(term_id)
                if term_data:
                    terms.append(term_data)
        
        if not terms:
            print("No terms found to generate interface")
            return
        
        # Generate interface
        interface = glossary.generate_clickable_interface(
            terms=terms,
            format_type=args.format,
            include_definitions=not args.no_definitions,
            include_examples=not args.no_examples,
            include_diagrams=not args.no_diagrams,
            include_references=args.include_references
        )
        
        # Save to file or print
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(interface)
                print(f"Generated {args.format} interface saved to {args.output}")
            except Exception as e:
                print(f"Error saving interface to file: {e}")
        else:
            print(interface)


if __name__ == "__main__":
    main()