"""
Study plan generator module for AI Note System.
Generates personalized study plans based on mastery data.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import argparse

# Setup logging
logger = logging.getLogger("ai_note_system.processing.study_plan_generator")

def generate_study_plan(
    user_id: str,
    weeks: int = 4,
    hours_per_week: Optional[int] = None,
    focus_areas: Optional[List[str]] = None,
    db_manager=None
) -> Dict[str, Any]:
    """
    Generate a personalized study plan based on mastery data.
    
    Args:
        user_id (str): ID of the user to generate a plan for
        weeks (int): Number of weeks to plan for
        hours_per_week (int, optional): Target study hours per week
        focus_areas (List[str], optional): Specific areas to focus on
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Generated study plan
    """
    logger.info(f"Generating {weeks}-week study plan for user {user_id}")
    
    # Get user's notes and mastery data
    notes, mastery_data = get_user_data(user_id, db_manager)
    
    if not notes:
        logger.warning(f"No notes found for user {user_id}")
        return {
            "user_id": user_id,
            "weeks": weeks,
            "error": "No notes found for user"
        }
    
    # Determine study hours if not provided
    if hours_per_week is None:
        # Default to 10 hours per week, adjusted by number of notes
        hours_per_week = min(max(len(notes) // 2, 5), 20)
    
    # Identify weak areas and prioritize topics
    prioritized_topics = prioritize_topics(notes, mastery_data, focus_areas)
    
    # Generate weekly plan
    weekly_plan = create_weekly_plan(prioritized_topics, weeks, hours_per_week)
    
    # Create full study plan
    study_plan = {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(),
        "weeks": weeks,
        "hours_per_week": hours_per_week,
        "focus_areas": focus_areas or [],
        "weekly_plan": weekly_plan,
        "prioritized_topics": prioritized_topics
    }
    
    return study_plan

def get_user_data(user_id: str, db_manager=None) -> tuple:
    """
    Get user's notes and mastery data.
    
    Args:
        user_id (str): ID of the user
        db_manager: Database manager instance
        
    Returns:
        tuple: (notes, mastery_data)
    """
    # If database manager is available, use it
    if db_manager:
        return get_user_data_from_db(user_id, db_manager)
    
    # Otherwise, use a simple file-based approach (for testing)
    return get_user_data_from_files(user_id)

def get_user_data_from_db(user_id: str, db_manager) -> tuple:
    """
    Get user's notes and mastery data from the database.
    
    Args:
        user_id (str): ID of the user
        db_manager: Database manager instance
        
    Returns:
        tuple: (notes, mastery_data)
    """
    try:
        # Get user's notes
        notes = db_manager.get_notes_by_user(user_id)
        
        # Get mastery data for each note
        mastery_data = {}
        for note in notes:
            note_id = note.get("id")
            if note_id:
                mastery = db_manager.get_mastery_data(note_id)
                if mastery:
                    mastery_data[note_id] = mastery
        
        return notes, mastery_data
        
    except Exception as e:
        logger.error(f"Error getting user data from database: {str(e)}")
        return [], {}

def get_user_data_from_files(user_id: str) -> tuple:
    """
    Get user's notes and mastery data from files (for testing).
    
    Args:
        user_id (str): ID of the user
        
    Returns:
        tuple: (notes, mastery_data)
    """
    # This is a simplified implementation for testing
    # In a real implementation, this would read from actual files
    
    # Create some sample notes
    notes = [
        {
            "id": "note1",
            "title": "Introduction to Machine Learning",
            "tags": ["machine learning", "ai", "introduction"],
            "timestamp": (datetime.now() - timedelta(days=10)).isoformat()
        },
        {
            "id": "note2",
            "title": "Neural Networks Fundamentals",
            "tags": ["machine learning", "neural networks", "deep learning"],
            "timestamp": (datetime.now() - timedelta(days=7)).isoformat()
        },
        {
            "id": "note3",
            "title": "Convolutional Neural Networks",
            "tags": ["machine learning", "neural networks", "cnn", "deep learning"],
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "id": "note4",
            "title": "Recurrent Neural Networks",
            "tags": ["machine learning", "neural networks", "rnn", "deep learning"],
            "timestamp": (datetime.now() - timedelta(days=3)).isoformat()
        },
        {
            "id": "note5",
            "title": "Reinforcement Learning",
            "tags": ["machine learning", "reinforcement learning", "deep learning"],
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
    
    # Create sample mastery data
    mastery_data = {
        "note1": {
            "mastery_score": 0.85,
            "strengths": [
                {"topic": "supervised learning", "score": 0.9},
                {"topic": "classification", "score": 0.8}
            ],
            "weaknesses": [
                {"topic": "unsupervised learning", "score": 0.6}
            ]
        },
        "note2": {
            "mastery_score": 0.7,
            "strengths": [
                {"topic": "perceptrons", "score": 0.8}
            ],
            "weaknesses": [
                {"topic": "backpropagation", "score": 0.5},
                {"topic": "activation functions", "score": 0.6}
            ]
        },
        "note3": {
            "mastery_score": 0.6,
            "strengths": [],
            "weaknesses": [
                {"topic": "convolutional layers", "score": 0.5},
                {"topic": "pooling", "score": 0.6},
                {"topic": "image recognition", "score": 0.5}
            ]
        },
        "note4": {
            "mastery_score": 0.4,
            "strengths": [],
            "weaknesses": [
                {"topic": "lstm", "score": 0.3},
                {"topic": "sequence modeling", "score": 0.4},
                {"topic": "time series", "score": 0.5}
            ]
        },
        "note5": {
            "mastery_score": 0.3,
            "strengths": [],
            "weaknesses": [
                {"topic": "q-learning", "score": 0.3},
                {"topic": "policy gradients", "score": 0.2},
                {"topic": "markov decision processes", "score": 0.4}
            ]
        }
    }
    
    return notes, mastery_data

def prioritize_topics(
    notes: List[Dict[str, Any]],
    mastery_data: Dict[str, Dict[str, Any]],
    focus_areas: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Prioritize topics based on mastery data and focus areas.
    
    Args:
        notes (List[Dict[str, Any]]): User's notes
        mastery_data (Dict[str, Dict[str, Any]]): Mastery data for each note
        focus_areas (List[str], optional): Specific areas to focus on
        
    Returns:
        List[Dict[str, Any]]: Prioritized topics
    """
    # Create a list of topics with priority scores
    topics = []
    
    for note in notes:
        note_id = note.get("id")
        if not note_id or note_id not in mastery_data:
            continue
        
        # Get mastery data for this note
        mastery = mastery_data[note_id]
        mastery_score = mastery.get("mastery_score", 0.5)
        
        # Calculate priority score (lower mastery = higher priority)
        priority_score = 1.0 - mastery_score
        
        # Adjust priority based on recency (more recent = higher priority)
        timestamp = note.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - dt).days
                recency_factor = max(0.5, 1.0 - (days_ago / 30))  # 0.5 to 1.0 based on recency
                priority_score *= recency_factor
            except (ValueError, TypeError):
                pass
        
        # Adjust priority based on focus areas
        if focus_areas:
            tags = note.get("tags", [])
            if any(area.lower() in [tag.lower() for tag in tags] for area in focus_areas):
                priority_score *= 1.5  # Boost priority for focus areas
        
        # Add topic to list
        topics.append({
            "note_id": note_id,
            "title": note.get("title", "Untitled"),
            "mastery_score": mastery_score,
            "priority_score": priority_score,
            "strengths": mastery.get("strengths", []),
            "weaknesses": mastery.get("weaknesses", []),
            "tags": note.get("tags", [])
        })
    
    # Sort topics by priority score (highest first)
    topics.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return topics

