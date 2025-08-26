"""
Community Knowledge Sharing Layer

This module provides functionality for sharing insights, flashcards, and mind maps with others,
upvoting high-quality resources, and building collective learning packs.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import uuid
import re

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class SharingPermission:
    """Permission levels for shared content"""
    PUBLIC = "public"  # Anyone can view
    REGISTERED = "registered"  # Only registered users can view
    PRIVATE = "private"  # Only specified users can view

class ContentType:
    """Types of content that can be shared"""
    NOTE = "note"
    FLASHCARD = "flashcard"
    MINDMAP = "mindmap"
    WHITEBOARD = "whiteboard"
    ESSAY = "essay"
    LEARNING_PACK = "learning_pack"

class CommunitySharing:
    """
    Community Knowledge Sharing Layer
    
    Features:
    - Share anonymized insights, flashcards, and mind maps
    - Upvote high-quality resources and summaries
    - Build collective learning packs
    - Discover relevant content from other users
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None):
        """Initialize the community sharing system"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create shared content table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_content (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            original_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT,
            anonymized BOOLEAN NOT NULL DEFAULT 1,
            permission TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            views INTEGER NOT NULL DEFAULT 0,
            upvotes INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create shared content tags table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_content_tags (
            id INTEGER PRIMARY KEY,
            content_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            FOREIGN KEY (content_id) REFERENCES shared_content(id)
        )
        ''')
        
        # Create shared content access table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_content_access (
            id INTEGER PRIMARY KEY,
            content_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (content_id) REFERENCES shared_content(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create learning packs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_packs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            topic TEXT NOT NULL,
            difficulty TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            views INTEGER NOT NULL DEFAULT 0,
            upvotes INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create learning pack items table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_pack_items (
            id INTEGER PRIMARY KEY,
            pack_id INTEGER NOT NULL,
            content_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (pack_id) REFERENCES learning_packs(id),
            FOREIGN KEY (content_id) REFERENCES shared_content(id)
        )
        ''')
        
        # Create upvotes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS upvotes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content_id INTEGER,
            pack_id INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (content_id) REFERENCES shared_content(id),
            FOREIGN KEY (pack_id) REFERENCES learning_packs(id)
        )
        ''')
        
        conn.commit()
    
    def share_content(self, user_id: int, content_type: str, 
                    original_id: Optional[int], title: str,
                    description: Optional[str] = None,
                    content: Optional[str] = None,
                    anonymized: bool = True,
                    permission: str = SharingPermission.PUBLIC,
                    tags: List[str] = None) -> int:
        """
        Share content with the community
        
        Args:
            user_id: The ID of the user sharing the content
            content_type: The type of content being shared
            original_id: The ID of the original content in its source table
            title: The title of the shared content
            description: Optional description of the shared content
            content: Optional content text (for anonymized content)
            anonymized: Whether to anonymize the content
            permission: The permission level for the shared content
            tags: Optional list of tags for the shared content
            
        Returns:
            The ID of the shared content
        """
        logger.info(f"Sharing {content_type} content: {title}")
        
        # If content is to be anonymized, we need to process it
        if anonymized and content:
            content = self._anonymize_content(content)
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO shared_content (
            user_id, content_type, original_id, title, description, content,
            anonymized, permission, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, content_type, original_id, title, description, content,
            1 if anonymized else 0, permission, now, now
        ))
        
        content_id = cursor.lastrowid
        
        # Add tags if provided
        if tags:
            for tag in tags:
                cursor.execute('''
                INSERT INTO shared_content_tags (content_id, tag)
                VALUES (?, ?)
                ''', (content_id, tag))
        
        conn.commit()
        
        return content_id
    
    def get_shared_content(self, content_id: int) -> Dict[str, Any]:
        """
        Get shared content by ID
        
        Args:
            content_id: The ID of the shared content
            
        Returns:
            Dictionary with shared content details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, content_type, original_id, title, description, content,
               anonymized, permission, created_at, updated_at, views, upvotes
        FROM shared_content
        WHERE id = ?
        ''', (content_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        shared_content = {
            'id': row[0],
            'user_id': row[1],
            'content_type': row[2],
            'original_id': row[3],
            'title': row[4],
            'description': row[5],
            'content': row[6],
            'anonymized': bool(row[7]),
            'permission': row[8],
            'created_at': row[9],
            'updated_at': row[10],
            'views': row[11],
            'upvotes': row[12],
            'tags': []
        }
        
        # Get tags for the shared content
        cursor.execute('''
        SELECT tag FROM shared_content_tags
        WHERE content_id = ?
        ''', (content_id,))
        
        shared_content['tags'] = [row[0] for row in cursor.fetchall()]
        
        # Increment view count
        cursor.execute('''
        UPDATE shared_content
        SET views = views + 1
        WHERE id = ?
        ''', (content_id,))
        
        conn.commit()
        
        return shared_content
    
    def search_shared_content(self, query: str, content_type: Optional[str] = None,
                            tags: List[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for shared content
        
        Args:
            query: The search query
            content_type: Optional content type filter
            tags: Optional list of tags to filter by
            limit: Maximum number of results to return
            
        Returns:
            List of shared content summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Build the query
        sql_query = '''
        SELECT sc.id, sc.user_id, sc.content_type, sc.title, sc.description,
               sc.created_at, sc.views, sc.upvotes
        FROM shared_content sc
        '''
        
        params = []
        where_clauses = ["sc.permission = 'public'"]  # Only include public content by default
        
        # Add content type filter
        if content_type:
            where_clauses.append("sc.content_type = ?")
            params.append(content_type)
        
        # Add search query filter
        if query:
            where_clauses.append("(sc.title LIKE ? OR sc.description LIKE ? OR sc.content LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])
        
        # Add tags filter
        if tags:
            sql_query += '''
            JOIN shared_content_tags sct ON sc.id = sct.content_id
            '''
            placeholders = ', '.join(['?'] * len(tags))
            where_clauses.append(f"sct.tag IN ({placeholders})")
            params.extend(tags)
        
        # Combine where clauses
        if where_clauses:
            sql_query += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add order by and limit
        sql_query += '''
        GROUP BY sc.id
        ORDER BY sc.upvotes DESC, sc.views DESC
        LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(sql_query, params)
        
        results = []
        for row in cursor.fetchall():
            result = {
                'id': row[0],
                'user_id': row[1],
                'content_type': row[2],
                'title': row[3],
                'description': row[4],
                'created_at': row[5],
                'views': row[6],
                'upvotes': row[7]
            }
            results.append(result)
        
        return results
    
    def upvote_content(self, user_id: int, content_id: int) -> bool:
        """
        Upvote shared content
        
        Args:
            user_id: The ID of the user upvoting
            content_id: The ID of the shared content
            
        Returns:
            True if the upvote was successful, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check if the user has already upvoted this content
        cursor.execute('''
        SELECT id FROM upvotes
        WHERE user_id = ? AND content_id = ?
        ''', (user_id, content_id))
        
        if cursor.fetchone():
            return False  # User has already upvoted
        
        # Add upvote
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO upvotes (user_id, content_id, created_at)
        VALUES (?, ?, ?)
        ''', (user_id, content_id, now))
        
        # Update upvote count
        cursor.execute('''
        UPDATE shared_content
        SET upvotes = upvotes + 1
        WHERE id = ?
        ''', (content_id,))
        
        conn.commit()
        
        return True
    
    def create_learning_pack(self, user_id: int, title: str, 
                           description: Optional[str], topic: str,
                           difficulty: Optional[str] = None,
                           content_ids: List[int] = None) -> int:
        """
        Create a learning pack
        
        Args:
            user_id: The ID of the user creating the pack
            title: The title of the learning pack
            description: Optional description of the learning pack
            topic: The topic of the learning pack
            difficulty: Optional difficulty level of the learning pack
            content_ids: Optional list of content IDs to include in the pack
            
        Returns:
            The ID of the created learning pack
        """
        logger.info(f"Creating learning pack: {title}")
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO learning_packs (
            user_id, title, description, topic, difficulty, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, title, description, topic, difficulty, now, now))
        
        pack_id = cursor.lastrowid
        
        # Add content items if provided
        if content_ids:
            for position, content_id in enumerate(content_ids, 1):
                cursor.execute('''
                INSERT INTO learning_pack_items (pack_id, content_id, position)
                VALUES (?, ?, ?)
                ''', (pack_id, content_id, position))
        
        conn.commit()
        
        return pack_id
    
    def get_learning_pack(self, pack_id: int) -> Dict[str, Any]:
        """
        Get a learning pack by ID
        
        Args:
            pack_id: The ID of the learning pack
            
        Returns:
            Dictionary with learning pack details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, title, description, topic, difficulty,
               created_at, updated_at, views, upvotes
        FROM learning_packs
        WHERE id = ?
        ''', (pack_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        learning_pack = {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'description': row[3],
            'topic': row[4],
            'difficulty': row[5],
            'created_at': row[6],
            'updated_at': row[7],
            'views': row[8],
            'upvotes': row[9],
            'items': []
        }
        
        # Get items for the learning pack
        cursor.execute('''
        SELECT lpi.id, lpi.content_id, lpi.position, lpi.notes,
               sc.title, sc.content_type
        FROM learning_pack_items lpi
        JOIN shared_content sc ON lpi.content_id = sc.id
        WHERE lpi.pack_id = ?
        ORDER BY lpi.position
        ''', (pack_id,))
        
        for row in cursor.fetchall():
            item = {
                'id': row[0],
                'content_id': row[1],
                'position': row[2],
                'notes': row[3],
                'title': row[4],
                'content_type': row[5]
            }
            learning_pack['items'].append(item)
        
        # Increment view count
        cursor.execute('''
        UPDATE learning_packs
        SET views = views + 1
        WHERE id = ?
        ''', (pack_id,))
        
        conn.commit()
        
        return learning_pack
    
    def search_learning_packs(self, query: str, topic: Optional[str] = None,
                            difficulty: Optional[str] = None,
                            limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for learning packs
        
        Args:
            query: The search query
            topic: Optional topic filter
            difficulty: Optional difficulty filter
            limit: Maximum number of results to return
            
        Returns:
            List of learning pack summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Build the query
        sql_query = '''
        SELECT id, user_id, title, description, topic, difficulty,
               created_at, views, upvotes
        FROM learning_packs
        '''
        
        params = []
        where_clauses = []
        
        # Add topic filter
        if topic:
            where_clauses.append("topic = ?")
            params.append(topic)
        
        # Add difficulty filter
        if difficulty:
            where_clauses.append("difficulty = ?")
            params.append(difficulty)
        
        # Add search query filter
        if query:
            where_clauses.append("(title LIKE ? OR description LIKE ? OR topic LIKE ?)")
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])
        
        # Combine where clauses
        if where_clauses:
            sql_query += f" WHERE {' AND '.join(where_clauses)}"
        
        # Add order by and limit
        sql_query += '''
        ORDER BY upvotes DESC, views DESC
        LIMIT ?
        '''
        params.append(limit)
        
        cursor.execute(sql_query, params)
        
        results = []
        for row in cursor.fetchall():
            result = {
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'description': row[3],
                'topic': row[4],
                'difficulty': row[5],
                'created_at': row[6],
                'views': row[7],
                'upvotes': row[8]
            }
            results.append(result)
        
        return results
    
    def upvote_learning_pack(self, user_id: int, pack_id: int) -> bool:
        """
        Upvote a learning pack
        
        Args:
            user_id: The ID of the user upvoting
            pack_id: The ID of the learning pack
            
        Returns:
            True if the upvote was successful, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check if the user has already upvoted this pack
        cursor.execute('''
        SELECT id FROM upvotes
        WHERE user_id = ? AND pack_id = ?
        ''', (user_id, pack_id))
        
        if cursor.fetchone():
            return False  # User has already upvoted
        
        # Add upvote
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO upvotes (user_id, pack_id, created_at)
        VALUES (?, ?, ?)
        ''', (user_id, pack_id, now))
        
        # Update upvote count
        cursor.execute('''
        UPDATE learning_packs
        SET upvotes = upvotes + 1
        WHERE id = ?
        ''', (pack_id,))
        
        conn.commit()
        
        return True
    
    def add_item_to_learning_pack(self, pack_id: int, content_id: int, 
                                position: Optional[int] = None,
                                notes: Optional[str] = None) -> int:
        """
        Add an item to a learning pack
        
        Args:
            pack_id: The ID of the learning pack
            content_id: The ID of the shared content
            position: Optional position in the pack (if not provided, will be added at the end)
            notes: Optional notes about the item
            
        Returns:
            The ID of the created item
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # If position is not provided, add at the end
        if position is None:
            cursor.execute('''
            SELECT MAX(position) FROM learning_pack_items
            WHERE pack_id = ?
            ''', (pack_id,))
            
            max_position = cursor.fetchone()[0]
            position = (max_position or 0) + 1
        
        cursor.execute('''
        INSERT INTO learning_pack_items (pack_id, content_id, position, notes)
        VALUES (?, ?, ?, ?)
        ''', (pack_id, content_id, position, notes))
        
        item_id = cursor.lastrowid
        
        # Update the learning pack's updated_at timestamp
        now = datetime.now().isoformat()
        cursor.execute('''
        UPDATE learning_packs
        SET updated_at = ?
        WHERE id = ?
        ''', (now, pack_id))
        
        conn.commit()
        
        return item_id
    
    def remove_item_from_learning_pack(self, item_id: int) -> bool:
        """
        Remove an item from a learning pack
        
        Args:
            item_id: The ID of the item to remove
            
        Returns:
            True if the item was removed, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get the pack ID for the item
        cursor.execute('''
        SELECT pack_id FROM learning_pack_items
        WHERE id = ?
        ''', (item_id,))
        
        row = cursor.fetchone()
        if not row:
            return False
        
        pack_id = row[0]
        
        # Remove the item
        cursor.execute('''
        DELETE FROM learning_pack_items
        WHERE id = ?
        ''', (item_id,))
        
        # Update the learning pack's updated_at timestamp
        now = datetime.now().isoformat()
        cursor.execute('''
        UPDATE learning_packs
        SET updated_at = ?
        WHERE id = ?
        ''', (now, pack_id))
        
        conn.commit()
        
        return True
    
    def get_trending_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending shared content
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of trending content summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, content_type, title, description,
               created_at, views, upvotes
        FROM shared_content
        WHERE permission = 'public'
        ORDER BY (upvotes * 3 + views) DESC, created_at DESC
        LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            result = {
                'id': row[0],
                'user_id': row[1],
                'content_type': row[2],
                'title': row[3],
                'description': row[4],
                'created_at': row[5],
                'views': row[6],
                'upvotes': row[7]
            }
            results.append(result)
        
        return results
    
    def get_trending_learning_packs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending learning packs
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of trending learning pack summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, title, description, topic, difficulty,
               created_at, views, upvotes
        FROM learning_packs
        ORDER BY (upvotes * 3 + views) DESC, created_at DESC
        LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            result = {
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'description': row[3],
                'topic': row[4],
                'difficulty': row[5],
                'created_at': row[6],
                'views': row[7],
                'upvotes': row[8]
            }
            results.append(result)
        
        return results
    
    def get_recommended_content(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recommended content for a user based on their interests and activity
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of results to return
            
        Returns:
            List of recommended content summaries
        """
        # Get the user's interests (tags from their notes and upvoted content)
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get tags from user's notes
        cursor.execute('''
        SELECT DISTINCT t.name
        FROM notes n
        JOIN note_tags nt ON n.id = nt.note_id
        JOIN tags t ON nt.tag_id = t.id
        WHERE n.user_id = ?
        ''', (user_id,))
        
        user_tags = [row[0] for row in cursor.fetchall()]
        
        # Get tags from content the user has upvoted
        cursor.execute('''
        SELECT DISTINCT sct.tag
        FROM upvotes u
        JOIN shared_content sc ON u.content_id = sc.id
        JOIN shared_content_tags sct ON sc.id = sct.content_id
        WHERE u.user_id = ?
        ''', (user_id,))
        
        user_tags.extend([row[0] for row in cursor.fetchall()])
        
        # If no tags found, return trending content
        if not user_tags:
            return self.get_trending_content(limit)
        
        # Find content with matching tags
        placeholders = ', '.join(['?'] * len(user_tags))
        
        cursor.execute(f'''
        SELECT sc.id, sc.user_id, sc.content_type, sc.title, sc.description,
               sc.created_at, sc.views, sc.upvotes, COUNT(sct.tag) as tag_matches
        FROM shared_content sc
        JOIN shared_content_tags sct ON sc.id = sct.content_id
        WHERE sc.permission = 'public'
        AND sct.tag IN ({placeholders})
        AND sc.user_id != ?
        AND sc.id NOT IN (
            SELECT content_id FROM upvotes WHERE user_id = ? AND content_id IS NOT NULL
        )
        GROUP BY sc.id
        ORDER BY tag_matches DESC, sc.upvotes DESC
        LIMIT ?
        ''', user_tags + [user_id, user_id, limit])
        
        results = []
        for row in cursor.fetchall():
            result = {
                'id': row[0],
                'user_id': row[1],
                'content_type': row[2],
                'title': row[3],
                'description': row[4],
                'created_at': row[5],
                'views': row[6],
                'upvotes': row[7],
                'relevance': row[8]  # Number of matching tags
            }
            results.append(result)
        
        return results
    
    def _anonymize_content(self, content: str) -> str:
        """
        Anonymize content by removing personal information
        
        Args:
            content: The content to anonymize
            
        Returns:
            Anonymized content
        """
        # Replace email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
        
        # Replace phone numbers
        content = re.sub(r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE]', content)
        
        # Replace URLs
        content = re.sub(r'https?://\S+', '[URL]', content)
        
        # Replace names (this is a simplified approach and might not catch all names)
        # For a more robust solution, you would need to use NER (Named Entity Recognition)
        common_names = [
            'John', 'Jane', 'Michael', 'David', 'Sarah', 'Emily', 'James', 'Robert',
            'Jennifer', 'William', 'Elizabeth', 'Richard', 'Linda', 'Thomas', 'Patricia'
        ]
        
        for name in common_names:
            content = re.sub(r'\b' + name + r'\b', '[NAME]', content, flags=re.IGNORECASE)
        
        return content

# Helper functions for easier access to community sharing functionality

def share_content(db_manager, user_id: int, content_type: str, 
                original_id: Optional[int], title: str,
                description: Optional[str] = None,
                content: Optional[str] = None,
                anonymized: bool = True,
                tags: List[str] = None) -> int:
    """
    Share content with the community
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user sharing the content
        content_type: The type of content being shared
        original_id: The ID of the original content in its source table
        title: The title of the shared content
        description: Optional description of the shared content
        content: Optional content text (for anonymized content)
        anonymized: Whether to anonymize the content
        tags: Optional list of tags for the shared content
        
    Returns:
        The ID of the shared content
    """
    sharing = CommunitySharing(db_manager)
    return sharing.share_content(
        user_id, content_type, original_id, title, description,
        content, anonymized, SharingPermission.PUBLIC, tags
    )

def create_learning_pack(db_manager, user_id: int, title: str, 
                       topic: str, description: Optional[str] = None,
                       content_ids: List[int] = None) -> int:
    """
    Create a learning pack
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user creating the pack
        title: The title of the learning pack
        topic: The topic of the learning pack
        description: Optional description of the learning pack
        content_ids: Optional list of content IDs to include in the pack
        
    Returns:
        The ID of the created learning pack
    """
    sharing = CommunitySharing(db_manager)
    return sharing.create_learning_pack(user_id, title, description, topic, None, content_ids)

def get_trending_content(db_manager, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get trending shared content
    
    Args:
        db_manager: Database manager instance
        limit: Maximum number of results to return
        
    Returns:
        List of trending content summaries
    """
    sharing = CommunitySharing(db_manager)
    return sharing.get_trending_content(limit)

def get_recommended_content(db_manager, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recommended content for a user based on their interests and activity
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        limit: Maximum number of results to return
        
    Returns:
        List of recommended content summaries
    """
    sharing = CommunitySharing(db_manager)
    return sharing.get_recommended_content(user_id, limit)