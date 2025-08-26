"""
Mastery estimator module for AI Note System.
Estimates user mastery of topics based on review history and quiz performance.
"""

import os
import logging
import json
import math
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.processing.ml_enhancements.mastery_estimator")

def estimate_mastery(
    item_id: str,
    review_history: Optional[List[Dict[str, Any]]] = None,
    quiz_results: Optional[List[Dict[str, Any]]] = None,
    spaced_repetition_data: Optional[Dict[str, Any]] = None,
    item_type: str = "note",
    db_manager=None
) -> Dict[str, Any]:
    """
    Estimate mastery level for a specific item.
    
    Args:
        item_id (str): ID of the item to estimate mastery for
        review_history (List[Dict[str, Any]], optional): History of reviews
        quiz_results (List[Dict[str, Any]], optional): Results of quizzes
        spaced_repetition_data (Dict[str, Any], optional): Spaced repetition data
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Mastery estimation results
    """
    logger.info(f"Estimating mastery for {item_type} {item_id}")
    
    # Get review history if not provided
    if review_history is None:
        review_history = get_review_history(item_id, item_type, db_manager)
    
    # Get quiz results if not provided
    if quiz_results is None:
        quiz_results = get_quiz_results(item_id, item_type, db_manager)
    
    # Get spaced repetition data if not provided
    if spaced_repetition_data is None:
        spaced_repetition_data = get_spaced_repetition_data(item_id, item_type, db_manager)
    
    # Calculate mastery score based on available data
    mastery_score = calculate_mastery_score(review_history, quiz_results, spaced_repetition_data)
    
    # Calculate confidence in the mastery score
    confidence = calculate_confidence(review_history, quiz_results, spaced_repetition_data)
    
    # Identify strengths and weaknesses
    strengths, weaknesses = identify_strengths_and_weaknesses(review_history, quiz_results)
    
    # Generate recommendations for improvement
    recommendations = generate_recommendations(mastery_score, strengths, weaknesses)
    
    # Create mastery report
    mastery_report = {
        "item_id": item_id,
        "item_type": item_type,
        "mastery_score": mastery_score,
        "confidence": confidence,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "timestamp": datetime.now().isoformat()
    }
    
    return mastery_report

def get_review_history(
    item_id: str,
    item_type: str = "note",
    db_manager=None
) -> List[Dict[str, Any]]:
    """
    Get review history for an item.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        List[Dict[str, Any]]: Review history
    """
    # If database manager is available, use it
    if db_manager:
        return get_review_history_from_db(item_id, item_type, db_manager)
    
    # Otherwise, use a simple file-based approach
    return get_review_history_from_file(item_id, item_type)

def get_review_history_from_db(
    item_id: str,
    item_type: str = "note",
    db_manager=None
) -> List[Dict[str, Any]]:
    """
    Get review history for an item from the database.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        List[Dict[str, Any]]: Review history
    """
    try:
        # This is a placeholder for database integration
        # In a real implementation, this would query the database
        
        # For now, return an empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting review history from database: {str(e)}")
        return []

def get_review_history_from_file(
    item_id: str,
    item_type: str = "note"
) -> List[Dict[str, Any]]:
    """
    Get review history for an item from a file.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        
    Returns:
        List[Dict[str, Any]]: Review history
    """
    try:
        # Create a file path for the review history
        file_path = get_data_file_path(item_id, item_type, "review_history")
        
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # If the file doesn't exist, return an empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting review history from file: {str(e)}")
        return []

def get_quiz_results(
    item_id: str,
    item_type: str = "note",
    db_manager=None
) -> List[Dict[str, Any]]:
    """
    Get quiz results for an item.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        List[Dict[str, Any]]: Quiz results
    """
    # If database manager is available, use it
    if db_manager:
        return get_quiz_results_from_db(item_id, item_type, db_manager)
    
    # Otherwise, use a simple file-based approach
    return get_quiz_results_from_file(item_id, item_type)

def get_quiz_results_from_db(
    item_id: str,
    item_type: str = "note",
    db_manager=None
) -> List[Dict[str, Any]]:
    """
    Get quiz results for an item from the database.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        List[Dict[str, Any]]: Quiz results
    """
    try:
        # This is a placeholder for database integration
        # In a real implementation, this would query the database
        
        # For now, return an empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting quiz results from database: {str(e)}")
        return []

