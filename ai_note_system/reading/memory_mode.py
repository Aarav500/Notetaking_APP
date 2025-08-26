"""
Long-Term Memory Mode module for AI Note System.
Provides functionality for persistent recall of book content over time.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.reading.memory_mode")

class LongTermMemoryMode:
    """
    Long-Term Memory Mode class for persistent recall of book content.
    Generates summaries, tracks knowledge decay, and schedules reviews.
    """
    
    def __init__(self, db_manager=None, embedder=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Long-Term Memory Mode.
        
        Args:
            db_manager: Database manager instance
            embedder: Embedder instance for semantic processing
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.db_manager = db_manager
        self.embedder = embedder
        self.config = config or {}
        self._ensure_memory_tables()
        
        # Default decay parameters
        self.default_decay_params = {
            "initial_strength": 1.0,  # Initial memory strength
            "decay_rate": 0.05,       # Daily decay rate
            "recall_boost": 0.2,      # Boost from each review
            "threshold": 0.5          # Threshold for suggesting review
        }
        
        logger.debug("Initialized LongTermMemoryMode")
    
    def _ensure_memory_tables(self) -> None:
        """
        Ensure the memory-related tables exist in the database.
        """
        if not self.db_manager:
            logger.warning("No database manager provided, skipping table creation")
            return
            
        # Create pdf_summaries table
        summaries_query = """
        CREATE TABLE IF NOT EXISTS pdf_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            summary_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(summaries_query)
        
        # Create pdf_timelines table
        timelines_query = """
        CREATE TABLE IF NOT EXISTS pdf_timelines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            timeline_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(timelines_query)
        
        # Create pdf_knowledge_decay table
        decay_query = """
        CREATE TABLE IF NOT EXISTS pdf_knowledge_decay (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            concept TEXT NOT NULL,
            initial_strength REAL NOT NULL,
            current_strength REAL NOT NULL,
            decay_rate REAL NOT NULL,
            last_reviewed TIMESTAMP,
            next_review TIMESTAMP,
            review_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(decay_query)
        
        # Create pdf_concept_links table
        links_query = """
        CREATE TABLE IF NOT EXISTS pdf_concept_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concept TEXT NOT NULL,
            book_id_1 INTEGER NOT NULL,
            book_id_2 INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            similarity_score REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id_1) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id_2) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(links_query)
        
        logger.debug("Ensured memory tables exist in database")
    
    def generate_summary(self, 
                       book_id: int, 
                       user_id: int, 
                       summary_type: str = "medium") -> Dict[str, Any]:
        """
        Generate a summary of a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            summary_type (str): Type of summary (short, medium, long)
            
        Returns:
            Dict[str, Any]: Generated summary
        """
        logger.info(f"Generating {summary_type} summary for book {book_id}")
        
        # Get book information
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        book_query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        book = self.db_manager.execute_query(book_query, (book_id,)).fetchone()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return {"error": f"Book not found: {book_id}"}
        
        # Check if summary already exists
        existing_summary = self.get_summary(book_id, user_id, summary_type)
        if existing_summary and "error" not in existing_summary:
            logger.info(f"{summary_type.capitalize()} summary already exists for book {book_id}")
            return existing_summary
        
        # Get book content for summarization
        file_path = book["file_path"]
        
        # Extract text from PDF
        from ai_note_system.inputs.pdf_input import extract_text_from_pdf
        
        try:
            extraction_result = extract_text_from_pdf(file_path)
            if "error" in extraction_result:
                logger.error(f"Error extracting text from PDF: {extraction_result['error']}")
                return {"error": f"Error extracting text from PDF: {extraction_result['error']}"}
            
            text = extraction_result.get("text", "")
            
            # Get annotations to include in summary
            annotations_query = """
            SELECT * FROM pdf_annotations
            WHERE book_id = ? AND user_id = ? AND annotation_type = 'highlight'
            ORDER BY page_number
            """
            
            annotations = self.db_manager.execute_query(annotations_query, (book_id, user_id)).fetchall()
            
            # Generate summary using LLM
            from ai_note_system.api.llm_interface import get_llm_interface
            
            # Get LLM interface
            llm = get_llm_interface("openai", model="gpt-4")
            
            # Determine summary length based on type
            if summary_type == "short":
                word_count = 500  # ~5 min read
                reading_time = "5-minute"
            elif summary_type == "long":
                word_count = 3000  # ~30 min read
                reading_time = "30-minute"
            else:  # medium
                word_count = 1500  # ~15 min read
                reading_time = "15-minute"
            
            # Create prompt
            prompt = f"""
            Generate a {reading_time} summary of the book "{book['title']}" by {book['author'] or 'Unknown'}.
            
            The summary should be approximately {word_count} words and include:
            1. Main themes and key concepts
            2. Important arguments and evidence
            3. Practical applications and takeaways
            4. Critical insights and conclusions
            
            Format the summary with clear headings, bullet points where appropriate, and a logical flow.
            """
            
            # If we have highlights, include them in the prompt
            if annotations:
                highlights = []
                for annotation in annotations:
                    highlights.append({
                        "page": annotation["page_number"],
                        "text": annotation["content"]
                    })
                
                highlights_text = "\n\n".join([f"Page {h['page']}: {h['text']}" for h in highlights])
                
                prompt += f"""
                
                Additionally, incorporate the following highlighted passages that the user found important:
                
                {highlights_text}
                
                Ensure these highlighted concepts are well-represented in the summary.
                """
            
            # Generate summary
            summary_content = llm.generate(prompt)
            
            # Save summary to database
            summary_data = self.save_summary(
                book_id=book_id,
                user_id=user_id,
                summary_type=summary_type,
                content=summary_content
            )
            
            logger.info(f"Generated {summary_type} summary for book {book_id}")
            return summary_data
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {"error": f"Error generating summary: {str(e)}"}
    
    def save_summary(self,
                   book_id: int,
                   user_id: int,
                   summary_type: str,
                   content: str) -> Dict[str, Any]:
        """
        Save a summary to the database.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            summary_type (str): Type of summary (short, medium, long)
            content (str): Summary content
            
        Returns:
            Dict[str, Any]: Saved summary data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning summary without saving")
            return {
                "book_id": book_id,
                "user_id": user_id,
                "summary_type": summary_type,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO pdf_summaries (
            book_id, user_id, summary_type, content
        )
        VALUES (?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (book_id, user_id, summary_type, content)
            )
            
            summary_id = cursor.lastrowid
            
            logger.debug(f"Saved {summary_type} summary {summary_id} for book {book_id}")
            
            return {
                "id": summary_id,
                "book_id": book_id,
                "user_id": user_id,
                "summary_type": summary_type,
                "content": content,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving summary: {str(e)}")
            return {
                "error": f"Error saving summary: {str(e)}",
                "summary_type": summary_type
            }
    
    def get_summary(self,
                  book_id: int,
                  user_id: int,
                  summary_type: str = "medium") -> Dict[str, Any]:
        """
        Get a summary for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            summary_type (str): Type of summary (short, medium, long)
            
        Returns:
            Dict[str, Any]: Summary data
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        query = """
        SELECT * FROM pdf_summaries
        WHERE book_id = ? AND user_id = ? AND summary_type = ?
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        result = self.db_manager.execute_query(query, (book_id, user_id, summary_type)).fetchone()
        
        if not result:
            logger.warning(f"No {summary_type} summary found for book {book_id}")
            return {"error": f"No {summary_type} summary found"}
        
        return dict(result)
    
    def generate_timeline(self,
                        book_id: int,
                        user_id: int) -> Dict[str, Any]:
        """
        Generate a timeline of key concepts from a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: Generated timeline
        """
        logger.info(f"Generating timeline for book {book_id}")
        
        # Get book information
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        book_query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        book = self.db_manager.execute_query(book_query, (book_id,)).fetchone()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return {"error": f"Book not found: {book_id}"}
        
        # Check if timeline already exists
        existing_timeline = self.get_timeline(book_id, user_id)
        if existing_timeline and "error" not in existing_timeline:
            logger.info(f"Timeline already exists for book {book_id}")
            return existing_timeline
        
        # Get medium summary to use as basis for timeline
        summary = self.get_summary(book_id, user_id, "medium")
        if "error" in summary:
            # Try to generate summary if it doesn't exist
            summary = self.generate_summary(book_id, user_id, "medium")
            if "error" in summary:
                logger.error(f"Error getting summary for timeline: {summary['error']}")
                return {"error": f"Error getting summary for timeline: {summary['error']}"}
        
        # Get structure to help with timeline organization
        structure_query = """
        SELECT * FROM pdf_structure
        WHERE book_id = ?
        ORDER BY level, page_number
        """
        
        structure = self.db_manager.execute_query(structure_query, (book_id,)).fetchall()
        
        # Generate timeline using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate a timeline of key concepts and examples from the book "{book['title']}" by {book['author'] or 'Unknown'}.
        
        Use the following summary as a basis:
        
        {summary['content']}
        """
        
        # If we have structure, include it in the prompt
        if structure:
            structure_text = "\n".join([f"{s['level']}. {s['title']} (Page {s['page_number']})" for s in structure])
            
            prompt += f"""
            
            The book has the following structure:
            
            {structure_text}
            
            Use this structure to organize the timeline chronologically based on the book's flow.
            """
        
        prompt += """
        
        Format the timeline as a JSON array with objects containing:
        1. "position": Sequential position in the timeline (1, 2, 3, etc.)
        2. "title": Title of the concept or example
        3. "description": Brief description of the concept or example
        4. "importance": Importance level (high, medium, low)
        
        The timeline should capture the progression of ideas and concepts throughout the book.
        """
        
        # Generate timeline
        try:
            timeline_data = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "position": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "importance": {"type": "string"}
                        },
                        "required": ["position", "title", "description", "importance"]
                    }
                }
            )
            
            # Save timeline to database
            timeline_result = self.save_timeline(
                book_id=book_id,
                user_id=user_id,
                timeline_data=json.dumps(timeline_data)
            )
            
            logger.info(f"Generated timeline for book {book_id}")
            return timeline_result
            
        except Exception as e:
            logger.error(f"Error generating timeline: {str(e)}")
            return {"error": f"Error generating timeline: {str(e)}"}
    
    def save_timeline(self,
                    book_id: int,
                    user_id: int,
                    timeline_data: str) -> Dict[str, Any]:
        """
        Save a timeline to the database.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            timeline_data (str): JSON string of timeline data
            
        Returns:
            Dict[str, Any]: Saved timeline data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning timeline without saving")
            return {
                "book_id": book_id,
                "user_id": user_id,
                "timeline_data": timeline_data,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO pdf_timelines (
            book_id, user_id, timeline_data
        )
        VALUES (?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (book_id, user_id, timeline_data)
            )
            
            timeline_id = cursor.lastrowid
            
            logger.debug(f"Saved timeline {timeline_id} for book {book_id}")
            
            return {
                "id": timeline_id,
                "book_id": book_id,
                "user_id": user_id,
                "timeline_data": timeline_data,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving timeline: {str(e)}")
            return {
                "error": f"Error saving timeline: {str(e)}"
            }
    
    def get_timeline(self,
                   book_id: int,
                   user_id: int) -> Dict[str, Any]:
        """
        Get a timeline for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: Timeline data
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        query = """
        SELECT * FROM pdf_timelines
        WHERE book_id = ? AND user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """
        
        result = self.db_manager.execute_query(query, (book_id, user_id)).fetchone()
        
        if not result:
            logger.warning(f"No timeline found for book {book_id}")
            return {"error": "No timeline found"}
        
        return dict(result)
    
    def extract_key_concepts(self,
                           book_id: int,
                           user_id: int,
                           max_concepts: int = 10) -> List[Dict[str, Any]]:
        """
        Extract key concepts from a book for knowledge decay tracking.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            max_concepts (int): Maximum number of concepts to extract
            
        Returns:
            List[Dict[str, Any]]: Extracted concepts
        """
        logger.info(f"Extracting key concepts for book {book_id}")
        
        # Get book information
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        book_query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        book = self.db_manager.execute_query(book_query, (book_id,)).fetchone()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return []
        
        # Get medium summary to use as basis for concept extraction
        summary = self.get_summary(book_id, user_id, "medium")
        if "error" in summary:
            # Try to generate summary if it doesn't exist
            summary = self.generate_summary(book_id, user_id, "medium")
            if "error" in summary:
                logger.error(f"Error getting summary for concept extraction: {summary['error']}")
                return []
        
        # Get annotations to help with concept extraction
        annotations_query = """
        SELECT * FROM pdf_annotations
        WHERE book_id = ? AND user_id = ? AND annotation_type = 'highlight'
        ORDER BY page_number
        """
        
        annotations = self.db_manager.execute_query(annotations_query, (book_id, user_id)).fetchall()
        
        # Generate concepts using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Extract the {max_concepts} most important concepts from the book "{book['title']}" by {book['author'] or 'Unknown'}.
        
        Use the following summary as a basis:
        
        {summary['content']}
        """
        
        # If we have annotations, include them in the prompt
        if annotations:
            highlights = []
            for annotation in annotations:
                highlights.append({
                    "page": annotation["page_number"],
                    "text": annotation["content"]
                })
            
            highlights_text = "\n\n".join([f"Page {h['page']}: {h['text']}" for h in highlights])
            
            prompt += f"""
            
            Additionally, consider the following highlighted passages that the user found important:
            
            {highlights_text}
            """
        
        prompt += f"""
        
        For each concept, provide:
        1. The concept name (a short, clear phrase)
        2. A brief description of the concept
        3. The importance of the concept to understanding the book (high, medium, low)
        
        Format your response as a JSON array with objects containing fields:
        - concept: The concept name
        - description: Brief description
        - importance: Importance level (high, medium, low)
        
        Focus on the most important concepts that are worth remembering long-term.
        """
        
        # Extract concepts
        try:
            concepts = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "concept": {"type": "string"},
                            "description": {"type": "string"},
                            "importance": {"type": "string"}
                        },
                        "required": ["concept", "description", "importance"]
                    }
                }
            )
            
            logger.info(f"Extracted {len(concepts)} key concepts for book {book_id}")
            return concepts
            
        except Exception as e:
            logger.error(f"Error extracting key concepts: {str(e)}")
            return []
    
    def track_knowledge_decay(self,
                            book_id: int,
                            user_id: int,
                            decay_params: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """
        Set up knowledge decay tracking for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            decay_params (Dict[str, float], optional): Custom decay parameters
            
        Returns:
            List[Dict[str, Any]]: Tracked concepts with decay information
        """
        logger.info(f"Setting up knowledge decay tracking for book {book_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Use default decay parameters if not provided
        if not decay_params:
            decay_params = self.default_decay_params
        
        # Extract key concepts if not already tracked
        decay_query = """
        SELECT * FROM pdf_knowledge_decay
        WHERE book_id = ? AND user_id = ?
        """
        
        existing_concepts = self.db_manager.execute_query(decay_query, (book_id, user_id)).fetchall()
        
        if existing_concepts:
            logger.info(f"Knowledge decay already being tracked for book {book_id}")
            return [dict(concept) for concept in existing_concepts]
        
        # Extract key concepts
        concepts = self.extract_key_concepts(book_id, user_id)
        
        if not concepts:
            logger.error(f"No concepts extracted for book {book_id}")
            return []
        
        # Set up decay tracking for each concept
        tracked_concepts = []
        current_time = datetime.now()
        
        for concept_data in concepts:
            # Adjust initial strength based on importance
            initial_strength = decay_params["initial_strength"]
            if concept_data["importance"] == "high":
                initial_strength *= 1.2
            elif concept_data["importance"] == "low":
                initial_strength *= 0.8
            
            # Calculate next review time based on decay rate
            decay_rate = decay_params["decay_rate"]
            days_until_review = int(-1 * (1 / decay_rate) * 
                                   (initial_strength - decay_params["threshold"]))
            next_review = current_time + timedelta(days=days_until_review)
            
            # Insert into database
            insert_query = """
            INSERT INTO pdf_knowledge_decay (
                book_id, user_id, concept, initial_strength, current_strength,
                decay_rate, last_reviewed, next_review, review_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            try:
                cursor = self.db_manager.execute_query(
                    insert_query,
                    (
                        book_id, user_id, concept_data["concept"], initial_strength,
                        initial_strength, decay_rate, current_time.isoformat(),
                        next_review.isoformat(), 0
                    )
                )
                
                concept_id = cursor.lastrowid
                
                tracked_concept = {
                    "id": concept_id,
                    "book_id": book_id,
                    "user_id": user_id,
                    "concept": concept_data["concept"],
                    "description": concept_data["description"],
                    "importance": concept_data["importance"],
                    "initial_strength": initial_strength,
                    "current_strength": initial_strength,
                    "decay_rate": decay_rate,
                    "last_reviewed": current_time.isoformat(),
                    "next_review": next_review.isoformat(),
                    "review_count": 0
                }
                
                tracked_concepts.append(tracked_concept)
                
            except Exception as e:
                logger.error(f"Error tracking concept decay: {str(e)}")
        
        logger.info(f"Set up knowledge decay tracking for {len(tracked_concepts)} concepts in book {book_id}")
        return tracked_concepts
    
    def update_concept_strength(self,
                              concept_id: int,
                              recall_quality: float) -> Dict[str, Any]:
        """
        Update the strength of a concept based on recall quality.
        
        Args:
            concept_id (int): ID of the concept
            recall_quality (float): Quality of recall (0.0-1.0)
            
        Returns:
            Dict[str, Any]: Updated concept data
        """
        logger.info(f"Updating strength for concept {concept_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Get concept data
        query = """
        SELECT * FROM pdf_knowledge_decay
        WHERE id = ?
        """
        
        concept = self.db_manager.execute_query(query, (concept_id,)).fetchone()
        
        if not concept:
            logger.error(f"Concept not found: {concept_id}")
            return {"error": f"Concept not found: {concept_id}"}
        
        # Convert to dictionary
        concept_data = dict(concept)
        
        # Update strength based on recall quality
        current_strength = concept_data["current_strength"]
        recall_boost = self.default_decay_params["recall_boost"]
        
        # Adjust boost based on recall quality
        adjusted_boost = recall_boost * recall_quality
        
        # Calculate new strength
        new_strength = min(1.0, current_strength + adjusted_boost)
        
        # Calculate next review time based on decay rate
        decay_rate = concept_data["decay_rate"]
        threshold = self.default_decay_params["threshold"]
        
        days_until_review = int(-1 * (1 / decay_rate) * 
                               (new_strength - threshold))
        
        current_time = datetime.now()
        next_review = current_time + timedelta(days=days_until_review)
        
        # Update database
        update_query = """
        UPDATE pdf_knowledge_decay
        SET current_strength = ?, last_reviewed = ?, next_review = ?, review_count = review_count + 1
        WHERE id = ?
        """
        
        try:
            self.db_manager.execute_query(
                update_query,
                (new_strength, current_time.isoformat(), next_review.isoformat(), concept_id)
            )
            
            # Update concept data
            concept_data["current_strength"] = new_strength
            concept_data["last_reviewed"] = current_time.isoformat()
            concept_data["next_review"] = next_review.isoformat()
            concept_data["review_count"] += 1
            
            logger.info(f"Updated strength for concept {concept_id}: {current_strength:.2f} -> {new_strength:.2f}")
            return concept_data
            
        except Exception as e:
            logger.error(f"Error updating concept strength: {str(e)}")
            return {"error": f"Error updating concept strength: {str(e)}"}
    
    def get_due_concepts(self,
                       user_id: int,
                       book_id: Optional[int] = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get concepts that are due for review.
        
        Args:
            user_id (int): ID of the user
            book_id (int, optional): ID of the book to filter by
            limit (int): Maximum number of concepts to return
            
        Returns:
            List[Dict[str, Any]]: Due concepts
        """
        logger.info(f"Getting due concepts for user {user_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT kd.*, b.title as book_title
        FROM pdf_knowledge_decay kd
        JOIN pdf_books b ON kd.book_id = b.id
        WHERE kd.user_id = ? AND kd.next_review <= ?
        """
        
        params = [user_id, datetime.now().isoformat()]
        
        if book_id is not None:
            query += " AND kd.book_id = ?"
            params.append(book_id)
        
        query += " ORDER BY kd.next_review ASC LIMIT ?"
        params.append(limit)
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def generate_contextual_reminder(self,
                                   book_id: int,
                                   user_id: int) -> Dict[str, Any]:
        """
        Generate a contextual reminder for a previously read book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: Generated reminder
        """
        logger.info(f"Generating contextual reminder for book {book_id}")
        
        # Get book information
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        book_query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        book = self.db_manager.execute_query(book_query, (book_id,)).fetchone()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return {"error": f"Book not found: {book_id}"}
        
        # Get short summary
        summary = self.get_summary(book_id, user_id, "short")
        if "error" in summary:
            # Try to generate summary if it doesn't exist
            summary = self.generate_summary(book_id, user_id, "short")
            if "error" in summary:
                logger.error(f"Error getting summary for reminder: {summary['error']}")
                return {"error": f"Error getting summary for reminder: {summary['error']}"}
        
        # Get key concepts
        decay_query = """
        SELECT * FROM pdf_knowledge_decay
        WHERE book_id = ? AND user_id = ?
        ORDER BY current_strength ASC
        LIMIT 5
        """
        
        concepts = self.db_manager.execute_query(decay_query, (book_id, user_id)).fetchall()
        
        # Calculate time since last read
        last_read = datetime.fromisoformat(book["last_read"])
        now = datetime.now()
        days_since_read = (now - last_read).days
        
        if days_since_read < 30:
            time_period = f"{days_since_read} days"
        elif days_since_read < 365:
            months = days_since_read // 30
            time_period = f"{months} months"
        else:
            years = days_since_read // 365
            time_period = f"{years} year" + ("s" if years > 1 else "")
        
        # Generate reminder using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate a contextual reminder for the book "{book['title']}" by {book['author'] or 'Unknown'} that the user read {time_period} ago.
        
        The reminder should include:
        1. A brief recap of the book (5-minute read)
        2. 3 core quiz questions to test recall of key concepts
        3. A note about why this book remains relevant
        
        Use the following summary as a basis:
        
        {summary['content']}
        """
        
        # If we have concepts, include them in the prompt
        if concepts:
            concepts_text = "\n".join([f"- {c['concept']}: {c['current_strength']:.2f} strength" for c in concepts])
            
            prompt += f"""
            
            Focus on these key concepts that may need reinforcement:
            
            {concepts_text}
            
            Include questions specifically targeting these concepts.
            """
        
        # Generate reminder
        try:
            reminder_content = llm.generate(prompt)
            
            reminder = {
                "book_id": book_id,
                "user_id": user_id,
                "book_title": book["title"],
                "book_author": book["author"],
                "time_since_read": time_period,
                "content": reminder_content,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated contextual reminder for book {book_id}")
            return reminder
            
        except Exception as e:
            logger.error(f"Error generating contextual reminder: {str(e)}")
            return {"error": f"Error generating contextual reminder: {str(e)}"}
    
    def link_concepts_across_books(self,
                                 user_id: int,
                                 min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """
        Link overlapping concepts across books.
        
        Args:
            user_id (int): ID of the user
            min_similarity (float): Minimum similarity score for linking
            
        Returns:
            List[Dict[str, Any]]: Linked concepts
        """
        logger.info(f"Linking concepts across books for user {user_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        if not self.embedder:
            logger.error("No embedder available for concept linking")
            return []
        
        # Get all concepts for the user
        query = """
        SELECT kd.*, b.title as book_title
        FROM pdf_knowledge_decay kd
        JOIN pdf_books b ON kd.book_id = b.id
        WHERE kd.user_id = ?
        """
        
        concepts = self.db_manager.execute_query(query, (user_id,)).fetchall()
        
        if not concepts:
            logger.warning(f"No concepts found for user {user_id}")
            return []
        
        # Convert to list of dictionaries
        concept_list = [dict(c) for c in concepts]
        
        # Group concepts by book
        concepts_by_book = {}
        for concept in concept_list:
            book_id = concept["book_id"]
            if book_id not in concepts_by_book:
                concepts_by_book[book_id] = []
            concepts_by_book[book_id].append(concept)
        
        # Find links between concepts in different books
        links = []
        
        # Get all book pairs
        book_ids = list(concepts_by_book.keys())
        for i in range(len(book_ids)):
            for j in range(i + 1, len(book_ids)):
                book_id_1 = book_ids[i]
                book_id_2 = book_ids[j]
                
                # Get concepts for each book
                concepts_1 = concepts_by_book[book_id_1]
                concepts_2 = concepts_by_book[book_id_2]
                
                # Compare each concept pair
                for concept_1 in concepts_1:
                    # Get embedding for concept 1
                    concept_1_text = f"{concept_1['concept']}: {concept_1.get('description', '')}"
                    concept_1_embedding = self.embedder.get_embedding(concept_1_text)
                    
                    for concept_2 in concepts_2:
                        # Get embedding for concept 2
                        concept_2_text = f"{concept_2['concept']}: {concept_2.get('description', '')}"
                        concept_2_embedding = self.embedder.get_embedding(concept_2_text)
                        
                        # Calculate similarity
                        similarity = self.embedder.calculate_similarity(concept_1_embedding, concept_2_embedding)
                        
                        # If similarity is high enough, create a link
                        if similarity >= min_similarity:
                            # Check if link already exists
                            link_query = """
                            SELECT * FROM pdf_concept_links
                            WHERE (book_id_1 = ? AND book_id_2 = ? AND concept = ? AND user_id = ?)
                            OR (book_id_1 = ? AND book_id_2 = ? AND concept = ? AND user_id = ?)
                            """
                            
                            existing_link = self.db_manager.execute_query(
                                link_query, 
                                (
                                    book_id_1, book_id_2, concept_1['concept'], user_id,
                                    book_id_2, book_id_1, concept_2['concept'], user_id
                                )
                            ).fetchone()
                            
                            if existing_link:
                                continue
                            
                            # Generate description of the link using LLM
                            from ai_note_system.api.llm_interface import get_llm_interface
                            
                            # Get LLM interface
                            llm = get_llm_interface("openai", model="gpt-4")
                            
                            # Create prompt
                            prompt = f"""
                            Describe the relationship between these two similar concepts from different books:
                            
                            Book 1: {concept_1['book_title']}
                            Concept 1: {concept_1['concept']}
                            Description 1: {concept_1.get('description', '')}
                            
                            Book 2: {concept_2['book_title']}
                            Concept 2: {concept_2['concept']}
                            Description 2: {concept_2.get('description', '')}
                            
                            Provide a brief description of how these concepts are related, how they complement or contrast with each other,
                            and what insights can be gained by connecting them. Keep the description under 100 words.
                            """
                            
                            try:
                                link_description = llm.generate(prompt)
                                
                                # Insert link into database
                                insert_query = """
                                INSERT INTO pdf_concept_links (
                                    concept, book_id_1, book_id_2, user_id, similarity_score, description
                                )
                                VALUES (?, ?, ?, ?, ?, ?)
                                """
                                
                                cursor = self.db_manager.execute_query(
                                    insert_query,
                                    (
                                        concept_1['concept'], book_id_1, book_id_2,
                                        user_id, similarity, link_description
                                    )
                                )
                                
                                link_id = cursor.lastrowid
                                
                                link = {
                                    "id": link_id,
                                    "concept": concept_1['concept'],
                                    "book_id_1": book_id_1,
                                    "book_title_1": concept_1['book_title'],
                                    "book_id_2": book_id_2,
                                    "book_title_2": concept_2['book_title'],
                                    "user_id": user_id,
                                    "similarity_score": similarity,
                                    "description": link_description,
                                    "created_at": datetime.now().isoformat()
                                }
                                
                                links.append(link)
                                
                            except Exception as e:
                                logger.error(f"Error creating concept link: {str(e)}")
        
        logger.info(f"Created {len(links)} concept links across books for user {user_id}")
        return links
    
    def get_concept_links(self,
                        user_id: int,
                        book_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get concept links for a user.
        
        Args:
            user_id (int): ID of the user
            book_id (int, optional): ID of the book to filter by
            
        Returns:
            List[Dict[str, Any]]: Concept links
        """
        logger.info(f"Getting concept links for user {user_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT cl.*, b1.title as book_title_1, b2.title as book_title_2
        FROM pdf_concept_links cl
        JOIN pdf_books b1 ON cl.book_id_1 = b1.id
        JOIN pdf_books b2 ON cl.book_id_2 = b2.id
        WHERE cl.user_id = ?
        """
        
        params = [user_id]
        
        if book_id is not None:
            query += " AND (cl.book_id_1 = ? OR cl.book_id_2 = ?)"
            params.extend([book_id, book_id])
        
        query += " ORDER BY cl.created_at DESC"
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def generate_quick_recall_session(self,
                                    book_id: int,
                                    user_id: int) -> Dict[str, Any]:
        """
        Generate a quick recall session for refreshing book content.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: Quick recall session
        """
        logger.info(f"Generating quick recall session for book {book_id}")
        
        # Get book information
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        book_query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        book = self.db_manager.execute_query(book_query, (book_id,)).fetchone()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return {"error": f"Book not found: {book_id}"}
        
        # Get medium summary
        summary = self.get_summary(book_id, user_id, "medium")
        if "error" in summary:
            # Try to generate summary if it doesn't exist
            summary = self.generate_summary(book_id, user_id, "medium")
            if "error" in summary:
                logger.error(f"Error getting summary for quick recall: {summary['error']}")
                return {"error": f"Error getting summary for quick recall: {summary['error']}"}
        
        # Get key concepts
        decay_query = """
        SELECT * FROM pdf_knowledge_decay
        WHERE book_id = ? AND user_id = ?
        ORDER BY current_strength ASC
        LIMIT 10
        """
        
        concepts = self.db_manager.execute_query(decay_query, (book_id, user_id)).fetchall()
        
        # Get annotations
        annotations_query = """
        SELECT * FROM pdf_annotations
        WHERE book_id = ? AND user_id = ? AND annotation_type = 'highlight'
        ORDER BY page_number
        LIMIT 20
        """
        
        annotations = self.db_manager.execute_query(annotations_query, (book_id, user_id)).fetchall()
        
        # Generate quick recall session using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate a 15-minute interactive recall session for the book "{book['title']}" by {book['author'] or 'Unknown'}.
        
        The session should include:
        1. A structured summary of the book's key points
        2. Interactive elements to test recall (questions, fill-in-the-blanks, etc.)
        3. Diagram recall prompts (asking the user to visualize or sketch key concepts)
        4. A short quiz with varied question types
        
        Use the following summary as a basis:
        
        {summary['content']}
        """
        
        # If we have concepts, include them in the prompt
        if concepts:
            concepts_text = "\n".join([f"- {c['concept']}" for c in concepts])
            
            prompt += f"""
            
            Focus on these key concepts:
            
            {concepts_text}
            """
        
        # If we have annotations, include them in the prompt
        if annotations:
            highlights = []
            for annotation in annotations:
                highlights.append({
                    "page": annotation["page_number"],
                    "text": annotation["content"]
                })
            
            highlights_text = "\n\n".join([f"Page {h['page']}: {h['text']}" for h in highlights[:10]])
            
            prompt += f"""
            
            Include these highlighted passages from the user's notes:
            
            {highlights_text}
            """
        
        prompt += """
        
        Format the session as an interactive experience with clear sections:
        1. "Key Concepts Review" - A structured summary
        2. "Active Recall Exercises" - Interactive elements
        3. "Visualization Challenges" - Diagram recall prompts
        4. "Comprehension Quiz" - A short quiz
        
        The session should be engaging, varied, and designed to strengthen memory of the book's content.
        """
        
        # Generate quick recall session
        try:
            session_content = llm.generate(prompt)
            
            session = {
                "book_id": book_id,
                "user_id": user_id,
                "book_title": book["title"],
                "book_author": book["author"],
                "content": session_content,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated quick recall session for book {book_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error generating quick recall session: {str(e)}")
            return {"error": f"Error generating quick recall session: {str(e)}"}
"""