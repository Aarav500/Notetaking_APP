"""
Content Difficulty Estimator module for AI Note System.
Estimates the difficulty level of imported content and organizes notes by difficulty.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.learning.content_difficulty_estimator")

class DifficultyLevel:
    """
    Enum-like class for difficulty levels.
    """
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentDifficultyEstimator:
    """
    Estimates the difficulty level of content and organizes notes by difficulty.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the content difficulty estimator.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self._ensure_difficulty_table()
    
    def _ensure_difficulty_table(self) -> None:
        """
        Ensure the difficulty-related tables exist in the database.
        """
        # Create content_difficulty table
        difficulty_query = """
        CREATE TABLE IF NOT EXISTS content_difficulty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            difficulty_level TEXT NOT NULL,
            confidence REAL,
            estimated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            UNIQUE(note_id)
        )
        """
        self.db_manager.execute_query(difficulty_query)
        
        # Create difficulty_criteria table
        criteria_query = """
        CREATE TABLE IF NOT EXISTS difficulty_criteria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            beginner_threshold REAL,
            intermediate_threshold REAL,
            advanced_threshold REAL,
            weight REAL DEFAULT 1.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute_query(criteria_query)
        
        # Insert default criteria if not exists
        self._insert_default_criteria()
    
    def _insert_default_criteria(self) -> None:
        """
        Insert default difficulty criteria if they don't exist.
        """
        # Check if criteria already exist
        check_query = "SELECT COUNT(*) as count FROM difficulty_criteria"
        result = self.db_manager.execute_query(check_query).fetchone()
        
        if result and result["count"] > 0:
            return
        
        # Define default criteria
        default_criteria = [
            {
                "name": "vocabulary_complexity",
                "description": "Complexity of vocabulary used in the content",
                "beginner_threshold": 0.3,
                "intermediate_threshold": 0.6,
                "advanced_threshold": 0.8,
                "weight": 1.0
            },
            {
                "name": "concept_density",
                "description": "Density of concepts per paragraph",
                "beginner_threshold": 0.3,
                "intermediate_threshold": 0.6,
                "advanced_threshold": 0.8,
                "weight": 1.2
            },
            {
                "name": "prerequisite_knowledge",
                "description": "Amount of prerequisite knowledge required",
                "beginner_threshold": 0.2,
                "intermediate_threshold": 0.5,
                "advanced_threshold": 0.75,
                "weight": 1.5
            },
            {
                "name": "abstraction_level",
                "description": "Level of abstraction in the content",
                "beginner_threshold": 0.3,
                "intermediate_threshold": 0.6,
                "advanced_threshold": 0.8,
                "weight": 1.0
            },
            {
                "name": "technical_terminology",
                "description": "Amount of technical terminology used",
                "beginner_threshold": 0.25,
                "intermediate_threshold": 0.5,
                "advanced_threshold": 0.75,
                "weight": 1.2
            }
        ]
        
        # Insert default criteria
        for criterion in default_criteria:
            query = """
            INSERT INTO difficulty_criteria 
            (name, description, beginner_threshold, intermediate_threshold, advanced_threshold, weight)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(query, (
                criterion["name"],
                criterion["description"],
                criterion["beginner_threshold"],
                criterion["intermediate_threshold"],
                criterion["advanced_threshold"],
                criterion["weight"]
            ))
        
        logger.info(f"Inserted {len(default_criteria)} default difficulty criteria")
    
    def estimate_difficulty(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate the difficulty level of content.
        
        Args:
            content (Dict[str, Any]): Content to analyze
            
        Returns:
            Dict[str, Any]: Difficulty estimation result
        """
        logger.info("Estimating content difficulty")
        
        # Get content text
        text = content.get("text", "")
        summary = content.get("summary", "")
        title = content.get("title", "")
        
        # Use summary if available, otherwise use text
        content_text = summary if summary else text
        
        if not content_text:
            logger.warning("No content text available for difficulty estimation")
            return {
                "status": "error",
                "message": "No content text available for difficulty estimation"
            }
        
        # Get difficulty criteria
        criteria = self._get_difficulty_criteria()
        
        # Analyze content difficulty using LLM
        difficulty_scores = self._analyze_content_difficulty(content_text, title, criteria)
        
        # Calculate overall difficulty
        overall_difficulty, confidence = self._calculate_overall_difficulty(difficulty_scores)
        
        # Store difficulty if note_id is provided
        note_id = content.get("id")
        if note_id:
            self._store_difficulty(note_id, overall_difficulty, confidence)
        
        # Create result
        result = {
            "status": "success",
            "difficulty_level": overall_difficulty,
            "confidence": confidence,
            "criteria_scores": difficulty_scores
        }
        
        logger.info(f"Estimated difficulty level: {overall_difficulty} (confidence: {confidence:.2f})")
        return result
    
    def _get_difficulty_criteria(self) -> List[Dict[str, Any]]:
        """
        Get difficulty criteria from the database.
        
        Returns:
            List[Dict[str, Any]]: List of difficulty criteria
        """
        query = "SELECT * FROM difficulty_criteria ORDER BY id"
        results = self.db_manager.execute_query(query).fetchall()
        
        criteria = [dict(result) for result in results]
        return criteria
    
    def _analyze_content_difficulty(self, content_text: str, title: str, criteria: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Analyze content difficulty using LLM.
        
        Args:
            content_text (str): Content text to analyze
            title (str): Content title
            criteria (List[Dict[str, Any]]): Difficulty criteria
            
        Returns:
            Dict[str, float]: Difficulty scores for each criterion
        """
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        criteria_descriptions = "\n".join([
            f"- {criterion['name']}: {criterion['description']}"
            for criterion in criteria
        ])
        
        prompt = f"""
        Analyze the difficulty level of the following content based on these criteria:
        
        {criteria_descriptions}
        
        For each criterion, provide a score from 0.0 to 1.0, where:
        - 0.0 to 0.3: Beginner level
        - 0.3 to 0.6: Intermediate level
        - 0.6 to 0.8: Advanced level
        - 0.8 to 1.0: Expert level
        
        Content Title: {title}
        
        Content:
        {content_text[:2000]}...
        
        Format your response as a JSON object with criterion names as keys and scores as values.
        Include a brief explanation for each score.
        """
        
        # Generate analysis
        response = llm.generate_text(prompt)
        
        try:
            # Parse response
            analysis = json.loads(response)
            
            # Extract scores
            scores = {}
            for criterion in criteria:
                name = criterion["name"]
                if name in analysis:
                    # If the response includes both score and explanation
                    if isinstance(analysis[name], dict) and "score" in analysis[name]:
                        scores[name] = analysis[name]["score"]
                    # If the response is just the score
                    elif isinstance(analysis[name], (int, float)):
                        scores[name] = float(analysis[name])
                    # Default to 0.5 if format is unexpected
                    else:
                        scores[name] = 0.5
                else:
                    # Default to 0.5 if criterion is missing
                    scores[name] = 0.5
            
            return scores
            
        except Exception as e:
            logger.error(f"Error parsing difficulty analysis: {e}")
            
            # Return default scores
            return {criterion["name"]: 0.5 for criterion in criteria}
    
    def _calculate_overall_difficulty(self, scores: Dict[str, float]) -> Tuple[str, float]:
        """
        Calculate overall difficulty level from individual scores.
        
        Args:
            scores (Dict[str, float]): Difficulty scores for each criterion
            
        Returns:
            Tuple[str, float]: Overall difficulty level and confidence
        """
        # Get criteria with weights
        criteria = self._get_difficulty_criteria()
        
        # Calculate weighted average
        total_weight = 0
        weighted_sum = 0
        
        for criterion in criteria:
            name = criterion["name"]
            weight = criterion["weight"]
            
            if name in scores:
                weighted_sum += scores[name] * weight
                total_weight += weight
        
        # Calculate average score
        avg_score = weighted_sum / total_weight if total_weight > 0 else 0.5
        
        # Determine difficulty level
        if avg_score < 0.3:
            difficulty = DifficultyLevel.BEGINNER
        elif avg_score < 0.6:
            difficulty = DifficultyLevel.INTERMEDIATE
        elif avg_score < 0.8:
            difficulty = DifficultyLevel.ADVANCED
        else:
            difficulty = DifficultyLevel.EXPERT
        
        # Calculate confidence based on variance of scores
        if len(scores) > 1:
            variance = sum((score - avg_score) ** 2 for score in scores.values()) / len(scores)
            # Higher variance means lower confidence
            confidence = max(0.5, 1.0 - variance)
        else:
            confidence = 0.7  # Default confidence
        
        return difficulty, confidence
    
    def _store_difficulty(self, note_id: int, difficulty_level: str, confidence: float) -> None:
        """
        Store difficulty level for a note.
        
        Args:
            note_id (int): ID of the note
            difficulty_level (str): Difficulty level
            confidence (float): Confidence in the estimation
        """
        query = """
        INSERT INTO content_difficulty (note_id, difficulty_level, confidence)
        VALUES (?, ?, ?)
        ON CONFLICT(note_id) 
        DO UPDATE SET difficulty_level = ?, confidence = ?, estimated_at = CURRENT_TIMESTAMP
        """
        
        self.db_manager.execute_query(query, (note_id, difficulty_level, confidence, difficulty_level, confidence))
        logger.debug(f"Stored difficulty level {difficulty_level} for note {note_id}")
    
    def get_note_difficulty(self, note_id: int) -> Optional[Dict[str, Any]]:
        """
        Get difficulty level for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            Optional[Dict[str, Any]]: Difficulty information or None if not found
        """
        query = """
        SELECT * FROM content_difficulty
        WHERE note_id = ?
        """
        
        result = self.db_manager.execute_query(query, (note_id,)).fetchone()
        
        if result:
            return dict(result)
        else:
            return None
    
    def set_note_difficulty(self, note_id: int, difficulty_level: str, confidence: Optional[float] = None) -> bool:
        """
        Manually set difficulty level for a note.
        
        Args:
            note_id (int): ID of the note
            difficulty_level (str): Difficulty level
            confidence (float, optional): Confidence in the estimation
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate difficulty level
        valid_levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        if difficulty_level not in valid_levels:
            logger.error(f"Invalid difficulty level: {difficulty_level}")
            return False
        
        # Use default confidence if not provided
        if confidence is None:
            confidence = 1.0  # High confidence for manual setting
        
        # Store difficulty
        self._store_difficulty(note_id, difficulty_level, confidence)
        
        return True
    
    def organize_by_difficulty(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Organize notes by difficulty level.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Notes organized by difficulty level
        """
        # Get notes with difficulty levels
        query = """
        SELECT n.id, n.title, n.created_at, cd.difficulty_level, cd.confidence
        FROM notes n
        LEFT JOIN content_difficulty cd ON n.id = cd.note_id
        ORDER BY cd.difficulty_level, n.title
        """
        
        results = self.db_manager.execute_query(query).fetchall()
        
        # Organize by difficulty
        organized = {
            DifficultyLevel.BEGINNER: [],
            DifficultyLevel.INTERMEDIATE: [],
            DifficultyLevel.ADVANCED: [],
            DifficultyLevel.EXPERT: [],
            "unknown": []
        }
        
        for result in results:
            note = dict(result)
            difficulty = note.get("difficulty_level")
            
            if difficulty in organized:
                organized[difficulty].append(note)
            else:
                organized["unknown"].append(note)
        
        return organized
    
    def generate_difficulty_analytics(self) -> Dict[str, Any]:
        """
        Generate analytics about note difficulty distribution.
        
        Returns:
            Dict[str, Any]: Difficulty analytics
        """
        # Get difficulty distribution
        query = """
        SELECT difficulty_level, COUNT(*) as count
        FROM content_difficulty
        GROUP BY difficulty_level
        """
        
        results = self.db_manager.execute_query(query).fetchall()
        
        # Create distribution
        distribution = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 0,
            DifficultyLevel.ADVANCED: 0,
            DifficultyLevel.EXPERT: 0
        }
        
        total_notes = 0
        for result in results:
            difficulty = result["difficulty_level"]
            count = result["count"]
            
            if difficulty in distribution:
                distribution[difficulty] = count
                total_notes += count
        
        # Calculate percentages
        percentages = {}
        for level, count in distribution.items():
            percentages[level] = (count / total_notes) * 100 if total_notes > 0 else 0
        
        # Get notes without difficulty estimation
        missing_query = """
        SELECT COUNT(*) as count
        FROM notes n
        LEFT JOIN content_difficulty cd ON n.id = cd.note_id
        WHERE cd.id IS NULL
        """
        
        missing_result = self.db_manager.execute_query(missing_query).fetchone()
        missing_count = missing_result["count"] if missing_result else 0
        
        # Create analytics
        analytics = {
            "distribution": distribution,
            "percentages": percentages,
            "total_notes": total_notes,
            "missing_difficulty": missing_count
        }
        
        return analytics
    
    def generate_learning_path(self, start_level: str = DifficultyLevel.BEGINNER, target_level: str = DifficultyLevel.ADVANCED) -> Dict[str, Any]:
        """
        Generate a learning path based on note difficulty levels.
        
        Args:
            start_level (str): Starting difficulty level
            target_level (str): Target difficulty level
            
        Returns:
            Dict[str, Any]: Generated learning path
        """
        # Validate difficulty levels
        valid_levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        if start_level not in valid_levels or target_level not in valid_levels:
            logger.error(f"Invalid difficulty levels: {start_level} -> {target_level}")
            return {
                "status": "error",
                "message": "Invalid difficulty levels"
            }
        
        # Get difficulty levels in order
        level_order = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 1,
            DifficultyLevel.ADVANCED: 2,
            DifficultyLevel.EXPERT: 3
        }
        
        # Ensure target level is higher than start level
        if level_order[target_level] <= level_order[start_level]:
            logger.error(f"Target level must be higher than start level: {start_level} -> {target_level}")
            return {
                "status": "error",
                "message": "Target level must be higher than start level"
            }
        
        # Get notes for each difficulty level
        levels_to_include = []
        for level, order in level_order.items():
            if level_order[start_level] <= order <= level_order[target_level]:
                levels_to_include.append(level)
        
        # Build query
        placeholders = ", ".join(["?" for _ in levels_to_include])
        query = f"""
        SELECT n.id, n.title, n.summary, n.created_at, cd.difficulty_level, cd.confidence
        FROM notes n
        JOIN content_difficulty cd ON n.id = cd.note_id
        WHERE cd.difficulty_level IN ({placeholders})
        ORDER BY 
            CASE cd.difficulty_level 
                WHEN 'beginner' THEN 1 
                WHEN 'intermediate' THEN 2 
                WHEN 'advanced' THEN 3 
                WHEN 'expert' THEN 4 
                ELSE 5 
            END,
            n.title
        """
        
        results = self.db_manager.execute_query(query, tuple(levels_to_include)).fetchall()
        
        # Organize notes by difficulty
        notes_by_difficulty = {}
        for level in levels_to_include:
            notes_by_difficulty[level] = []
        
        for result in results:
            note = dict(result)
            difficulty = note.get("difficulty_level")
            
            if difficulty in notes_by_difficulty:
                notes_by_difficulty[difficulty].append(note)
        
        # Create learning path
        learning_path = {
            "status": "success",
            "start_level": start_level,
            "target_level": target_level,
            "stages": []
        }
        
        # Add stages for each difficulty level
        for level in levels_to_include:
            notes = notes_by_difficulty[level]
            
            if notes:
                stage = {
                    "difficulty_level": level,
                    "title": f"{level.capitalize()} Level",
                    "description": f"Master {level} concepts and skills",
                    "notes": notes
                }
                
                learning_path["stages"].append(stage)
        
        return learning_path
    
    def filter_notes_by_difficulty(self, difficulty_level: str) -> List[Dict[str, Any]]:
        """
        Filter notes by difficulty level.
        
        Args:
            difficulty_level (str): Difficulty level to filter by
            
        Returns:
            List[Dict[str, Any]]: Filtered notes
        """
        # Validate difficulty level
        valid_levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        if difficulty_level not in valid_levels:
            logger.error(f"Invalid difficulty level: {difficulty_level}")
            return []
        
        # Get notes with the specified difficulty level
        query = """
        SELECT n.id, n.title, n.summary, n.created_at, cd.difficulty_level, cd.confidence
        FROM notes n
        JOIN content_difficulty cd ON n.id = cd.note_id
        WHERE cd.difficulty_level = ?
        ORDER BY n.title
        """
        
        results = self.db_manager.execute_query(query, (difficulty_level,)).fetchall()
        
        notes = [dict(result) for result in results]
        return notes

