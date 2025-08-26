"""
Adaptive quiz generator module for AI Note System.
Generates quizzes that adapt to the user's mastery level.
"""

import os
import logging
import json
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.processing.ml_enhancements.quiz_adaptive_trainer")

# Import mastery estimator for mastery level calculation
from .mastery_estimator import estimate_mastery

def generate_adaptive_quiz(
    item_id: str,
    content: Dict[str, Any],
    mastery_report: Optional[Dict[str, Any]] = None,
    question_count: int = 5,
    question_types: Optional[List[str]] = None,
    difficulty: Optional[str] = None,
    focus_areas: Optional[List[str]] = None,
    model: str = "gpt-4",
    db_manager=None
) -> Dict[str, Any]:
    """
    Generate an adaptive quiz based on the user's mastery level.
    
    Args:
        item_id (str): ID of the item to generate a quiz for
        content (Dict[str, Any]): The content to generate a quiz from
        mastery_report (Dict[str, Any], optional): Mastery report
        question_count (int): Number of questions to generate
        question_types (List[str], optional): Types of questions to include
        difficulty (str, optional): Difficulty level (easy, medium, hard)
        focus_areas (List[str], optional): Areas to focus on
        model (str): The model to use for generation
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Generated quiz
    """
    logger.info(f"Generating adaptive quiz for item {item_id}")
    
    # Get mastery report if not provided
    if mastery_report is None:
        mastery_report = estimate_mastery(item_id, item_type="note", db_manager=db_manager)
    
    # Set default question types if not provided
    if question_types is None:
        question_types = ["open_ended", "mcq", "fill_blank"]
    
    # Determine difficulty based on mastery level if not provided
    if difficulty is None:
        difficulty = determine_difficulty(mastery_report)
    
    # Determine focus areas based on weaknesses if not provided
    if focus_areas is None:
        focus_areas = determine_focus_areas(mastery_report)
    
    # Generate questions based on difficulty and focus areas
    questions = []
    
    # Distribute questions among question types
    type_counts = distribute_question_types(question_count, question_types)
    
    # Generate questions for each type
    for q_type, count in type_counts.items():
        if q_type == "open_ended":
            new_questions = generate_open_ended_questions(
                content, count, difficulty, focus_areas, model
            )
        elif q_type == "mcq":
            new_questions = generate_mcq_questions(
                content, count, difficulty, focus_areas, model
            )
        elif q_type == "fill_blank":
            new_questions = generate_fill_blank_questions(
                content, count, difficulty, focus_areas, model
            )
        else:
            logger.warning(f"Unknown question type: {q_type}")
            continue
        
        questions.extend(new_questions)
    
    # Shuffle questions
    random.shuffle(questions)
    
    # Create quiz
    quiz = {
        "item_id": item_id,
        "title": content.get("title", "Adaptive Quiz"),
        "difficulty": difficulty,
        "focus_areas": focus_areas,
        "questions": questions,
        "timestamp": datetime.now().isoformat()
    }
    
    return quiz

def determine_difficulty(mastery_report: Dict[str, Any]) -> str:
    """
    Determine appropriate difficulty level based on mastery report.
    
    Args:
        mastery_report (Dict[str, Any]): Mastery report
        
    Returns:
        str: Difficulty level (easy, medium, hard)
    """
    # Extract mastery score
    mastery_score = mastery_report.get("mastery_score", 0.5)
    
    # Determine difficulty based on mastery score
    if mastery_score < 0.3:
        return "easy"
    elif mastery_score < 0.7:
        return "medium"
    else:
        return "hard"

def determine_focus_areas(mastery_report: Dict[str, Any]) -> List[str]:
    """
    Determine focus areas based on weaknesses in mastery report.
    
    Args:
        mastery_report (Dict[str, Any]): Mastery report
        
    Returns:
        List[str]: Focus areas
    """
    # Extract weaknesses
    weaknesses = mastery_report.get("weaknesses", [])
    
    # Use weaknesses as focus areas
    focus_areas = [w["topic"] for w in weaknesses]
    
    # If no weaknesses, use general focus
    if not focus_areas:
        return ["general"]
    
    return focus_areas

