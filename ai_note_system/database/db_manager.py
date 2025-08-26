"""
Database manager module for AI Note System.
Handles SQLite database operations for storing and retrieving notes.
"""

import os
import sqlite3
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.database.db_manager")

class DatabaseManager:
    """
    Database manager class for AI Note System.
    Handles SQLite database operations for storing and retrieving notes.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Connect to database
        self.connect()
        
    def connect(self):
        """
        Connect to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            logger.debug(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
            
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")
            
    def __enter__(self):
        """
        Context manager entry.
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close()
        
    # CRUD operations for notes
    
    def create_note(self, note_data: Dict[str, Any]) -> int:
        """
        Create a new note in the database.
        
        Args:
            note_data (Dict[str, Any]): Note data including title, text, summary, etc.
            
        Returns:
            int: ID of the created note
        """
        try:
            # Extract note fields
            title = note_data.get("title", "Untitled")
            text = note_data.get("text", "")
            summary = note_data.get("summary", None)
            source_type = note_data.get("source_type", "text")
            path = note_data.get("path", None)
            timestamp = note_data.get("timestamp", datetime.now().isoformat())
            
            # Calculate word and character counts
            word_count = len(text.split()) if text else 0
            char_count = len(text) if text else 0
            
            # Insert note
            self.cursor.execute('''
            INSERT INTO notes (
                title, text, summary, timestamp, source_type, 
                word_count, char_count, path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                title, text, summary, timestamp, source_type, 
                word_count, char_count, path
            ))
            
            note_id = self.cursor.lastrowid
            
            # Add tags if provided
            tags = note_data.get("tags", [])
            if tags:
                self.add_tags_to_note(note_id, tags)
            
            # Add key points if provided
            keypoints = note_data.get("keypoints", [])
            if keypoints:
                self.add_keypoints_to_note(note_id, keypoints)
            
            # Add glossary terms if provided
            glossary = note_data.get("glossary", {})
            if glossary:
                self.add_glossary_to_note(note_id, glossary)
            
            # Add questions if provided
            questions = note_data.get("questions", [])
            if questions:
                self.add_questions_to_note(note_id, questions)
            
            self.conn.commit()
            logger.info(f"Created note with ID {note_id}: {title}")
            return note_id
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error creating note: {e}")
            raise
    
    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a note by ID.
        
        Args:
            note_id (int): ID of the note to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Note data or None if not found
        """
        try:
            # Get note
            self.cursor.execute('''
            SELECT * FROM notes WHERE id = ?
            ''', (note_id,))
            
            note = self.cursor.fetchone()
            if not note:
                return None
            
            # Convert to dictionary
            note_dict = dict(note)
            
            # Get tags
            note_dict["tags"] = self.get_note_tags(note_id)
            
            # Get key points
            note_dict["keypoints"] = self.get_note_keypoints(note_id)
            
            # Get glossary
            note_dict["glossary"] = self.get_note_glossary(note_id)
            
            # Get questions
            note_dict["questions"] = self.get_note_questions(note_id)
            
            # Get related notes
            note_dict["related_notes"] = self.get_related_notes(note_id)
            
            return note_dict
            
        except sqlite3.Error as e:
            logger.error(f"Error getting note: {e}")
            return None
    
    def update_note(self, note_id: int, note_data: Dict[str, Any]) -> bool:
        """
        Update an existing note.
        
        Args:
            note_id (int): ID of the note to update
            note_data (Dict[str, Any]): Updated note data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if note exists
            self.cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
            if not self.cursor.fetchone():
                logger.error(f"Note with ID {note_id} not found")
                return False
            
            # Update fields that are provided
            update_fields = []
            update_values = []
            
            for field in ["title", "text", "summary", "source_type", "path"]:
                if field in note_data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(note_data[field])
            
            # Update word and character counts if text is provided
            if "text" in note_data:
                text = note_data["text"]
                update_fields.append("word_count = ?")
                update_values.append(len(text.split()) if text else 0)
                update_fields.append("char_count = ?")
                update_values.append(len(text) if text else 0)
            
            if update_fields:
                # Construct and execute update query
                query = f"UPDATE notes SET {', '.join(update_fields)} WHERE id = ?"
                update_values.append(note_id)
                self.cursor.execute(query, update_values)
            
            # Update tags if provided
            if "tags" in note_data:
                # Remove existing tags
                self.cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
                # Add new tags
                self.add_tags_to_note(note_id, note_data["tags"])
            
            # Update key points if provided
            if "keypoints" in note_data:
                # Remove existing key points
                self.cursor.execute("DELETE FROM keypoints WHERE note_id = ?", (note_id,))
                # Add new key points
                self.add_keypoints_to_note(note_id, note_data["keypoints"])
            
            # Update glossary if provided
            if "glossary" in note_data:
                # Remove existing glossary terms
                self.cursor.execute("DELETE FROM glossary WHERE note_id = ?", (note_id,))
                # Add new glossary terms
                self.add_glossary_to_note(note_id, note_data["glossary"])
            
            # Update questions if provided
            if "questions" in note_data:
                # Remove existing questions
                self.cursor.execute("DELETE FROM questions WHERE note_id = ?", (note_id,))
                # Add new questions
                self.add_questions_to_note(note_id, note_data["questions"])
            
            self.conn.commit()
            logger.info(f"Updated note with ID {note_id}")
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error updating note: {e}")
            return False
    
    def delete_note(self, note_id: int) -> bool:
        """
        Delete a note.
        
        Args:
            note_id (int): ID of the note to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if note exists
            self.cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
            if not self.cursor.fetchone():
                logger.error(f"Note with ID {note_id} not found")
                return False
            
            # Delete note (cascading delete will handle related records)
            self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            
            self.conn.commit()
            logger.info(f"Deleted note with ID {note_id}")
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error deleting note: {e}")
            return False
    
    def search_notes(
        self, 
        query: str = None, 
        tags: List[str] = None, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for notes.
        
        Args:
            query (str, optional): Search query
            tags (List[str], optional): List of tags to filter by
            limit (int): Maximum number of results
            offset (int): Offset for pagination
            
        Returns:
            List[Dict[str, Any]]: List of matching notes
        """
        try:
            # Build query
            sql = "SELECT id, title, summary, timestamp, source_type FROM notes"
            params = []
            
            # Add WHERE clause if needed
            where_clauses = []
            
            if query:
                where_clauses.append("(title LIKE ? OR text LIKE ? OR summary LIKE ?)")
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            if tags:
                placeholders = ", ".join(["?"] * len(tags))
                where_clauses.append(f"""
                id IN (
                    SELECT note_id FROM note_tags 
                    JOIN tags ON note_tags.tag_id = tags.id 
                    WHERE tags.name IN ({placeholders})
                    GROUP BY note_id
                    HAVING COUNT(DISTINCT tags.name) = ?
                )
                """)
                params.extend(tags)
                params.append(len(tags))  # Ensure all tags are matched
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY, LIMIT, and OFFSET
            sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Execute query
            self.cursor.execute(sql, params)
            
            # Fetch results
            results = []
            for row in self.cursor.fetchall():
                note = dict(row)
                note["tags"] = self.get_note_tags(note["id"])
                results.append(note)
            
            return results
            
        except sqlite3.Error as e:
            logger.error(f"Error searching notes: {e}")
            return []
    
    # Helper methods for tags
    
    def add_tags_to_note(self, note_id: int, tags: List[str]) -> None:
        """
        Add tags to a note.
        
        Args:
            note_id (int): ID of the note
            tags (List[str]): List of tag names
        """
        for tag in tags:
            # Get or create tag
            self.cursor.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                (tag,)
            )
            
            self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
            tag_id = self.cursor.fetchone()["id"]
            
            # Link tag to note
            self.cursor.execute(
                "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
                (note_id, tag_id)
            )
    
    def get_note_tags(self, note_id: int) -> List[str]:
        """
        Get tags for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            List[str]: List of tag names
        """
        self.cursor.execute("""
        SELECT tags.name FROM tags
        JOIN note_tags ON tags.id = note_tags.tag_id
        WHERE note_tags.note_id = ?
        """, (note_id,))
        
        return [row["name"] for row in self.cursor.fetchall()]
    
    # Helper methods for key points
    
    def add_keypoints_to_note(self, note_id: int, keypoints: List[Any]) -> None:
        """
        Add key points to a note.
        
        Args:
            note_id (int): ID of the note
            keypoints (List[Any]): List of key points
        """
        for i, point in enumerate(keypoints):
            if isinstance(point, dict) and "content" in point:
                content = point["content"]
            else:
                content = str(point)
                
            self.cursor.execute(
                "INSERT INTO keypoints (note_id, content, order_index) VALUES (?, ?, ?)",
                (note_id, content, i)
            )
    
    def get_note_keypoints(self, note_id: int) -> List[Dict[str, Any]]:
        """
        Get key points for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            List[Dict[str, Any]]: List of key points
        """
        self.cursor.execute("""
        SELECT id, content, order_index FROM keypoints
        WHERE note_id = ?
        ORDER BY order_index
        """, (note_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Helper methods for glossary
    
    def add_glossary_to_note(self, note_id: int, glossary: Dict[str, str]) -> None:
        """
        Add glossary terms to a note.
        
        Args:
            note_id (int): ID of the note
            glossary (Dict[str, str]): Dictionary of terms and definitions
        """
        for term, definition in glossary.items():
            self.cursor.execute(
                "INSERT INTO glossary (note_id, term, definition) VALUES (?, ?, ?)",
                (note_id, term, definition)
            )
    
    def get_note_glossary(self, note_id: int) -> Dict[str, str]:
        """
        Get glossary terms for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            Dict[str, str]: Dictionary of terms and definitions
        """
        self.cursor.execute("""
        SELECT term, definition FROM glossary
        WHERE note_id = ?
        """, (note_id,))
        
        return {row["term"]: row["definition"] for row in self.cursor.fetchall()}
    
    # Helper methods for questions
    
    def add_questions_to_note(self, note_id: int, questions: List[Dict[str, Any]]) -> None:
        """
        Add questions to a note.
        
        Args:
            note_id (int): ID of the note
            questions (List[Dict[str, Any]]): List of questions
        """
        for question in questions:
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
                q_type = question.get("type", "basic")
                difficulty = question.get("difficulty", "medium")
                
                self.cursor.execute(
                    """
                    INSERT INTO questions 
                    (note_id, question, answer, type, difficulty) 
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (note_id, q_text, answer, q_type, difficulty)
                )
    
    def get_note_questions(self, note_id: int) -> List[Dict[str, Any]]:
        """
        Get questions for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            List[Dict[str, Any]]: List of questions
        """
        self.cursor.execute("""
        SELECT id, question, answer, type, difficulty, 
               last_reviewed, review_count, next_review 
        FROM questions
        WHERE note_id = ?
        """, (note_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Methods for related notes
    
    def add_related_notes(self, note_id: int, related_notes: List[Tuple[int, float]]) -> None:
        """
        Add related notes.
        
        Args:
            note_id (int): ID of the note
            related_notes (List[Tuple[int, float]]): List of (related_note_id, similarity) tuples
        """
        for related_id, similarity in related_notes:
            self.cursor.execute(
                """
                INSERT OR REPLACE INTO related_notes 
                (note_id, related_note_id, similarity) 
                VALUES (?, ?, ?)
                """,
                (note_id, related_id, similarity)
            )
    
    def get_related_notes(self, note_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get related notes.
        
        Args:
            note_id (int): ID of the note
            limit (int): Maximum number of related notes to return
            
        Returns:
            List[Dict[str, Any]]: List of related notes
        """
        self.cursor.execute("""
        SELECT n.id, n.title, r.similarity
        FROM notes n
        JOIN related_notes r ON n.id = r.related_note_id
        WHERE r.note_id = ?
        ORDER BY r.similarity DESC
        LIMIT ?
        """, (note_id, limit))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # Methods for spaced repetition
    
    def schedule_review(self, note_id: int, quality: int) -> bool:
        """
        Schedule a review for a note using the SM-2 algorithm.
        
        Args:
            note_id (int): ID of the note
            quality (int): Quality of recall (0-5)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current review data
            self.cursor.execute("""
            SELECT review_count, next_review FROM notes
            WHERE id = ?
            """, (note_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return False
                
            review_count = row["review_count"] or 0
            
            # Calculate next review date using SM-2 algorithm
            now = datetime.now()
            
            # SM-2 algorithm parameters
            if quality < 3:
                # If quality is less than 3, reset review count
                interval = 1  # Review again in 1 day
                review_count = 0
            else:
                # Calculate new interval
                if review_count == 0:
                    interval = 1
                elif review_count == 1:
                    interval = 6
                else:
                    # Get previous interval
                    if row["next_review"]:
                        try:
                            prev_date = datetime.fromisoformat(row["next_review"])
                            prev_interval = (prev_date - now).days
                            interval = int(prev_interval * (0.5 + (quality - 3) * 0.1))
                        except (ValueError, TypeError):
                            interval = 6 * review_count
                    else:
                        interval = 6 * review_count
                
                # Ensure minimum interval
                interval = max(1, interval)
                
                # Increment review count
                review_count += 1
            
            # Calculate next review date
            next_review = (now + Path(f"{interval}d")).isoformat()
            
            # Update note
            self.cursor.execute("""
            UPDATE notes
            SET last_reviewed = ?, review_count = ?, next_review = ?
            WHERE id = ?
            """, (now.isoformat(), review_count, next_review, note_id))
            
            self.conn.commit()
            logger.info(f"Scheduled review for note {note_id} in {interval} days")
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error scheduling review: {e}")
            return False
    
    def get_due_reviews(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get notes due for review.
        
        Args:
            limit (int): Maximum number of notes to return
            
        Returns:
            List[Dict[str, Any]]: List of notes due for review
        """
        now = datetime.now().isoformat()
        
        self.cursor.execute("""
        SELECT id, title, last_reviewed, review_count, next_review
        FROM notes
        WHERE next_review IS NOT NULL AND next_review <= ?
        ORDER BY next_review
        LIMIT ?
        """, (now, limit))
        
        return [dict(row) for row in self.cursor.fetchall()]

def init_db(db_path: str) -> None:
    """
    Initialize the database with the required tables.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    logger.info(f"Initializing database at {db_path}")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create notes table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                summary TEXT,
                timestamp TEXT NOT NULL,
                source_type TEXT NOT NULL,
                word_count INTEGER,
                char_count INTEGER,
                path TEXT,
                last_reviewed TEXT,
                review_count INTEGER DEFAULT 0,
                next_review TEXT
            )
            ''')
            
            # Create tags table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Create note_tags table (many-to-many relationship)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_tags (
                note_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (note_id, tag_id),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
            ''')
            
            # Create keypoints table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS keypoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                content TEXT NOT NULL,
                order_index INTEGER,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Create glossary table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS glossary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                term TEXT NOT NULL,
                definition TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Create questions table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                type TEXT NOT NULL,
                difficulty TEXT,
                last_reviewed TEXT,
                review_count INTEGER DEFAULT 0,
                next_review TEXT,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Create related_notes table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS related_notes (
                note_id INTEGER,
                related_note_id INTEGER,
                similarity REAL,
                PRIMARY KEY (note_id, related_note_id),
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                FOREIGN KEY (related_note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        raise