def estimate_difficulty(db_manager, content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Estimate the difficulty level of content.
    
    Args:
        db_manager: Database manager instance
        content (Dict[str, Any]): Content to analyze
        
    Returns:
        Dict[str, Any]: Difficulty estimation result
    """
    estimator = ContentDifficultyEstimator(db_manager)
    return estimator.estimate_difficulty(content)

def set_difficulty(db_manager, note_id: int, difficulty_level: str) -> bool:
    """
    Manually set difficulty level for a note.
    
    Args:
        db_manager: Database manager instance
        note_id (int): ID of the note
        difficulty_level (str): Difficulty level
        
    Returns:
        bool: True if successful, False otherwise
    """
    estimator = ContentDifficultyEstimator(db_manager)
    return estimator.set_note_difficulty(note_id, difficulty_level)

def organize_by_difficulty(db_manager) -> Dict[str, List[Dict[str, Any]]]:
    """
    Organize notes by difficulty level.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: Notes organized by difficulty level
    """
    estimator = ContentDifficultyEstimator(db_manager)
    return estimator.organize_by_difficulty()

def generate_difficulty_learning_path(db_manager, start_level: str = "beginner", target_level: str = "advanced") -> Dict[str, Any]:
    """
    Generate a learning path based on note difficulty levels.
    
    Args:
        db_manager: Database manager instance
        start_level (str): Starting difficulty level
        target_level (str): Target difficulty level
        
    Returns:
        Dict[str, Any]: Generated learning path
    """
    estimator = ContentDifficultyEstimator(db_manager)
    return estimator.generate_learning_path(start_level, target_level)

def difficulty_analytics(db_manager) -> Dict[str, Any]:
    """
    Generate analytics about note difficulty distribution.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Difficulty analytics
    """
    estimator = ContentDifficultyEstimator(db_manager)
    return estimator.generate_difficulty_analytics()

def filter_notes_by_difficulty(db_manager, difficulty_level: str) -> List[Dict[str, Any]]:
    """
    Filter notes by difficulty level.
    
    Args:
        db_manager: Database manager instance
        difficulty_level (str): Difficulty level to filter by
        
    Returns:
        List[Dict[str, Any]]: Filtered notes
    """
    estimator = ContentDifficultyEstimator(db_manager)
    return estimator.filter_notes_by_difficulty(difficulty_level)