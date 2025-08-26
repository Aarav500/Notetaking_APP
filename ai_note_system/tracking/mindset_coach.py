"""
AI-Powered Mindset & Habits Coach

This module provides functionality for tracking and improving learning habits,
including consistency streaks, focus session quality, and energy/mood patterns.
It integrates with the existing study tracker, accountability agent, and goal roadmap
to provide personalized habit suggestions and adjustments to learning plans.
"""

import os
import logging
import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import time
import threading
import random
from enum import Enum
from dataclasses import dataclass, asdict, field

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface
from ..learning.goal_roadmap import GoalRoadmapGenerator
from .study_tracker import StudyTracker, SessionType, SessionStatus, StudySession
from ..agents.accountability_agent import AccountabilityAgent

# Set up logging
logger = logging.getLogger(__name__)

class MoodLevel(Enum):
    """Enum for mood levels"""
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    HIGH = 4
    VERY_HIGH = 5

@dataclass
class MoodEntry:
    """Class for tracking mood entries"""
    id: Optional[int] = None
    user_id: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    energy_level: MoodLevel = MoodLevel.NEUTRAL
    motivation_level: MoodLevel = MoodLevel.NEUTRAL
    focus_level: MoodLevel = MoodLevel.NEUTRAL
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = data['timestamp'].isoformat()
        data['energy_level'] = data['energy_level'].value
        data['motivation_level'] = data['motivation_level'].value
        data['focus_level'] = data['focus_level'].value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoodEntry':
        """Create from dictionary"""
        if isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['energy_level'] = MoodLevel(data['energy_level'])
        data['motivation_level'] = MoodLevel(data['motivation_level'])
        data['focus_level'] = MoodLevel(data['focus_level'])
        return cls(**data)

