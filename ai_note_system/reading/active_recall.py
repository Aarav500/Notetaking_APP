"""
Active Recall module for AI Note System.
Provides functionality for generating questions, flashcards, and mind maps during reading.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.reading.active_recall")

class ActiveRecallGenerator:
    """
    Active Recall Generator class for creating learning materials during reading.
    Generates micro-questions, flashcards, and mind maps based on content.
    """
    
    def __init__(self, db_manager=None, embedder=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Active Recall Generator.
        
        Args:
            db_manager: Database manager instance
            embedder: Embedder instance for semantic processing
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.db_manager = db_manager
        self.embedder = embedder
        self.config = config or {}
        self._ensure_active_recall_tables()
        
        logger.debug("Initialized ActiveRecallGenerator")
    
    def _ensure_active_recall_tables(self) -> None:
        """
        Ensure the active recall related tables exist in the database.
        """
        if not self.db_manager:
            logger.warning("No database manager provided, skipping table creation")
            return
            
        # Create pdf_questions table
        questions_query = """
        CREATE TABLE IF NOT EXISTS pdf_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            section_text TEXT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            question_type TEXT NOT NULL,
            difficulty TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(questions_query)
        
        # Create pdf_flashcards table
        flashcards_query = """
        CREATE TABLE IF NOT EXISTS pdf_flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            front_text TEXT NOT NULL,
            back_text TEXT NOT NULL,
            image_path TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(flashcards_query)
        
        # Create pdf_mindmaps table
        mindmaps_query = """
        CREATE TABLE IF NOT EXISTS pdf_mindmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            central_concept TEXT NOT NULL,
            map_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(mindmaps_query)
        
        logger.debug("Ensured active recall tables exist in database")
    
    def generate_micro_questions(self, 
                               book_id: int, 
                               user_id: int, 
                               page_number: int, 
                               text: str,
                               count: int = 3,
                               question_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate micro-questions for a section of text.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            text (str): Text to generate questions from
            count (int): Number of questions to generate
            question_types (List[str], optional): Types of questions to generate
            
        Returns:
            List[Dict[str, Any]]: Generated questions
        """
        logger.info(f"Generating {count} micro-questions for book {book_id}, page {page_number}")
        
        # Default question types if not provided
        if not question_types:
            question_types = ["factual", "conceptual", "application"]
        
        # Truncate text if too long
        max_text_length = 2000
        if len(text) > max_text_length:
            # Try to truncate at sentence boundary
            truncated_text = text[:max_text_length]
            last_period = truncated_text.rfind('.')
            if last_period > max_text_length * 0.8:  # If period is reasonably close to the end
                text = truncated_text[:last_period + 1]
            else:
                text = truncated_text
        
        # Generate questions using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate {count} thought-provoking questions based on the following text. 
        The questions should test understanding and recall of key concepts.
        
        Text from page {page_number}:
        {text}
        
        Generate a mix of the following question types:
        {', '.join(question_types)}
        
        For each question, provide:
        1. The question
        2. The correct answer
        3. The question type (factual, conceptual, application)
        4. Difficulty level (easy, medium, hard)
        
        Format your response as a JSON array with objects containing fields:
        - question: The question text
        - answer: The correct answer
        - question_type: Type of question
        - difficulty: Difficulty level
        
        Only include questions that can be answered based on the provided text.
        """
        
        # Generate questions
        try:
            response = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "answer": {"type": "string"},
                            "question_type": {"type": "string"},
                            "difficulty": {"type": "string"}
                        },
                        "required": ["question", "answer", "question_type", "difficulty"]
                    }
                }
            )
            
            # Save questions to database
            questions = []
            for q in response:
                question_data = self.save_question(
                    book_id=book_id,
                    user_id=user_id,
                    page_number=page_number,
                    section_text=text[:500],  # Store first 500 chars of section
                    question=q["question"],
                    answer=q["answer"],
                    question_type=q["question_type"],
                    difficulty=q["difficulty"]
                )
                questions.append(question_data)
            
            logger.info(f"Generated {len(questions)} micro-questions for book {book_id}, page {page_number}")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating micro-questions: {str(e)}")
            return []
    
    def save_question(self,
                    book_id: int,
                    user_id: int,
                    page_number: int,
                    section_text: str,
                    question: str,
                    answer: str,
                    question_type: str,
                    difficulty: str) -> Dict[str, Any]:
        """
        Save a question to the database.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            section_text (str): Text the question is based on
            question (str): Question text
            answer (str): Answer text
            question_type (str): Type of question
            difficulty (str): Difficulty level
            
        Returns:
            Dict[str, Any]: Saved question data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning question without saving")
            return {
                "book_id": book_id,
                "user_id": user_id,
                "page_number": page_number,
                "section_text": section_text,
                "question": question,
                "answer": answer,
                "question_type": question_type,
                "difficulty": difficulty,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO pdf_questions (
            book_id, user_id, page_number, section_text,
            question, answer, question_type, difficulty
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (
                    book_id, user_id, page_number, section_text,
                    question, answer, question_type, difficulty
                )
            )
            
            question_id = cursor.lastrowid
            
            logger.debug(f"Saved question {question_id} for book {book_id}, page {page_number}")
            
            return {
                "id": question_id,
                "book_id": book_id,
                "user_id": user_id,
                "page_number": page_number,
                "section_text": section_text,
                "question": question,
                "answer": answer,
                "question_type": question_type,
                "difficulty": difficulty,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving question: {str(e)}")
            return {
                "error": f"Error saving question: {str(e)}",
                "question": question,
                "answer": answer
            }
    
    def get_questions(self,
                    book_id: int,
                    user_id: int,
                    page_number: Optional[int] = None,
                    question_type: Optional[str] = None,
                    difficulty: Optional[str] = None,
                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get questions for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int, optional): Page number to filter by
            question_type (str, optional): Question type to filter by
            difficulty (str, optional): Difficulty level to filter by
            limit (int): Maximum number of questions to return
            
        Returns:
            List[Dict[str, Any]]: List of questions
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT * FROM pdf_questions
        WHERE book_id = ? AND user_id = ?
        """
        
        params = [book_id, user_id]
        
        if page_number is not None:
            query += " AND page_number = ?"
            params.append(page_number)
        
        if question_type:
            query += " AND question_type = ?"
            params.append(question_type)
        
        if difficulty:
            query += " AND difficulty = ?"
            params.append(difficulty)
        
        query += " ORDER BY page_number, created_at LIMIT ?"
        params.append(limit)
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def generate_flashcards_from_image(self,
                                     book_id: int,
                                     user_id: int,
                                     page_number: int,
                                     image_path: str,
                                     count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate flashcards from an image using GPT-Vision.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            image_path (str): Path to the image
            count (int): Number of flashcards to generate
            
        Returns:
            List[Dict[str, Any]]: Generated flashcards
        """
        logger.info(f"Generating {count} flashcards from image for book {book_id}, page {page_number}")
        
        # Check if image exists
        if not os.path.exists(image_path):
            logger.error(f"Image not found: {image_path}")
            return []
        
        # Generate flashcards using GPT-Vision
        try:
            from ai_note_system.api.llm_interface import get_llm_interface
            
            # Get LLM interface with vision capabilities
            llm = get_llm_interface("openai", model="gpt-4-vision-preview")
            
            # Read image as base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt
            prompt = f"""
            Generate {count} flashcards based on the content in this image from page {page_number}.
            Focus on key concepts, definitions, and important facts.
            
            For each flashcard, provide:
            1. Front text (question or concept)
            2. Back text (answer or explanation)
            3. Tags (comma-separated keywords)
            
            Format your response as a JSON array with objects containing fields:
            - front_text: Text for the front of the flashcard
            - back_text: Text for the back of the flashcard
            - tags: Comma-separated tags
            """
            
            # Generate flashcards
            response = llm.generate_structured_output_with_image(
                prompt=prompt,
                image_data=image_data,
                output_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "front_text": {"type": "string"},
                            "back_text": {"type": "string"},
                            "tags": {"type": "string"}
                        },
                        "required": ["front_text", "back_text", "tags"]
                    }
                }
            )
            
            # Save flashcards to database
            flashcards = []
            for fc in response:
                flashcard_data = self.save_flashcard(
                    book_id=book_id,
                    user_id=user_id,
                    page_number=page_number,
                    front_text=fc["front_text"],
                    back_text=fc["back_text"],
                    image_path=image_path,
                    tags=fc["tags"]
                )
                flashcards.append(flashcard_data)
            
            logger.info(f"Generated {len(flashcards)} flashcards from image for book {book_id}, page {page_number}")
            return flashcards
            
        except Exception as e:
            logger.error(f"Error generating flashcards from image: {str(e)}")
            return []
    
    def generate_flashcards_from_text(self,
                                    book_id: int,
                                    user_id: int,
                                    page_number: int,
                                    text: str,
                                    count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate flashcards from text.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            text (str): Text to generate flashcards from
            count (int): Number of flashcards to generate
            
        Returns:
            List[Dict[str, Any]]: Generated flashcards
        """
        logger.info(f"Generating {count} flashcards from text for book {book_id}, page {page_number}")
        
        # Truncate text if too long
        max_text_length = 2000
        if len(text) > max_text_length:
            # Try to truncate at sentence boundary
            truncated_text = text[:max_text_length]
            last_period = truncated_text.rfind('.')
            if last_period > max_text_length * 0.8:  # If period is reasonably close to the end
                text = truncated_text[:last_period + 1]
            else:
                text = truncated_text
        
        # Generate flashcards using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate {count} flashcards based on the following text from page {page_number}.
        Focus on key concepts, definitions, and important facts.
        
        Text:
        {text}
        
        For each flashcard, provide:
        1. Front text (question or concept)
        2. Back text (answer or explanation)
        3. Tags (comma-separated keywords)
        
        Format your response as a JSON array with objects containing fields:
        - front_text: Text for the front of the flashcard
        - back_text: Text for the back of the flashcard
        - tags: Comma-separated tags
        """
        
        # Generate flashcards
        try:
            response = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "front_text": {"type": "string"},
                            "back_text": {"type": "string"},
                            "tags": {"type": "string"}
                        },
                        "required": ["front_text", "back_text", "tags"]
                    }
                }
            )
            
            # Save flashcards to database
            flashcards = []
            for fc in response:
                flashcard_data = self.save_flashcard(
                    book_id=book_id,
                    user_id=user_id,
                    page_number=page_number,
                    front_text=fc["front_text"],
                    back_text=fc["back_text"],
                    image_path=None,
                    tags=fc["tags"]
                )
                flashcards.append(flashcard_data)
            
            logger.info(f"Generated {len(flashcards)} flashcards from text for book {book_id}, page {page_number}")
            return flashcards
            
        except Exception as e:
            logger.error(f"Error generating flashcards from text: {str(e)}")
            return []
    
    def save_flashcard(self,
                     book_id: int,
                     user_id: int,
                     page_number: int,
                     front_text: str,
                     back_text: str,
                     image_path: Optional[str] = None,
                     tags: Optional[str] = None) -> Dict[str, Any]:
        """
        Save a flashcard to the database.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            front_text (str): Text for the front of the flashcard
            back_text (str): Text for the back of the flashcard
            image_path (str, optional): Path to the image
            tags (str, optional): Comma-separated tags
            
        Returns:
            Dict[str, Any]: Saved flashcard data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning flashcard without saving")
            return {
                "book_id": book_id,
                "user_id": user_id,
                "page_number": page_number,
                "front_text": front_text,
                "back_text": back_text,
                "image_path": image_path,
                "tags": tags,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO pdf_flashcards (
            book_id, user_id, page_number, front_text,
            back_text, image_path, tags
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (
                    book_id, user_id, page_number, front_text,
                    back_text, image_path, tags
                )
            )
            
            flashcard_id = cursor.lastrowid
            
            logger.debug(f"Saved flashcard {flashcard_id} for book {book_id}, page {page_number}")
            
            return {
                "id": flashcard_id,
                "book_id": book_id,
                "user_id": user_id,
                "page_number": page_number,
                "front_text": front_text,
                "back_text": back_text,
                "image_path": image_path,
                "tags": tags,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving flashcard: {str(e)}")
            return {
                "error": f"Error saving flashcard: {str(e)}",
                "front_text": front_text,
                "back_text": back_text
            }
    
    def get_flashcards(self,
                     book_id: int,
                     user_id: int,
                     page_number: Optional[int] = None,
                     tags: Optional[str] = None,
                     limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get flashcards for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int, optional): Page number to filter by
            tags (str, optional): Tags to filter by (comma-separated)
            limit (int): Maximum number of flashcards to return
            
        Returns:
            List[Dict[str, Any]]: List of flashcards
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT * FROM pdf_flashcards
        WHERE book_id = ? AND user_id = ?
        """
        
        params = [book_id, user_id]
        
        if page_number is not None:
            query += " AND page_number = ?"
            params.append(page_number)
        
        if tags:
            # Split tags and create LIKE conditions for each tag
            tag_list = [tag.strip() for tag in tags.split(',')]
            tag_conditions = []
            for tag in tag_list:
                tag_conditions.append("tags LIKE ?")
                params.append(f"%{tag}%")
            
            if tag_conditions:
                query += " AND (" + " OR ".join(tag_conditions) + ")"
        
        query += " ORDER BY page_number, created_at LIMIT ?"
        params.append(limit)
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def generate_mindmap_from_highlights(self,
                                       book_id: int,
                                       user_id: int,
                                       title: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a mind map from highlighted content.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            title (str, optional): Title for the mind map
            
        Returns:
            Dict[str, Any]: Generated mind map
        """
        logger.info(f"Generating mind map from highlights for book {book_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Get book information
        book_query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        book = self.db_manager.execute_query(book_query, (book_id,)).fetchone()
        if not book:
            logger.error(f"Book not found: {book_id}")
            return {"error": f"Book not found: {book_id}"}
        
        # Get highlighted annotations
        annotations_query = """
        SELECT * FROM pdf_annotations
        WHERE book_id = ? AND user_id = ? AND annotation_type = 'highlight'
        ORDER BY page_number
        """
        
        annotations = self.db_manager.execute_query(annotations_query, (book_id, user_id)).fetchall()
        
        if not annotations:
            logger.warning(f"No highlights found for book {book_id}")
            return {"error": "No highlights found"}
        
        # Extract highlighted text
        highlights = []
        for annotation in annotations:
            highlights.append({
                "page": annotation["page_number"],
                "text": annotation["content"]
            })
        
        # Generate mind map using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        highlights_text = "\n\n".join([f"Page {h['page']}: {h['text']}" for h in highlights])
        
        if not title:
            title = f"Mind Map for {book['title']}"
        
        prompt = f"""
        Generate a mind map based on the following highlighted text from the book "{book['title']}".
        
        Highlighted text:
        {highlights_text}
        
        Create a hierarchical mind map with:
        1. A central concept (the main topic)
        2. Main branches (key themes or categories)
        3. Sub-branches (supporting concepts, details, examples)
        
        Format your response as a JSON object with the following structure:
        {{
            "central_concept": "Main topic",
            "branches": [
                {{
                    "name": "Branch 1",
                    "sub_branches": [
                        {{"name": "Sub-branch 1.1"}},
                        {{"name": "Sub-branch 1.2", "sub_branches": [...]}},
                        ...
                    ]
                }},
                {{
                    "name": "Branch 2",
                    "sub_branches": [...]
                }},
                ...
            ]
        }}
        
        Ensure the mind map captures the key concepts and their relationships from the highlighted text.
        """
        
        # Generate mind map
        try:
            response = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "object",
                    "properties": {
                        "central_concept": {"type": "string"},
                        "branches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "sub_branches": {"type": "array"}
                                },
                                "required": ["name"]
                            }
                        }
                    },
                    "required": ["central_concept", "branches"]
                }
            )
            
            # Save mind map to database
            mindmap_data = self.save_mindmap(
                book_id=book_id,
                user_id=user_id,
                title=title,
                central_concept=response["central_concept"],
                map_data=json.dumps(response)
            )
            
            logger.info(f"Generated mind map for book {book_id}")
            return mindmap_data
            
        except Exception as e:
            logger.error(f"Error generating mind map: {str(e)}")
            return {"error": f"Error generating mind map: {str(e)}"}
    
    def save_mindmap(self,
                   book_id: int,
                   user_id: int,
                   title: str,
                   central_concept: str,
                   map_data: str) -> Dict[str, Any]:
        """
        Save a mind map to the database.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            title (str): Title of the mind map
            central_concept (str): Central concept of the mind map
            map_data (str): JSON string of mind map data
            
        Returns:
            Dict[str, Any]: Saved mind map data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning mind map without saving")
            return {
                "book_id": book_id,
                "user_id": user_id,
                "title": title,
                "central_concept": central_concept,
                "map_data": map_data,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO pdf_mindmaps (
            book_id, user_id, title, central_concept, map_data
        )
        VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (book_id, user_id, title, central_concept, map_data)
            )
            
            mindmap_id = cursor.lastrowid
            
            logger.debug(f"Saved mind map {mindmap_id} for book {book_id}")
            
            return {
                "id": mindmap_id,
                "book_id": book_id,
                "user_id": user_id,
                "title": title,
                "central_concept": central_concept,
                "map_data": map_data,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving mind map: {str(e)}")
            return {
                "error": f"Error saving mind map: {str(e)}",
                "title": title,
                "central_concept": central_concept
            }
    
    def get_mindmaps(self,
                   book_id: int,
                   user_id: int) -> List[Dict[str, Any]]:
        """
        Get mind maps for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of mind maps
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        query = """
        SELECT * FROM pdf_mindmaps
        WHERE book_id = ? AND user_id = ?
        ORDER BY created_at DESC
        """
        
        results = self.db_manager.execute_query(query, (book_id, user_id)).fetchall()
        
        return [dict(result) for result in results]
"""