def get_quiz_results_from_file(
    item_id: str,
    item_type: str = "note"
) -> List[Dict[str, Any]]:
    """
    Get quiz results for an item from a file.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        
    Returns:
        List[Dict[str, Any]]: Quiz results
    """
    try:
        # Create a file path for the quiz results
        file_path = get_data_file_path(item_id, item_type, "quiz_results")
        
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # If the file doesn't exist, return an empty list
        return []
        
    except Exception as e:
        logger.error(f"Error getting quiz results from file: {str(e)}")
        return []

def get_spaced_repetition_data(
    item_id: str,
    item_type: str = "note",
    db_manager=None
) -> Dict[str, Any]:
    """
    Get spaced repetition data for an item.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Spaced repetition data
    """
    # If database manager is available, use it
    if db_manager:
        return get_spaced_repetition_data_from_db(item_id, item_type, db_manager)
    
    # Otherwise, use a simple file-based approach
    return get_spaced_repetition_data_from_file(item_id, item_type)

def get_spaced_repetition_data_from_db(
    item_id: str,
    item_type: str = "note",
    db_manager=None
) -> Dict[str, Any]:
    """
    Get spaced repetition data for an item from the database.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Spaced repetition data
    """
    try:
        # This is a placeholder for database integration
        # In a real implementation, this would query the database
        
        # For now, return default values
        return {
            "item_id": item_id,
            "item_type": item_type,
            "easiness_factor": 2.5,
            "interval": 0,
            "repetitions": 0,
            "review_count": 0,
            "last_reviewed": None,
            "next_review": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting spaced repetition data from database: {str(e)}")
        return {}

def get_spaced_repetition_data_from_file(
    item_id: str,
    item_type: str = "note"
) -> Dict[str, Any]:
    """
    Get spaced repetition data for an item from a file.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        
    Returns:
        Dict[str, Any]: Spaced repetition data
    """
    try:
        # Create a file path for the spaced repetition data
        file_path = get_data_file_path(item_id, item_type, "spaced_repetition")
        
        # Check if the file exists
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # If the file doesn't exist, return default values
        return {
            "item_id": item_id,
            "item_type": item_type,
            "easiness_factor": 2.5,
            "interval": 0,
            "repetitions": 0,
            "review_count": 0,
            "last_reviewed": None,
            "next_review": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting spaced repetition data from file: {str(e)}")
        return {}

def get_data_file_path(
    item_id: str,
    item_type: str,
    data_type: str
) -> str:
    """
    Get the file path for data.
    
    Args:
        item_id (str): ID of the item
        item_type (str): Type of item (note, topic, etc.)
        data_type (str): Type of data (review_history, quiz_results, spaced_repetition)
        
    Returns:
        str: File path
    """
    # Get the path to the data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_dir = os.path.join(project_dir, "data", "mastery")
    
    # Create a file name based on item type, ID, and data type
    file_name = f"{item_type}_{item_id}_{data_type}.json"
    
    return os.path.join(data_dir, file_name)

def calculate_mastery_score(
    review_history: List[Dict[str, Any]],
    quiz_results: List[Dict[str, Any]],
    spaced_repetition_data: Dict[str, Any]
) -> float:
    """
    Calculate mastery score based on review history, quiz results, and spaced repetition data.
    
    Args:
        review_history (List[Dict[str, Any]]): History of reviews
        quiz_results (List[Dict[str, Any]]): Results of quizzes
        spaced_repetition_data (Dict[str, Any]): Spaced repetition data
        
    Returns:
        float: Mastery score (0-1)
    """
    # Calculate mastery score based on spaced repetition data
    sr_score = calculate_sr_mastery_score(spaced_repetition_data)
    
    # Calculate mastery score based on quiz results
    quiz_score = calculate_quiz_mastery_score(quiz_results)
    
    # Calculate mastery score based on review history
    review_score = calculate_review_mastery_score(review_history)
    
    # Combine scores with weights
    weights = {
        "sr": 0.4,
        "quiz": 0.4,
        "review": 0.2
    }
    
    # Adjust weights based on available data
    if not spaced_repetition_data:
        weights["sr"] = 0
    if not quiz_results:
        weights["quiz"] = 0
    if not review_history:
        weights["review"] = 0
    
    # Normalize weights
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}
    else:
        # If no data is available, return a default score
        return 0.0
    
    # Calculate weighted score
    mastery_score = (
        weights["sr"] * sr_score +
        weights["quiz"] * quiz_score +
        weights["review"] * review_score
    )
    
    return mastery_score

def calculate_sr_mastery_score(
    spaced_repetition_data: Dict[str, Any]
) -> float:
    """
    Calculate mastery score based on spaced repetition data.
    
    Args:
        spaced_repetition_data (Dict[str, Any]): Spaced repetition data
        
    Returns:
        float: Mastery score (0-1)
    """
    if not spaced_repetition_data:
        return 0.0
    
    # Extract values
    easiness_factor = spaced_repetition_data.get("easiness_factor", 2.5)
    repetitions = spaced_repetition_data.get("repetitions", 0)
    interval = spaced_repetition_data.get("interval", 0)
    review_count = spaced_repetition_data.get("review_count", 0)
    box = spaced_repetition_data.get("box", 0)
    
    # Calculate score based on algorithm
    if "box" in spaced_repetition_data:
        # Leitner system
        # Maximum box is 5 (90 days)
        max_box = 5
        score = min(1.0, box / max_box)
    else:
        # SM-2 algorithm
        # Normalize easiness factor (1.3 to 2.5+)
        ef_score = min(1.0, max(0.0, (easiness_factor - 1.3) / 1.2))
        
        # Normalize repetitions (0 to 10+)
        rep_score = min(1.0, repetitions / 10)
        
        # Normalize interval (0 to 365+)
        int_score = min(1.0, interval / 365)
        
        # Combine scores
        score = (ef_score + rep_score + int_score) / 3
    
    return score

def calculate_quiz_mastery_score(
    quiz_results: List[Dict[str, Any]]
) -> float:
    """
    Calculate mastery score based on quiz results.
    
    Args:
        quiz_results (List[Dict[str, Any]]): Results of quizzes
        
    Returns:
        float: Mastery score (0-1)
    """
    if not quiz_results:
        return 0.0
    
    # Calculate average score across all quizzes
    total_score = 0.0
    total_weight = 0.0
    
    for result in quiz_results:
        score = result.get("score", 0.0)
        
        # Get timestamp and calculate recency weight
        timestamp = result.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - dt).days
                # More recent quizzes have higher weight
                recency_weight = max(0.1, 1.0 - (days_ago / 365))
            except (ValueError, TypeError):
                recency_weight = 1.0
        else:
            recency_weight = 1.0
        
        # Get difficulty and calculate difficulty weight
        difficulty = result.get("difficulty", "medium")
        if difficulty == "easy":
            difficulty_weight = 0.5
        elif difficulty == "medium":
            difficulty_weight = 1.0
        elif difficulty == "hard":
            difficulty_weight = 1.5
        else:
            difficulty_weight = 1.0
        
        # Calculate combined weight
        weight = recency_weight * difficulty_weight
        
        # Add weighted score
        total_score += score * weight
        total_weight += weight
    
    # Calculate weighted average
    if total_weight > 0:
        return total_score / total_weight
    else:
        return 0.0

