"""
Integration test script for the AI Note System.
Demonstrates how the new features work together with existing functionality.
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_note_system.integration_test")

# Import required modules
from ai_note_system.database.db_manager import DatabaseManager
from ai_note_system.processing.summarizer import summarize_text
from ai_note_system.processing.keypoints_extractor import extract_key_points
from ai_note_system.processing.application_context_generator import ApplicationContextGenerator
from ai_note_system.processing.microlearning_generator import MicrolearningGenerator
from ai_note_system.visualization.interactive_glossary import InteractiveGlossary
from ai_note_system.tracking.cognitive_load_monitor import CognitiveLoadMonitor
from ai_note_system.tracking.distraction_tracker import DistractionTracker
from ai_note_system.agents.project_planning import ProjectPlanningCoordinator

class IntegrationTest:
    """
    Integration test for the AI Note System.
    Tests how the new features work together with existing functionality.
    """
    
    def __init__(self, db_path: str, output_dir: str):
        """
        Initialize the integration test.
        
        Args:
            db_path (str): Path to the database file
            output_dir (str): Directory to save output files
        """
        self.db_path = db_path
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize database manager
        self.db_manager = DatabaseManager(db_path)
        
        # Initialize components
        self.app_context_generator = ApplicationContextGenerator(
            db_manager=self.db_manager,
            output_dir=output_dir
        )
        
        self.microlearning_generator = MicrolearningGenerator(
            db_manager=self.db_manager,
            output_dir=output_dir
        )
        
        self.glossary = InteractiveGlossary(
            db_manager=self.db_manager,
            output_dir=output_dir
        )
        
        self.cognitive_load_monitor = CognitiveLoadMonitor(
            user_id="test_user",
            db_manager=self.db_manager,
            data_dir=output_dir
        )
        
        self.distraction_tracker = DistractionTracker(
            user_id="test_user",
            db_manager=self.db_manager,
            data_dir=output_dir
        )
        
        self.project_planner = ProjectPlanningCoordinator(
            db_manager=self.db_manager,
            output_dir=output_dir
        )
        
        logger.info("Initialized integration test components")
    
    def create_test_note(self, title: str, content: str) -> int:
        """
        Create a test note in the database.
        
        Args:
            title (str): Title of the note
            content (str): Content of the note
            
        Returns:
            int: ID of the created note
        """
        # Create notes table if it doesn't exist
        self.db_manager.cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # Insert note
        timestamp = datetime.now().isoformat()
        self.db_manager.cursor.execute('''
        INSERT INTO notes (title, text, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        ''', (title, content, timestamp, timestamp))
        
        self.db_manager.conn.commit()
        note_id = self.db_manager.cursor.lastrowid
        
        logger.info(f"Created test note with ID {note_id}: {title}")
        return note_id
    
    def run_test(self):
        """
        Run the integration test.
        """
        logger.info("Starting integration test")
        
        # Step 1: Create a test note about machine learning
        note_content = """
        # Machine Learning Fundamentals
        
        Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.
        
        ## Types of Machine Learning
        
        1. **Supervised Learning**: The algorithm is trained on labeled data, learning to map inputs to known outputs.
        
        2. **Unsupervised Learning**: The algorithm works with unlabeled data, finding patterns and relationships without guidance.
        
        3. **Reinforcement Learning**: The algorithm learns by interacting with an environment, receiving rewards or penalties for actions.
        
        ## Common Algorithms
        
        - **Linear Regression**: Predicts continuous values based on input features.
        - **Decision Trees**: Creates a tree-like model of decisions based on feature values.
        - **Neural Networks**: Inspired by the human brain, consists of interconnected nodes (neurons) organized in layers.
        - **Support Vector Machines**: Finds the hyperplane that best separates classes in the feature space.
        - **K-means Clustering**: Groups similar data points together based on feature similarity.
        
        ## Evaluation Metrics
        
        - **Accuracy**: Proportion of correct predictions among the total predictions.
        - **Precision**: Proportion of true positives among all positive predictions.
        - **Recall**: Proportion of true positives identified among all actual positives.
        - **F1 Score**: Harmonic mean of precision and recall.
        - **ROC Curve**: Plot of true positive rate against false positive rate at various thresholds.
        
        ## Challenges in Machine Learning
        
        - **Overfitting**: Model performs well on training data but poorly on unseen data.
        - **Underfitting**: Model is too simple to capture the underlying pattern in the data.
        - **Data Quality**: Poor quality data leads to poor model performance.
        - **Feature Selection**: Choosing the most relevant features for the model.
        - **Interpretability**: Understanding why a model makes certain predictions.
        """
        
        note_id = self.create_test_note("Machine Learning Fundamentals", note_content)
        
        # Step 2: Process the note with existing functionality
        logger.info("Processing note with existing functionality")
        
        # Summarize the note
        summary = summarize_text(note_content)
        logger.info(f"Generated summary: {summary[:100]}...")
        
        # Extract key points
        key_points = extract_key_points(note_content)
        logger.info(f"Extracted {len(key_points)} key points")
        
        # Step 3: Use the new features with the note
        logger.info("Testing new features with the note")
        
        # Test 1: Generate application context
        logger.info("Testing Real-World Application Context Generator")
        app_context = self.app_context_generator.generate_application_context(
            note_id=note_id,
            include_use_cases=True,
            include_industry_applications=True,
            include_historical_context=True
        )
        
        logger.info(f"Generated application context for '{app_context['concept']}'")
        logger.info(f"Generated {len(app_context.get('use_cases', []))} use cases")
        logger.info(f"Generated {len(app_context.get('industry_applications', []))} industry applications")
        
        # Test 2: Generate microlearning content
        logger.info("Testing Auto-Microlearning Generator")
        microlearning = self.microlearning_generator.generate_microlearning(
            note_id=note_id,
            duration_minutes=3,
            include_question=True,
            include_diagram=True
        )
        
        logger.info(f"Generated microlearning: {microlearning.get('title', '')}")
        logger.info(f"Microlearning duration: {microlearning.get('duration_minutes', 0)} minutes")
        
        # Test 3: Add terms to glossary
        logger.info("Testing Interactive Visual Glossary")
        
        # Add machine learning term
        ml_term = self.glossary.add_term(
            term="Machine Learning",
            definition="A subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            category="Artificial Intelligence",
            importance=5
        )
        
        # Add supervised learning term
        sl_term = self.glossary.add_term(
            term="Supervised Learning",
            definition="A type of machine learning where the algorithm is trained on labeled data, learning to map inputs to known outputs.",
            category="Machine Learning",
            importance=4,
            related_terms=[
                {"term": "Machine Learning", "relationship_type": "parent"}
            ]
        )
        
        # Scan note for terms
        found_terms = self.glossary.scan_note_for_terms(note_id=note_id)
        logger.info(f"Found {len(found_terms)} glossary terms in the note")
        
        # Generate glossary interface
        terms = [ml_term, sl_term]
        html_interface = self.glossary.generate_clickable_interface(
            terms=terms,
            format_type="html",
            include_definitions=True,
            include_examples=True,
            include_references=True
        )
        
        # Save HTML interface
        html_path = os.path.join(self.output_dir, "glossary.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_interface)
        
        logger.info(f"Saved glossary HTML interface to {html_path}")
        
        # Test 4: Track cognitive load
        logger.info("Testing Stress & Cognitive Load Monitor")
        
        # Record self-report
        cognitive_report = self.cognitive_load_monitor.record_self_report(
            cognitive_load=6,
            stress_level=5,
            fatigue_level=4,
            focus_level=7,
            notes="Working on machine learning concepts"
        )
        
        logger.info(f"Recorded cognitive load self-report")
        
        # Generate recommendations
        recommendations = self.cognitive_load_monitor.generate_recommendations(
            cognitive_load=6,
            stress_level=5,
            fatigue_level=4,
            focus_level=7
        )
        
        logger.info(f"Generated {len(recommendations)} cognitive load recommendations")
        
        # Test 5: Track distractions
        logger.info("Testing Distraction Tracking & Intervention")
        
        # Record distraction
        distraction = self.distraction_tracker.record_distraction(
            distraction_type="app_switch",
            duration_seconds=120,
            app_name="Social Media",
            notes="Checked notifications"
        )
        
        logger.info(f"Recorded distraction event")
        
        # Generate intervention
        intervention = self.distraction_tracker.generate_intervention(
            distraction_frequency=3,
            total_distraction_time=300,
            current_focus_time=1800
        )
        
        logger.info(f"Generated distraction intervention: {intervention.get('message', '')}")
        
        # Test 6: Generate project plan
        logger.info("Testing Multi-Agent Cooperative Project Planning")
        
        # Create project plan
        project_plan = self.project_planner.create_project_plan(
            project_name="Machine Learning Image Classifier",
            project_description="Build an image classifier using machine learning techniques",
            project_goals=["Create a CNN model", "Achieve 90% accuracy", "Deploy as a web service"],
            timeline_weeks=4,
            complexity="medium"
        )
        
        logger.info(f"Generated project plan for '{project_plan.get('project_name', '')}'")
        logger.info(f"Project plan has {len(project_plan.get('milestones', []))} milestones")
        
        # Save project plan
        plan_path = os.path.join(self.output_dir, "project_plan.json")
        with open(plan_path, "w") as f:
            import json
            json.dump(project_plan, f, indent=2)
        
        logger.info(f"Saved project plan to {plan_path}")
        
        # Step 4: Integration test summary
        logger.info("Integration test completed successfully")
        logger.info(f"All output files saved to {self.output_dir}")
        
        return {
            "note_id": note_id,
            "summary": summary,
            "key_points": key_points,
            "application_context": app_context,
            "microlearning": microlearning,
            "glossary_terms": terms,
            "cognitive_load": cognitive_report,
            "distraction": distraction,
            "project_plan": project_plan,
            "output_dir": self.output_dir
        }


def main():
    """
    Main function to run the integration test.
    """
    parser = argparse.ArgumentParser(description="AI Note System Integration Test")
    parser.add_argument("--db-path", default="test_integration.db", help="Path to the database file")
    parser.add_argument("--output-dir", default="integration_test_output", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Run integration test
    test = IntegrationTest(db_path=args.db_path, output_dir=args.output_dir)
    result = test.run_test()
    
    print("\nIntegration Test Summary:")
    print("=" * 50)
    print(f"Note ID: {result['note_id']}")
    print(f"Generated summary length: {len(result['summary'])}")
    print(f"Extracted key points: {len(result['key_points'])}")
    print(f"Application context use cases: {len(result['application_context'].get('use_cases', []))}")
    print(f"Microlearning duration: {result['microlearning'].get('duration_minutes', 0)} minutes")
    print(f"Glossary terms: {len(result['glossary_terms'])}")
    print(f"Cognitive load recommendations: {len(result['cognitive_load'].get('recommendations', []))}")
    print(f"Project plan milestones: {len(result['project_plan'].get('milestones', []))}")
    print(f"All output files saved to: {result['output_dir']}")
    print("=" * 50)


if __name__ == "__main__":
    main()