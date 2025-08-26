"""
Script to initialize the SQLite database for AI Note System.
This script creates the basic tables needed for the note-taking system.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

def init_db(db_path):
    """
    Initialize the database with the necessary tables.
    
    Args:
        db_path (str): Path to the database file
    """
    # Connect to the database (creates it if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        text TEXT,
        summary TEXT,
        source_type TEXT,
        source_path TEXT,
        word_count INTEGER,
        char_count INTEGER,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_reviewed_at TEXT,
        review_count INTEGER DEFAULT 0,
        next_review_at TEXT,
        easiness_factor REAL DEFAULT 2.5
    )
    ''')
    
    # Create tags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
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
        definition TEXT,
        FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
    )
    ''')
    
    # Create questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        note_id INTEGER,
        question TEXT NOT NULL,
        answer TEXT,
        question_type TEXT,
        options TEXT,
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
    
    # Create note_embeddings table
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
    
    # Create embedding_models table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embedding_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        dimensions INTEGER NOT NULL,
        description TEXT
    )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

def main():
    """Initialize the database."""
    # Define database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "pansophy.db")
    
    # Initialize the database
    print(f"Initializing database at: {db_path}")
    init_db(db_path)
    print("Database initialization complete.")

if __name__ == "__main__":
    main()