def distribute_question_types(
    question_count: int,
    question_types: List[str]
) -> Dict[str, int]:
    """
    Distribute questions among question types.
    
    Args:
        question_count (int): Total number of questions
        question_types (List[str]): Types of questions to include
        
    Returns:
        Dict[str, int]: Number of questions for each type
    """
    # Initialize counts
    type_counts = {q_type: 0 for q_type in question_types}
    
    # Distribute questions evenly
    for i in range(question_count):
        q_type = question_types[i % len(question_types)]
        type_counts[q_type] += 1
    
    return type_counts

def generate_open_ended_questions(
    content: Dict[str, Any],
    count: int,
    difficulty: str,
    focus_areas: List[str],
    model: str
) -> List[Dict[str, Any]]:
    """
    Generate open-ended questions.
    
    Args:
        content (Dict[str, Any]): The content to generate questions from
        count (int): Number of questions to generate
        difficulty (str): Difficulty level (easy, medium, hard)
        focus_areas (List[str]): Areas to focus on
        model (str): The model to use for generation
        
    Returns:
        List[Dict[str, Any]]: Generated questions
    """
    logger.info(f"Generating {count} open-ended questions with difficulty {difficulty}")
    
    # This would typically use an LLM to generate questions
    # For now, we'll implement a simplified version
    
    # Extract text from content
    text = content.get("text", "")
    summary = content.get("summary", "")
    title = content.get("title", "")
    
    # Combine text for analysis
    analysis_text = f"{title}\n\n{summary}\n\n{text}"
    
    # Generate questions based on difficulty
    questions = []
    
    # In a real implementation, this would use an LLM to generate questions
    # For now, we'll return placeholder questions
    for i in range(count):
        focus = focus_areas[i % len(focus_areas)] if focus_areas else "general"
        
        if difficulty == "easy":
            question = f"Explain the basic concept of {focus} in your own words."
            answer = f"This would be an explanation of {focus}."
        elif difficulty == "medium":
            question = f"Compare and contrast different aspects of {focus}."
            answer = f"This would be a comparison of different aspects of {focus}."
        else:  # hard
            question = f"Critically analyze the implications of {focus} in complex scenarios."
            answer = f"This would be a critical analysis of {focus}."
        
        questions.append({
            "type": "open_ended",
            "question": question,
            "answer": answer,
            "difficulty": difficulty,
            "focus_area": focus
        })
    
    return questions

def generate_mcq_questions(
    content: Dict[str, Any],
    count: int,
    difficulty: str,
    focus_areas: List[str],
    model: str
) -> List[Dict[str, Any]]:
    """
    Generate multiple-choice questions.
    
    Args:
        content (Dict[str, Any]): The content to generate questions from
        count (int): Number of questions to generate
        difficulty (str): Difficulty level (easy, medium, hard)
        focus_areas (List[str]): Areas to focus on
        model (str): The model to use for generation
        
    Returns:
        List[Dict[str, Any]]: Generated questions
    """
    logger.info(f"Generating {count} MCQ questions with difficulty {difficulty}")
    
    # This would typically use an LLM to generate questions
    # For now, we'll implement a simplified version
    
    # Extract text from content
    text = content.get("text", "")
    summary = content.get("summary", "")
    title = content.get("title", "")
    
    # Combine text for analysis
    analysis_text = f"{title}\n\n{summary}\n\n{text}"
    
    # Generate questions based on difficulty
    questions = []
    
    # In a real implementation, this would use an LLM to generate questions
    # For now, we'll return placeholder questions
    for i in range(count):
        focus = focus_areas[i % len(focus_areas)] if focus_areas else "general"
        
        if difficulty == "easy":
            question = f"Which of the following best describes {focus}?"
            options = [
                f"A basic description of {focus}",
                f"An incorrect description of {focus}",
                f"A partially correct description of {focus}",
                f"An unrelated concept"
            ]
            answer = options[0]
        elif difficulty == "medium":
            question = f"Which of the following is NOT a characteristic of {focus}?"
            options = [
                f"An incorrect characteristic of {focus}",
                f"A correct characteristic of {focus}",
                f"Another correct characteristic of {focus}",
                f"A third correct characteristic of {focus}"
            ]
            answer = options[0]
        else:  # hard
            question = f"Which of the following statements about {focus} is most accurate in complex scenarios?"
            options = [
                f"A nuanced and accurate statement about {focus}",
                f"A partially correct statement about {focus}",
                f"A common misconception about {focus}",
                f"An oversimplified statement about {focus}"
            ]
            answer = options[0]
        
        questions.append({
            "type": "mcq",
            "question": question,
            "options": options,
            "answer": answer,
            "difficulty": difficulty,
            "focus_area": focus
        })
    
    return questions

