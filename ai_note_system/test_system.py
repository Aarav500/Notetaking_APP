"""
Simplified test script for AI Note System.
This script tests the database functionality by directly interacting with the SQLite database.
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ai_note_system.test")

def test_database():
    """Test database functionality."""
    logger.info("Testing database functionality")
    
    # Define database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pansophy.db")
    logger.info(f"Using database at: {db_path}")
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify database structure
        logger.info("Verifying database structure")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        expected_tables = ['notes', 'tags', 'note_tags', 'keypoints', 'glossary', 'questions', 'related_notes']
        for table in expected_tables:
            if table in table_names:
                logger.info(f"Table '{table}' exists")
            else:
                logger.warning(f"Table '{table}' does not exist")
        
        # Insert a test note
        logger.info("Inserting test note")
        current_time = datetime.now().isoformat()
        cursor.execute("""
        INSERT INTO notes (title, text, summary, source_type, word_count, char_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Test Note",
            "This is a test note to verify database functionality.",
            "Test note summary.",
            "text",
            10,
            50,
            current_time,
            current_time
        ))
        
        # Get the ID of the inserted note
        note_id = cursor.lastrowid
        logger.info(f"Inserted test note with ID: {note_id}")
        
        # Insert a test tag
        logger.info("Inserting test tag")
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", ("test",))
        cursor.execute("SELECT id FROM tags WHERE name = ?", ("test",))
        tag_id = cursor.fetchone()[0]
        
        # Link the note to the tag
        logger.info("Linking note to tag")
        cursor.execute("INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)", (note_id, tag_id))
        
        # Insert a test keypoint
        logger.info("Inserting test keypoint")
        cursor.execute("""
        INSERT INTO keypoints (note_id, content, order_index)
        VALUES (?, ?, ?)
        """, (note_id, "This is a test keypoint", 1))
        
        # Commit the changes
        conn.commit()
        
        # Verify the inserted data
        logger.info("Verifying inserted data")
        cursor.execute("SELECT title, text FROM notes WHERE id = ?", (note_id,))
        note = cursor.fetchone()
        logger.info(f"Retrieved note: {note[0]}")
        
        # Clean up (optional)
        logger.info("Cleaning up test data")
        cursor.execute("DELETE FROM keypoints WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        
        # Close the connection
        conn.close()
        
        logger.info("Database test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        success = test_database()
        if not success:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)