class MindsetCoach:
    """
    AI-Powered Mindset & Habits Coach
    
    Tracks:
    - Daily consistency streaks
    - Focus session quality
    - Energy & mood patterns
    
    Uses GPT agents to:
    - Suggest habit tweaks
    - Provide encouragement nudges
    - Auto-schedule breaks based on cognitive load
    
    Integrates with goal roadmap to adjust plans based on consistency realities.
    """
    
    def __init__(self, db_manager: DatabaseManager, llm_interface: Optional[LLMInterface] = None):
        """Initialize the mindset coach"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        self.study_tracker = StudyTracker(db_manager.db_path)
        self.accountability_agent = AccountabilityAgent(db_manager)
        self.goal_roadmap = GoalRoadmapGenerator()
        
        # Ensure database tables exist
        self._ensure_tables()
        
        # Initialize scheduler for periodic checks
        self.scheduler_thread = None
        self.scheduler_running = False
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create mood tracking table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            energy_level INTEGER NOT NULL,
            motivation_level INTEGER NOT NULL,
            focus_level INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create consistency streaks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS consistency_streaks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            streak_type TEXT NOT NULL,
            current_streak INTEGER NOT NULL DEFAULT 0,
            longest_streak INTEGER NOT NULL DEFAULT 0,
            last_activity_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create focus session quality table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS focus_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            session_id INTEGER NOT NULL,
            quality_score REAL NOT NULL,
            distractions_count INTEGER NOT NULL DEFAULT 0,
            posture_changes INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (session_id) REFERENCES study_sessions(id)
        )
        ''')
        
        # Create habit suggestions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_suggestions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            suggestion TEXT NOT NULL,
            context TEXT,
            created_at TEXT NOT NULL,
            implemented BOOLEAN NOT NULL DEFAULT 0,
            effectiveness_rating INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    
    def log_mood(self, user_id: int, energy_level: MoodLevel, motivation_level: MoodLevel, 
                focus_level: MoodLevel, notes: str = "") -> int:
        """
        Log the user's current mood and energy levels
        
        Args:
            user_id: The ID of the user
            energy_level: The user's energy level
            motivation_level: The user's motivation level
            focus_level: The user's focus level
            notes: Optional notes about the mood entry
            
        Returns:
            The ID of the created mood entry
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO mood_entries (user_id, timestamp, energy_level, motivation_level, focus_level, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, timestamp, energy_level.value, motivation_level.value, focus_level.value, notes))
        
        entry_id = cursor.lastrowid
        conn.commit()
        
        # After logging mood, check if we should generate habit suggestions
        self._check_for_habit_suggestions(user_id)
        
        return entry_id
    
    def get_mood_entries(self, user_id: int, limit: int = 10, 
                        start_date: Optional[datetime] = None, 
                        end_date: Optional[datetime] = None) -> List[MoodEntry]:
        """
        Get the user's mood entries
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of entries to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            List of mood entries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM mood_entries WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        entries = []
        for row in rows:
            entry = {
                'id': row[0],
                'user_id': row[1],
                'timestamp': datetime.fromisoformat(row[2]),
                'energy_level': row[3],
                'motivation_level': row[4],
                'focus_level': row[5],
                'notes': row[6]
            }
            entries.append(MoodEntry.from_dict(entry))
        
        return entries
    
    def update_consistency_streak(self, user_id: int, streak_type: str) -> Tuple[int, int]:
        """
        Update the user's consistency streak for a specific activity type
        
        Args:
            user_id: The ID of the user
            streak_type: The type of streak (e.g., 'daily_study', 'note_taking')
            
        Returns:
            Tuple of (current_streak, longest_streak)
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get current streak info
        cursor.execute('''
        SELECT current_streak, longest_streak, last_activity_date 
        FROM consistency_streaks 
        WHERE user_id = ? AND streak_type = ?
        ''', (user_id, streak_type))
        
        row = cursor.fetchone()
        today = datetime.now().date()
        
        if row:
            current_streak, longest_streak, last_activity_date = row
            last_date = datetime.fromisoformat(last_activity_date).date()
            
            # Check if this is a consecutive day
            date_diff = (today - last_date).days
            
            if date_diff == 1:
                # Consecutive day, increment streak
                current_streak += 1
                if current_streak > longest_streak:
                    longest_streak = current_streak
            elif date_diff == 0:
                # Same day, no change to streak
                pass
            else:
                # Streak broken
                current_streak = 1
            
            cursor.execute('''
            UPDATE consistency_streaks
            SET current_streak = ?, longest_streak = ?, last_activity_date = ?
            WHERE user_id = ? AND streak_type = ?
            ''', (current_streak, longest_streak, today.isoformat(), user_id, streak_type))
        else:
            # First time tracking this streak type
            current_streak = 1
            longest_streak = 1
            
            cursor.execute('''
            INSERT INTO consistency_streaks (user_id, streak_type, current_streak, longest_streak, last_activity_date)
            VALUES (?, ?, ?, ?, ?)
            ''', (user_id, streak_type, current_streak, longest_streak, today.isoformat()))
        
        conn.commit()
        return (current_streak, longest_streak)
    
    def get_consistency_streaks(self, user_id: int) -> Dict[str, Dict[str, int]]:
        """
        Get all consistency streaks for a user
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary of streak types with current and longest streak values
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT streak_type, current_streak, longest_streak, last_activity_date
        FROM consistency_streaks
        WHERE user_id = ?
        ''', (user_id,))
        
        streaks = {}
        for row in cursor.fetchall():
            streak_type, current_streak, longest_streak, last_activity_date = row
            streaks[streak_type] = {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'last_activity_date': last_activity_date
            }
        
        return streaks
    
    def record_focus_session_quality(self, user_id: int, session_id: int, 
                                    quality_score: float, distractions_count: int = 0,
                                    posture_changes: int = 0) -> int:
        """
        Record the quality metrics for a focus session
        
        Args:
            user_id: The ID of the user
            session_id: The ID of the study session
            quality_score: Score from 0.0 to 1.0 indicating session quality
            distractions_count: Number of distractions detected
            posture_changes: Number of posture changes detected
            
        Returns:
            The ID of the created focus session record
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO focus_sessions 
        (user_id, session_id, quality_score, distractions_count, posture_changes, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, quality_score, distractions_count, posture_changes, timestamp))
        
        focus_id = cursor.lastrowid
        conn.commit()
        
        return focus_id
    
    def get_focus_session_stats(self, user_id: int, 
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get statistics about focus sessions
        
        Args:
            user_id: The ID of the user
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            
        Returns:
            Dictionary with focus session statistics
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT 
            AVG(quality_score) as avg_quality,
            AVG(distractions_count) as avg_distractions,
            AVG(posture_changes) as avg_posture_changes,
            COUNT(*) as total_sessions
        FROM focus_sessions
        WHERE user_id = ?
        '''
        
        params = [user_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        if row:
            return {
                'average_quality_score': row[0] or 0,
                'average_distractions': row[1] or 0,
                'average_posture_changes': row[2] or 0,
                'total_sessions': row[3] or 0
            }
        else:
            return {
                'average_quality_score': 0,
                'average_distractions': 0,
                'average_posture_changes': 0,
                'total_sessions': 0
            }
    
    def generate_habit_suggestion(self, user_id: int, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a personalized habit suggestion using LLM
        
        Args:
            user_id: The ID of the user
            context: Optional context for the suggestion
            
        Returns:
            Dictionary with the generated suggestion
        """
        # Get user's recent mood entries
        mood_entries = self.get_mood_entries(user_id, limit=5)
        
        # Get user's consistency streaks
        streaks = self.get_consistency_streaks(user_id)
        
        # Get focus session stats
        focus_stats = self.get_focus_session_stats(user_id, 
                                                 start_date=datetime.now() - timedelta(days=14))
        
        # Get recent study sessions
        recent_sessions = self.study_tracker.get_sessions(limit=5, 
                                                        start_date=datetime.now() - timedelta(days=14))
        
        # Prepare prompt for LLM
        prompt = f"""
        As an AI-powered mindset and habits coach, generate a personalized habit suggestion for a student.
        
        Recent mood patterns:
        {self._format_mood_entries(mood_entries)}
        
        Consistency streaks:
        {self._format_streaks(streaks)}
        
        Focus session statistics:
        {self._format_focus_stats(focus_stats)}
        
        Recent study sessions:
        {self._format_study_sessions(recent_sessions)}
        
        Additional context:
        {context or "No additional context provided."}
        
        Based on this information, suggest ONE specific habit tweak or improvement that would be most impactful.
        Your suggestion should be concrete, actionable, and tailored to the user's specific patterns.
        Include a brief explanation of why this suggestion would be helpful.
        
        Format your response as:
        SUGGESTION: [Your specific, actionable habit suggestion]
        EXPLANATION: [Brief explanation of why this would be helpful]
        """
        
        # Generate suggestion using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=300)
        
        # Parse response
        suggestion_text = ""
        explanation_text = ""
        
        for line in response.split('\n'):
            if line.startswith('SUGGESTION:'):
                suggestion_text = line.replace('SUGGESTION:', '').strip()
            elif line.startswith('EXPLANATION:'):
                explanation_text = line.replace('EXPLANATION:', '').strip()
        
        # Store suggestion in database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO habit_suggestions (user_id, suggestion, context, created_at, implemented)
        VALUES (?, ?, ?, ?, 0)
        ''', (user_id, suggestion_text, explanation_text, created_at))
        
        suggestion_id = cursor.lastrowid
        conn.commit()
        
        return {
            'id': suggestion_id,
            'suggestion': suggestion_text,
            'explanation': explanation_text,
            'created_at': created_at
        }
    
    def get_habit_suggestions(self, user_id: int, limit: int = 10, 
                             implemented_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get habit suggestions for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of suggestions to return
            implemented_only: If True, only return implemented suggestions
            
        Returns:
            List of habit suggestions
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT id, suggestion, context, created_at, implemented, effectiveness_rating FROM habit_suggestions WHERE user_id = ?"
        params = [user_id]
        
        if implemented_only:
            query += " AND implemented = 1"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        suggestions = []
        for row in rows:
            suggestion = {
                'id': row[0],
                'suggestion': row[1],
                'explanation': row[2],
                'created_at': row[3],
                'implemented': bool(row[4]),
                'effectiveness_rating': row[5]
            }
            suggestions.append(suggestion)
        
        return suggestions
    
    def mark_suggestion_implemented(self, suggestion_id: int, implemented: bool = True) -> None:
        """
        Mark a habit suggestion as implemented
        
        Args:
            suggestion_id: The ID of the suggestion
            implemented: Whether the suggestion is implemented
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE habit_suggestions
        SET implemented = ?
        WHERE id = ?
        ''', (1 if implemented else 0, suggestion_id))
        
        conn.commit()
    
    def rate_suggestion_effectiveness(self, suggestion_id: int, rating: int) -> None:
        """
        Rate the effectiveness of a habit suggestion
        
        Args:
            suggestion_id: The ID of the suggestion
            rating: Rating from 1 to 5
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE habit_suggestions
        SET effectiveness_rating = ?
        WHERE id = ?
        ''', (rating, suggestion_id))
        
        conn.commit()
    
    def adjust_roadmap_based_on_consistency(self, user_id: int, roadmap_id: str) -> Dict[str, Any]:
        """
        Adjust a goal roadmap based on the user's consistency patterns
        
        Args:
            user_id: The ID of the user
            roadmap_id: The ID of the roadmap to adjust
            
        Returns:
            The adjusted roadmap
        """
        # Load the existing roadmap
        # This would typically be stored in a database or file
        # For now, we'll assume it's stored in a file
        roadmap_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'roadmaps', f'{roadmap_id}.json')
        
        try:
            with open(roadmap_path, 'r') as f:
                roadmap = json.load(f)
        except FileNotFoundError:
            logger.error(f"Roadmap {roadmap_id} not found")
            return {}
        
        # Get user's consistency streaks
        streaks = self.get_consistency_streaks(user_id)
        
        # Get focus session stats
        focus_stats = self.get_focus_session_stats(user_id, 
                                                 start_date=datetime.now() - timedelta(days=30))
        
        # Get mood patterns
        mood_entries = self.get_mood_entries(user_id, limit=10)
        
        # Analyze patterns to determine adjustment factors
        adjustment_factors = self._calculate_adjustment_factors(streaks, focus_stats, mood_entries)
        
        # Adjust the roadmap
        adjusted_roadmap = self._apply_adjustments_to_roadmap(roadmap, adjustment_factors)
        
        # Save the adjusted roadmap
        adjusted_roadmap_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'roadmaps', f'{roadmap_id}_adjusted.json')
        
        os.makedirs(os.path.dirname(adjusted_roadmap_path), exist_ok=True)
        
        with open(adjusted_roadmap_path, 'w') as f:
            json.dump(adjusted_roadmap, f, indent=2)
        
        return adjusted_roadmap
    
    def _calculate_adjustment_factors(self, streaks: Dict[str, Dict[str, int]], 
                                     focus_stats: Dict[str, Any],
                                     mood_entries: List[MoodEntry]) -> Dict[str, float]:
        """
        Calculate adjustment factors based on user patterns
        
        Args:
            streaks: User's consistency streaks
            focus_stats: Focus session statistics
            mood_entries: Recent mood entries
            
        Returns:
            Dictionary of adjustment factors
        """
        factors = {
            'time_adjustment': 1.0,  # Multiplier for time estimates
            'difficulty_adjustment': 1.0,  # Multiplier for difficulty estimates
            'break_frequency': 1.0,  # Multiplier for break frequency
            'session_length': 1.0,  # Multiplier for recommended session length
        }
        
        # Adjust based on consistency streaks
        daily_study_streak = streaks.get('daily_study', {}).get('current_streak', 0)
        if daily_study_streak < 3:
            # Less consistent users need more buffer time
            factors['time_adjustment'] *= 1.2
        elif daily_study_streak > 7:
            # More consistent users might need less buffer time
            factors['time_adjustment'] *= 0.9
        
        # Adjust based on focus quality
        avg_quality = focus_stats.get('average_quality_score', 0)
        if avg_quality < 0.5:
            # Users with poor focus quality need shorter sessions
            factors['session_length'] *= 0.8
            factors['break_frequency'] *= 1.3
        elif avg_quality > 0.8:
            # Users with good focus quality can handle longer sessions
            factors['session_length'] *= 1.2
            factors['break_frequency'] *= 0.8
        
        # Adjust based on mood patterns
        avg_energy = sum(entry.energy_level.value for entry in mood_entries) / len(mood_entries) if mood_entries else 3
        if avg_energy < 2.5:
            # Users with low energy need more breaks and easier tasks
            factors['break_frequency'] *= 1.2
            factors['difficulty_adjustment'] *= 0.9
        
        return factors
    
    def _apply_adjustments_to_roadmap(self, roadmap: Dict[str, Any], 
                                     adjustment_factors: Dict[str, float]) -> Dict[str, Any]:
        """
        Apply adjustment factors to a roadmap
        
        Args:
            roadmap: The original roadmap
            adjustment_factors: Adjustment factors to apply
            
        Returns:
            The adjusted roadmap
        """
        adjusted_roadmap = roadmap.copy()
        
        # Adjust weekly plan
        if 'weekly_plan' in adjusted_roadmap:
            for week in adjusted_roadmap['weekly_plan']:
                # Adjust estimated hours
                if 'estimated_hours' in week:
                    week['estimated_hours'] = round(week['estimated_hours'] * adjustment_factors['time_adjustment'], 1)
                
                # Adjust session recommendations
                if 'recommended_sessions' in week:
                    for session in week['recommended_sessions']:
                        if 'duration_minutes' in session:
                            session['duration_minutes'] = round(session['duration_minutes'] * adjustment_factors['session_length'])
                        
                        if 'break_interval_minutes' in session:
                            session['break_interval_minutes'] = round(session['break_interval_minutes'] * adjustment_factors['break_frequency'])
        
        # Adjust learning requirements
        if 'learning_requirements' in adjusted_roadmap:
            for req in adjusted_roadmap['learning_requirements']:
                if 'estimated_hours' in req:
                    req['estimated_hours'] = round(req['estimated_hours'] * adjustment_factors['time_adjustment'], 1)
                
                if 'difficulty' in req and isinstance(req['difficulty'], (int, float)):
                    # Adjust difficulty within bounds (1-5)
                    new_difficulty = req['difficulty'] * adjustment_factors['difficulty_adjustment']
                    req['difficulty'] = max(1, min(5, round(new_difficulty)))
        
        # Add adjustment metadata
        adjusted_roadmap['adjustment_metadata'] = {
            'original_roadmap_id': roadmap.get('id', 'unknown'),
            'adjustment_timestamp': datetime.now().isoformat(),
            'adjustment_factors': adjustment_factors,
            'adjustment_reason': "Adjusted based on user's consistency patterns, focus quality, and mood patterns."
        }
        
        return adjusted_roadmap
    
    def _check_for_habit_suggestions(self, user_id: int) -> None:
        """
        Check if we should generate habit suggestions based on recent patterns
        
        Args:
            user_id: The ID of the user
        """
        # Get the most recent suggestion
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT created_at FROM habit_suggestions
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        # If no previous suggestion or last suggestion was more than 3 days ago
        if not row or (datetime.now() - datetime.fromisoformat(row[0])).days > 3:
            # Generate a new suggestion
            self.generate_habit_suggestion(user_id)
    
    def _format_mood_entries(self, entries: List[MoodEntry]) -> str:
        """Format mood entries for LLM prompt"""
        if not entries:
            return "No recent mood entries."
        
        result = []
        for entry in entries:
            result.append(f"- {entry.timestamp.strftime('%Y-%m-%d %H:%M')}: Energy: {entry.energy_level.name}, " +
                         f"Motivation: {entry.motivation_level.name}, Focus: {entry.focus_level.name}")
            if entry.notes:
                result.append(f"  Notes: {entry.notes}")
        
        return "\n".join(result)
    
    def _format_streaks(self, streaks: Dict[str, Dict[str, int]]) -> str:
        """Format consistency streaks for LLM prompt"""
        if not streaks:
            return "No consistency streaks recorded."
        
        result = []
        for streak_type, data in streaks.items():
            result.append(f"- {streak_type}: Current streak: {data['current_streak']} days, " +
                         f"Longest streak: {data['longest_streak']} days, " +
                         f"Last activity: {data['last_activity_date']}")
        
        return "\n".join(result)
    
    def _format_focus_stats(self, stats: Dict[str, Any]) -> str:
        """Format focus session stats for LLM prompt"""
        return (f"Average quality score: {stats['average_quality_score']:.2f}/1.0\n" +
                f"Average distractions per session: {stats['average_distractions']:.1f}\n" +
                f"Average posture changes per session: {stats['average_posture_changes']:.1f}\n" +
                f"Total sessions: {stats['total_sessions']}")
    
    def _format_study_sessions(self, sessions: List[StudySession]) -> str:
        """Format study sessions for LLM prompt"""
        if not sessions:
            return "No recent study sessions."
        
        result = []
        for session in sessions:
            duration_mins = session.duration_minutes if hasattr(session, 'duration_minutes') else 0
            result.append(f"- {session.start_time.strftime('%Y-%m-%d %H:%M')}: " +
                         f"Type: {session.session_type.name if hasattr(session, 'session_type') else 'Unknown'}, " +
                         f"Duration: {duration_mins} minutes, " +
                         f"Status: {session.status.name if hasattr(session, 'status') else 'Unknown'}")
        
        return "\n".join(result)
    
    def start_scheduler(self) -> None:
        """Start the scheduler thread for periodic checks"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            return
        
        self.scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop_scheduler(self) -> None:
        """Stop the scheduler thread"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1.0)
    
    def _scheduler_loop(self) -> None:
        """Main loop for the scheduler thread"""
        while self.scheduler_running:
            try:
                # Check for users who need encouragement nudges
                self._check_for_encouragement_nudges()
                
                # Check for users who need break scheduling
                self._check_for_break_scheduling()
                
                # Sleep for a while before next check
                time.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error in mindset coach scheduler: {e}")
                time.sleep(60)  # Sleep for a minute before retrying
    
    def _check_for_encouragement_nudges(self) -> None:
        """Check if any users need encouragement nudges"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get users who haven't had activity in 2+ days but less than 7 days
        two_days_ago = (datetime.now() - timedelta(days=2)).date().isoformat()
        seven_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        
        cursor.execute('''
        SELECT DISTINCT user_id FROM consistency_streaks
        WHERE last_activity_date < ? AND last_activity_date > ?
        ''', (two_days_ago, seven_days_ago))
        
        for row in cursor.fetchall():
            user_id = row[0]
            self._send_encouragement_nudge(user_id)
    
    def _send_encouragement_nudge(self, user_id: int) -> None:
        """Send an encouragement nudge to a user"""
        # Get user's recent mood entries
        mood_entries = self.get_mood_entries(user_id, limit=3)
        
        # Get user's consistency streaks
        streaks = self.get_consistency_streaks(user_id)
        
        # Prepare prompt for LLM
        prompt = f"""
        As an AI-powered mindset coach, generate a personalized encouragement message for a student who hasn't studied in a few days.
        
        Recent mood patterns:
        {self._format_mood_entries(mood_entries)}
        
        Consistency streaks (now broken):
        {self._format_streaks(streaks)}
        
        Generate a brief, encouraging message that acknowledges the break in routine but motivates them to return to their studies.
        Be supportive, not judgmental. Keep it under 100 words.
        """
        
        # Generate message using LLM
        message = self.llm_interface.generate_text(prompt, max_tokens=150)
        
        # Send the message via the accountability agent
        # This assumes the accountability agent has a method for sending messages
        # If not, this would need to be implemented
        try:
            self.accountability_agent.send_message(user_id, message)
            logger.info(f"Sent encouragement nudge to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send encouragement nudge to user {user_id}: {e}")
    
    def _check_for_break_scheduling(self) -> None:
        """Check for active study sessions that might need break scheduling"""
        # Get active study sessions
        active_sessions = self.study_tracker.get_sessions(status=SessionStatus.ACTIVE)
        
        for session in active_sessions:
            # Check if session has been going for a while without breaks
            if hasattr(session, 'start_time'):
                session_duration = (datetime.now() - session.start_time).total_seconds() / 60
                
                # If session has been going for more than 45 minutes without a break
                if session_duration > 45:
                    user_id = session.user_id if hasattr(session, 'user_id') else 0
                    self._suggest_break(user_id, session)
    
    def _suggest_break(self, user_id: int, session: StudySession) -> None:
        """Suggest a break for a long study session"""
        # Get user's recent focus quality
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT quality_score FROM focus_sessions
        WHERE user_id = ? AND session_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        ''', (user_id, session.id if hasattr(session, 'id') else 0))
        
        row = cursor.fetchone()
        recent_quality = row[0] if row else 0.8  # Default to 0.8 if no data
        
        # Determine break duration based on focus quality
        if recent_quality < 0.5:
            break_duration = 15  # Longer break for poor focus
        elif recent_quality < 0.7:
            break_duration = 10  # Medium break for average focus
        else:
            break_duration = 5   # Short break for good focus
        
        # Suggest the break
        # This would typically send a notification to the user
        # For now, we'll just log it
        logger.info(f"Suggesting a {break_duration}-minute break for user {user_id} in session {session.id if hasattr(session, 'id') else 'unknown'}")
        
        # In a real implementation, this would trigger a notification
        # For example:
        # self.notification_manager.send_notification(
        #     user_id, 
        #     f"Time for a {break_duration}-minute break! Your focus has been {recent_quality:.0%}."
        # )