def create_weekly_plan(
    prioritized_topics: List[Dict[str, Any]],
    weeks: int,
    hours_per_week: int
) -> List[Dict[str, Any]]:
    """
    Create a weekly study plan based on prioritized topics.
    
    Args:
        prioritized_topics (List[Dict[str, Any]]): Prioritized topics
        weeks (int): Number of weeks to plan for
        hours_per_week (int): Target study hours per week
        
    Returns:
        List[Dict[str, Any]]: Weekly plan
    """
    # Create empty weekly plan
    weekly_plan = []
    
    # Calculate total study hours
    total_hours = weeks * hours_per_week
    
    # Calculate hours per topic (minimum 1 hour per topic)
    topics_count = len(prioritized_topics)
    if topics_count == 0:
        return weekly_plan
    
    # Allocate hours based on priority scores
    total_priority = sum(topic["priority_score"] for topic in prioritized_topics)
    
    # Ensure total_priority is not zero to avoid division by zero
    if total_priority == 0:
        total_priority = 1.0
    
    # Allocate hours to each topic
    for topic in prioritized_topics:
        # Calculate hours based on priority score
        topic_hours = max(1, int((topic["priority_score"] / total_priority) * total_hours))
        topic["allocated_hours"] = topic_hours
    
    # Distribute topics across weeks
    remaining_hours = {i: hours_per_week for i in range(weeks)}
    
    # First, allocate high-priority topics
    for topic in prioritized_topics:
        # Find the week with the most remaining hours
        week_idx = max(remaining_hours, key=remaining_hours.get)
        
        # Calculate hours to allocate to this week
        hours = min(topic["allocated_hours"], remaining_hours[week_idx])
        
        # Add topic to weekly plan
        if week_idx >= len(weekly_plan):
            weekly_plan.append({
                "week": week_idx + 1,
                "topics": []
            })
        
        weekly_plan[week_idx]["topics"].append({
            "note_id": topic["note_id"],
            "title": topic["title"],
            "hours": hours,
            "focus_areas": [w["topic"] for w in topic["weaknesses"][:3]]
        })
        
        # Update remaining hours
        remaining_hours[week_idx] -= hours
        topic["allocated_hours"] -= hours
        
        # If topic still has hours, allocate to other weeks
        while topic["allocated_hours"] > 0:
            # Find the next week with the most remaining hours
            if not remaining_hours:
                break
                
            week_idx = max(remaining_hours, key=remaining_hours.get)
            
            # Calculate hours to allocate to this week
            hours = min(topic["allocated_hours"], remaining_hours[week_idx])
            
            # If no hours left in any week, break
            if hours <= 0:
                break
            
            # Add topic to weekly plan
            if week_idx >= len(weekly_plan):
                weekly_plan.append({
                    "week": week_idx + 1,
                    "topics": []
                })
            
            # Check if topic already exists in this week
            existing_topic = next((t for t in weekly_plan[week_idx]["topics"] if t["note_id"] == topic["note_id"]), None)
            
            if existing_topic:
                # Update existing topic
                existing_topic["hours"] += hours
            else:
                # Add new topic
                weekly_plan[week_idx]["topics"].append({
                    "note_id": topic["note_id"],
                    "title": topic["title"],
                    "hours": hours,
                    "focus_areas": [w["topic"] for w in topic["weaknesses"][:3]]
                })
            
            # Update remaining hours
            remaining_hours[week_idx] -= hours
            topic["allocated_hours"] -= hours
            
            # If no hours left in this week, remove it from remaining_hours
            if remaining_hours[week_idx] <= 0:
                del remaining_hours[week_idx]
    
    # Sort weekly plan by week number
    weekly_plan.sort(key=lambda x: x["week"])
    
    # Add daily breakdown for each week
    for week in weekly_plan:
        week["daily_plan"] = create_daily_plan(week["topics"])
    
    return weekly_plan

