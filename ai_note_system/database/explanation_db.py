"""
Explanation database module for AI Note System.
Extends the database manager with tables and methods for storing and retrieving explanations.
"""

import os
import sqlite3
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# Setup logging
logger = logging.getLogger("ai_note_system.database.explanation_db")

# Import database manager
from .db_manager import DatabaseManager

def init_explanation_tables(db_path: str) -> None:
    """
    Initialize the explanation tables in the database.
    
    Args:
        db_path (str): Path to the SQLite database file
    """
    logger.info(f"Initializing explanation tables in database at {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create explanations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS explanations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                concept TEXT NOT NULL,
                explanation_text TEXT NOT NULL,
                audio_path TEXT,
                timestamp TEXT NOT NULL,
                analysis TEXT,
                clarity_score REAL,
                understanding_score REAL
            )
            ''')
            
            conn.commit()
            logger.info("Explanation tables initialized successfully")
            
    except sqlite3.Error as e:
        logger.error(f"Error initializing explanation tables: {e}")
        raise

class ExplanationDatabaseManager(DatabaseManager):
    """
    Database manager for explanations.
    Extends the DatabaseManager with methods for storing and retrieving explanations.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the ExplanationDatabaseManager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        super().__init__(db_path)
        
        # Initialize explanation tables if they don't exist
        init_explanation_tables(db_path)
    
    def add_explanation(
        self,
        user_id: str,
        topic: str,
        concept: str,
        explanation_text: str,
        audio_path: Optional[str] = None,
        analysis: Optional[str] = None,
        clarity_score: float = 0.0,
        understanding_score: float = 0.0
    ) -> int:
        """
        Add an explanation to the database.
        
        Args:
            user_id (str): ID of the user
            topic (str): Topic of the explanation
            concept (str): Concept being explained
            explanation_text (str): Transcribed explanation text
            audio_path (str, optional): Path to the audio file
            analysis (str, optional): JSON string of the analysis
            clarity_score (float): Clarity score (0-10)
            understanding_score (float): Understanding score (0-10)
            
        Returns:
            int: ID of the added explanation
        """
        try:
            timestamp = datetime.now().isoformat()
            
            self.cursor.execute('''
            INSERT INTO explanations (
                user_id, topic, concept, explanation_text, audio_path,
                timestamp, analysis, clarity_score, understanding_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, topic, concept, explanation_text, audio_path,
                timestamp, analysis, clarity_score, understanding_score
            ))
            
            explanation_id = self.cursor.lastrowid
            self.conn.commit()
            
            logger.info(f"Added explanation with ID {explanation_id} for user {user_id}")
            return explanation_id
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error adding explanation: {e}")
            raise
    
    def get_explanation(self, explanation_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an explanation by ID.
        
        Args:
            explanation_id (int): ID of the explanation
            
        Returns:
            Optional[Dict[str, Any]]: Explanation data or None if not found
        """
        try:
            self.cursor.execute('''
            SELECT * FROM explanations WHERE id = ?
            ''', (explanation_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return None
            
            explanation = dict(row)
            
            # Parse analysis JSON if present
            if explanation.get("analysis"):
                try:
                    explanation["analysis"] = json.loads(explanation["analysis"])
                except json.JSONDecodeError:
                    pass
            
            return explanation
            
        except sqlite3.Error as e:
            logger.error(f"Error getting explanation: {e}")
            return None
    
    def get_explanations(
        self,
        user_id: str,
        limit: int = 10,
        topic: Optional[str] = None,
        concept: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get explanations for a user.
        
        Args:
            user_id (str): ID of the user
            limit (int): Maximum number of explanations to return
            topic (str, optional): Filter by topic
            concept (str, optional): Filter by concept
            
        Returns:
            List[Dict[str, Any]]: List of explanations
        """
        try:
            query = "SELECT * FROM explanations WHERE user_id = ?"
            params = [user_id]
            
            if topic:
                query += " AND topic = ?"
                params.append(topic)
            
            if concept:
                query += " AND concept = ?"
                params.append(concept)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            self.cursor.execute(query, params)
            
            explanations = []
            for row in self.cursor.fetchall():
                explanation = dict(row)
                
                # Parse analysis JSON if present
                if explanation.get("analysis"):
                    try:
                        explanation["analysis"] = json.loads(explanation["analysis"])
                    except json.JSONDecodeError:
                        pass
                
                explanations.append(explanation)
            
            return explanations
            
        except sqlite3.Error as e:
            logger.error(f"Error getting explanations: {e}")
            return []
    
    def get_clarity_scores(
        self,
        user_id: str,
        topic: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get clarity scores for a user over a period of time.
        
        Args:
            user_id (str): ID of the user
            topic (str, optional): Filter by topic
            days (int): Number of days to look back
            
        Returns:
            List[Dict[str, Any]]: List of clarity scores with timestamps
        """
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            query = '''
            SELECT id, topic, concept, timestamp, clarity_score
            FROM explanations
            WHERE user_id = ? AND timestamp >= ?
            '''
            params = [user_id, cutoff_date]
            
            if topic:
                query += " AND topic = ?"
                params.append(topic)
            
            query += " ORDER BY timestamp"
            
            self.cursor.execute(query, params)
            
            return [dict(row) for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Error getting clarity scores: {e}")
            return []

def get_db_manager(db_path: Optional[str] = None) -> ExplanationDatabaseManager:
    """
    Get a database manager instance.
    
    Args:
        db_path (str, optional): Path to the SQLite database file
        
    Returns:
        ExplanationDatabaseManager: Database manager instance
    """
    if db_path is None:
        # Use default database path
        db_path = os.path.join("data", "pansophy.db")
    
    return ExplanationDatabaseManager(db_path)