# Helper functions for easier access to mindset coach functionality

def log_mood(db_manager, user_id: int, energy_level: int, motivation_level: int, 
            focus_level: int, notes: str = "") -> int:
    """
    Log the user's current mood and energy levels
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        energy_level: The user's energy level (1-5)
        motivation_level: The user's motivation level (1-5)
        focus_level: The user's focus level (1-5)
        notes: Optional notes about the mood entry
        
    Returns:
        The ID of the created mood entry
    """
    coach = MindsetCoach(db_manager)
    return coach.log_mood(
        user_id, 
        MoodLevel(energy_level), 
        MoodLevel(motivation_level), 
        MoodLevel(focus_level), 
        notes
    )

def update_streak(db_manager, user_id: int, streak_type: str) -> Tuple[int, int]:
    """
    Update the user's consistency streak for a specific activity type
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        streak_type: The type of streak (e.g., 'daily_study', 'note_taking')
        
    Returns:
        Tuple of (current_streak, longest_streak)
    """
    coach = MindsetCoach(db_manager)
    return coach.update_consistency_streak(user_id, streak_type)

def get_habit_suggestion(db_manager, user_id: int) -> Dict[str, Any]:
    """
    Generate a personalized habit suggestion
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        
    Returns:
        Dictionary with the generated suggestion
    """
    coach = MindsetCoach(db_manager)
    return coach.generate_habit_suggestion(user_id)

def adjust_roadmap(db_manager, user_id: int, roadmap_id: str) -> Dict[str, Any]:
    """
    Adjust a goal roadmap based on the user's consistency patterns
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        roadmap_id: The ID of the roadmap to adjust
        
    Returns:
        The adjusted roadmap
    """
    coach = MindsetCoach(db_manager)
    return coach.adjust_roadmap_based_on_consistency(user_id, roadmap_id)