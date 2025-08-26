"""
Stress & Cognitive Load Monitor module for AI Note System.
Monitors cognitive fatigue and stress levels using various inputs and provides study recommendations.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import time
import statistics
import math
import re

# Setup logging
logger = logging.getLogger("ai_note_system.tracking.cognitive_load_monitor")

# Import required modules
from ..database.db_manager import DatabaseManager

class CognitiveLoadMonitor:
    """
    Monitors cognitive load and stress levels using various inputs.
    Provides recommendations for study adjustments based on cognitive state.
    """
    
    def __init__(
        self,
        user_id: str,
        db_manager: Optional[DatabaseManager] = None,
        enable_webcam: bool = False,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Cognitive Load Monitor.
        
        Args:
            user_id (str): ID of the user
            db_manager (DatabaseManager, optional): Database manager instance
            enable_webcam (bool): Whether to enable webcam-based monitoring
            data_dir (str, optional): Directory to store cognitive load data
        """
        self.user_id = user_id
        self.db_manager = db_manager
        self.enable_webcam = enable_webcam
        
        # Set data directory
        self.data_dir = data_dir or os.path.join("data", "cognitive_load")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize keyboard monitoring data
        self.keyboard_data = {
            "typing_speed": [],
            "error_rate": [],
            "pause_frequency": [],
            "timestamp": []
        }
        
        # Initialize webcam monitoring if enabled
        self.webcam_monitor = None
        if enable_webcam:
            try:
                from .webcam_expression_detector import WebcamExpressionDetector
                self.webcam_monitor = WebcamExpressionDetector()
                logger.info("Webcam expression detection enabled")
            except ImportError:
                logger.warning("Webcam expression detection module not available")
                self.enable_webcam = False
        
        logger.info(f"Initialized Cognitive Load Monitor for user {user_id}")
        
        # Initialize database tables if needed
        if self.db_manager:
            self._init_database()
    
    def _init_database(self) -> None:
        """
        Initialize database tables for cognitive load monitoring.
        """
        try:
            # Create cognitive_load_data table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cognitive_load_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                cognitive_load REAL,
                stress_level REAL,
                fatigue_level REAL,
                focus_level REAL,
                data_source TEXT,
                session_id TEXT,
                notes TEXT
            )
            ''')
            
            # Create cognitive_load_recommendations table if it doesn't exist
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cognitive_load_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                recommendation_type TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                cognitive_load REAL,
                stress_level REAL,
                applied BOOLEAN DEFAULT 0,
                feedback TEXT
            )
            ''')
            
            self.db_manager.conn.commit()
            logger.debug("Cognitive load database tables initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database tables: {e}")
    
    def start_keyboard_monitoring(self, session_id: Optional[str] = None) -> None:
        """
        Start monitoring keyboard usage patterns.
        
        Args:
            session_id (str, optional): ID for the current study session
        """
        # Reset keyboard data
        self.keyboard_data = {
            "typing_speed": [],
            "error_rate": [],
            "pause_frequency": [],
            "timestamp": []
        }
        
        self.session_id = session_id or f"session_{int(time.time())}"
        
        # Start keyboard hook (simplified implementation)
        logger.info(f"Started keyboard monitoring for session {self.session_id}")
        
        # In a real implementation, you would set up a keyboard hook
        # For example, using pynput or pyHook libraries
        # This would track keystrokes, timing, and corrections
    
    def stop_keyboard_monitoring(self) -> Dict[str, Any]:
        """
        Stop monitoring keyboard usage patterns and analyze the data.
        
        Returns:
            Dict[str, Any]: Analysis of keyboard usage patterns
        """
        logger.info(f"Stopped keyboard monitoring for session {self.session_id}")
        
        # In a real implementation, you would remove the keyboard hook here
        
        # Analyze collected data
        analysis = self._analyze_keyboard_data()
        
        # Save analysis to database
        if self.db_manager:
            self._save_cognitive_load_data(
                cognitive_load=analysis.get("cognitive_load", 0),
                stress_level=analysis.get("stress_level", 0),
                fatigue_level=analysis.get("fatigue_level", 0),
                focus_level=analysis.get("focus_level", 0),
                data_source="keyboard",
                session_id=self.session_id
            )
        
        return analysis
    
    def _analyze_keyboard_data(self) -> Dict[str, Any]:
        """
        Analyze keyboard usage patterns to estimate cognitive load.
        
        Returns:
            Dict[str, Any]: Analysis results
        """
        # In a real implementation, this would analyze actual keyboard data
        # Here we'll simulate some analysis based on typical patterns
        
        # Simulate some keyboard metrics
        # In a real implementation, these would be calculated from actual data
        avg_typing_speed = 50  # words per minute
        typing_speed_variance = 10
        avg_error_rate = 0.05  # 5% errors
        avg_pause_frequency = 2  # pauses per minute
        
        # Estimate cognitive load based on these metrics
        # Higher variance in typing speed, higher error rate, and more pauses
        # typically indicate higher cognitive load
        cognitive_load = min(10, max(1, 
            5 + 
            (typing_speed_variance / 10) + 
            (avg_error_rate * 20) + 
            (avg_pause_frequency / 2)
        ))
        
        # Estimate stress level (simplified model)
        stress_level = min(10, max(1, cognitive_load * 0.8 + 1))
        
        # Estimate fatigue level (simplified model)
        fatigue_level = min(10, max(1, cognitive_load * 0.6 + 2))
        
        # Estimate focus level (inverse of cognitive load)
        focus_level = min(10, max(1, 11 - cognitive_load))
        
        return {
            "cognitive_load": cognitive_load,
            "stress_level": stress_level,
            "fatigue_level": fatigue_level,
            "focus_level": focus_level,
            "typing_speed": avg_typing_speed,
            "typing_speed_variance": typing_speed_variance,
            "error_rate": avg_error_rate,
            "pause_frequency": avg_pause_frequency,
            "timestamp": datetime.now().isoformat()
        }
    
    def capture_webcam_expression(self) -> Dict[str, Any]:
        """
        Capture and analyze facial expressions using webcam.
        
        Returns:
            Dict[str, Any]: Analysis of facial expressions
        """
        if not self.enable_webcam or not self.webcam_monitor:
            logger.warning("Webcam monitoring is not enabled")
            return {"error": "Webcam monitoring not enabled"}
        
        try:
            # In a real implementation, this would capture and analyze a webcam frame
            # Here we'll simulate some analysis
            
            # Simulate expression analysis
            expressions = {
                "neutral": 0.6,
                "confused": 0.2,
                "focused": 0.1,
                "stressed": 0.1
            }
            
            # Estimate cognitive load based on expressions
            cognitive_load = min(10, max(1, 
                5 + 
                (expressions.get("confused", 0) * 10) + 
                (expressions.get("stressed", 0) * 8) - 
                (expressions.get("focused", 0) * 5)
            ))
            
            # Estimate stress level
            stress_level = min(10, max(1, expressions.get("stressed", 0) * 10))
            
            # Estimate fatigue level
            fatigue_level = min(10, max(1, 
                5 - (expressions.get("focused", 0) * 10) + 
                (expressions.get("neutral", 0) * 5)
            ))
            
            # Estimate focus level
            focus_level = min(10, max(1, expressions.get("focused", 0) * 10))
            
            result = {
                "expressions": expressions,
                "cognitive_load": cognitive_load,
                "stress_level": stress_level,
                "fatigue_level": fatigue_level,
                "focus_level": focus_level,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to database
            if self.db_manager:
                self._save_cognitive_load_data(
                    cognitive_load=cognitive_load,
                    stress_level=stress_level,
                    fatigue_level=fatigue_level,
                    focus_level=focus_level,
                    data_source="webcam",
                    session_id=getattr(self, "session_id", f"session_{int(time.time())}")
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error capturing webcam expression: {e}")
            return {"error": f"Error capturing webcam expression: {e}"}
    
    def record_self_report(
        self,
        cognitive_load: int,
        stress_level: int,
        fatigue_level: int,
        focus_level: int,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Record self-reported cognitive load and related metrics.
        
        Args:
            cognitive_load (int): Self-reported cognitive load (1-10)
            stress_level (int): Self-reported stress level (1-10)
            fatigue_level (int): Self-reported fatigue level (1-10)
            focus_level (int): Self-reported focus level (1-10)
            notes (str, optional): Additional notes about current state
            
        Returns:
            Dict[str, Any]: Recorded data
        """
        # Validate inputs
        cognitive_load = max(1, min(10, cognitive_load))
        stress_level = max(1, min(10, stress_level))
        fatigue_level = max(1, min(10, fatigue_level))
        focus_level = max(1, min(10, focus_level))
        
        # Create record
        record = {
            "user_id": self.user_id,
            "cognitive_load": cognitive_load,
            "stress_level": stress_level,
            "fatigue_level": fatigue_level,
            "focus_level": focus_level,
            "notes": notes,
            "timestamp": datetime.now().isoformat(),
            "data_source": "self_report",
            "session_id": getattr(self, "session_id", f"session_{int(time.time())}")
        }
        
        # Save to database
        if self.db_manager:
            self._save_cognitive_load_data(
                cognitive_load=cognitive_load,
                stress_level=stress_level,
                fatigue_level=fatigue_level,
                focus_level=focus_level,
                data_source="self_report",
                session_id=record["session_id"],
                notes=notes
            )
        else:
            # Save to file if database not available
            self._save_to_file(record)
        
        logger.info(f"Recorded self-report for user {self.user_id}")
        
        # Generate recommendations based on self-report
        recommendations = self.generate_recommendations(
            cognitive_load=cognitive_load,
            stress_level=stress_level,
            fatigue_level=fatigue_level,
            focus_level=focus_level
        )
        
        record["recommendations"] = recommendations
        
        return record
    
    def _save_cognitive_load_data(
        self,
        cognitive_load: float,
        stress_level: float,
        fatigue_level: float,
        focus_level: float,
        data_source: str,
        session_id: str,
        notes: Optional[str] = None
    ) -> int:
        """
        Save cognitive load data to database.
        
        Args:
            cognitive_load (float): Cognitive load level
            stress_level (float): Stress level
            fatigue_level (float): Fatigue level
            focus_level (float): Focus level
            data_source (str): Source of the data (keyboard, webcam, self_report)
            session_id (str): ID of the current session
            notes (str, optional): Additional notes
            
        Returns:
            int: ID of the saved record
        """
        try:
            self.db_manager.cursor.execute('''
            INSERT INTO cognitive_load_data (
                user_id, timestamp, cognitive_load, stress_level,
                fatigue_level, focus_level, data_source, session_id, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                datetime.now().isoformat(),
                cognitive_load,
                stress_level,
                fatigue_level,
                focus_level,
                data_source,
                session_id,
                notes
            ))
            
            self.db_manager.conn.commit()
            record_id = self.db_manager.cursor.lastrowid
            
            logger.debug(f"Saved cognitive load data with ID {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error saving cognitive load data: {e}")
            return -1
    
    def _save_to_file(self, data: Dict[str, Any]) -> str:
        """
        Save data to file.
        
        Args:
            data (Dict[str, Any]): Data to save
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Create filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cognitive_load_{self.user_id}_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Saved cognitive load data to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving cognitive load data to file: {e}")
            return ""
    
    def generate_recommendations(
        self,
        cognitive_load: float,
        stress_level: float,
        fatigue_level: float,
        focus_level: float
    ) -> List[Dict[str, str]]:
        """
        Generate study recommendations based on cognitive state.
        
        Args:
            cognitive_load (float): Cognitive load level
            stress_level (float): Stress level
            fatigue_level (float): Fatigue level
            focus_level (float): Focus level
            
        Returns:
            List[Dict[str, str]]: List of recommendations
        """
        recommendations = []
        
        # High cognitive load recommendations
        if cognitive_load >= 7:
            recommendations.append({
                "type": "cognitive_load",
                "recommendation": "Switch to a simpler topic or review familiar material"
            })
            recommendations.append({
                "type": "cognitive_load",
                "recommendation": "Break down complex topics into smaller, manageable chunks"
            })
        
        # High stress recommendations
        if stress_level >= 7:
            recommendations.append({
                "type": "stress",
                "recommendation": "Take a 5-minute mindfulness break to reduce stress"
            })
            recommendations.append({
                "type": "stress",
                "recommendation": "Try deep breathing exercises (4-7-8 technique)"
            })
        
        # High fatigue recommendations
        if fatigue_level >= 7:
            recommendations.append({
                "type": "fatigue",
                "recommendation": "Take a 15-20 minute power nap"
            })
            recommendations.append({
                "type": "fatigue",
                "recommendation": "Switch to a different type of activity that requires less focus"
            })
        
        # Low focus recommendations
        if focus_level <= 4:
            recommendations.append({
                "type": "focus",
                "recommendation": "Try the Pomodoro technique (25 min work, 5 min break)"
            })
            recommendations.append({
                "type": "focus",
                "recommendation": "Remove distractions from your environment"
            })
        
        # General recommendations
        if len(recommendations) == 0:
            if cognitive_load >= 5:
                recommendations.append({
                    "type": "general",
                    "recommendation": "Consider taking a short break before continuing"
                })
            else:
                recommendations.append({
                    "type": "general",
                    "recommendation": "Current cognitive state is optimal for learning"
                })
        
        # Save recommendations to database
        if self.db_manager:
            for rec in recommendations:
                self._save_recommendation(
                    recommendation_type=rec["type"],
                    recommendation=rec["recommendation"],
                    cognitive_load=cognitive_load,
                    stress_level=stress_level
                )
        
        return recommendations
    
    def _save_recommendation(
        self,
        recommendation_type: str,
        recommendation: str,
        cognitive_load: float,
        stress_level: float
    ) -> int:
        """
        Save a recommendation to the database.
        
        Args:
            recommendation_type (str): Type of recommendation
            recommendation (str): The recommendation text
            cognitive_load (float): Current cognitive load
            stress_level (float): Current stress level
            
        Returns:
            int: ID of the saved recommendation
        """
        try:
            self.db_manager.cursor.execute('''
            INSERT INTO cognitive_load_recommendations (
                user_id, timestamp, recommendation_type, recommendation,
                cognitive_load, stress_level
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                self.user_id,
                datetime.now().isoformat(),
                recommendation_type,
                recommendation,
                cognitive_load,
                stress_level
            ))
            
            self.db_manager.conn.commit()
            rec_id = self.db_manager.cursor.lastrowid
            
            logger.debug(f"Saved recommendation with ID {rec_id}")
            return rec_id
            
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            return -1
    
    def get_cognitive_load_history(
        self,
        days: int = 7,
        data_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get cognitive load history for the user.
        
        Args:
            days (int): Number of days to look back
            data_source (str, optional): Filter by data source
            
        Returns:
            List[Dict[str, Any]]: Cognitive load history
        """
        if not self.db_manager:
            logger.warning("Database manager is required to get cognitive load history")
            return []
        
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Build query
            query = '''
            SELECT * FROM cognitive_load_data 
            WHERE user_id = ? AND timestamp >= ?
            '''
            params = [self.user_id, cutoff_date]
            
            if data_source:
                query += " AND data_source = ?"
                params.append(data_source)
            
            query += " ORDER BY timestamp DESC"
            
            # Execute query
            self.db_manager.cursor.execute(query, params)
            
            # Convert rows to dictionaries
            history = []
            for row in self.db_manager.cursor.fetchall():
                history.append(dict(row))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting cognitive load history: {e}")
            return []
    
    def get_recommendations_history(
        self,
        days: int = 7,
        recommendation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations history for the user.
        
        Args:
            days (int): Number of days to look back
            recommendation_type (str, optional): Filter by recommendation type
            
        Returns:
            List[Dict[str, Any]]: Recommendations history
        """
        if not self.db_manager:
            logger.warning("Database manager is required to get recommendations history")
            return []
        
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Build query
            query = '''
            SELECT * FROM cognitive_load_recommendations 
            WHERE user_id = ? AND timestamp >= ?
            '''
            params = [self.user_id, cutoff_date]
            
            if recommendation_type:
                query += " AND recommendation_type = ?"
                params.append(recommendation_type)
            
            query += " ORDER BY timestamp DESC"
            
            # Execute query
            self.db_manager.cursor.execute(query, params)
            
            # Convert rows to dictionaries
            history = []
            for row in self.db_manager.cursor.fetchall():
                history.append(dict(row))
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting recommendations history: {e}")
            return []
    
    def analyze_cognitive_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze patterns in cognitive load data.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Get cognitive load history
        history = self.get_cognitive_load_history(days=days)
        
        if not history:
            return {
                "error": "No cognitive load data available for analysis",
                "user_id": self.user_id,
                "days_analyzed": days
            }
        
        # Extract data for analysis
        cognitive_loads = []
        stress_levels = []
        fatigue_levels = []
        focus_levels = []
        timestamps = []
        
        for entry in history:
            cognitive_loads.append(entry.get("cognitive_load", 0))
            stress_levels.append(entry.get("stress_level", 0))
            fatigue_levels.append(entry.get("fatigue_level", 0))
            focus_levels.append(entry.get("focus_level", 0))
            timestamps.append(entry.get("timestamp", ""))
        
        # Calculate statistics
        avg_cognitive_load = statistics.mean(cognitive_loads) if cognitive_loads else 0
        avg_stress_level = statistics.mean(stress_levels) if stress_levels else 0
        avg_fatigue_level = statistics.mean(fatigue_levels) if fatigue_levels else 0
        avg_focus_level = statistics.mean(focus_levels) if focus_levels else 0
        
        # Analyze time-of-day patterns
        time_patterns = self._analyze_time_patterns(history)
        
        # Analyze correlations
        correlations = {
            "stress_cognitive_load": self._calculate_correlation(stress_levels, cognitive_loads),
            "fatigue_cognitive_load": self._calculate_correlation(fatigue_levels, cognitive_loads),
            "focus_cognitive_load": self._calculate_correlation(focus_levels, cognitive_loads)
        }
        
        return {
            "user_id": self.user_id,
            "days_analyzed": days,
            "data_points": len(history),
            "averages": {
                "cognitive_load": avg_cognitive_load,
                "stress_level": avg_stress_level,
                "fatigue_level": avg_fatigue_level,
                "focus_level": avg_focus_level
            },
            "time_patterns": time_patterns,
            "correlations": correlations,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _analyze_time_patterns(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze time-of-day patterns in cognitive load data.
        
        Args:
            history (List[Dict[str, Any]]): Cognitive load history
            
        Returns:
            Dict[str, Any]: Time pattern analysis
        """
        # Group data by time of day
        morning = []  # 5:00 - 11:59
        afternoon = []  # 12:00 - 16:59
        evening = []  # 17:00 - 21:59
        night = []  # 22:00 - 4:59
        
        for entry in history:
            try:
                dt = datetime.fromisoformat(entry.get("timestamp", ""))
                hour = dt.hour
                
                if 5 <= hour < 12:
                    morning.append(entry.get("cognitive_load", 0))
                elif 12 <= hour < 17:
                    afternoon.append(entry.get("cognitive_load", 0))
                elif 17 <= hour < 22:
                    evening.append(entry.get("cognitive_load", 0))
                else:
                    night.append(entry.get("cognitive_load", 0))
                
            except (ValueError, TypeError):
                continue
        
        # Calculate averages
        avg_morning = statistics.mean(morning) if morning else 0
        avg_afternoon = statistics.mean(afternoon) if afternoon else 0
        avg_evening = statistics.mean(evening) if evening else 0
        avg_night = statistics.mean(night) if night else 0
        
        # Determine optimal time
        times = [
            ("morning", avg_morning, len(morning)),
            ("afternoon", avg_afternoon, len(afternoon)),
            ("evening", avg_evening, len(evening)),
            ("night", avg_night, len(night))
        ]
        
        # Sort by cognitive load (lower is better) and then by sample size (higher is better)
        times.sort(key=lambda x: (x[1], -x[2]))
        
        optimal_time = times[0][0] if times else "unknown"
        
        return {
            "morning": {
                "average_cognitive_load": avg_morning,
                "samples": len(morning)
            },
            "afternoon": {
                "average_cognitive_load": avg_afternoon,
                "samples": len(afternoon)
            },
            "evening": {
                "average_cognitive_load": avg_evening,
                "samples": len(evening)
            },
            "night": {
                "average_cognitive_load": avg_night,
                "samples": len(night)
            },
            "optimal_time": optimal_time
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient between two lists.
        
        Args:
            x (List[float]): First list of values
            y (List[float]): Second list of values
            
        Returns:
            float: Correlation coefficient
        """
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        
        # Calculate means
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Calculate covariance and variances
        cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        var_x = sum((val - mean_x) ** 2 for val in x)
        var_y = sum((val - mean_y) ** 2 for val in y)
        
        # Calculate correlation
        if var_x == 0 or var_y == 0:
            return 0.0
        
        return cov / (math.sqrt(var_x) * math.sqrt(var_y))


def main():
    """
    Command-line interface for the Cognitive Load Monitor.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Stress & Cognitive Load Monitor")
    parser.add_argument("--user", required=True, help="User ID")
    parser.add_argument("--action", choices=["self_report", "keyboard", "webcam", "analyze", "history"], 
                        required=True, help="Action to perform")
    parser.add_argument("--cognitive-load", type=int, help="Self-reported cognitive load (1-10)")
    parser.add_argument("--stress", type=int, help="Self-reported stress level (1-10)")
    parser.add_argument("--fatigue", type=int, help="Self-reported fatigue level (1-10)")
    parser.add_argument("--focus", type=int, help="Self-reported focus level (1-10)")
    parser.add_argument("--notes", help="Additional notes for self-report")
    parser.add_argument("--days", type=int, default=7, help="Number of days for history or analysis")
    parser.add_argument("--db-path", help="Path to the database file")
    parser.add_argument("--enable-webcam", action="store_true", help="Enable webcam monitoring")
    parser.add_argument("--data-dir", help="Directory to store data")
    
    args = parser.parse_args()
    
    # Initialize database manager if db_path is provided
    db_manager = None
    if args.db_path:
        from ..database.db_manager import DatabaseManager
        db_manager = DatabaseManager(args.db_path)
    
    # Initialize monitor
    monitor = CognitiveLoadMonitor(
        user_id=args.user,
        db_manager=db_manager,
        enable_webcam=args.enable_webcam,
        data_dir=args.data_dir
    )
    
    # Perform action
    if args.action == "self_report":
        if args.cognitive_load is None or args.stress is None or args.fatigue is None or args.focus is None:
            print("Error: cognitive-load, stress, fatigue, and focus are required for self_report action")
            return
        
        result = monitor.record_self_report(
            cognitive_load=args.cognitive_load,
            stress_level=args.stress,
            fatigue_level=args.fatigue,
            focus_level=args.focus,
            notes=args.notes
        )
        
        print("\nSelf-Report Recorded:")
        print(f"Cognitive Load: {result['cognitive_load']}/10")
        print(f"Stress Level: {result['stress_level']}/10")
        print(f"Fatigue Level: {result['fatigue_level']}/10")
        print(f"Focus Level: {result['focus_level']}/10")
        
        if "recommendations" in result and result["recommendations"]:
            print("\nRecommendations:")
            for rec in result["recommendations"]:
                print(f"- {rec['recommendation']}")
        
    elif args.action == "keyboard":
        print("Starting keyboard monitoring...")
        print("Type naturally for a few minutes, then press Ctrl+C to stop monitoring.")
        
        try:
            monitor.start_keyboard_monitoring()
            
            # In a real implementation, this would wait for user input
            # Here we'll just simulate some time passing
            time.sleep(5)
            
            result = monitor.stop_keyboard_monitoring()
            
            print("\nKeyboard Monitoring Results:")
            print(f"Cognitive Load: {result['cognitive_load']:.1f}/10")
            print(f"Stress Level: {result['stress_level']:.1f}/10")
            print(f"Fatigue Level: {result['fatigue_level']:.1f}/10")
            print(f"Focus Level: {result['focus_level']:.1f}/10")
            print(f"Typing Speed: {result['typing_speed']} WPM")
            print(f"Error Rate: {result['error_rate']:.1%}")
            
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user.")
            result = monitor.stop_keyboard_monitoring()
            
            print("\nKeyboard Monitoring Results:")
            print(f"Cognitive Load: {result['cognitive_load']:.1f}/10")
            print(f"Stress Level: {result['stress_level']:.1f}/10")
            print(f"Fatigue Level: {result['fatigue_level']:.1f}/10")
            print(f"Focus Level: {result['focus_level']:.1f}/10")
            
    elif args.action == "webcam":
        if not args.enable_webcam:
            print("Error: --enable-webcam flag is required for webcam action")
            return
        
        print("Capturing webcam expression...")
        result = monitor.capture_webcam_expression()
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print("\nWebcam Expression Analysis:")
        print(f"Cognitive Load: {result['cognitive_load']:.1f}/10")
        print(f"Stress Level: {result['stress_level']:.1f}/10")
        print(f"Fatigue Level: {result['fatigue_level']:.1f}/10")
        print(f"Focus Level: {result['focus_level']:.1f}/10")
        
        print("\nDetected Expressions:")
        for expr, value in result["expressions"].items():
            print(f"- {expr}: {value:.1%}")
        
    elif args.action == "analyze":
        print(f"Analyzing cognitive patterns over the past {args.days} days...")
        result = monitor.analyze_cognitive_patterns(days=args.days)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return
        
        print("\nCognitive Pattern Analysis:")
        print(f"Data points analyzed: {result['data_points']}")
        
        print("\nAverages:")
        avgs = result["averages"]
        print(f"- Cognitive Load: {avgs['cognitive_load']:.1f}/10")
        print(f"- Stress Level: {avgs['stress_level']:.1f}/10")
        print(f"- Fatigue Level: {avgs['fatigue_level']:.1f}/10")
        print(f"- Focus Level: {avgs['focus_level']:.1f}/10")
        
        print("\nTime Patterns:")
        time_patterns = result["time_patterns"]
        print(f"- Morning: {time_patterns['morning']['average_cognitive_load']:.1f}/10 ({time_patterns['morning']['samples']} samples)")
        print(f"- Afternoon: {time_patterns['afternoon']['average_cognitive_load']:.1f}/10 ({time_patterns['afternoon']['samples']} samples)")
        print(f"- Evening: {time_patterns['evening']['average_cognitive_load']:.1f}/10 ({time_patterns['evening']['samples']} samples)")
        print(f"- Night: {time_patterns['night']['average_cognitive_load']:.1f}/10 ({time_patterns['night']['samples']} samples)")
        print(f"- Optimal study time: {time_patterns['optimal_time']}")
        
        print("\nCorrelations:")
        corrs = result["correlations"]
        print(f"- Stress vs. Cognitive Load: {corrs['stress_cognitive_load']:.2f}")
        print(f"- Fatigue vs. Cognitive Load: {corrs['fatigue_cognitive_load']:.2f}")
        print(f"- Focus vs. Cognitive Load: {corrs['focus_cognitive_load']:.2f}")
        
    elif args.action == "history":
        print(f"Retrieving cognitive load history for the past {args.days} days...")
        history = monitor.get_cognitive_load_history(days=args.days)
        
        if not history:
            print("No history data available.")
            return
        
        print(f"\nFound {len(history)} records:")
        
        for i, entry in enumerate(history[:10], 1):  # Show only first 10 entries
            dt = datetime.fromisoformat(entry["timestamp"])
            formatted_time = dt.strftime("%Y-%m-%d %H:%M")
            
            print(f"\n{i}. {formatted_time} ({entry['data_source']})")
            print(f"   Cognitive Load: {entry['cognitive_load']:.1f}/10")
            print(f"   Stress Level: {entry['stress_level']:.1f}/10")
            print(f"   Fatigue Level: {entry['fatigue_level']:.1f}/10")
            print(f"   Focus Level: {entry['focus_level']:.1f}/10")
        
        if len(history) > 10:
            print(f"\n... and {len(history) - 10} more records.")


if __name__ == "__main__":
    main()