def generate_fill_blank_questions(
    content: Dict[str, Any],
    count: int,
    difficulty: str,
    focus_areas: List[str],
    model: str
) -> List[Dict[str, Any]]:
    """
    Generate fill-in-the-blank questions.
    
    Args:
        content (Dict[str, Any]): The content to generate questions from
        count (int): Number of questions to generate
        difficulty (str): Difficulty level (easy, medium, hard)
        focus_areas (List[str]): Areas to focus on
        model (str): The model to use for generation
        
    Returns:
        List[Dict[str, Any]]: Generated questions
    """
    logger.info(f"Generating {count} fill-in-the-blank questions with difficulty {difficulty}")
    
    # This would typically use an LLM to generate questions
    # For now, we'll implement a simplified version
    
    # Extract text from content
    text = content.get("text", "")
    summary = content.get("summary", "")
    title = content.get("title", "")
    
    # Combine text for analysis
    analysis_text = f"{title}\n\n{summary}\n\n{text}"
    
    # Generate questions based on difficulty
    questions = []
    
    # In a real implementation, this would use an LLM to generate questions
    # For now, we'll return placeholder questions
    for i in range(count):
        focus = focus_areas[i % len(focus_areas)] if focus_areas else "general"
        
        if difficulty == "easy":
            question = f"{focus} is a concept that involves _____."
            answer = f"basic principles"
        elif difficulty == "medium":
            question = f"The relationship between {focus} and other concepts can be described as _____."
            answer = f"interconnected"
        else:  # hard
            question = f"In complex scenarios, {focus} demonstrates _____ properties that distinguish it from similar concepts."
            answer = f"unique"
        
        questions.append({
            "type": "fill_blank",
            "text": question,
            "answer": answer,
            "difficulty": difficulty,
            "focus_area": focus
        })
    
    return questions

def save_quiz_results(
    item_id: str,
    quiz_id: str,
    results: Dict[str, Any],
    db_manager=None
) -> Dict[str, Any]:
    """
    Save quiz results.
    
    Args:
        item_id (str): ID of the item
        quiz_id (str): ID of the quiz
        results (Dict[str, Any]): Quiz results
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Result of the save operation
    """
    logger.info(f"Saving quiz results for item {item_id}, quiz {quiz_id}")
    
    # If database manager is available, use it
    if db_manager:
        return save_quiz_results_to_db(item_id, quiz_id, results, db_manager)
    
    # Otherwise, use a simple file-based approach
    return save_quiz_results_to_file(item_id, quiz_id, results)