def calculate_review_mastery_score(
    review_history: List[Dict[str, Any]]
) -> float:
    """
    Calculate mastery score based on review history.
    
    Args:
        review_history (List[Dict[str, Any]]): History of reviews
        
    Returns:
        float: Mastery score (0-1)
    """
    if not review_history:
        return 0.0
    
    # Calculate average quality across all reviews
    total_quality = 0.0
    total_weight = 0.0
    
    for review in review_history:
        quality = review.get("quality", 0)
        
        # Normalize quality (0-5) to (0-1)
        normalized_quality = quality / 5.0
        
        # Get timestamp and calculate recency weight
        timestamp = review.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - dt).days
                # More recent reviews have higher weight
                recency_weight = max(0.1, 1.0 - (days_ago / 365))
            except (ValueError, TypeError):
                recency_weight = 1.0
        else:
            recency_weight = 1.0
        
        # Add weighted quality
        total_quality += normalized_quality * recency_weight
        total_weight += recency_weight
    
    # Calculate weighted average
    if total_weight > 0:
        return total_quality / total_weight
    else:
        return 0.0

def calculate_confidence(
    review_history: List[Dict[str, Any]],
    quiz_results: List[Dict[str, Any]],
    spaced_repetition_data: Dict[str, Any]
) -> float:
    """
    Calculate confidence in the mastery score.
    
    Args:
        review_history (List[Dict[str, Any]]): History of reviews
        quiz_results (List[Dict[str, Any]]): Results of quizzes
        spaced_repetition_data (Dict[str, Any]): Spaced repetition data
        
    Returns:
        float: Confidence (0-1)
    """
    # Calculate confidence based on amount and recency of data
    
    # Count data points
    review_count = len(review_history)
    quiz_count = len(quiz_results)
    sr_count = 1 if spaced_repetition_data else 0
    
    # Calculate data count confidence
    total_count = review_count + quiz_count + sr_count
    count_confidence = min(1.0, total_count / 10)  # 10+ data points = full confidence
    
    # Calculate recency confidence
    recency_confidence = 0.0
    recency_count = 0
    
    # Check recency of review history
    for review in review_history:
        timestamp = review.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - dt).days
                # More recent reviews contribute more to confidence
                recency_confidence += max(0.0, 1.0 - (days_ago / 365))
                recency_count += 1
            except (ValueError, TypeError):
                pass
    
    # Check recency of quiz results
    for result in quiz_results:
        timestamp = result.get("timestamp")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - dt).days
                # More recent quizzes contribute more to confidence
                recency_confidence += max(0.0, 1.0 - (days_ago / 365))
                recency_count += 1
            except (ValueError, TypeError):
                pass
    
    # Check recency of spaced repetition data
    if spaced_repetition_data:
        timestamp = spaced_repetition_data.get("last_reviewed")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                days_ago = (datetime.now() - dt).days
                # More recent reviews contribute more to confidence
                recency_confidence += max(0.0, 1.0 - (days_ago / 365))
                recency_count += 1
            except (ValueError, TypeError):
                pass
    
    # Calculate average recency confidence
    if recency_count > 0:
        recency_confidence /= recency_count
    
    # Combine confidences
    confidence = (count_confidence + recency_confidence) / 2
    
    return confidence

