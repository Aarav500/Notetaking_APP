"""
Embedder module for AI Note System.
Handles generating, storing, and retrieving embeddings for notes.
"""

import os
import logging
import json
import sqlite3
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Import embedding interfaces
from ..api.embedding_interface import (
    EmbeddingInterface,
    OpenAIEmbeddingInterface,
    SentenceTransformersInterface,
    HuggingFaceEmbeddingInterface
)

# Setup logging
logger = logging.getLogger("ai_note_system.embeddings.embedder")

class Embedder:
    """
    Embedder class for AI Note System.
    Handles generating, storing, and retrieving embeddings for notes.
    """
    
    def __init__(self, db_path: str, model_name: str = "all-MiniLM-L6-v2", cache_embeddings: bool = True):
        """
        Initialize the Embedder.
        
        Args:
            db_path (str): Path to the SQLite database file
            model_name (str): Name of the embedding model to use
            cache_embeddings (bool): Whether to cache embeddings in memory
        """
        self.db_path = db_path
        self.model_name = model_name
        self.cache_embeddings = cache_embeddings
        self.embedding_cache = {}
        
        # Initialize embedding model
        self.embedding_model = self._initialize_embedding_model(model_name)
        
        # Ensure database has the necessary tables
        self._ensure_embedding_tables()
    
    def _initialize_embedding_model(self, model_name: str) -> EmbeddingInterface:
        """
        Initialize the embedding model.
        
        Args:
            model_name (str): Name of the embedding model to use
            
        Returns:
            EmbeddingInterface: Initialized embedding model
        """
        logger.info(f"Initializing embedding model: {model_name}")
        
        try:
            # Try to use SentenceTransformers
            return SentenceTransformersInterface(model_name=model_name)
        except ImportError:
            logger.warning("SentenceTransformers not available, falling back to OpenAI")
            try:
                # Fall back to OpenAI
                return OpenAIEmbeddingInterface()
            except ImportError:
                logger.warning("OpenAI not available, falling back to Hugging Face")
                try:
                    # Fall back to Hugging Face
                    return HuggingFaceEmbeddingInterface()
                except ImportError:
                    logger.error("No embedding model available")
                    raise ImportError("No embedding model available")
    
    def _ensure_embedding_tables(self) -> None:
        """
        Ensure that the database has the necessary tables for storing embeddings.
        """
        logger.info("Ensuring embedding tables exist")
        
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create note_embeddings table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                model_name TEXT NOT NULL,
                embedding BLOB NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
                UNIQUE (note_id, model_name)
            )
            ''')
            
            # Create embedding_models table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS embedding_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                dimensions INTEGER NOT NULL,
                description TEXT
            )
            ''')
            
            # Commit changes
            conn.commit()
            
            logger.info("Embedding tables created successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Error creating embedding tables: {e}")
            raise
            
        finally:
            # Close connection
            if conn:
                conn.close()
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text (str): Text to generate embedding for
            
        Returns:
            List[float]: Embedding vector
        """
        logger.debug(f"Generating embedding for text (length: {len(text)})")
        
        try:
            # Generate embedding
            embedding = self.embedding_model.get_embeddings(text)
            
            logger.debug(f"Embedding generated: {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def store_note_embedding(self, note_id: int, text: str) -> bool:
        """
        Generate and store an embedding for a note.
        
        Args:
            note_id (int): ID of the note
            text (str): Text to generate embedding for
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Storing embedding for note {note_id}")
        
        try:
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Store embedding model info if not already stored
            cursor.execute(
                "INSERT OR IGNORE INTO embedding_models (name, dimensions, description) VALUES (?, ?, ?)",
                (self.model_name, len(embedding), f"Embedding model: {self.model_name}")
            )
            
            # Convert embedding to binary
            embedding_binary = self._embedding_to_binary(embedding)
            
            # Store embedding
            cursor.execute('''
            INSERT OR REPLACE INTO note_embeddings 
            (note_id, model_name, embedding, created_at) 
            VALUES (?, ?, ?, ?)
            ''', (note_id, self.model_name, embedding_binary, datetime.now().isoformat()))
            
            # Commit changes
            conn.commit()
            
            # Update cache if enabled
            if self.cache_embeddings:
                self.embedding_cache[(note_id, self.model_name)] = embedding
            
            logger.info(f"Embedding stored for note {note_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            return False
            
        finally:
            # Close connection
            if conn:
                conn.close()
    
    def get_note_embedding(self, note_id: int, model_name: Optional[str] = None) -> Optional[List[float]]:
        """
        Get the embedding for a note.
        
        Args:
            note_id (int): ID of the note
            model_name (str, optional): Name of the embedding model
            
        Returns:
            Optional[List[float]]: Embedding vector or None if not found
        """
        model_name = model_name or self.model_name
        
        # Check cache first if enabled
        if self.cache_embeddings and (note_id, model_name) in self.embedding_cache:
            return self.embedding_cache[(note_id, model_name)]
        
        logger.debug(f"Getting embedding for note {note_id} with model {model_name}")
        
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get embedding
            cursor.execute(
                "SELECT embedding FROM note_embeddings WHERE note_id = ? AND model_name = ?",
                (note_id, model_name)
            )
            
            result = cursor.fetchone()
            
            if result:
                # Convert binary to embedding
                embedding = self._binary_to_embedding(result[0])
                
                # Update cache if enabled
                if self.cache_embeddings:
                    self.embedding_cache[(note_id, model_name)] = embedding
                
                return embedding
            else:
                logger.debug(f"No embedding found for note {note_id} with model {model_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None
            
        finally:
            # Close connection
            if conn:
                conn.close()
    
    def search_notes_by_embedding(
        self, 
        query_text: str, 
        limit: int = 10, 
        threshold: float = 0.7,
        filter_tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for notes by semantic similarity using embeddings.
        
        Args:
            query_text (str): Query text to search for
            limit (int): Maximum number of results to return
            threshold (float): Minimum similarity threshold (0-1)
            filter_tags (List[str], optional): List of tags to filter by
            
        Returns:
            List[Dict[str, Any]]: List of matching notes with similarity scores
        """
        logger.info(f"Searching notes by embedding: {query_text}")
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query_text)
            
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all note embeddings
            if filter_tags:
                placeholders = ", ".join(["?"] * len(filter_tags))
                cursor.execute(f'''
                SELECT ne.note_id, ne.embedding, n.title, n.summary, n.timestamp, n.source_type
                FROM note_embeddings ne
                JOIN notes n ON ne.note_id = n.id
                WHERE ne.model_name = ? AND n.id IN (
                    SELECT note_id FROM note_tags 
                    JOIN tags ON note_tags.tag_id = tags.id 
                    WHERE tags.name IN ({placeholders})
                    GROUP BY note_id
                    HAVING COUNT(DISTINCT tags.name) = ?
                )
                ''', [self.model_name] + filter_tags + [len(filter_tags)])
            else:
                cursor.execute('''
                SELECT ne.note_id, ne.embedding, n.title, n.summary, n.timestamp, n.source_type
                FROM note_embeddings ne
                JOIN notes n ON ne.note_id = n.id
                WHERE ne.model_name = ?
                ''', (self.model_name,))
            
            # Calculate similarities
            results = []
            for row in cursor.fetchall():
                note_id = row["note_id"]
                embedding_binary = row["embedding"]
                embedding = self._binary_to_embedding(embedding_binary)
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, embedding)
                
                # Add to results if above threshold
                if similarity >= threshold:
                    # Get tags for the note
                    cursor.execute('''
                    SELECT tags.name FROM tags
                    JOIN note_tags ON tags.id = note_tags.tag_id
                    WHERE note_tags.note_id = ?
                    ''', (note_id,))
                    
                    tags = [tag["name"] for tag in cursor.fetchall()]
                    
                    # Add to results
                    results.append({
                        "id": note_id,
                        "title": row["title"],
                        "summary": row["summary"],
                        "timestamp": row["timestamp"],
                        "source_type": row["source_type"],
                        "tags": tags,
                        "similarity": similarity
                    })
            
            # Sort by similarity (descending)
            results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Limit results
            results = results[:limit]
            
            logger.info(f"Found {len(results)} matching notes")
            return results
            
        except Exception as e:
            logger.error(f"Error searching notes by embedding: {e}")
            return []
            
        finally:
            # Close connection
            if conn:
                conn.close()
    
    def update_embeddings_for_all_notes(self) -> Tuple[int, int]:
        """
        Update embeddings for all notes in the database.
        
        Returns:
            Tuple[int, int]: (number of successful updates, number of failed updates)
        """
        logger.info("Updating embeddings for all notes")
        
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all notes
            cursor.execute("SELECT id, text FROM notes")
            notes = cursor.fetchall()
            
            success_count = 0
            fail_count = 0
            
            # Update embeddings for each note
            for note_id, text in notes:
                try:
                    if self.store_note_embedding(note_id, text):
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    logger.error(f"Error updating embedding for note {note_id}: {e}")
                    fail_count += 1
            
            logger.info(f"Updated embeddings for {success_count} notes, {fail_count} failed")
            return (success_count, fail_count)
            
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            return (0, 0)
            
        finally:
            # Close connection
            if conn:
                conn.close()
    
    def _embedding_to_binary(self, embedding: List[float]) -> bytes:
        """
        Convert an embedding to binary for storage.
        
        Args:
            embedding (List[float]): Embedding vector
            
        Returns:
            bytes: Binary representation of the embedding
        """
        return np.array(embedding, dtype=np.float32).tobytes()
    
    def _binary_to_embedding(self, binary: bytes) -> List[float]:
        """
        Convert binary data to an embedding.
        
        Args:
            binary (bytes): Binary representation of the embedding
            
        Returns:
            List[float]: Embedding vector
        """
        return np.frombuffer(binary, dtype=np.float32).tolist()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1 (List[float]): First vector
            vec2 (List[float]): Second vector
            
        Returns:
            float: Cosine similarity (0-1)
        """
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        # Avoid division by zero
        if norm_a == 0 or norm_b == 0:
            return 0
        
        similarity = dot_product / (norm_a * norm_b)
        
        # Ensure result is between 0 and 1
        return max(0, min(1, similarity))