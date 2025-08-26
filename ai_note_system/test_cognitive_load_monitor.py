"""
Unit tests for the Stress & Cognitive Load Monitor module.
"""

import os
import unittest
import tempfile
import json
import sqlite3
from datetime import datetime, timedelta

from ai_note_system.tracking.cognitive_load_monitor import CognitiveLoadMonitor
from ai_note_system.database.db_manager import DatabaseManager

class MockWebcamMonitor:
    """Mock webcam monitor for testing."""
    
    def capture_frame(self):
        """Return a mock frame."""
        return None
    
    def analyze_expression(self, frame):
        """Return mock expression analysis."""
        return {
            "neutral": 0.6,
            "confused": 0.2,
            "focused": 0.1,
            "stressed": 0.1
        }

class TestCognitiveLoadMonitor(unittest.TestCase):
    """Test cases for the CognitiveLoadMonitor class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary database
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp()
        self.db_manager = DatabaseManager(self.temp_db_path)
        
        # Create a temporary output directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize monitor
        self.monitor = CognitiveLoadMonitor(
            user_id="test_user",
            db_manager=self.db_manager,
            enable_webcam=False,
            data_dir=self.temp_dir
        )
        
        # Initialize database tables
        self.monitor._init_database()
    
    def tearDown(self):
        """Clean up test environment."""
        self.db_manager.conn.close()
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        
        # Clean up temporary output directory
        for filename in os.listdir(self.temp_dir):
            os.unlink(os.path.join(self.temp_dir, filename))
        os.rmdir(self.temp_dir)
    
    def test_record_self_report(self):
        """Test recording a self-report."""
        # Record a self-report
        result = self.monitor.record_self_report(
            cognitive_load=7,
            stress_level=6,
            fatigue_level=5,
            focus_level=4,
            notes="Test self-report"
        )
        
        # Check result
        self.assertEqual(result["user_id"], "test_user")
        self.assertEqual(result["cognitive_load"], 7)
        self.assertEqual(result["stress_level"], 6)
        self.assertEqual(result["fatigue_level"], 5)
        self.assertEqual(result["focus_level"], 4)
        self.assertEqual(result["notes"], "Test self-report")
        self.assertIn("timestamp", result)
        self.assertIn("recommendations", result)
        
        # Check that data was saved to database
        self.db_manager.cursor.execute('''
        SELECT * FROM cognitive_load_data WHERE user_id = ?
        ''', ("test_user",))
        
        row = self.db_manager.cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["cognitive_load"], 7)
        self.assertEqual(row["stress_level"], 6)
        self.assertEqual(row["fatigue_level"], 5)
        self.assertEqual(row["focus_level"], 4)
        self.assertEqual(row["notes"], "Test self-report")
    
    def test_generate_recommendations(self):
        """Test generating recommendations based on cognitive state."""
        # Generate recommendations for high cognitive load
        recommendations = self.monitor.generate_recommendations(
            cognitive_load=8,
            stress_level=7,
            fatigue_level=6,
            focus_level=3
        )
        
        # Check that recommendations were generated
        self.assertGreater(len(recommendations), 0)
        
        # Check that recommendations were saved to database
        self.db_manager.cursor.execute('''
        SELECT COUNT(*) as count FROM cognitive_load_recommendations
        ''')
        
        row = self.db_manager.cursor.fetchone()
        self.assertGreater(row["count"], 0)
        
        # Generate recommendations for low cognitive load
        recommendations = self.monitor.generate_recommendations(
            cognitive_load=3,
            stress_level=2,
            fatigue_level=2,
            focus_level=8
        )
        
        # Check that recommendations were generated
        self.assertGreater(len(recommendations), 0)
    
    def test_analyze_keyboard_data(self):
        """Test analyzing keyboard data."""
        # Start keyboard monitoring
        self.monitor.start_keyboard_monitoring(session_id="test_session")
        
        # Analyze keyboard data
        analysis = self.monitor._analyze_keyboard_data()
        
        # Check analysis
        self.assertIn("cognitive_load", analysis)
        self.assertIn("stress_level", analysis)
        self.assertIn("fatigue_level", analysis)
        self.assertIn("focus_level", analysis)
        self.assertIn("typing_speed", analysis)
        self.assertIn("error_rate", analysis)
        self.assertIn("pause_frequency", analysis)
        self.assertIn("timestamp", analysis)
    
    def test_get_cognitive_load_history(self):
        """Test getting cognitive load history."""
        # Add some test data
        for i in range(5):
            self.monitor.record_self_report(
                cognitive_load=5 + i,
                stress_level=4 + i,
                fatigue_level=3 + i,
                focus_level=6 - i,
                notes=f"Test report {i+1}"
            )
        
        # Get history
        history = self.monitor.get_cognitive_load_history(days=7)
        
        # Check history
        self.assertEqual(len(history), 5)
        self.assertEqual(history[0]["notes"], "Test report 5")  # Most recent first
        self.assertEqual(history[4]["notes"], "Test report 1")  # Oldest last
    
    def test_get_recommendations_history(self):
        """Test getting recommendations history."""
        # Generate some recommendations
        self.monitor.generate_recommendations(
            cognitive_load=8,
            stress_level=7,
            fatigue_level=6,
            focus_level=3
        )
        
        # Get history
        history = self.monitor.get_recommendations_history(days=7)
        
        # Check history
        self.assertGreater(len(history), 0)
    
    def test_analyze_cognitive_patterns(self):
        """Test analyzing cognitive patterns."""
        # Add some test data with different timestamps
        now = datetime.now()
        
        for i in range(10):
            timestamp = (now - timedelta(days=i)).isoformat()
            
            self.db_manager.cursor.execute('''
            INSERT INTO cognitive_load_data (
                user_id, timestamp, cognitive_load, stress_level,
                fatigue_level, focus_level, data_source, session_id, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "test_user",
                timestamp,
                5 + (i % 3),  # Vary cognitive load
                4 + (i % 3),  # Vary stress level
                3 + (i % 3),  # Vary fatigue level
                6 - (i % 3),  # Vary focus level
                "self_report",
                f"session_{i}",
                f"Test report {i+1}"
            ))
        
        self.db_manager.conn.commit()
        
        # Analyze patterns
        analysis = self.monitor.analyze_cognitive_patterns(days=30)
        
        # Check analysis
        self.assertIn("user_id", analysis)
        self.assertIn("days_analyzed", analysis)
        self.assertIn("data_points", analysis)
        self.assertIn("averages", analysis)
        self.assertIn("time_patterns", analysis)
        self.assertIn("correlations", analysis)
        
        # Check that averages were calculated
        self.assertIn("cognitive_load", analysis["averages"])
        self.assertIn("stress_level", analysis["averages"])
        self.assertIn("fatigue_level", analysis["averages"])
        self.assertIn("focus_level", analysis["averages"])
        
        # Check that time patterns were analyzed
        self.assertIn("optimal_time", analysis["time_patterns"])
    
    def test_save_to_file(self):
        """Test saving data to file."""
        # Create test data
        data = {
            "user_id": "test_user",
            "cognitive_load": 7,
            "stress_level": 6,
            "fatigue_level": 5,
            "focus_level": 4,
            "notes": "Test data",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        filepath = self.monitor._save_to_file(data)
        
        # Check that file was created
        self.assertTrue(os.path.exists(filepath))
        
        # Check file contents
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data["user_id"], "test_user")
        self.assertEqual(saved_data["cognitive_load"], 7)
        self.assertEqual(saved_data["stress_level"], 6)
        self.assertEqual(saved_data["fatigue_level"], 5)
        self.assertEqual(saved_data["focus_level"], 4)
        self.assertEqual(saved_data["notes"], "Test data")


if __name__ == "__main__":
    unittest.main()