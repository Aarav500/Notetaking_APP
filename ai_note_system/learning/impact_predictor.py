"""
Learning Impact Predictor

This module provides functionality for predicting mastery time, probability of forgetting,
and readiness for exams, as well as dynamically updating predictions based on performance.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import math

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class ImpactPredictor:
    """
    Learning Impact Predictor
    
    Features:
    - Predict mastery time for concepts
    - Calculate probability of forgetting without review
    - Assess readiness for exams in specific domains
    - Dynamically update predictions based on performance
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None):
        """Initialize the impact predictor"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create learning predictions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_predictions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            topic_id INTEGER,
            topic_name TEXT NOT NULL,
            predicted_mastery_hours REAL,
            current_mastery_level REAL NOT NULL DEFAULT 0.0,
            forgetting_rate REAL NOT NULL DEFAULT 0.1,
            last_review_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create learning performance table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_performance (
            id INTEGER PRIMARY KEY,
            prediction_id INTEGER NOT NULL,
            performance_type TEXT NOT NULL,
            score REAL NOT NULL,
            duration_minutes REAL,
            timestamp TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (prediction_id) REFERENCES learning_predictions(id)
        )
        ''')
        
        # Create exam readiness table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_readiness (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            exam_name TEXT NOT NULL,
            exam_date TEXT,
            readiness_score REAL NOT NULL DEFAULT 0.0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create exam topics table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_topics (
            id INTEGER PRIMARY KEY,
            exam_id INTEGER NOT NULL,
            prediction_id INTEGER NOT NULL,
            weight REAL NOT NULL DEFAULT 1.0,
            FOREIGN KEY (exam_id) REFERENCES exam_readiness(id),
            FOREIGN KEY (prediction_id) REFERENCES learning_predictions(id)
        )
        ''')
        
        conn.commit()
    
    def predict_mastery_time(self, user_id: int, topic_name: str, 
                           topic_id: Optional[int] = None,
                           topic_content: Optional[str] = None,
                           user_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Predict the time required to master a topic
        
        Args:
            user_id: The ID of the user
            topic_name: The name of the topic
            topic_id: Optional ID of the topic in the database
            topic_content: Optional content of the topic
            user_history: Optional learning history of the user
            
        Returns:
            Dictionary with prediction details
        """
        logger.info(f"Predicting mastery time for topic: {topic_name}")
        
        # Get user's learning history if not provided
        if user_history is None:
            user_history = self._get_user_learning_history(user_id)
        
        # Calculate initial mastery level based on user history
        initial_mastery = self._calculate_initial_mastery(topic_name, user_history)
        
        # Determine topic complexity
        complexity = self._determine_topic_complexity(topic_name, topic_content)
        
        # Calculate predicted mastery hours based on complexity and initial mastery
        predicted_hours = self._calculate_predicted_hours(complexity, initial_mastery)
        
        # Calculate forgetting rate based on user history
        forgetting_rate = self._calculate_forgetting_rate(user_id, topic_name, user_history)
        
        # Store prediction in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO learning_predictions (
            user_id, topic_id, topic_name, predicted_mastery_hours,
            current_mastery_level, forgetting_rate, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, topic_id, topic_name, predicted_hours,
            initial_mastery, forgetting_rate, now, now
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        
        return {
            'id': prediction_id,
            'user_id': user_id,
            'topic_id': topic_id,
            'topic_name': topic_name,
            'predicted_mastery_hours': predicted_hours,
            'current_mastery_level': initial_mastery,
            'forgetting_rate': forgetting_rate,
            'created_at': now,
            'updated_at': now
        }
    
    def calculate_forgetting_probability(self, prediction_id: int, 
                                       days_since_review: Optional[int] = None) -> float:
        """
        Calculate the probability of forgetting a topic without review
        
        Args:
            prediction_id: The ID of the learning prediction
            days_since_review: Optional number of days since last review
            
        Returns:
            Probability of forgetting (0.0 to 1.0)
        """
        # Get prediction details
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT current_mastery_level, forgetting_rate, last_review_date
        FROM learning_predictions
        WHERE id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return 1.0  # If prediction not found, assume 100% forgetting
        
        mastery_level, forgetting_rate, last_review_date = row
        
        # Calculate days since last review
        if days_since_review is None:
            if last_review_date:
                last_review = datetime.fromisoformat(last_review_date)
                days_since_review = (datetime.now() - last_review).days
            else:
                days_since_review = 30  # Default to 30 days if no review date
        
        # Calculate forgetting probability using Ebbinghaus forgetting curve
        # P(forgetting) = 1 - (mastery_level * e^(-forgetting_rate * days))
        forgetting_prob = 1.0 - (mastery_level * math.exp(-forgetting_rate * days_since_review))
        
        # Ensure probability is between 0 and 1
        forgetting_prob = max(0.0, min(1.0, forgetting_prob))
        
        return forgetting_prob
    
    def assess_exam_readiness(self, user_id: int, exam_name: str, 
                            topic_weights: Dict[str, float],
                            exam_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess readiness for an exam in a specific domain
        
        Args:
            user_id: The ID of the user
            exam_name: The name of the exam
            topic_weights: Dictionary mapping topic names to their weights in the exam
            exam_date: Optional date of the exam
            
        Returns:
            Dictionary with readiness assessment
        """
        logger.info(f"Assessing readiness for exam: {exam_name}")
        
        # Create exam readiness record
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO exam_readiness (
            user_id, exam_name, exam_date, readiness_score, created_at, updated_at
        )
        VALUES (?, ?, ?, 0.0, ?, ?)
        ''', (user_id, exam_name, exam_date, now, now))
        
        exam_id = cursor.lastrowid
        
        # Calculate readiness for each topic
        total_weight = sum(topic_weights.values())
        weighted_readiness_sum = 0.0
        
        for topic_name, weight in topic_weights.items():
            # Get prediction for this topic
            cursor.execute('''
            SELECT id, current_mastery_level, forgetting_rate, last_review_date
            FROM learning_predictions
            WHERE user_id = ? AND topic_name = ?
            ORDER BY updated_at DESC
            LIMIT 1
            ''', (user_id, topic_name))
            
            row = cursor.fetchone()
            
            if row:
                prediction_id, mastery_level, forgetting_rate, last_review_date = row
                
                # Calculate days until exam
                days_until_exam = 30  # Default to 30 days
                if exam_date:
                    exam_datetime = datetime.fromisoformat(exam_date)
                    days_until_exam = max(0, (exam_datetime - datetime.now()).days)
                
                # Calculate forgetting by exam date
                if last_review_date:
                    last_review = datetime.fromisoformat(last_review_date)
                    days_since_review = (datetime.now() - last_review).days
                    days_by_exam = days_since_review + days_until_exam
                else:
                    days_by_exam = days_until_exam
                
                # Calculate expected mastery at exam time
                expected_mastery = mastery_level * math.exp(-forgetting_rate * days_by_exam)
                expected_mastery = max(0.0, min(1.0, expected_mastery))
                
                # Add to weighted sum
                normalized_weight = weight / total_weight
                weighted_readiness_sum += expected_mastery * normalized_weight
                
                # Link topic to exam
                cursor.execute('''
                INSERT INTO exam_topics (exam_id, prediction_id, weight)
                VALUES (?, ?, ?)
                ''', (exam_id, prediction_id, normalized_weight))
            else:
                # Topic not found, create a new prediction with low mastery
                prediction = self.predict_mastery_time(user_id, topic_name)
                prediction_id = prediction['id']
                
                # Link topic to exam
                normalized_weight = weight / total_weight
                cursor.execute('''
                INSERT INTO exam_topics (exam_id, prediction_id, weight)
                VALUES (?, ?, ?)
                ''', (exam_id, prediction_id, normalized_weight))
        
        # Update overall readiness score
        cursor.execute('''
        UPDATE exam_readiness
        SET readiness_score = ?
        WHERE id = ?
        ''', (weighted_readiness_sum, exam_id))
        
        conn.commit()
        
        return {
            'id': exam_id,
            'user_id': user_id,
            'exam_name': exam_name,
            'exam_date': exam_date,
            'readiness_score': weighted_readiness_sum,
            'created_at': now,
            'updated_at': now,
            'topic_weights': topic_weights
        }
    
    def update_performance(self, prediction_id: int, performance_type: str,
                         score: float, duration_minutes: Optional[float] = None,
                         notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Update learning prediction based on performance
        
        Args:
            prediction_id: The ID of the learning prediction
            performance_type: The type of performance (quiz, exercise, etc.)
            score: The performance score (0.0 to 1.0)
            duration_minutes: Optional duration of the activity in minutes
            notes: Optional notes about the performance
            
        Returns:
            Dictionary with updated prediction
        """
        logger.info(f"Updating performance for prediction {prediction_id}")
        
        # Record the performance
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO learning_performance (
            prediction_id, performance_type, score, duration_minutes, timestamp, notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (prediction_id, performance_type, score, duration_minutes, timestamp, notes))
        
        performance_id = cursor.lastrowid
        
        # Get current prediction data
        cursor.execute('''
        SELECT current_mastery_level, forgetting_rate, predicted_mastery_hours
        FROM learning_predictions
        WHERE id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.commit()
            return {'error': 'Prediction not found'}
        
        current_mastery, forgetting_rate, predicted_hours = row
        
        # Update mastery level based on performance
        new_mastery = self._update_mastery_level(current_mastery, score, performance_type)
        
        # Update forgetting rate based on performance history
        cursor.execute('''
        SELECT score, timestamp
        FROM learning_performance
        WHERE prediction_id = ?
        ORDER BY timestamp
        ''', (prediction_id,))
        
        performances = [(row[0], row[1]) for row in cursor.fetchall()]
        new_forgetting_rate = self._update_forgetting_rate(forgetting_rate, performances)
        
        # Update predicted hours if needed
        new_predicted_hours = predicted_hours
        if duration_minutes is not None:
            # Adjust prediction based on actual time spent
            hours_spent = duration_minutes / 60.0
            mastery_gain = new_mastery - current_mastery
            if mastery_gain > 0:
                # Extrapolate total hours needed based on current progress
                new_predicted_hours = hours_spent * (1.0 / mastery_gain)
        
        # Update the prediction
        cursor.execute('''
        UPDATE learning_predictions
        SET current_mastery_level = ?, forgetting_rate = ?, 
            predicted_mastery_hours = ?, last_review_date = ?, updated_at = ?
        WHERE id = ?
        ''', (new_mastery, new_forgetting_rate, new_predicted_hours, timestamp, timestamp, prediction_id))
        
        conn.commit()
        
        # Return the updated prediction
        return {
            'id': prediction_id,
            'performance_id': performance_id,
            'current_mastery_level': new_mastery,
            'forgetting_rate': new_forgetting_rate,
            'predicted_mastery_hours': new_predicted_hours,
            'last_review_date': timestamp,
            'updated_at': timestamp
        }
    
    def get_prediction(self, prediction_id: int) -> Dict[str, Any]:
        """
        Get a learning prediction by ID
        
        Args:
            prediction_id: The ID of the learning prediction
            
        Returns:
            Dictionary with prediction details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, topic_id, topic_name, predicted_mastery_hours,
               current_mastery_level, forgetting_rate, last_review_date,
               created_at, updated_at
        FROM learning_predictions
        WHERE id = ?
        ''', (prediction_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        prediction = {
            'id': row[0],
            'user_id': row[1],
            'topic_id': row[2],
            'topic_name': row[3],
            'predicted_mastery_hours': row[4],
            'current_mastery_level': row[5],
            'forgetting_rate': row[6],
            'last_review_date': row[7],
            'created_at': row[8],
            'updated_at': row[9],
            'performances': []
        }
        
        # Get performances for this prediction
        cursor.execute('''
        SELECT id, performance_type, score, duration_minutes, timestamp, notes
        FROM learning_performance
        WHERE prediction_id = ?
        ORDER BY timestamp DESC
        ''', (prediction_id,))
        
        for row in cursor.fetchall():
            performance = {
                'id': row[0],
                'performance_type': row[1],
                'score': row[2],
                'duration_minutes': row[3],
                'timestamp': row[4],
                'notes': row[5]
            }
            prediction['performances'].append(performance)
        
        return prediction
    
    def get_user_predictions(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get learning predictions for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of predictions to return
            
        Returns:
            List of prediction summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, topic_name, predicted_mastery_hours, current_mastery_level,
               forgetting_rate, last_review_date, updated_at
        FROM learning_predictions
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        predictions = []
        for row in cursor.fetchall():
            prediction = {
                'id': row[0],
                'topic_name': row[1],
                'predicted_mastery_hours': row[2],
                'current_mastery_level': row[3],
                'forgetting_rate': row[4],
                'last_review_date': row[5],
                'updated_at': row[6]
            }
            predictions.append(prediction)
        
        return predictions
    
    def get_exam_readiness(self, exam_id: int) -> Dict[str, Any]:
        """
        Get exam readiness assessment by ID
        
        Args:
            exam_id: The ID of the exam readiness assessment
            
        Returns:
            Dictionary with exam readiness details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, exam_name, exam_date, readiness_score, created_at, updated_at
        FROM exam_readiness
        WHERE id = ?
        ''', (exam_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        exam = {
            'id': row[0],
            'user_id': row[1],
            'exam_name': row[2],
            'exam_date': row[3],
            'readiness_score': row[4],
            'created_at': row[5],
            'updated_at': row[6],
            'topics': []
        }
        
        # Get topics for this exam
        cursor.execute('''
        SELECT et.prediction_id, et.weight, lp.topic_name, lp.current_mastery_level
        FROM exam_topics et
        JOIN learning_predictions lp ON et.prediction_id = lp.id
        WHERE et.exam_id = ?
        ORDER BY et.weight DESC
        ''', (exam_id,))
        
        for row in cursor.fetchall():
            topic = {
                'prediction_id': row[0],
                'weight': row[1],
                'topic_name': row[2],
                'mastery_level': row[3]
            }
            exam['topics'].append(topic)
        
        return exam
    
    def get_user_exams(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get exam readiness assessments for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of assessments to return
            
        Returns:
            List of exam readiness summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, exam_name, exam_date, readiness_score, updated_at
        FROM exam_readiness
        WHERE user_id = ?
        ORDER BY updated_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        exams = []
        for row in cursor.fetchall():
            exam = {
                'id': row[0],
                'exam_name': row[1],
                'exam_date': row[2],
                'readiness_score': row[3],
                'updated_at': row[4]
            }
            exams.append(exam)
        
        return exams
    
    def _get_user_learning_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's learning history from the database"""
        # This would typically query the user's study sessions, quiz results, etc.
        # For simplicity, we'll return an empty list
        return []
    
    def _calculate_initial_mastery(self, topic_name: str, 
                                 user_history: List[Dict[str, Any]]) -> float:
        """Calculate initial mastery level based on user history"""
        # This would analyze the user's history to determine initial mastery
        # For simplicity, we'll return a default value
        return 0.1  # Start with 10% mastery
    
    def _determine_topic_complexity(self, topic_name: str, 
                                  topic_content: Optional[str] = None) -> float:
        """Determine the complexity of a topic"""
        # This would analyze the topic content to determine complexity
        # For simplicity, we'll use a default value
        if topic_content:
            # Simple heuristic: longer content is more complex
            return min(1.0, len(topic_content) / 10000)
        else:
            return 0.5  # Medium complexity
    
    def _calculate_predicted_hours(self, complexity: float, 
                                 initial_mastery: float) -> float:
        """Calculate predicted hours to mastery based on complexity and initial mastery"""
        # Simple model: more complex topics take longer, higher initial mastery reduces time
        base_hours = 10.0  # Base hours for medium complexity
        complexity_factor = 1.0 + (complexity * 2.0)  # 1.0 to 3.0
        mastery_factor = 1.0 - (initial_mastery * 0.8)  # 0.2 to 1.0
        
        predicted_hours = base_hours * complexity_factor * mastery_factor
        return round(predicted_hours, 1)
    
    def _calculate_forgetting_rate(self, user_id: int, topic_name: str,
                                 user_history: List[Dict[str, Any]]) -> float:
        """Calculate forgetting rate based on user history"""
        # This would analyze the user's history to determine forgetting rate
        # For simplicity, we'll return a default value
        return 0.1  # Default forgetting rate
    
    def _update_mastery_level(self, current_mastery: float, score: float,
                            performance_type: str) -> float:
        """Update mastery level based on performance"""
        # Different performance types have different impacts
        if performance_type == 'quiz':
            weight = 0.2
        elif performance_type == 'exercise':
            weight = 0.3
        elif performance_type == 'project':
            weight = 0.5
        else:
            weight = 0.1
        
        # Calculate new mastery level
        mastery_gain = (score - current_mastery) * weight
        new_mastery = current_mastery + mastery_gain
        
        # Ensure mastery is between 0 and 1
        return max(0.0, min(1.0, new_mastery))
    
    def _update_forgetting_rate(self, current_rate: float,
                              performances: List[Tuple[float, str]]) -> float:
        """Update forgetting rate based on performance history"""
        if len(performances) < 2:
            return current_rate
        
        # Calculate average performance change over time
        performance_changes = []
        for i in range(1, len(performances)):
            prev_score, prev_time = performances[i-1]
            curr_score, curr_time = performances[i]
            
            prev_datetime = datetime.fromisoformat(prev_time)
            curr_datetime = datetime.fromisoformat(curr_time)
            
            days_diff = (curr_datetime - prev_datetime).days
            if days_diff > 0:
                score_diff = curr_score - prev_score
                daily_change = score_diff / days_diff
                performance_changes.append(daily_change)
        
        if not performance_changes:
            return current_rate
        
        # Adjust forgetting rate based on average performance change
        avg_change = sum(performance_changes) / len(performance_changes)
        
        # If performance improves over time, decrease forgetting rate
        # If performance declines over time, increase forgetting rate
        rate_adjustment = -avg_change * 0.5
        new_rate = current_rate + rate_adjustment
        
        # Ensure rate is between 0.01 and 0.5
        return max(0.01, min(0.5, new_rate))

# Helper functions for easier access to impact predictor functionality

def predict_mastery_time(db_manager, user_id: int, topic_name: str) -> Dict[str, Any]:
    """
    Predict the time required to master a topic
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        topic_name: The name of the topic
        
    Returns:
        Dictionary with prediction details
    """
    predictor = ImpactPredictor(db_manager)
    return predictor.predict_mastery_time(user_id, topic_name)

def assess_exam_readiness(db_manager, user_id: int, exam_name: str, 
                        topic_weights: Dict[str, float]) -> Dict[str, Any]:
    """
    Assess readiness for an exam in a specific domain
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        exam_name: The name of the exam
        topic_weights: Dictionary mapping topic names to their weights in the exam
        
    Returns:
        Dictionary with readiness assessment
    """
    predictor = ImpactPredictor(db_manager)
    return predictor.assess_exam_readiness(user_id, exam_name, topic_weights)

def update_performance(db_manager, prediction_id: int, performance_type: str,
                     score: float) -> Dict[str, Any]:
    """
    Update learning prediction based on performance
    
    Args:
        db_manager: Database manager instance
        prediction_id: The ID of the learning prediction
        performance_type: The type of performance (quiz, exercise, etc.)
        score: The performance score (0.0 to 1.0)
        
    Returns:
        Dictionary with updated prediction
    """
    predictor = ImpactPredictor(db_manager)
    return predictor.update_performance(prediction_id, performance_type, score)