def identify_strengths_and_weaknesses(
    review_history: List[Dict[str, Any]],
    quiz_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Identify strengths and weaknesses based on review history and quiz results.
    
    Args:
        review_history (List[Dict[str, Any]]): History of reviews
        quiz_results (List[Dict[str, Any]]): Results of quizzes
        
    Returns:
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: Strengths and weaknesses
    """
    # This would typically analyze quiz results to identify specific topics
    # For now, we'll implement a simplified version
    
    strengths = []
    weaknesses = []
    
    # Analyze quiz results by topic
    topic_scores = {}
    
    for result in quiz_results:
        # Get topic and score
        topic = result.get("topic", "general")
        score = result.get("score", 0.0)
        
        # Add to topic scores
        if topic not in topic_scores:
            topic_scores[topic] = []
        
        topic_scores[topic].append(score)
    
    # Calculate average score for each topic
    for topic, scores in topic_scores.items():
        avg_score = sum(scores) / len(scores)
        
        # Classify as strength or weakness
        if avg_score >= 0.8:
            strengths.append({
                "topic": topic,
                "score": avg_score,
                "confidence": min(1.0, len(scores) / 5)  # 5+ quizzes = full confidence
            })
        elif avg_score <= 0.6:
            weaknesses.append({
                "topic": topic,
                "score": avg_score,
                "confidence": min(1.0, len(scores) / 5)  # 5+ quizzes = full confidence
            })
    
    # Sort strengths and weaknesses by score
    strengths.sort(key=lambda x: x["score"], reverse=True)
    weaknesses.sort(key=lambda x: x["score"])
    
    return strengths, weaknesses

def generate_recommendations(
    mastery_score: float,
    strengths: List[Dict[str, Any]],
    weaknesses: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate recommendations for improvement based on mastery score, strengths, and weaknesses.
    
    Args:
        mastery_score (float): Mastery score
        strengths (List[Dict[str, Any]]): Strengths
        weaknesses (List[Dict[str, Any]]): Weaknesses
        
    Returns:
        List[str]: Recommendations
    """
    recommendations = []
    
    # Recommendations based on mastery score
    if mastery_score < 0.3:
        recommendations.append("Focus on building a solid foundation of the basic concepts.")
        recommendations.append("Consider reviewing the material more frequently.")
    elif mastery_score < 0.7:
        recommendations.append("Continue regular practice to reinforce your understanding.")
        recommendations.append("Focus on areas where you're less confident.")
    else:
        recommendations.append("You have a good understanding of the material.")
        recommendations.append("Consider exploring advanced topics or applications.")
    
    # Recommendations based on weaknesses
    for weakness in weaknesses[:3]:  # Limit to top 3 weaknesses
        topic = weakness["topic"]
        recommendations.append(f"Focus on improving your understanding of {topic}.")
    
    # Recommendations based on strengths
    if strengths:
        topic = strengths[0]["topic"]  # Top strength
        recommendations.append(f"Leverage your strength in {topic} to help understand related topics.")
    
    return recommendations