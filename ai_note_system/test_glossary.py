"""
Unit tests for the Interactive Visual Glossary module.
"""

import os
import unittest
import tempfile
import json
import sqlite3
from datetime import datetime

from ai_note_system.visualization.interactive_glossary import InteractiveGlossary
from ai_note_system.database.db_manager import DatabaseManager

class MockEmbeddingInterface:
    """Mock embedding interface for testing."""
    
    def get_embedding(self, text):
        """Return a mock embedding."""
        return [0.1] * 10
    
    def calculate_similarity(self, embedding1, embedding2):
        """Return a mock similarity score."""
        return 0.85

class MockLLMInterface:
    """Mock LLM interface for testing."""
    
    def generate_text(self, prompt, **kwargs):
        """Return a mock generated text."""
        return "This is a mock generated text."
    
    def generate_structured_output(self, prompt, output_schema, **kwargs):
        """Return a mock structured output."""
        if "properties" in output_schema and "use_cases" in output_schema["properties"]:
            return {
                "use_cases": [
                    {
                        "title": "Mock Use Case",
                        "description": "This is a mock use case.",
                        "domain": "Testing",
                        "impact": "High",
                        "example": "Example of mock use case."
                    }
                ]
            }
        return {}

class TestInteractiveGlossary(unittest.TestCase):
    """Test cases for the InteractiveGlossary class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary database
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp()
        self.db_manager = DatabaseManager(self.temp_db_path)
        
        # Create a temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize glossary with mock interfaces
        self.glossary = InteractiveGlossary(
            db_manager=self.db_manager,
            output_dir=self.temp_dir
        )
        
        # Replace LLM and embedding interfaces with mocks
        self.glossary.llm = MockLLMInterface()
        self.glossary.embedder = MockEmbeddingInterface()
        
        # Initialize database tables
        self.glossary._init_database()
        
        # Create a test note in the database
        self.db_manager.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        self.db_manager.cursor.execute('''
        INSERT INTO notes (title, text, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ''', (
            "Test Note",
            "This is a test note containing the term artificial intelligence and machine learning.",
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        self.db_manager.conn.commit()
        self.test_note_id = self.db_manager.cursor.lastrowid
    
    def tearDown(self):
        """Clean up test environment."""
        self.db_manager.conn.close()
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
        # Clean up temporary output directory
        for filename in os.listdir(self.temp_dir):
            os.unlink(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)
    
    def test_add_term(self):
        """Test adding a term to the glossary."""
        # Add a term
        result = self.glossary.add_term(
            term="Artificial Intelligence",
            definition="The simulation of human intelligence in machines.",
            category="Computer Science",
            importance=5
        )
        
        # Check result
        self.assertIn("id", result)
        self.assertEqual(result["term"], "Artificial Intelligence")
        self.assertEqual(result["definition"], "The simulation of human intelligence in machines.")
        self.assertEqual(result["category"], "Computer Science")
        self.assertEqual(result["importance"], 5)
        
        # Check that term was added to database
        self.db_manager.cursor.execute('''
        SELECT * FROM glossary_terms WHERE term = ?
        ''', ("Artificial Intelligence",))
        
        row = self.db_manager.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["term"], "Artificial Intelligence")
    
    def test_update_term(self):
        """Test updating a term in the glossary."""
        # Add a term
        term = self.glossary.add_term(
            term="Machine Learning",
            definition="A subset of AI that enables systems to learn from data.",
            category="Computer Science",
            importance=4
        )
        
        # Update the term
        updated_term = self.glossary.update_term(
            term_id=term["id"],
            definition="A field of AI that enables systems to learn and improve from experience.",
            importance=5
        )
        
        # Check result
        self.assertEqual(updated_term["term"], "Machine Learning")
        self.assertEqual(
            updated_term["definition"], 
            "A field of AI that enables systems to learn and improve from experience."
        )
        self.assertEqual(updated_term["category"], "Computer Science")
        self.assertEqual(updated_term["importance"], 5)
    
    def test_get_term(self):
        """Test retrieving a term from the glossary."""
        # Add a term
        term = self.glossary.add_term(
            term="Deep Learning",
            definition="A subset of machine learning based on artificial neural networks.",
            category="Computer Science",
            importance=4
        )
        
        # Get the term
        retrieved_term = self.glossary.get_term("Deep Learning")
        
        # Check result
        self.assertEqual(retrieved_term["id"], term["id"])
        self.assertEqual(retrieved_term["term"], "Deep Learning")
        self.assertEqual(
            retrieved_term["definition"], 
            "A subset of machine learning based on artificial neural networks."
        )
    
    def test_search_terms(self):
        """Test searching for terms in the glossary."""
        # Add some terms
        self.glossary.add_term(
            term="Neural Network",
            definition="A computing system inspired by biological neural networks.",
            category="Computer Science",
            importance=4
        )
        
        self.glossary.add_term(
            term="Convolutional Neural Network",
            definition="A class of neural networks commonly used for image recognition.",
            category="Computer Science",
            importance=3
        )
        
        # Search for terms
        results = self.glossary.search_terms(query="neural")
        
        # Check results
        self.assertEqual(len(results), 2)
        self.assertTrue(any(r["term"] == "Neural Network" for r in results))
        self.assertTrue(any(r["term"] == "Convolutional Neural Network" for r in results))
        
        # Test semantic search
        results = self.glossary.search_terms(query="image processing", semantic_search=True)
        
        # With our mock embedder, all terms will have high similarity
        self.assertGreater(len(results), 0)
    
    def test_scan_note_for_terms(self):
        """Test scanning a note for glossary terms."""
        # Add terms that appear in the test note
        self.glossary.add_term(
            term="Artificial Intelligence",
            definition="The simulation of human intelligence in machines.",
            category="Computer Science",
            importance=5
        )
        
        self.glossary.add_term(
            term="Machine Learning",
            definition="A subset of AI that enables systems to learn from data.",
            category="Computer Science",
            importance=4
        )
        
        # Scan the note
        found_terms = self.glossary.scan_note_for_terms(note_id=self.test_note_id)
        
        # Check results
        self.assertEqual(len(found_terms), 2)
        self.assertTrue(any(t["term"] == "Artificial Intelligence" for t in found_terms))
        self.assertTrue(any(t["term"] == "Machine Learning" for t in found_terms))
        
        # Check that references were added
        self.db_manager.cursor.execute('''
        SELECT COUNT(*) as count FROM term_references
        ''')
        
        row = self.db_manager.cursor.fetchone()
        self.assertEqual(row["count"], 2)
    
    def test_generate_clickable_interface(self):
        """Test generating clickable interfaces for terms."""
        # Add some terms
        self.glossary.add_term(
            term="Reinforcement Learning",
            definition="A type of machine learning where an agent learns to make decisions by taking actions in an environment.",
            category="Computer Science",
            importance=4
        )
        
        self.glossary.add_term(
            term="Supervised Learning",
            definition="A type of machine learning where the model is trained on labeled data.",
            category="Computer Science",
            importance=3
        )
        
        # Get terms
        terms = []
        self.db_manager.cursor.execute("SELECT id FROM glossary_terms")
        for row in self.db_manager.cursor.fetchall():
            term = self.glossary.get_term_by_id(row["id"])
            if term:
                terms.append(term)
        
        # Generate HTML interface
        html = self.glossary.generate_clickable_interface(
            terms=terms,
            format_type="html"
        )
        
        # Check HTML
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Reinforcement Learning", html)
        self.assertIn("Supervised Learning", html)
        
        # Generate Markdown interface
        md = self.glossary.generate_clickable_interface(
            terms=terms,
            format_type="markdown"
        )
        
        # Check Markdown
        self.assertIn("# Interactive Glossary", md)
        self.assertIn("## Reinforcement Learning", md)
        self.assertIn("## Supervised Learning", md)
        
        # Generate text interface
        text = self.glossary.generate_clickable_interface(
            terms=terms,
            format_type="text"
        )
        
        # Check text
        self.assertIn("INTERACTIVE GLOSSARY", text)
        self.assertIn("REINFORCEMENT LEARNING", text)
        self.assertIn("SUPERVISED LEARNING", text)


if __name__ == "__main__":
    unittest.main()