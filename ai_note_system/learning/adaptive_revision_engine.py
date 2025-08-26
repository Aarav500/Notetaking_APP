"""
Adaptive Revision Engine module for AI Note System.
Provides functionality to track knowledge decay and optimize revision schedules.
"""

import os
import json
import logging
import math
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from collections import defaultdict

# Setup logging
logger = logging.getLogger("ai_note_system.learning.adaptive_revision_engine")

class AdaptiveRevisionEngine:
    """
    Adaptive Revision Engine class for optimizing revision schedules.
    Uses spaced repetition and knowledge decay models to personalize review timing.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Adaptive Revision Engine.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Default memory model parameters
        self.default_memory_params = {
            "initial_strength": 1.0,  # Initial memory strength
            "decay_rate": 0.1,        # Base decay rate
            "min_strength": 0.2,      # Minimum memory strength before review
            "review_boost": 0.5,      # Memory strength boost from review
            "difficulty_factor": 1.0  # Difficulty factor (higher = harder to remember)
        }
        
        # User-specific memory parameters (will be updated based on performance)
        self.user_memory_params = self.config.get("memory_params", self.default_memory_params.copy())
        
        # Topic-specific parameters (will be populated as user interacts with topics)
        self.topic_params = {}
        
        # Review history
        self.review_history = []
        
        logger.debug("Initialized AdaptiveRevisionEngine")
    
    def calculate_memory_strength(self, 
                                 topic_id: str,
                                 last_review_time: datetime,
                                 review_count: int,
                                 performance_score: float,
                                 current_time: Optional[datetime] = None) -> float:
        """
        Calculate current memory strength for a topic based on decay model.
        
        Args:
            topic_id (str): ID of the topic
            last_review_time (datetime): Time of last review
            review_count (int): Number of previous reviews
            performance_score (float): Score from last review (0.0 to 1.0)
            current_time (datetime, optional): Current time (defaults to now)
            
        Returns:
            float: Current memory strength (0.0 to 1.0)
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Get topic-specific parameters or use defaults
        topic_params = self.topic_params.get(topic_id, {})
        decay_rate = topic_params.get("decay_rate", self.user_memory_params["decay_rate"])
        difficulty_factor = topic_params.get("difficulty_factor", self.user_memory_params["difficulty_factor"])
        
        # Calculate time elapsed since last review in days
        elapsed_days = (current_time - last_review_time).total_seconds() / (24 * 3600)
        
        # Adjust decay rate based on review count and performance
        adjusted_decay_rate = decay_rate * difficulty_factor / (1 + 0.1 * review_count * performance_score)
        
        # Calculate memory strength using exponential decay model
        initial_strength = topic_params.get("last_strength", self.user_memory_params["initial_strength"])
        memory_strength = initial_strength * math.exp(-adjusted_decay_rate * elapsed_days)
        
        # Ensure memory strength is between 0 and 1
        memory_strength = max(0.0, min(1.0, memory_strength))
        
        logger.debug(f"Calculated memory strength for topic {topic_id}: {memory_strength:.4f}")
        return memory_strength
    
    def schedule_next_review(self, 
                            topic_id: str,
                            current_strength: float,
                            target_strength: Optional[float] = None,
                            current_time: Optional[datetime] = None) -> datetime:
        """
        Schedule the next review time for a topic.
        
        Args:
            topic_id (str): ID of the topic
            current_strength (float): Current memory strength
            target_strength (float, optional): Target memory strength for review
            current_time (datetime, optional): Current time (defaults to now)
            
        Returns:
            datetime: Recommended next review time
        """
        if current_time is None:
            current_time = datetime.now()
        
        if target_strength is None:
            target_strength = self.user_memory_params["min_strength"]
        
        # Get topic-specific parameters or use defaults
        topic_params = self.topic_params.get(topic_id, {})
        decay_rate = topic_params.get("decay_rate", self.user_memory_params["decay_rate"])
        difficulty_factor = topic_params.get("difficulty_factor", self.user_memory_params["difficulty_factor"])
        
        # Calculate time until memory decays to target strength
        if current_strength <= target_strength:
            # If current strength is already below target, schedule review soon
            days_until_review = 0.25  # 6 hours
        else:
            # Calculate days until memory decays to target strength
            adjusted_decay_rate = decay_rate * difficulty_factor
            days_until_review = max(0.25, math.log(current_strength / target_strength) / adjusted_decay_rate)
        
        # Calculate next review time
        next_review_time = current_time + timedelta(days=days_until_review)
        
        logger.debug(f"Scheduled next review for topic {topic_id}: {next_review_time.isoformat()}")
        return next_review_time
    
    def record_review_result(self,
                           topic_id: str,
                           performance_score: float,
                           review_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Record the result of a review and update memory model parameters.
        
        Args:
            topic_id (str): ID of the topic
            performance_score (float): Score from review (0.0 to 1.0)
            review_time (datetime, optional): Time of review (defaults to now)
            
        Returns:
            Dict[str, Any]: Updated topic parameters
        """
        if review_time is None:
            review_time = datetime.now()
        
        # Get topic parameters or create new entry
        if topic_id not in self.topic_params:
            self.topic_params[topic_id] = self.user_memory_params.copy()
            self.topic_params[topic_id]["review_count"] = 0
            self.topic_params[topic_id]["last_review_time"] = review_time
            self.topic_params[topic_id]["last_strength"] = self.user_memory_params["initial_strength"]
        
        topic_params = self.topic_params[topic_id]
        
        # Calculate current strength before review
        current_strength = self.calculate_memory_strength(
            topic_id,
            topic_params["last_review_time"],
            topic_params["review_count"],
            topic_params.get("last_performance", 0.5),
            review_time
        )
        
        # Update review count
        topic_params["review_count"] += 1
        
        # Update last review time
        topic_params["last_review_time"] = review_time
        
        # Update last performance
        topic_params["last_performance"] = performance_score
        
        # Calculate new memory strength after review
        review_boost = self.user_memory_params["review_boost"]
        new_strength = min(1.0, current_strength + (1.0 - current_strength) * review_boost * performance_score)
        topic_params["last_strength"] = new_strength
        
        # Adjust difficulty factor based on performance
        if performance_score < 0.5:
            # If performance is poor, increase difficulty factor
            topic_params["difficulty_factor"] = min(2.0, topic_params["difficulty_factor"] * 1.1)
        elif performance_score > 0.8:
            # If performance is good, decrease difficulty factor
            topic_params["difficulty_factor"] = max(0.5, topic_params["difficulty_factor"] * 0.95)
        
        # Add to review history
        self.review_history.append({
            "topic_id": topic_id,
            "review_time": review_time.isoformat(),
            "performance_score": performance_score,
            "strength_before": current_strength,
            "strength_after": new_strength,
            "difficulty_factor": topic_params["difficulty_factor"]
        })
        
        # Schedule next review
        next_review_time = self.schedule_next_review(topic_id, new_strength)
        topic_params["next_review_time"] = next_review_time
        
        logger.info(f"Recorded review result for topic {topic_id}: score={performance_score:.2f}, next_review={next_review_time.isoformat()}")
        return topic_params
    
    def get_due_topics(self, 
                      current_time: Optional[datetime] = None,
                      limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get topics that are due for review.
        
        Args:
            current_time (datetime, optional): Current time (defaults to now)
            limit (int, optional): Maximum number of topics to return
            
        Returns:
            List[Dict[str, Any]]: List of topics due for review
        """
        if current_time is None:
            current_time = datetime.now()
        
        due_topics = []
        
        for topic_id, params in self.topic_params.items():
            if "next_review_time" in params and params["next_review_time"] <= current_time:
                # Calculate current memory strength
                current_strength = self.calculate_memory_strength(
                    topic_id,
                    params["last_review_time"],
                    params["review_count"],
                    params.get("last_performance", 0.5),
                    current_time
                )
                
                due_topics.append({
                    "topic_id": topic_id,
                    "current_strength": current_strength,
                    "last_review_time": params["last_review_time"].isoformat(),
                    "next_review_time": params["next_review_time"].isoformat(),
                    "review_count": params["review_count"],
                    "difficulty_factor": params["difficulty_factor"]
                })
        
        # Sort by memory strength (lowest first)
        due_topics.sort(key=lambda x: x["current_strength"])
        
        # Apply limit if specified
        if limit is not None:
            due_topics = due_topics[:limit]
        
        logger.info(f"Found {len(due_topics)} topics due for review")
        return due_topics
    
    def generate_revision_schedule(self,
                                 topic_ids: List[str],
                                 days_ahead: int = 30,
                                 current_time: Optional[datetime] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a revision schedule for multiple topics.
        
        Args:
            topic_ids (List[str]): List of topic IDs to include in schedule
            days_ahead (int): Number of days to schedule ahead
            current_time (datetime, optional): Current time (defaults to now)
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Revision schedule by date
        """
        if current_time is None:
            current_time = datetime.now()
        
        end_time = current_time + timedelta(days=days_ahead)
        schedule = defaultdict(list)
        
        for topic_id in topic_ids:
            if topic_id not in self.topic_params:
                logger.warning(f"Topic {topic_id} not found in memory model")
                continue
            
            params = self.topic_params[topic_id]
            review_time = params.get("next_review_time")
            
            if review_time is None:
                # If no next review time, calculate it
                current_strength = self.calculate_memory_strength(
                    topic_id,
                    params["last_review_time"],
                    params["review_count"],
                    params.get("last_performance", 0.5),
                    current_time
                )
                review_time = self.schedule_next_review(topic_id, current_strength, current_time=current_time)
            
            # Add all reviews within the time window
            while review_time <= end_time:
                date_key = review_time.strftime("%Y-%m-%d")
                schedule[date_key].append({
                    "topic_id": topic_id,
                    "review_time": review_time.isoformat(),
                    "estimated_strength": self.calculate_memory_strength(
                        topic_id,
                        params["last_review_time"],
                        params["review_count"],
                        params.get("last_performance", 0.5),
                        review_time
                    )
                })
                
                # Schedule next review after this one
                review_time = self.schedule_next_review(
                    topic_id, 
                    self.user_memory_params["initial_strength"], 
                    current_time=review_time
                )
        
        logger.info(f"Generated revision schedule for {len(topic_ids)} topics over {days_ahead} days")
        return dict(schedule)
    
    def integrate_with_roadmap(self,
                             roadmap: Dict[str, Any],
                             topic_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Integrate revision schedule with a learning roadmap.
        
        Args:
            roadmap (Dict[str, Any]): Learning roadmap from GoalRoadmapGenerator
            topic_mapping (Dict[str, str]): Mapping from roadmap items to topic IDs
            
        Returns:
            Dict[str, Any]: Integrated roadmap with revision schedule
        """
        if "schedule" not in roadmap:
            logger.error("Roadmap does not contain a schedule")
            return roadmap
        
        # Create a copy of the roadmap
        integrated_roadmap = json.loads(json.dumps(roadmap))
        
        # Add revision tasks to the schedule
        for date_str, tasks in integrated_roadmap["schedule"].items():
            # Convert date string to datetime
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid date format in roadmap: {date_str}")
                continue
            
            # Get topics due for revision on this date
            due_topics = []
            for topic_id in topic_mapping.values():
                if topic_id in self.topic_params:
                    params = self.topic_params[topic_id]
                    if "next_review_time" in params:
                        next_review = params["next_review_time"]
                        if next_review.date() == date.date():
                            due_topics.append(topic_id)
            
            # Add revision tasks
            for topic_id in due_topics:
                # Find roadmap item for this topic
                roadmap_item = None
                for item_id, mapped_topic_id in topic_mapping.items():
                    if mapped_topic_id == topic_id:
                        roadmap_item = item_id
                        break
                
                if roadmap_item:
                    # Add revision task
                    revision_task = {
                        "type": "revision",
                        "item_id": roadmap_item,
                        "topic_id": topic_id,
                        "estimated_time": 0.5,  # 30 minutes for revision
                        "priority": "high"
                    }
                    tasks.append(revision_task)
        
        logger.info(f"Integrated revision schedule with roadmap")
        return integrated_roadmap
    
    def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze review performance and generate insights.
        
        Returns:
            Dict[str, Any]: Performance analysis and insights
        """
        if not self.review_history:
            logger.warning("No review history available for analysis")
            return {"error": "No review history available"}
        
        # Group reviews by topic
        topic_reviews = defaultdict(list)
        for review in self.review_history:
            topic_reviews[review["topic_id"]].append(review)
        
        # Calculate performance metrics by topic
        topic_metrics = {}
        for topic_id, reviews in topic_reviews.items():
            # Sort reviews by time
            sorted_reviews = sorted(reviews, key=lambda x: x["review_time"])
            
            # Calculate average performance
            avg_performance = sum(r["performance_score"] for r in reviews) / len(reviews)
            
            # Calculate performance trend
            if len(reviews) >= 3:
                recent_avg = sum(r["performance_score"] for r in sorted_reviews[-3:]) / 3
                older_avg = sum(r["performance_score"] for r in sorted_reviews[:-3]) / max(1, len(sorted_reviews) - 3)
                trend = recent_avg - older_avg
            else:
                trend = 0
            
            # Calculate forgetting rate
            forgetting_rate = self.topic_params.get(topic_id, {}).get("decay_rate", self.user_memory_params["decay_rate"])
            
            topic_metrics[topic_id] = {
                "review_count": len(reviews),
                "average_performance": avg_performance,
                "performance_trend": trend,
                "forgetting_rate": forgetting_rate,
                "difficulty_factor": self.topic_params.get(topic_id, {}).get("difficulty_factor", 1.0),
                "last_review_time": sorted_reviews[-1]["review_time"] if reviews else None
            }
        
        # Generate overall insights
        overall_performance = sum(m["average_performance"] for m in topic_metrics.values()) / max(1, len(topic_metrics))
        
        # Identify topics with high forgetting rates
        difficult_topics = [
            topic_id for topic_id, metrics in topic_metrics.items()
            if metrics["difficulty_factor"] > 1.2
        ]
        
        # Identify topics with improving performance
        improving_topics = [
            topic_id for topic_id, metrics in topic_metrics.items()
            if metrics["performance_trend"] > 0.1
        ]
        
        # Generate recommendations
        recommendations = []
        
        if difficult_topics:
            recommendations.append({
                "type": "difficult_topics",
                "message": "Consider more frequent reviews for these difficult topics",
                "topics": difficult_topics
            })
        
        if improving_topics:
            recommendations.append({
                "type": "improving_topics",
                "message": "Performance is improving for these topics, consider spacing out reviews",
                "topics": improving_topics
            })
        
        analysis = {
            "overall_performance": overall_performance,
            "topic_metrics": topic_metrics,
            "difficult_topics": difficult_topics,
            "improving_topics": improving_topics,
            "recommendations": recommendations
        }
        
        logger.info(f"Analyzed performance across {len(topic_metrics)} topics")
        return analysis
    
    def visualize_memory_decay(self,
                              topic_ids: List[str],
                              days_ahead: int = 30,
                              output_path: Optional[str] = None) -> str:
        """
        Visualize memory decay curves for topics.
        
        Args:
            topic_ids (List[str]): List of topic IDs to visualize
            days_ahead (int): Number of days to project ahead
            output_path (str, optional): Path to save the visualization
            
        Returns:
            str: Path to the saved visualization or error message
        """
        if not topic_ids:
            logger.warning("No topics provided for visualization")
            return "Error: No topics provided"
        
        # Create figure
        plt.figure(figsize=(12, 8))
        
        # Current time
        current_time = datetime.now()
        
        # Generate time points
        days = np.linspace(0, days_ahead, 100)
        time_points = [current_time + timedelta(days=d) for d in days]
        
        # Plot memory decay for each topic
        for topic_id in topic_ids:
            if topic_id not in self.topic_params:
                logger.warning(f"Topic {topic_id} not found in memory model")
                continue
            
            params = self.topic_params[topic_id]
            
            # Calculate memory strength at each time point
            strengths = [
                self.calculate_memory_strength(
                    topic_id,
                    params["last_review_time"],
                    params["review_count"],
                    params.get("last_performance", 0.5),
                    t
                )
                for t in time_points
            ]
            
            # Plot decay curve
            plt.plot(days, strengths, label=f"Topic {topic_id}")
            
            # Plot scheduled reviews
            next_review = params.get("next_review_time")
            if next_review and next_review <= time_points[-1]:
                days_until_review = (next_review - current_time).total_seconds() / (24 * 3600)
                plt.axvline(x=days_until_review, linestyle='--', alpha=0.5)
                plt.text(days_until_review, 0.5, f"Review {topic_id}", rotation=90, alpha=0.7)
        
        # Add threshold line
        plt.axhline(y=self.user_memory_params["min_strength"], linestyle=':', color='red', alpha=0.7, label="Review Threshold")
        
        # Add labels and legend
        plt.xlabel("Days from Now")
        plt.ylabel("Memory Strength")
        plt.title("Memory Decay Curves and Review Schedule")
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save or show the figure
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            plt.close()
            logger.info(f"Saved memory decay visualization to {output_path}")
            return output_path
        else:
            # Create a temporary file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name)
            plt.close()
            logger.info(f"Saved memory decay visualization to temporary file {temp_file.name}")
            return temp_file.name
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the memory model to a file.
        
        Args:
            filepath (str): Path to save the state
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert datetime objects to strings
            serializable_topic_params = {}
            for topic_id, params in self.topic_params.items():
                serializable_params = {}
                for key, value in params.items():
                    if isinstance(value, datetime):
                        serializable_params[key] = value.isoformat()
                    else:
                        serializable_params[key] = value
                serializable_topic_params[topic_id] = serializable_params
            
            state = {
                "user_memory_params": self.user_memory_params,
                "topic_params": serializable_topic_params,
                "review_history": self.review_history
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Saved memory model state to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving memory model state: {str(e)}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the memory model state from a file.
        
        Args:
            filepath (str): Path to the state file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.user_memory_params = state.get("user_memory_params", self.default_memory_params.copy())
            self.review_history = state.get("review_history", [])
            
            # Convert string timestamps back to datetime objects
            topic_params = {}
            for topic_id, params in state.get("topic_params", {}).items():
                topic_params[topic_id] = {}
                for key, value in params.items():
                    if key in ["last_review_time", "next_review_time"] and isinstance(value, str):
                        try:
                            topic_params[topic_id][key] = datetime.fromisoformat(value)
                        except ValueError:
                            logger.warning(f"Invalid datetime format in state file: {value}")
                            topic_params[topic_id][key] = datetime.now()
                    else:
                        topic_params[topic_id][key] = value
            
            self.topic_params = topic_params
            
            logger.info(f"Loaded memory model state from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading memory model state: {str(e)}")
            return False