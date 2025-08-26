"""
Test script for the new features in AI Note System.
Tests the PDF reading and retention features and the coding theory-practice bridge.
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from ai_note_system.reading.pdf_viewer import PDFViewer
from ai_note_system.reading.active_recall import ActiveRecallGenerator
from ai_note_system.reading.memory_mode import LongTermMemoryMode
from ai_note_system.learning.coding_bridge import CodingCompetencyMap

# Import database manager for testing
from ai_note_system.database.db_manager import DatabaseManager

class TestNewFeatures(unittest.TestCase):
    """Test case for the new features in AI Note System."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Use in-memory database for testing
        cls.db_manager = DatabaseManager(":memory:")
        
        # Initialize test objects
        cls.pdf_viewer = PDFViewer(cls.db_manager)
        cls.active_recall = ActiveRecallGenerator(cls.db_manager)
        cls.memory_mode = LongTermMemoryMode(cls.db_manager)
        cls.coding_bridge = CodingCompetencyMap(cls.db_manager)
        
        # Create test user
        cls.user_id = 1
        
        # Create test directory for PDF files
        cls.test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Create a simple PDF file for testing
        cls.test_pdf_path = os.path.join(cls.test_dir, "test.pdf")
        cls._create_test_pdf(cls.test_pdf_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        # Remove test files
        if os.path.exists(cls.test_pdf_path):
            os.remove(cls.test_pdf_path)
        
        # Remove test directory if empty
        if os.path.exists(cls.test_dir) and not os.listdir(cls.test_dir):
            os.rmdir(cls.test_dir)
    
    @classmethod
    def _create_test_pdf(cls, path: str):
        """Create a simple PDF file for testing."""
        try:
            import fitz  # PyMuPDF
            
            # Create a new PDF document
            doc = fitz.open()
            
            # Add a page
            page = doc.new_page()
            
            # Add some text
            text = "This is a test PDF file for the AI Note System.\n\n"
            text += "It contains some sample text to test the PDF reading and retention features.\n\n"
            text += "The system should be able to extract text, generate questions, and create flashcards from this content.\n\n"
            text += "Additionally, it should be able to track knowledge decay and generate summaries for long-term retention."
            
            # Insert text
            page.insert_text((50, 50), text, fontsize=12)
            
            # Save the document
            doc.save(path)
            doc.close()
            
            print(f"Created test PDF at {path}")
            
        except ImportError:
            print("PyMuPDF not installed, skipping PDF creation")
            # Create an empty file
            with open(path, "w") as f:
                f.write("")
    
    def test_pdf_viewer(self):
        """Test PDF viewer functionality."""
        print("\nTesting PDF viewer...")
        
        # Add a book
        book = self.pdf_viewer.add_book(
            user_id=self.user_id,
            file_path=self.test_pdf_path,
            title="Test Book",
            author="Test Author"
        )
        
        # Check if book was added successfully
        self.assertNotIn("error", book)
        self.assertEqual(book["title"], "Test Book")
        self.assertEqual(book["author"], "Test Author")
        
        # Get book
        retrieved_book = self.pdf_viewer.get_book(book["id"])
        self.assertEqual(retrieved_book["title"], "Test Book")
        
        # Update reading progress
        updated_book = self.pdf_viewer.update_reading_progress(book["id"], 2)
        self.assertGreater(updated_book["reading_progress"], 0)
        
        # Add annotation
        annotation = self.pdf_viewer.add_annotation(
            book_id=book["id"],
            user_id=self.user_id,
            page_number=1,
            annotation_type="highlight",
            content="This is a test annotation",
            position={"x": 50, "y": 50, "width": 100, "height": 20}
        )
        
        # Check if annotation was added successfully
        self.assertNotIn("error", annotation)
        self.assertEqual(annotation["content"], "This is a test annotation")
        
        # Get annotations
        annotations = self.pdf_viewer.get_annotations(book["id"], self.user_id)
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0]["content"], "This is a test annotation")
        
        print("PDF viewer tests passed!")
        return book["id"]
    
    def test_active_recall(self):
        """Test active recall functionality."""
        print("\nTesting active recall...")
        
        # Add a book
        book_id = self.test_pdf_viewer()
        
        # Generate micro-questions
        questions = self.active_recall.generate_micro_questions(
            book_id=book_id,
            user_id=self.user_id,
            page_number=1,
            text="This is a test PDF file for the AI Note System. It contains sample text to test features.",
            count=2
        )
        
        # Check if questions were generated successfully
        self.assertIsInstance(questions, list)
        if questions:  # Skip if LLM is not available
            self.assertGreaterEqual(len(questions), 1)
            self.assertIn("question", questions[0])
            self.assertIn("answer", questions[0])
        
        # Generate flashcards from text
        flashcards = self.active_recall.generate_flashcards_from_text(
            book_id=book_id,
            user_id=self.user_id,
            page_number=1,
            text="This is a test PDF file for the AI Note System. It contains sample text to test features.",
            count=2
        )
        
        # Check if flashcards were generated successfully
        self.assertIsInstance(flashcards, list)
        if flashcards:  # Skip if LLM is not available
            self.assertGreaterEqual(len(flashcards), 1)
            self.assertIn("front_text", flashcards[0])
            self.assertIn("back_text", flashcards[0])
        
        # Get flashcards
        retrieved_flashcards = self.active_recall.get_flashcards(book_id, self.user_id)
        if flashcards:  # Skip if LLM is not available
            self.assertEqual(len(retrieved_flashcards), len(flashcards))
        
        print("Active recall tests passed!")
        return book_id
    
    def test_memory_mode(self):
        """Test long-term memory mode functionality."""
        print("\nTesting long-term memory mode...")
        
        # Add a book
        book_id = self.test_active_recall()
        
        # Generate summary
        summary = self.memory_mode.generate_summary(
            book_id=book_id,
            user_id=self.user_id,
            summary_type="short"
        )
        
        # Check if summary was generated successfully
        self.assertIsInstance(summary, dict)
        if "error" not in summary:  # Skip if LLM is not available
            self.assertIn("content", summary)
            self.assertEqual(summary["summary_type"], "short")
        
        # Get summary
        retrieved_summary = self.memory_mode.get_summary(book_id, self.user_id, "short")
        if "error" not in summary:  # Skip if LLM is not available
            self.assertEqual(retrieved_summary["summary_type"], "short")
        
        # Generate timeline
        timeline = self.memory_mode.generate_timeline(book_id, self.user_id)
        
        # Check if timeline was generated successfully
        self.assertIsInstance(timeline, dict)
        
        # Extract key concepts
        concepts = self.memory_mode.extract_key_concepts(book_id, self.user_id, max_concepts=3)
        
        # Check if concepts were extracted successfully
        self.assertIsInstance(concepts, list)
        
        # Track knowledge decay
        tracked_concepts = self.memory_mode.track_knowledge_decay(book_id, self.user_id)
        
        # Check if knowledge decay is being tracked
        self.assertIsInstance(tracked_concepts, list)
        
        # Generate contextual reminder
        reminder = self.memory_mode.generate_contextual_reminder(book_id, self.user_id)
        
        # Check if reminder was generated successfully
        self.assertIsInstance(reminder, dict)
        
        # Generate quick recall session
        session = self.memory_mode.generate_quick_recall_session(book_id, self.user_id)
        
        # Check if session was generated successfully
        self.assertIsInstance(session, dict)
        
        print("Long-term memory mode tests passed!")
        return book_id
    
    def test_coding_bridge(self):
        """Test coding theory-practice bridge functionality."""
        print("\nTesting coding theory-practice bridge...")
        
        # Create test notes
        notes = [
            {
                "title": "Python Basics",
                "content": "Python is a high-level programming language. It supports multiple programming paradigms including procedural, object-oriented, and functional programming."
            },
            {
                "title": "Data Structures",
                "content": "Common data structures in Python include lists, dictionaries, sets, and tuples. Each has its own use cases and performance characteristics."
            },
            {
                "title": "Algorithms",
                "content": "Sorting algorithms include bubble sort, merge sort, and quicksort. Search algorithms include linear search and binary search."
            }
        ]
        
        # Analyze notes for skills
        competency_map = self.coding_bridge.analyze_notes_for_skills(self.user_id, notes)
        
        # Check if competency map was generated successfully
        self.assertIsInstance(competency_map, dict)
        if "error" not in competency_map:  # Skip if LLM is not available
            self.assertIn("critical_manual", competency_map)
            self.assertIn("ai_assisted", competency_map)
            self.assertIn("theory_only", competency_map)
        
        # Get skills
        skills = self.coding_bridge.get_skills(self.user_id)
        
        # Check if skills were retrieved successfully
        self.assertIsInstance(skills, list)
        
        if skills:  # Skip if no skills were found
            # Generate practical tasks
            tasks = self.coding_bridge.generate_practical_tasks(
                user_id=self.user_id,
                skill_id=skills[0]["id"],
                count=2
            )
            
            # Check if tasks were generated successfully
            self.assertIsInstance(tasks, list)
            
            if tasks:  # Skip if LLM is not available
                # Get tasks
                retrieved_tasks = self.coding_bridge.get_tasks(self.user_id, skills[0]["id"])
                self.assertEqual(len(retrieved_tasks), len(tasks))
                
                # Generate Jupyter notebook
                notebook = self.coding_bridge.generate_jupyter_notebook(
                    user_id=self.user_id,
                    skill_ids=[skills[0]["id"]],
                    title="Test Notebook"
                )
                
                # Check if notebook was generated successfully
                self.assertIsInstance(notebook, dict)
                
                # Get notebooks
                notebooks = self.coding_bridge.get_notebooks(self.user_id)
                if "error" not in notebook:  # Skip if LLM is not available
                    self.assertEqual(len(notebooks), 1)
                
                # Track task completion
                tracking = self.coding_bridge.track_task_completion(
                    user_id=self.user_id,
                    task_id=tasks[0]["id"],
                    completion_type="manual"
                )
                
                # Check if tracking was successful
                self.assertIsInstance(tracking, dict)
                self.assertNotIn("error", tracking)
                
                # Get AI collaboration stats
                stats = self.coding_bridge.get_ai_collaboration_stats(self.user_id)
                
                # Check if stats were generated successfully
                self.assertIsInstance(stats, dict)
                self.assertEqual(stats["total_tasks"], 1)
                self.assertEqual(stats["manual_tasks"], 1)
                
                # Generate self-assessment
                assessment = self.coding_bridge.generate_self_assessment(self.user_id)
                
                # Check if assessment was generated successfully
                self.assertIsInstance(assessment, dict)
        
        print("Coding theory-practice bridge tests passed!")
    
    def test_all_features(self):
        """Test all new features."""
        print("\nTesting all new features...")
        
        # Test PDF viewer
        self.test_pdf_viewer()
        
        # Test active recall
        self.test_active_recall()
        
        # Test long-term memory mode
        self.test_memory_mode()
        
        # Test coding theory-practice bridge
        self.test_coding_bridge()
        
        print("All tests passed!")

if __name__ == "__main__":
    unittest.main()