def save_quiz_results_to_db(
    item_id: str,
    quiz_id: str,
    results: Dict[str, Any],
    db_manager
) -> Dict[str, Any]:
    """
    Save quiz results to the database.
    
    Args:
        item_id (str): ID of the item
        quiz_id (str): ID of the quiz
        results (Dict[str, Any]): Quiz results
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Result of the save operation
    """
    try:
        # This is a placeholder for database integration
        # In a real implementation, this would update the database
        
        logger.debug(f"Quiz results for item {item_id}, quiz {quiz_id} saved to database")
        return {"success": True}
        
    except Exception as e:
        error_msg = f"Error saving quiz results to database: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def save_quiz_results_to_file(
    item_id: str,
    quiz_id: str,
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Save quiz results to a file.
    
    Args:
        item_id (str): ID of the item
        quiz_id (str): ID of the quiz
        results (Dict[str, Any]): Quiz results
        
    Returns:
        Dict[str, Any]: Result of the save operation
    """
    try:
        # Get the path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        data_dir = os.path.join(project_dir, "data", "quiz_results")
        
        # Ensure directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Create a file name based on item ID and quiz ID
        file_name = f"quiz_{item_id}_{quiz_id}.json"
        file_path = os.path.join(data_dir, file_name)
        
        # Save results to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.debug(f"Quiz results saved to {file_path}")
        return {"success": True, "file_path": file_path}
        
    except Exception as e:
        error_msg = f"Error saving quiz results to file: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def analyze_quiz_results(
    results: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze quiz results to provide feedback and recommendations.
    
    Args:
        results (Dict[str, Any]): Quiz results
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    logger.info("Analyzing quiz results")
    
    # Extract quiz data
    questions = results.get("questions", [])
    answers = results.get("answers", [])
    
    if not questions or not answers or len(questions) != len(answers):
        logger.warning("Invalid quiz results format")
        return {
            "score": 0.0,
            "correct_count": 0,
            "total_count": len(questions),
            "topic_scores": {},
            "difficulty_scores": {},
            "recommendations": ["Review the material and try again."]
        }
    
    # Calculate overall score
    correct_count = 0
    topic_scores = {}
    difficulty_scores = {}
    
    for i, (question, answer) in enumerate(zip(questions, answers)):
        # Get question data
        q_type = question.get("type", "unknown")
        q_difficulty = question.get("difficulty", "medium")
        q_focus = question.get("focus_area", "general")
        
        # Check if answer is correct
        is_correct = False
        
        if q_type == "open_ended":
            # For open-ended questions, we would need an LLM to evaluate
            # For now, we'll assume the answer is correct if it's not empty
            is_correct = bool(answer.strip())
        elif q_type == "mcq":
            # For MCQs, check if the selected option matches the correct answer
            is_correct = answer == question.get("answer", "")
        elif q_type == "fill_blank":
            # For fill-in-the-blank, check if the answer matches
            is_correct = answer.lower() == question.get("answer", "").lower()
        
        # Update counts
        if is_correct:
            correct_count += 1
        
        # Update topic scores
        if q_focus not in topic_scores:
            topic_scores[q_focus] = {"correct": 0, "total": 0}
        
        topic_scores[q_focus]["total"] += 1
        if is_correct:
            topic_scores[q_focus]["correct"] += 1
        
        # Update difficulty scores
        if q_difficulty not in difficulty_scores:
            difficulty_scores[q_difficulty] = {"correct": 0, "total": 0}
        
        difficulty_scores[q_difficulty]["total"] += 1
        if is_correct:
            difficulty_scores[q_difficulty]["correct"] += 1
    
    # Calculate overall score
    score = correct_count / len(questions) if questions else 0.0
    
    # Calculate topic scores
    for topic, counts in topic_scores.items():
        counts["score"] = counts["correct"] / counts["total"] if counts["total"] > 0 else 0.0
    
    # Calculate difficulty scores
    for difficulty, counts in difficulty_scores.items():
        counts["score"] = counts["correct"] / counts["total"] if counts["total"] > 0 else 0.0
    
    # Generate recommendations
    recommendations = generate_quiz_recommendations(score, topic_scores, difficulty_scores)
    
    # Create analysis results
    analysis = {
        "score": score,
        "correct_count": correct_count,
        "total_count": len(questions),
        "topic_scores": topic_scores,
        "difficulty_scores": difficulty_scores,
        "recommendations": recommendations
    }
    
    return analysis

def generate_quiz_recommendations(
    score: float,
    topic_scores: Dict[str, Dict[str, Any]],
    difficulty_scores: Dict[str, Dict[str, Any]]
) -> List[str]:
    """
    Generate recommendations based on quiz results.
    
    Args:
        score (float): Overall score
        topic_scores (Dict[str, Dict[str, Any]]): Scores by topic
        difficulty_scores (Dict[str, Dict[str, Any]]): Scores by difficulty
        
    Returns:
        List[str]: Recommendations
    """
    recommendations = []
    
    # Recommendations based on overall score
    if score < 0.3:
        recommendations.append("Review the basic concepts and try again.")
        recommendations.append("Consider focusing on easier questions first.")
    elif score < 0.7:
        recommendations.append("You're making good progress. Continue practicing to improve your understanding.")
        recommendations.append("Focus on the topics where you scored lower.")
    else:
        recommendations.append("Great job! You have a good understanding of the material.")
        recommendations.append("Consider challenging yourself with more difficult questions.")
    
    # Recommendations based on topic scores
    weak_topics = []
    for topic, counts in topic_scores.items():
        if counts["score"] < 0.5 and counts["total"] >= 2:
            weak_topics.append(topic)
    
    if weak_topics:
        topics_str = ", ".join(weak_topics[:3])  # Limit to top 3
        recommendations.append(f"Focus on improving your understanding of: {topics_str}")
    
    # Recommendations based on difficulty scores
    if "hard" in difficulty_scores and difficulty_scores["hard"]["score"] < 0.3:
        recommendations.append("Practice with more challenging questions to improve your advanced understanding.")
    
    if "easy" in difficulty_scores and difficulty_scores["easy"]["score"] < 0.7:
        recommendations.append("Review the fundamental concepts to strengthen your foundation.")
    
    return recommendations