def create_daily_plan(topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Create a daily study plan for a week.
    
    Args:
        topics (List[Dict[str, Any]]): Topics to study this week
        
    Returns:
        List[Dict[str, Any]]: Daily plan
    """
    # Create empty daily plan (5 days, Monday to Friday)
    daily_plan = [{"day": i + 1, "topics": []} for i in range(5)]
    
    # Calculate total hours for the week
    total_hours = sum(topic["hours"] for topic in topics)
    
    # Calculate hours per day (distribute evenly)
    hours_per_day = total_hours / 5
    
    # Distribute topics across days
    remaining_hours = {i: hours_per_day for i in range(5)}
    
    # Copy topics to avoid modifying the original
    topics_copy = [topic.copy() for topic in topics]
    
    # Allocate topics to days
    for topic in topics_copy:
        # Find the day with the most remaining hours
        day_idx = max(remaining_hours, key=remaining_hours.get)
        
        # Calculate hours to allocate to this day
        hours = min(topic["hours"], remaining_hours[day_idx])
        
        # Add topic to daily plan
        daily_plan[day_idx]["topics"].append({
            "note_id": topic["note_id"],
            "title": topic["title"],
            "hours": hours,
            "focus_areas": topic.get("focus_areas", [])
        })
        
        # Update remaining hours
        remaining_hours[day_idx] -= hours
        topic["hours"] -= hours
        
        # If topic still has hours, allocate to other days
        while topic["hours"] > 0:
            # Find the next day with the most remaining hours
            if not remaining_hours:
                break
                
            day_idx = max(remaining_hours, key=remaining_hours.get)
            
            # Calculate hours to allocate to this day
            hours = min(topic["hours"], remaining_hours[day_idx])
            
            # If no hours left in any day, break
            if hours <= 0:
                break
            
            # Check if topic already exists in this day
            existing_topic = next((t for t in daily_plan[day_idx]["topics"] if t["note_id"] == topic["note_id"]), None)
            
            if existing_topic:
                # Update existing topic
                existing_topic["hours"] += hours
            else:
                # Add new topic
                daily_plan[day_idx]["topics"].append({
                    "note_id": topic["note_id"],
                    "title": topic["title"],
                    "hours": hours,
                    "focus_areas": topic.get("focus_areas", [])
                })
            
            # Update remaining hours
            remaining_hours[day_idx] -= hours
            topic["hours"] -= hours
            
            # If no hours left in this day, remove it from remaining_hours
            if remaining_hours[day_idx] <= 0:
                del remaining_hours[day_idx]
    
    return daily_plan

def save_study_plan(
    study_plan: Dict[str, Any],
    output_path: str
) -> Dict[str, Any]:
    """
    Save study plan to a file.
    
    Args:
        study_plan (Dict[str, Any]): Study plan to save
        output_path (str): Path to save the study plan
        
    Returns:
        Dict[str, Any]: Result of the save operation
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Save study plan as JSON
        with open(output_path, "w") as f:
            json.dump(study_plan, f, indent=2)
        
        logger.info(f"Study plan saved to {output_path}")
        return {"success": True, "output_path": output_path}
        
    except Exception as e:
        error_msg = f"Error saving study plan: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def main():
    """
    Command-line interface for generating study plans.
    """
    parser = argparse.ArgumentParser(description="Generate a personalized study plan")
    parser.add_argument("--user", required=True, help="User ID")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks to plan for")
    parser.add_argument("--hours", type=int, help="Target study hours per week")
    parser.add_argument("--focus", nargs="+", help="Specific areas to focus on")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    # Generate study plan
    study_plan = generate_study_plan(
        user_id=args.user,
        weeks=args.weeks,
        hours_per_week=args.hours,
        focus_areas=args.focus
    )
    
    # Save study plan if output path provided
    if args.output:
        save_study_plan(study_plan, args.output)
    else:
        # Print study plan as JSON
        print(json.dumps(study_plan, indent=2))

if __name__ == "__main__":
    main()