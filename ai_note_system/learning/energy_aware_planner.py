"""
Time & Energy-Aware Planning Engine for AI Note System.
Enhances study planning with energy and focus cycle tracking.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta, time
import math

# Setup logging
logger = logging.getLogger("ai_note_system.learning.energy_aware_planner")

# Import required modules
from ..processing.study_plan_generator import generate_study_plan

class EnergyAwarePlanner:
    """
    Enhances study planning with energy and focus cycle tracking.
    Dynamically adjusts plans based on user performance and energy levels.
    """
    
    def __init__(
        self,
        user_id: str,
        db_manager = None,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the Energy-Aware Planner.
        
        Args:
            user_id (str): ID of the user
            db_manager: Database manager instance
            data_dir (str, optional): Directory to store energy profile data
        """
        self.user_id = user_id
        self.db_manager = db_manager
        
        # Set data directory
        self.data_dir = data_dir or os.path.join("data", "energy_profiles")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load or create user energy profile
        self.energy_profile = self._load_energy_profile()
        
        logger.info(f"Initialized Energy-Aware Planner for user {user_id}")
    
    def _load_energy_profile(self) -> Dict[str, Any]:
        """
        Load the user's energy profile from storage.
        
        Returns:
            Dict[str, Any]: The user's energy profile
        """
        profile_path = os.path.join(self.data_dir, f"{self.user_id}_energy_profile.json")
        
        if os.path.exists(profile_path):
            try:
                with open(profile_path, "r") as f:
                    profile = json.load(f)
                logger.info(f"Loaded energy profile for user {self.user_id}")
                return profile
            except Exception as e:
                logger.error(f"Error loading energy profile: {e}")
        
        # Create default profile if not found
        default_profile = self._create_default_profile()
        self._save_energy_profile(default_profile)
        return default_profile
    
    def _create_default_profile(self) -> Dict[str, Any]:
        """
        Create a default energy profile for a new user.
        
        Returns:
            Dict[str, Any]: Default energy profile
        """
        # Default energy levels throughout the day (24-hour format)
        default_energy_cycle = [
            {"hour": 6, "energy": 5},   # 6 AM: Medium energy
            {"hour": 9, "energy": 8},   # 9 AM: High energy
            {"hour": 12, "energy": 6},  # 12 PM: Medium-high energy
            {"hour": 15, "energy": 4},  # 3 PM: Medium-low energy
            {"hour": 18, "energy": 6},  # 6 PM: Medium-high energy
            {"hour": 21, "energy": 3},  # 9 PM: Low energy
            {"hour": 0, "energy": 1}    # 12 AM: Very low energy
        ]
        
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "energy_cycle": default_energy_cycle,
            "focus_duration": 45,  # Default focus session duration in minutes
            "break_duration": 15,  # Default break duration in minutes
            "daily_energy_logs": [],
            "performance_data": [],
            "preferences": {
                "preferred_study_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "preferred_study_times": ["morning", "evening"],
                "task_preferences": {
                    "high_energy": ["new_concepts", "problem_solving", "active_recall"],
                    "medium_energy": ["review", "note_taking", "reading"],
                    "low_energy": ["organization", "passive_review", "planning"]
                }
            }
        }
    
    def _save_energy_profile(self, profile: Dict[str, Any]) -> None:
        """
        Save the user's energy profile to storage.
        
        Args:
            profile (Dict[str, Any]): The energy profile to save
        """
        profile_path = os.path.join(self.data_dir, f"{self.user_id}_energy_profile.json")
        
        try:
            # Update timestamp
            profile["updated_at"] = datetime.now().isoformat()
            
            # Save to file
            with open(profile_path, "w") as f:
                json.dump(profile, f, indent=2)
            
            logger.info(f"Saved energy profile for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error saving energy profile: {e}")
    
    def log_energy_level(
        self,
        energy_level: int,
        focus_level: int,
        timestamp: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log the user's current energy and focus levels.
        
        Args:
            energy_level (int): Energy level (1-10)
            focus_level (int): Focus level (1-10)
            timestamp (str, optional): Timestamp of the log (ISO format)
            notes (str, optional): Additional notes about the user's state
            
        Returns:
            Dict[str, Any]: The created log entry
        """
        # Validate levels
        energy_level = max(1, min(10, energy_level))
        focus_level = max(1, min(10, focus_level))
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp or datetime.now().isoformat(),
            "energy_level": energy_level,
            "focus_level": focus_level,
            "notes": notes
        }
        
        # Add to profile
        self.energy_profile["daily_energy_logs"].append(log_entry)
        
        # Update energy cycle based on new data
        self._update_energy_cycle()
        
        # Save profile
        self._save_energy_profile(self.energy_profile)
        
        return log_entry
    
    def _update_energy_cycle(self) -> None:
        """
        Update the user's energy cycle based on logged data.
        """
        # Get recent logs (last 30 days)
        recent_logs = []
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        for log in self.energy_profile["daily_energy_logs"]:
            if log["timestamp"] >= thirty_days_ago:
                recent_logs.append(log)
        
        # If not enough data, keep the current cycle
        if len(recent_logs) < 5:
            return
        
        # Group logs by hour and calculate average energy levels
        hour_energy = {}
        hour_focus = {}
        hour_counts = {}
        
        for log in recent_logs:
            try:
                dt = datetime.fromisoformat(log["timestamp"])
                hour = dt.hour
                
                if hour not in hour_energy:
                    hour_energy[hour] = 0
                    hour_focus[hour] = 0
                    hour_counts[hour] = 0
                
                hour_energy[hour] += log["energy_level"]
                hour_focus[hour] += log["focus_level"]
                hour_counts[hour] += 1
                
            except (ValueError, TypeError):
                continue
        
        # Calculate averages and create new energy cycle
        new_cycle = []
        for hour in sorted(hour_energy.keys()):
            if hour_counts[hour] > 0:
                avg_energy = round(hour_energy[hour] / hour_counts[hour], 1)
                avg_focus = round(hour_focus[hour] / hour_counts[hour], 1)
                
                new_cycle.append({
                    "hour": hour,
                    "energy": avg_energy,
                    "focus": avg_focus
                })
        
        # Update profile if we have enough data points
        if len(new_cycle) >= 3:
            self.energy_profile["energy_cycle"] = new_cycle
    
    def log_performance(
        self,
        activity_type: str,
        performance_score: float,
        duration_minutes: int,
        energy_level: Optional[int] = None,
        focus_level: Optional[int] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log the user's performance on a learning activity.
        
        Args:
            activity_type (str): Type of learning activity
            performance_score (float): Performance score (0-1)
            duration_minutes (int): Duration of the activity in minutes
            energy_level (int, optional): Energy level during the activity (1-10)
            focus_level (int, optional): Focus level during the activity (1-10)
            timestamp (str, optional): Timestamp of the activity (ISO format)
            metadata (Dict[str, Any], optional): Additional metadata about the activity
            
        Returns:
            Dict[str, Any]: The created performance entry
        """
        # Validate inputs
        performance_score = max(0.0, min(1.0, performance_score))
        
        if energy_level is not None:
            energy_level = max(1, min(10, energy_level))
        
        if focus_level is not None:
            focus_level = max(1, min(10, focus_level))
        
        # Create performance entry
        performance_entry = {
            "timestamp": timestamp or datetime.now().isoformat(),
            "activity_type": activity_type,
            "performance_score": performance_score,
            "duration_minutes": duration_minutes,
            "energy_level": energy_level,
            "focus_level": focus_level,
            "metadata": metadata or {}
        }
        
        # Add to profile
        self.energy_profile["performance_data"].append(performance_entry)
        
        # Save profile
        self._save_energy_profile(self.energy_profile)
        
        return performance_entry
    
    def get_optimal_study_times(
        self,
        date: Optional[str] = None,
        min_energy_level: int = 6,
        duration_hours: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Get optimal study times based on the user's energy profile.
        
        Args:
            date (str, optional): Date to get optimal times for (ISO format date)
            min_energy_level (int): Minimum energy level required (1-10)
            duration_hours (float): Desired study duration in hours
            
        Returns:
            List[Dict[str, Any]]: List of optimal study time slots
        """
        # Use today's date if not specified
        if date is None:
            date = datetime.now().date().isoformat()
        
        try:
            # Parse date
            date_obj = datetime.fromisoformat(date).date()
            
            # Get day of week
            day_of_week = date_obj.strftime("%A")
            
            # Check if this is a preferred study day
            preferred_days = self.energy_profile["preferences"]["preferred_study_days"]
            if day_of_week not in preferred_days:
                logger.info(f"{day_of_week} is not a preferred study day")
                return []
            
            # Get energy cycle
            energy_cycle = self.energy_profile["energy_cycle"]
            
            # Find time slots with sufficient energy
            optimal_slots = []
            
            for i in range(len(energy_cycle)):
                current = energy_cycle[i]
                
                # Skip if energy level is too low
                if current.get("energy", 0) < min_energy_level:
                    continue
                
                # Calculate end time based on next entry or wrap around
                next_idx = (i + 1) % len(energy_cycle)
                next_hour = energy_cycle[next_idx]["hour"]
                
                # Handle wrap around (e.g., from 23 to 0)
                if next_hour < current["hour"]:
                    next_hour += 24
                
                # Calculate available hours
                available_hours = next_hour - current["hour"]
                
                # Skip if not enough time
                if available_hours < 1:
                    continue
                
                # Calculate optimal duration (min of available and requested)
                optimal_duration = min(available_hours, duration_hours)
                
                # Create time slot
                start_hour = current["hour"]
                end_hour = start_hour + optimal_duration
                
                # Format times
                start_time = time(hour=start_hour % 24).strftime("%H:%M")
                end_time = time(hour=int(end_hour) % 24, 
                               minute=int((end_hour % 1) * 60)).strftime("%H:%M")
                
                # Create slot object
                slot = {
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration_hours": optimal_duration,
                    "energy_level": current.get("energy", 0),
                    "focus_level": current.get("focus", 0),
                    "recommended_activities": self._get_recommended_activities(current.get("energy", 0))
                }
                
                optimal_slots.append(slot)
            
            # Sort by energy level (highest first)
            optimal_slots.sort(key=lambda x: x["energy_level"], reverse=True)
            
            return optimal_slots
            
        except Exception as e:
            logger.error(f"Error getting optimal study times: {e}")
            return []
    
    def _get_recommended_activities(self, energy_level: float) -> List[str]:
        """
        Get recommended activities based on energy level.
        
        Args:
            energy_level (float): Current energy level
            
        Returns:
            List[str]: Recommended activities
        """
        preferences = self.energy_profile["preferences"]["task_preferences"]
        
        if energy_level >= 7:
            return preferences["high_energy"]
        elif energy_level >= 4:
            return preferences["medium_energy"]
        else:
            return preferences["low_energy"]
    
    def generate_energy_aware_plan(
        self,
        weeks: int = 4,
        hours_per_week: Optional[int] = None,
        focus_areas: Optional[List[str]] = None,
        min_energy_level: int = 5
    ) -> Dict[str, Any]:
        """
        Generate an energy-aware study plan.
        
        Args:
            weeks (int): Number of weeks to plan for
            hours_per_week (int, optional): Target study hours per week
            focus_areas (List[str], optional): Specific areas to focus on
            min_energy_level (int): Minimum energy level for scheduling tasks
            
        Returns:
            Dict[str, Any]: Generated study plan
        """
        logger.info(f"Generating energy-aware study plan for user {self.user_id}")
        
        # Generate base study plan
        base_plan = generate_study_plan(
            user_id=self.user_id,
            weeks=weeks,
            hours_per_week=hours_per_week,
            focus_areas=focus_areas,
            db_manager=self.db_manager
        )
        
        # Enhance with energy awareness
        energy_aware_plan = self._enhance_plan_with_energy_awareness(
            base_plan, min_energy_level
        )
        
        return energy_aware_plan
    
    def _enhance_plan_with_energy_awareness(
        self,
        base_plan: Dict[str, Any],
        min_energy_level: int
    ) -> Dict[str, Any]:
        """
        Enhance a study plan with energy awareness.
        
        Args:
            base_plan (Dict[str, Any]): Base study plan
            min_energy_level (int): Minimum energy level for scheduling tasks
            
        Returns:
            Dict[str, Any]: Enhanced study plan
        """
        # Create a copy of the base plan
        enhanced_plan = base_plan.copy()
        
        # Add energy awareness metadata
        enhanced_plan["energy_aware"] = True
        enhanced_plan["min_energy_level"] = min_energy_level
        enhanced_plan["energy_profile_summary"] = self._get_energy_profile_summary()
        
        # Enhance weekly plans
        if "weekly_plan" in enhanced_plan:
            enhanced_weekly_plan = []
            
            for week in enhanced_plan["weekly_plan"]:
                # Create a copy of the week
                enhanced_week = week.copy()
                
                # Calculate start date for this week
                week_num = week["week"]
                start_date = (datetime.now() + timedelta(days=(week_num - 1) * 7)).date()
                
                # Enhance daily plan with energy-aware scheduling
                if "daily_plan" in enhanced_week:
                    enhanced_daily_plan = []
                    
                    for day_idx, day in enumerate(enhanced_week["daily_plan"]):
                        # Create a copy of the day
                        enhanced_day = day.copy()
                        
                        # Calculate date for this day
                        day_date = (start_date + timedelta(days=day_idx)).date().isoformat()
                        
                        # Get optimal study times for this day
                        optimal_times = self.get_optimal_study_times(
                            date=day_date,
                            min_energy_level=min_energy_level
                        )
                        
                        # Add energy-aware scheduling
                        enhanced_day["date"] = day_date
                        enhanced_day["optimal_study_times"] = optimal_times
                        
                        # Assign topics to optimal times based on difficulty
                        if optimal_times and "topics" in enhanced_day:
                            enhanced_day["energy_aware_schedule"] = self._create_energy_aware_schedule(
                                day["topics"], optimal_times
                            )
                        
                        enhanced_daily_plan.append(enhanced_day)
                    
                    enhanced_week["daily_plan"] = enhanced_daily_plan
                
                enhanced_weekly_plan.append(enhanced_week)
            
            enhanced_plan["weekly_plan"] = enhanced_weekly_plan
        
        # Add adaptive recommendations based on performance
        enhanced_plan["adaptive_recommendations"] = self._generate_adaptive_recommendations()
        
        return enhanced_plan
    
    def _get_energy_profile_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the user's energy profile.
        
        Returns:
            Dict[str, Any]: Energy profile summary
        """
        # Calculate average energy levels by time of day
        morning_energy = 0
        afternoon_energy = 0
        evening_energy = 0
        morning_count = 0
        afternoon_count = 0
        evening_count = 0
        
        for entry in self.energy_profile["energy_cycle"]:
            hour = entry["hour"]
            energy = entry.get("energy", 0)
            
            if 5 <= hour < 12:  # Morning: 5 AM - 12 PM
                morning_energy += energy
                morning_count += 1
            elif 12 <= hour < 17:  # Afternoon: 12 PM - 5 PM
                afternoon_energy += energy
                afternoon_count += 1
            elif 17 <= hour < 22:  # Evening: 5 PM - 10 PM
                evening_energy += energy
                evening_count += 1
        
        # Calculate averages
        avg_morning = round(morning_energy / max(1, morning_count), 1)
        avg_afternoon = round(afternoon_energy / max(1, afternoon_count), 1)
        avg_evening = round(evening_energy / max(1, evening_count), 1)
        
        # Determine peak energy time
        peak_time = "morning"
        peak_energy = avg_morning
        
        if avg_afternoon > peak_energy:
            peak_time = "afternoon"
            peak_energy = avg_afternoon
        
        if avg_evening > peak_energy:
            peak_time = "evening"
            peak_energy = avg_evening
        
        # Create summary
        return {
            "average_energy": {
                "morning": avg_morning,
                "afternoon": avg_afternoon,
                "evening": avg_evening
            },
            "peak_energy_time": peak_time,
            "focus_session_duration": self.energy_profile["focus_duration"],
            "break_duration": self.energy_profile["break_duration"],
            "preferred_study_days": self.energy_profile["preferences"]["preferred_study_days"]
        }
    
    def _create_energy_aware_schedule(
        self,
        topics: List[Dict[str, Any]],
        optimal_times: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create an energy-aware schedule for a day.
        
        Args:
            topics (List[Dict[str, Any]]): Topics to study
            optimal_times (List[Dict[str, Any]]): Optimal study times
            
        Returns:
            List[Dict[str, Any]]: Energy-aware schedule
        """
        # Sort topics by difficulty (assuming more hours = more difficult)
        sorted_topics = sorted(topics, key=lambda x: x.get("hours", 0), reverse=True)
        
        # Sort optimal times by energy level
        sorted_times = sorted(optimal_times, key=lambda x: x["energy_level"], reverse=True)
        
        # Create schedule
        schedule = []
        remaining_topics = sorted_topics.copy()
        
        for time_slot in sorted_times:
            # Skip if no more topics
            if not remaining_topics:
                break
            
            # Get next topic
            topic = remaining_topics[0]
            
            # Calculate how much time to allocate
            topic_hours = topic.get("hours", 0)
            slot_hours = time_slot["duration_hours"]
            
            allocated_hours = min(topic_hours, slot_hours)
            
            # Create schedule entry
            entry = {
                "start_time": time_slot["start_time"],
                "end_time": time_slot["end_time"],
                "topic": topic["title"],
                "hours": allocated_hours,
                "energy_level": time_slot["energy_level"],
                "focus_areas": topic.get("focus_areas", []),
                "recommended_activities": time_slot["recommended_activities"]
            }
            
            schedule.append(entry)
            
            # Update remaining hours for the topic
            remaining_hours = topic_hours - allocated_hours
            
            if remaining_hours <= 0.1:  # Small threshold to account for floating point errors
                # Remove topic if completed
                remaining_topics.pop(0)
            else:
                # Update hours for the topic
                remaining_topics[0] = {**topic, "hours": remaining_hours}
        
        return schedule
    
    def _generate_adaptive_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate adaptive recommendations based on performance data.
        
        Returns:
            List[Dict[str, Any]]: Adaptive recommendations
        """
        recommendations = []
        
        # Get recent performance data (last 30 days)
        recent_data = []
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        for entry in self.energy_profile["performance_data"]:
            if entry["timestamp"] >= thirty_days_ago:
                recent_data.append(entry)
        
        # If not enough data, provide general recommendations
        if len(recent_data) < 5:
            recommendations.append({
                "type": "general",
                "recommendation": "Log more study sessions to receive personalized recommendations",
                "rationale": "Not enough performance data available yet"
            })
            return recommendations
        
        # Analyze performance by time of day
        morning_perf = []
        afternoon_perf = []
        evening_perf = []
        
        for entry in recent_data:
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                hour = dt.hour
                performance = entry["performance_score"]
                
                if 5 <= hour < 12:  # Morning: 5 AM - 12 PM
                    morning_perf.append(performance)
                elif 12 <= hour < 17:  # Afternoon: 12 PM - 5 PM
                    afternoon_perf.append(performance)
                elif 17 <= hour < 22:  # Evening: 5 PM - 10 PM
                    evening_perf.append(performance)
                
            except (ValueError, TypeError):
                continue
        
        # Calculate average performance by time of day
        avg_morning = sum(morning_perf) / max(1, len(morning_perf))
        avg_afternoon = sum(afternoon_perf) / max(1, len(afternoon_perf))
        avg_evening = sum(evening_perf) / max(1, len(evening_perf))
        
        # Recommend best time of day
        best_time = "morning"
        best_perf = avg_morning
        
        if avg_afternoon > best_perf:
            best_time = "afternoon"
            best_perf = avg_afternoon
        
        if avg_evening > best_perf:
            best_time = "evening"
            best_perf = avg_evening
        
        recommendations.append({
            "type": "time_of_day",
            "recommendation": f"Schedule challenging tasks during the {best_time}",
            "rationale": f"Your performance is highest during the {best_time} (avg score: {best_perf:.2f})"
        })
        
        # Analyze performance by activity type
        activity_perf = {}
        
        for entry in recent_data:
            activity = entry["activity_type"]
            performance = entry["performance_score"]
            
            if activity not in activity_perf:
                activity_perf[activity] = []
            
            activity_perf[activity].append(performance)
        
        # Find best and worst activities
        best_activity = None
        worst_activity = None
        best_perf = -1
        worst_perf = 2  # Higher than max possible (1.0)
        
        for activity, scores in activity_perf.items():
            if len(scores) < 3:  # Need at least 3 data points
                continue
                
            avg_perf = sum(scores) / len(scores)
            
            if avg_perf > best_perf:
                best_perf = avg_perf
                best_activity = activity
            
            if avg_perf < worst_perf:
                worst_perf = avg_perf
                worst_activity = activity
        
        if best_activity:
            recommendations.append({
                "type": "activity_strength",
                "recommendation": f"Continue with {best_activity} activities",
                "rationale": f"You perform well in {best_activity} (avg score: {best_perf:.2f})"
            })
        
        if worst_activity:
            recommendations.append({
                "type": "activity_weakness",
                "recommendation": f"Allocate more energy to {worst_activity} activities",
                "rationale": f"You may need more practice with {worst_activity} (avg score: {worst_perf:.2f})"
            })
        
        # Analyze correlation between energy level and performance
        energy_perf_corr = self._calculate_correlation(
            [e["energy_level"] for e in recent_data if e["energy_level"] is not None],
            [e["performance_score"] for e in recent_data if e["energy_level"] is not None]
        )
        
        if energy_perf_corr > 0.3:
            recommendations.append({
                "type": "energy_correlation",
                "recommendation": "Prioritize studying when your energy is high",
                "rationale": f"Your performance strongly correlates with energy level (corr: {energy_perf_corr:.2f})"
            })
        
        return recommendations
    
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
    Command-line interface for the Energy-Aware Planner.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Time & Energy-Aware Planning Engine")
    parser.add_argument("--user", required=True, help="User ID")
    parser.add_argument("--action", choices=["log_energy", "log_performance", "optimal_times", "generate_plan"], 
                        required=True, help="Action to perform")
    parser.add_argument("--energy", type=int, help="Energy level (1-10)")
    parser.add_argument("--focus", type=int, help="Focus level (1-10)")
    parser.add_argument("--notes", help="Additional notes")
    parser.add_argument("--activity", help="Activity type")
    parser.add_argument("--performance", type=float, help="Performance score (0-1)")
    parser.add_argument("--duration", type=int, help="Duration in minutes")
    parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    parser.add_argument("--min_energy", type=int, default=5, help="Minimum energy level")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks to plan")
    parser.add_argument("--hours", type=int, help="Hours per week")
    parser.add_argument("--focus_areas", nargs="+", help="Focus areas")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Initialize planner
    planner = EnergyAwarePlanner(user_id=args.user)
    
    # Perform action
    if args.action == "log_energy":
        if args.energy is None or args.focus is None:
            print("Error: energy and focus levels are required for log_energy action")
            return
        
        result = planner.log_energy_level(
            energy_level=args.energy,
            focus_level=args.focus,
            notes=args.notes
        )
        
        print(f"Logged energy level: {result}")
        
    elif args.action == "log_performance":
        if args.activity is None or args.performance is None or args.duration is None:
            print("Error: activity, performance, and duration are required for log_performance action")
            return
        
        result = planner.log_performance(
            activity_type=args.activity,
            performance_score=args.performance,
            duration_minutes=args.duration,
            energy_level=args.energy,
            focus_level=args.focus
        )
        
        print(f"Logged performance: {result}")
        
    elif args.action == "optimal_times":
        date = args.date or datetime.now().date().isoformat()
        
        result = planner.get_optimal_study_times(
            date=date,
            min_energy_level=args.min_energy
        )
        
        print(f"Optimal study times for {date}:")
        for slot in result:
            print(f"  {slot['start_time']} - {slot['end_time']} (Energy: {slot['energy_level']})")
            print(f"  Recommended activities: {', '.join(slot['recommended_activities'])}")
            print()
        
    elif args.action == "generate_plan":
        result = planner.generate_energy_aware_plan(
            weeks=args.weeks,
            hours_per_week=args.hours,
            focus_areas=args.focus_areas,
            min_energy_level=args.min_energy
        )
        
        # Save to file if output path provided
        if args.output:
            try:
                with open(args.output, "w") as f:
                    json.dump(result, f, indent=2)
                print(f"Energy-aware study plan saved to {args.output}")
            except Exception as e:
                print(f"Error saving plan: {e}")
        else:
            # Print summary
            print("\nENERGY-AWARE STUDY PLAN")
            print("=" * 50)
            
            print(f"\nUser: {result['user_id']}")
            print(f"Weeks: {result['weeks']}")
            print(f"Hours per week: {result['hours_per_week']}")
            
            if "energy_profile_summary" in result:
                summary = result["energy_profile_summary"]
                print("\nEnergy Profile Summary:")
                print(f"  Peak energy time: {summary['peak_energy_time']}")
                print(f"  Morning energy: {summary['average_energy']['morning']}")
                print(f"  Afternoon energy: {summary['average_energy']['afternoon']}")
                print(f"  Evening energy: {summary['average_energy']['evening']}")
            
            if "adaptive_recommendations" in result:
                print("\nAdaptive Recommendations:")
                for rec in result["adaptive_recommendations"]:
                    print(f"  - {rec['recommendation']}")
                    print(f"    Rationale: {rec['rationale']}")
            
            print("\nWeekly Plan:")
            for week in result.get("weekly_plan", []):
                print(f"\nWeek {week['week']}:")
                
                for day in week.get("daily_plan", []):
                    print(f"\n  Day {day['day']} ({day.get('date', 'N/A')}):")
                    
                    if "energy_aware_schedule" in day:
                        print("  Energy-Aware Schedule:")
                        for entry in day["energy_aware_schedule"]:
                            print(f"    {entry['start_time']} - {entry['end_time']}: {entry['topic']} (Energy: {entry['energy_level']})")
                    else:
                        print("  Topics:")
                        for topic in day.get("topics", []):
                            print(f"    - {topic['title']} ({topic.get('hours', 0)} hours)")


if __name__ == "__main__":
    main()