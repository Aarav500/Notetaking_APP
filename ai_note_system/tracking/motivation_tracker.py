"""
Emotion & Motivation Tracking Module

This module provides functionality to track learning performance versus motivation
with lightweight mood tagging and generate personalized study strategies based on
motivation cycles.

Features:
- Track motivation levels over time
- Correlate motivation with learning performance
- Generate insights based on motivation patterns
- Suggest personalized study strategies based on motivation cycles
"""

import os
import json
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import statistics
import math

# Import database module
from ..database.db_manager import DatabaseManager

# Set up logging
logger = logging.getLogger(__name__)

class MotivationTracker:
    """
    Class for tracking motivation levels and correlating with learning performance.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the MotivationTracker with a database manager.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db_manager = db_manager
        self._ensure_motivation_table()
    
    def _ensure_motivation_table(self) -> None:
        """
        Ensure the motivation_tracking table exists in the database.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS motivation_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            level INTEGER NOT NULL,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tags TEXT,
            activity_type TEXT,
            duration_minutes INTEGER,
            energy_level INTEGER,
            focus_level INTEGER,
            stress_level INTEGER,
            sleep_hours REAL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(create_table_query)
        
        # Create performance correlation table
        create_performance_table_query = """
        CREATE TABLE IF NOT EXISTS performance_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            motivation_id INTEGER,
            note_id INTEGER,
            activity_type TEXT,
            score REAL,
            duration_minutes INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (motivation_id) REFERENCES motivation_tracking(id) ON DELETE SET NULL,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(create_performance_table_query)
    
    def track_motivation(self, level: int, notes: Optional[str] = None, 
                        tags: Optional[List[str]] = None, activity_type: Optional[str] = None,
                        duration_minutes: Optional[int] = None, energy_level: Optional[int] = None,
                        focus_level: Optional[int] = None, stress_level: Optional[int] = None,
                        sleep_hours: Optional[float] = None) -> int:
        """
        Log current motivation level.
        
        Args:
            level: Motivation level (1-10)
            notes: Optional notes about current motivation
            tags: Optional tags for categorization
            activity_type: Type of activity (study, review, practice, etc.)
            duration_minutes: Duration of activity in minutes
            energy_level: Energy level (1-10)
            focus_level: Focus level (1-10)
            stress_level: Stress level (1-10)
            sleep_hours: Hours of sleep
        
        Returns:
            int: ID of the newly added motivation entry
        """
        # Validate motivation level
        if not 1 <= level <= 10:
            logger.error(f"Invalid motivation level: {level}. Must be between 1 and 10.")
            raise ValueError(f"Invalid motivation level: {level}. Must be between 1 and 10.")
        
        # Prepare data
        tags_str = ','.join(tags) if tags else None
        
        # Build the query
        query = """
        INSERT INTO motivation_tracking 
        (level, notes, tags, activity_type, duration_minutes, energy_level, focus_level, stress_level, sleep_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (level, notes, tags_str, activity_type, duration_minutes, 
                 energy_level, focus_level, stress_level, sleep_hours)
        
        # Execute the query
        cursor = self.db_manager.execute_query(query, values)
        motivation_id = cursor.lastrowid
        
        logger.info(f"Tracked motivation level {level} with ID {motivation_id}")
        return motivation_id
    
    def track_performance(self, activity_type: str, score: float, 
                         duration_minutes: Optional[int] = None, 
                         note_id: Optional[int] = None,
                         motivation_id: Optional[int] = None) -> int:
        """
        Track learning performance.
        
        Args:
            activity_type: Type of activity (quiz, review, practice, etc.)
            score: Performance score (0-100)
            duration_minutes: Duration of activity in minutes
            note_id: Optional ID of the related note
            motivation_id: Optional ID of the related motivation entry
        
        Returns:
            int: ID of the newly added performance entry
        """
        # Validate score
        if not 0 <= score <= 100:
            logger.error(f"Invalid score: {score}. Must be between 0 and 100.")
            raise ValueError(f"Invalid score: {score}. Must be between 0 and 100.")
        
        # Build the query
        query = """
        INSERT INTO performance_tracking 
        (activity_type, score, duration_minutes, note_id, motivation_id)
        VALUES (?, ?, ?, ?, ?)
        """
        
        values = (activity_type, score, duration_minutes, note_id, motivation_id)
        
        # Execute the query
        cursor = self.db_manager.execute_query(query, values)
        performance_id = cursor.lastrowid
        
        logger.info(f"Tracked performance score {score} for {activity_type} with ID {performance_id}")
        return performance_id
    
    def get_motivation_history(self, period_days: int = 30, 
                              activity_type: Optional[str] = None,
                              tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get motivation history for a specified period.
        
        Args:
            period_days: Number of days to look back
            activity_type: Filter by activity type
            tags: Filter by tags
        
        Returns:
            List of motivation entries
        """
        # Calculate start date
        start_date = datetime.now() - timedelta(days=period_days)
        
        # Build the query
        query = """
        SELECT * FROM motivation_tracking
        WHERE timestamp >= ?
        """
        
        params = [start_date.strftime('%Y-%m-%d %H:%M:%S')]
        
        # Add activity type filter if provided
        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)
        
        # Add tags filter if provided
        if tags:
            placeholders = ','.join(['?' for _ in tags])
            query += f" AND tags IN ({placeholders})"
            params.extend(tags)
        
        # Order by timestamp
        query += " ORDER BY timestamp ASC"
        
        # Execute the query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        # Convert to list of dictionaries
        motivation_entries = []
        for row in results:
            entry = dict(row)
            
            # Parse tags
            if entry.get('tags'):
                entry['tags'] = entry['tags'].split(',')
            else:
                entry['tags'] = []
            
            motivation_entries.append(entry)
        
        return motivation_entries
    
    def get_performance_history(self, period_days: int = 30, 
                               activity_type: Optional[str] = None,
                               note_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get performance history for a specified period.
        
        Args:
            period_days: Number of days to look back
            activity_type: Filter by activity type
            note_id: Filter by note ID
        
        Returns:
            List of performance entries
        """
        # Calculate start date
        start_date = datetime.now() - timedelta(days=period_days)
        
        # Build the query
        query = """
        SELECT * FROM performance_tracking
        WHERE timestamp >= ?
        """
        
        params = [start_date.strftime('%Y-%m-%d %H:%M:%S')]
        
        # Add activity type filter if provided
        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)
        
        # Add note ID filter if provided
        if note_id:
            query += " AND note_id = ?"
            params.append(note_id)
        
        # Order by timestamp
        query += " ORDER BY timestamp ASC"
        
        # Execute the query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        # Convert to list of dictionaries
        performance_entries = []
        for row in results:
            entry = dict(row)
            performance_entries.append(entry)
        
        return performance_entries
    
    def correlate_motivation_performance(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Correlate motivation levels with performance scores.
        
        Args:
            period_days: Number of days to look back
        
        Returns:
            Dictionary with correlation statistics
        """
        # Get motivation and performance data
        motivation_data = self.get_motivation_history(period_days)
        performance_data = self.get_performance_history(period_days)
        
        # Group performance data by day
        performance_by_day = {}
        for entry in performance_data:
            timestamp = entry['timestamp']
            day = timestamp.split(' ')[0]  # Extract date part
            
            if day not in performance_by_day:
                performance_by_day[day] = []
            
            performance_by_day[day].append(entry['score'])
        
        # Group motivation data by day
        motivation_by_day = {}
        for entry in motivation_data:
            timestamp = entry['timestamp']
            day = timestamp.split(' ')[0]  # Extract date part
            
            if day not in motivation_by_day:
                motivation_by_day[day] = []
            
            motivation_by_day[day].append(entry['level'])
        
        # Calculate average motivation and performance for each day
        daily_averages = []
        for day in set(list(motivation_by_day.keys()) + list(performance_by_day.keys())):
            if day in motivation_by_day and day in performance_by_day:
                avg_motivation = sum(motivation_by_day[day]) / len(motivation_by_day[day])
                avg_performance = sum(performance_by_day[day]) / len(performance_by_day[day])
                
                daily_averages.append({
                    'day': day,
                    'motivation': avg_motivation,
                    'performance': avg_performance
                })
        
        # Calculate correlation
        if len(daily_averages) < 2:
            return {
                'correlation': None,
                'daily_averages': daily_averages,
                'message': "Not enough data to calculate correlation"
            }
        
        # Extract motivation and performance values
        motivation_values = [entry['motivation'] for entry in daily_averages]
        performance_values = [entry['performance'] for entry in daily_averages]
        
        # Calculate Pearson correlation coefficient
        correlation = self._calculate_correlation(motivation_values, performance_values)
        
        # Calculate additional statistics
        stats = {
            'correlation': correlation,
            'daily_averages': daily_averages,
            'motivation_stats': {
                'mean': statistics.mean(motivation_values) if motivation_values else None,
                'median': statistics.median(motivation_values) if motivation_values else None,
                'min': min(motivation_values) if motivation_values else None,
                'max': max(motivation_values) if motivation_values else None
            },
            'performance_stats': {
                'mean': statistics.mean(performance_values) if performance_values else None,
                'median': statistics.median(performance_values) if performance_values else None,
                'min': min(performance_values) if performance_values else None,
                'max': max(performance_values) if performance_values else None
            }
        }
        
        return stats
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient between two lists.
        
        Args:
            x: First list of values
            y: Second list of values
        
        Returns:
            float: Correlation coefficient
        """
        n = len(x)
        
        # Calculate means
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Calculate covariance and standard deviations
        covariance = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        std_dev_x = math.sqrt(sum((val - mean_x) ** 2 for val in x))
        std_dev_y = math.sqrt(sum((val - mean_y) ** 2 for val in y))
        
        # Calculate correlation coefficient
        if std_dev_x == 0 or std_dev_y == 0:
            return 0  # No correlation if there's no variation
        
        correlation = covariance / (std_dev_x * std_dev_y)
        return correlation
    
    def generate_motivation_insights(self) -> Dict[str, Any]:
        """
        Generate insights based on motivation patterns.
        
        Returns:
            Dictionary with motivation insights
        """
        # Get motivation history for the last 90 days
        motivation_data = self.get_motivation_history(period_days=90)
        
        if not motivation_data:
            return {
                'message': "Not enough data to generate insights",
                'insights': []
            }
        
        # Group motivation data by day of week
        motivation_by_day_of_week = {i: [] for i in range(7)}  # 0 = Monday, 6 = Sunday
        
        for entry in motivation_data:
            timestamp = entry['timestamp']
            date_obj = datetime.strptime(timestamp.split(' ')[0], '%Y-%m-%d')
            day_of_week = date_obj.weekday()
            
            motivation_by_day_of_week[day_of_week].append(entry['level'])
        
        # Calculate average motivation by day of week
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        avg_by_day = []
        
        for day_num, levels in motivation_by_day_of_week.items():
            if levels:
                avg_motivation = sum(levels) / len(levels)
                avg_by_day.append({
                    'day': day_names[day_num],
                    'average_motivation': avg_motivation,
                    'sample_size': len(levels)
                })
        
        # Sort by average motivation
        avg_by_day.sort(key=lambda x: x['average_motivation'], reverse=True)
        
        # Generate insights
        insights = []
        
        # Best and worst days
        if avg_by_day:
            best_day = avg_by_day[0]
            worst_day = avg_by_day[-1]
            
            insights.append({
                'type': 'best_day',
                'message': f"Your highest motivation is typically on {best_day['day']} (average: {best_day['average_motivation']:.1f}/10)"
            })
            
            insights.append({
                'type': 'worst_day',
                'message': f"Your lowest motivation is typically on {worst_day['day']} (average: {worst_day['average_motivation']:.1f}/10)"
            })
        
        # Check for weekly patterns
        if len(avg_by_day) >= 5:  # Need at least 5 days of data
            weekday_avg = sum(entry['average_motivation'] for entry in avg_by_day if entry['day'] not in ['Saturday', 'Sunday']) / 5
            weekend_avg = sum(entry['average_motivation'] for entry in avg_by_day if entry['day'] in ['Saturday', 'Sunday']) / 2
            
            if weekend_avg > weekday_avg + 1:
                insights.append({
                    'type': 'weekend_preference',
                    'message': f"You tend to be more motivated on weekends (average: {weekend_avg:.1f}/10) than weekdays (average: {weekday_avg:.1f}/10)"
                })
            elif weekday_avg > weekend_avg + 1:
                insights.append({
                    'type': 'weekday_preference',
                    'message': f"You tend to be more motivated on weekdays (average: {weekday_avg:.1f}/10) than weekends (average: {weekend_avg:.1f}/10)"
                })
        
        # Check for correlation with other factors
        if len(motivation_data) >= 10:
            # Check correlation with sleep
            sleep_data = [(entry['level'], entry['sleep_hours']) for entry in motivation_data if entry['sleep_hours'] is not None]
            
            if len(sleep_data) >= 5:
                motivation_values = [entry[0] for entry in sleep_data]
                sleep_values = [entry[1] for entry in sleep_data]
                
                sleep_correlation = self._calculate_correlation(motivation_values, sleep_values)
                
                if sleep_correlation > 0.3:
                    insights.append({
                        'type': 'sleep_correlation',
                        'message': f"There's a positive correlation between your sleep and motivation (correlation: {sleep_correlation:.2f})"
                    })
                elif sleep_correlation < -0.3:
                    insights.append({
                        'type': 'sleep_correlation',
                        'message': f"There's a negative correlation between your sleep and motivation (correlation: {sleep_correlation:.2f})"
                    })
            
            # Check correlation with stress
            stress_data = [(entry['level'], entry['stress_level']) for entry in motivation_data if entry['stress_level'] is not None]
            
            if len(stress_data) >= 5:
                motivation_values = [entry[0] for entry in stress_data]
                stress_values = [entry[1] for entry in stress_data]
                
                stress_correlation = self._calculate_correlation(motivation_values, stress_values)
                
                if stress_correlation < -0.3:
                    insights.append({
                        'type': 'stress_correlation',
                        'message': f"Lower stress levels correlate with higher motivation (correlation: {stress_correlation:.2f})"
                    })
                elif stress_correlation > 0.3:
                    insights.append({
                        'type': 'stress_correlation',
                        'message': f"Interestingly, higher stress levels correlate with higher motivation for you (correlation: {stress_correlation:.2f})"
                    })
        
        # Check for motivation trends
        if len(motivation_data) >= 14:  # At least 2 weeks of data
            # Sort by timestamp
            sorted_data = sorted(motivation_data, key=lambda x: x['timestamp'])
            
            # Calculate 7-day moving average
            moving_avgs = []
            for i in range(len(sorted_data) - 6):
                window = sorted_data[i:i+7]
                avg = sum(entry['level'] for entry in window) / 7
                moving_avgs.append((window[-1]['timestamp'], avg))
            
            if len(moving_avgs) >= 2:
                first_avg = moving_avgs[0][1]
                last_avg = moving_avgs[-1][1]
                
                if last_avg > first_avg + 1:
                    insights.append({
                        'type': 'motivation_trend',
                        'message': f"Your motivation has been trending upward over the past {len(motivation_data)} days"
                    })
                elif first_avg > last_avg + 1:
                    insights.append({
                        'type': 'motivation_trend',
                        'message': f"Your motivation has been trending downward over the past {len(motivation_data)} days"
                    })
        
        return {
            'day_of_week_analysis': avg_by_day,
            'insights': insights
        }
    
    def generate_study_strategy(self) -> Dict[str, Any]:
        """
        Generate personalized study strategy based on motivation patterns.
        
        Returns:
            Dictionary with study strategy recommendations
        """
        # Get motivation insights
        insights = self.generate_motivation_insights()
        
        # Get correlation data
        correlation_data = self.correlate_motivation_performance(period_days=90)
        
        # Generate strategy recommendations
        strategies = []
        
        # Check if we have enough data
        if not insights.get('insights'):
            return {
                'message': "Not enough data to generate personalized study strategies",
                'strategies': [
                    "Track your motivation daily to receive personalized recommendations",
                    "Include details like sleep hours, stress levels, and activity types for better insights"
                ]
            }
        
        # Extract best day of week
        best_day = None
        for insight in insights['insights']:
            if insight['type'] == 'best_day':
                best_day = insight['message'].split(' ')[5]  # Extract day name
                break
        
        if best_day:
            strategies.append({
                'type': 'scheduling',
                'message': f"Schedule challenging or important study sessions on {best_day}s when your motivation is typically highest"
            })
        
        # Extract worst day of week
        worst_day = None
        for insight in insights['insights']:
            if insight['type'] == 'worst_day':
                worst_day = insight['message'].split(' ')[5]  # Extract day name
                break
        
        if worst_day:
            strategies.append({
                'type': 'scheduling',
                'message': f"On {worst_day}s, focus on easier or more enjoyable topics, or use external motivators like study groups"
            })
        
        # Check for weekend/weekday preference
        weekend_preference = False
        weekday_preference = False
        
        for insight in insights['insights']:
            if insight['type'] == 'weekend_preference':
                weekend_preference = True
            elif insight['type'] == 'weekday_preference':
                weekday_preference = True
        
        if weekend_preference:
            strategies.append({
                'type': 'scheduling',
                'message': "Reserve weekends for deep work on complex topics that require sustained focus"
            })
        elif weekday_preference:
            strategies.append({
                'type': 'scheduling',
                'message': "Use weekends for lighter review sessions or catching up, saving intensive study for weekdays"
            })
        
        # Check for sleep correlation
        for insight in insights['insights']:
            if insight['type'] == 'sleep_correlation' and 'positive correlation' in insight['message']:
                strategies.append({
                    'type': 'lifestyle',
                    'message': "Prioritize sleep quality to maximize your motivation and learning effectiveness"
                })
        
        # Check for stress correlation
        for insight in insights['insights']:
            if insight['type'] == 'stress_correlation' and 'Lower stress levels' in insight['message']:
                strategies.append({
                    'type': 'lifestyle',
                    'message': "Incorporate stress-reduction techniques like meditation or exercise before study sessions"
                })
        
        # Check motivation-performance correlation
        if correlation_data.get('correlation') is not None:
            correlation = correlation_data['correlation']
            
            if correlation > 0.5:
                strategies.append({
                    'type': 'performance',
                    'message': "Your performance strongly correlates with motivation. Consider using motivation-boosting techniques before important learning sessions."
                })
            elif correlation < 0.2:
                strategies.append({
                    'type': 'performance',
                    'message': "Your performance doesn't strongly depend on motivation. Focus on consistent study habits rather than waiting for motivation."
                })
        
        # Add general strategies based on available data
        motivation_stats = correlation_data.get('motivation_stats', {})
        
        if motivation_stats.get('mean') is not None and motivation_stats['mean'] < 5:
            strategies.append({
                'type': 'general',
                'message': "Your average motivation is relatively low. Consider setting smaller, achievable goals to build momentum."
            })
        
        if motivation_stats.get('max') is not None and motivation_stats.get('min') is not None:
            motivation_range = motivation_stats['max'] - motivation_stats['min']
            
            if motivation_range > 5:
                strategies.append({
                    'type': 'general',
                    'message': "Your motivation varies significantly. Create different study plans for high and low motivation days."
                })
            elif motivation_range < 3:
                strategies.append({
                    'type': 'general',
                    'message': "Your motivation is relatively stable. Focus on consistent daily routines rather than motivation-dependent strategies."
                })
        
        return {
            'insights': insights.get('insights', []),
            'strategies': strategies
        }


def track_motivation(db_manager: DatabaseManager, level: int, notes: Optional[str] = None, 
                    tags: Optional[List[str]] = None, activity_type: Optional[str] = None,
                    duration_minutes: Optional[int] = None, energy_level: Optional[int] = None,
                    focus_level: Optional[int] = None, stress_level: Optional[int] = None,
                    sleep_hours: Optional[float] = None) -> int:
    """
    Log current motivation level.
    
    Args:
        db_manager: DatabaseManager instance
        level: Motivation level (1-10)
        notes: Optional notes about current motivation
        tags: Optional tags for categorization
        activity_type: Type of activity (study, review, practice, etc.)
        duration_minutes: Duration of activity in minutes
        energy_level: Energy level (1-10)
        focus_level: Focus level (1-10)
        stress_level: Stress level (1-10)
        sleep_hours: Hours of sleep
    
    Returns:
        int: ID of the newly added motivation entry
    """
    tracker = MotivationTracker(db_manager)
    return tracker.track_motivation(
        level=level,
        notes=notes,
        tags=tags,
        activity_type=activity_type,
        duration_minutes=duration_minutes,
        energy_level=energy_level,
        focus_level=focus_level,
        stress_level=stress_level,
        sleep_hours=sleep_hours
    )


def track_performance(db_manager: DatabaseManager, activity_type: str, score: float, 
                     duration_minutes: Optional[int] = None, 
                     note_id: Optional[int] = None,
                     motivation_id: Optional[int] = None) -> int:
    """
    Track learning performance.
    
    Args:
        db_manager: DatabaseManager instance
        activity_type: Type of activity (quiz, review, practice, etc.)
        score: Performance score (0-100)
        duration_minutes: Duration of activity in minutes
        note_id: Optional ID of the related note
        motivation_id: Optional ID of the related motivation entry
    
    Returns:
        int: ID of the newly added performance entry
    """
    tracker = MotivationTracker(db_manager)
    return tracker.track_performance(
        activity_type=activity_type,
        score=score,
        duration_minutes=duration_minutes,
        note_id=note_id,
        motivation_id=motivation_id
    )


def get_motivation_history(db_manager: DatabaseManager, period_days: int = 30, 
                          activity_type: Optional[str] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Get motivation history for a specified period.
    
    Args:
        db_manager: DatabaseManager instance
        period_days: Number of days to look back
        activity_type: Filter by activity type
        tags: Filter by tags
    
    Returns:
        List of motivation entries
    """
    tracker = MotivationTracker(db_manager)
    return tracker.get_motivation_history(
        period_days=period_days,
        activity_type=activity_type,
        tags=tags
    )


def correlate_motivation_performance(db_manager: DatabaseManager, period_days: int = 30) -> Dict[str, Any]:
    """
    Correlate motivation levels with performance scores.
    
    Args:
        db_manager: DatabaseManager instance
        period_days: Number of days to look back
    
    Returns:
        Dictionary with correlation statistics
    """
    tracker = MotivationTracker(db_manager)
    return tracker.correlate_motivation_performance(period_days=period_days)


def generate_motivation_insights(db_manager: DatabaseManager) -> Dict[str, Any]:
    """
    Generate insights based on motivation patterns.
    
    Args:
        db_manager: DatabaseManager instance
    
    Returns:
        Dictionary with motivation insights
    """
    tracker = MotivationTracker(db_manager)
    return tracker.generate_motivation_insights()


def generate_study_strategy(db_manager: DatabaseManager) -> Dict[str, Any]:
    """
    Generate personalized study strategy based on motivation patterns.
    
    Args:
        db_manager: DatabaseManager instance
    
    Returns:
        Dictionary with study strategy recommendations
    """
    tracker = MotivationTracker(db_manager)
    return tracker.generate_study_strategy()