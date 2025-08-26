"""
Spaced repetition module for AI Note System.
Handles scheduling and tracking of spaced repetition reviews.
"""

import os
import logging
import json
import math
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.spaced_repetition")

class SpacedRepetition:
    """
    Spaced repetition scheduler class.
    Implements the SM-2 algorithm for spaced repetition scheduling.
    """
    
    def __init__(self, db_manager=None):
        """
        Initialize the spaced repetition scheduler.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def schedule_review(
        self,
        item_id: str,
        quality: int,
        item_type: str = "note",
        algorithm: str = "SM-2",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a review for an item based on the quality of recall.
        
        Args:
            item_id (str): ID of the item to schedule
            quality (int): Quality of recall (0-5)
            item_type (str): Type of item (note, question, etc.)
            algorithm (str): Spaced repetition algorithm to use
            metadata (Dict[str, Any], optional): Additional metadata
            
        Returns:
            Dict[str, Any]: Updated review data
        """
        logger.info(f"Scheduling review for {item_type} {item_id}")
        
        # Get existing review data if available
        review_data = self.get_review_data(item_id, item_type)
        
        # Update review data based on algorithm
        if algorithm == "SM-2":
            updated_data = self.sm2_algorithm(review_data, quality)
        elif algorithm == "Leitner":
            updated_data = self.leitner_algorithm(review_data, quality)
        else:
            logger.warning(f"Unknown algorithm: {algorithm}, falling back to SM-2")
            updated_data = self.sm2_algorithm(review_data, quality)
        
        # Add metadata if provided
        if metadata:
            updated_data.update(metadata)
        
        # Save updated review data
        self.save_review_data(item_id, item_type, updated_data)
        
        return updated_data
    
    def get_review_data(self, item_id: str, item_type: str = "note") -> Dict[str, Any]:
        """
        Get review data for an item.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            Dict[str, Any]: Review data
        """
        # If database manager is available, use it
        if self.db_manager:
            return self.get_review_data_from_db(item_id, item_type)
        
        # Otherwise, use a simple file-based approach
        return self.get_review_data_from_file(item_id, item_type)
    
    def get_review_data_from_db(self, item_id: str, item_type: str = "note") -> Dict[str, Any]:
        """
        Get review data for an item from the database.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            Dict[str, Any]: Review data
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
                "next_review": datetime.now().isoformat(),
                "box": 0  # For Leitner system
            }
            
        except Exception as e:
            logger.error(f"Error getting review data from database: {str(e)}")
            return self.get_default_review_data(item_id, item_type)
    
    def get_review_data_from_file(self, item_id: str, item_type: str = "note") -> Dict[str, Any]:
        """
        Get review data for an item from a file.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            Dict[str, Any]: Review data
        """
        try:
            # Create a file path for the review data
            file_path = self.get_review_data_path(item_id, item_type)
            
            # Check if the file exists
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # If the file doesn't exist, return default values
            return self.get_default_review_data(item_id, item_type)
            
        except Exception as e:
            logger.error(f"Error getting review data from file: {str(e)}")
            return self.get_default_review_data(item_id, item_type)
    
    def get_default_review_data(self, item_id: str, item_type: str = "note") -> Dict[str, Any]:
        """
        Get default review data for a new item.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            Dict[str, Any]: Default review data
        """
        return {
            "item_id": item_id,
            "item_type": item_type,
            "easiness_factor": 2.5,
            "interval": 0,
            "repetitions": 0,
            "review_count": 0,
            "last_reviewed": None,
            "next_review": datetime.now().isoformat(),
            "box": 0  # For Leitner system
        }
    
    def save_review_data(self, item_id: str, item_type: str, data: Dict[str, Any]) -> bool:
        """
        Save review data for an item.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            data (Dict[str, Any]): Review data
            
        Returns:
            bool: True if successful, False otherwise
        """
        # If database manager is available, use it
        if self.db_manager:
            return self.save_review_data_to_db(item_id, item_type, data)
        
        # Otherwise, use a simple file-based approach
        return self.save_review_data_to_file(item_id, item_type, data)
    
    def save_review_data_to_db(self, item_id: str, item_type: str, data: Dict[str, Any]) -> bool:
        """
        Save review data for an item to the database.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            data (Dict[str, Any]): Review data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a placeholder for database integration
            # In a real implementation, this would update the database
            
            logger.debug(f"Review data for {item_type} {item_id} saved to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving review data to database: {str(e)}")
            return False
    
    def save_review_data_to_file(self, item_id: str, item_type: str, data: Dict[str, Any]) -> bool:
        """
        Save review data for an item to a file.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            data (Dict[str, Any]): Review data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create a file path for the review data
            file_path = self.get_review_data_path(item_id, item_type)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the data to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Review data for {item_type} {item_id} saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving review data to file: {str(e)}")
            return False
    
    def get_review_data_path(self, item_id: str, item_type: str) -> str:
        """
        Get the file path for review data.
        
        Args:
            item_id (str): ID of the item
            item_type (str): Type of item (note, question, etc.)
            
        Returns:
            str: File path
        """
        # Get the path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(current_dir))
        data_dir = os.path.join(project_dir, "data", "spaced_repetition")
        
        # Create a file name based on item type and ID
        file_name = f"{item_type}_{item_id}.json"
        
        return os.path.join(data_dir, file_name)
    
    def sm2_algorithm(self, review_data: Dict[str, Any], quality: int) -> Dict[str, Any]:
        """
        Implement the SM-2 algorithm for spaced repetition.
        
        Args:
            review_data (Dict[str, Any]): Current review data
            quality (int): Quality of recall (0-5)
            
        Returns:
            Dict[str, Any]: Updated review data
        """
        # Extract current values
        easiness_factor = review_data.get("easiness_factor", 2.5)
        interval = review_data.get("interval", 0)
        repetitions = review_data.get("repetitions", 0)
        review_count = review_data.get("review_count", 0)
        
        # Ensure quality is in range 0-5
        quality = max(0, min(5, quality))
        
        # Update review count
        review_count += 1
        
        # Calculate new values based on quality
        if quality < 3:
            # If quality is less than 3, reset repetitions
            repetitions = 0
            interval = 1
        else:
            # Otherwise, increment repetitions and calculate new interval
            repetitions += 1
            
            if repetitions == 1:
                interval = 1
            elif repetitions == 2:
                interval = 6
            else:
                interval = round(interval * easiness_factor)
        
        # Update easiness factor
        easiness_factor = max(1.3, easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        
        # Calculate next review date
        last_reviewed = datetime.now()
        next_review = last_reviewed + timedelta(days=interval)
        
        # Update review data
        updated_data = review_data.copy()
        updated_data.update({
            "easiness_factor": easiness_factor,
            "interval": interval,
            "repetitions": repetitions,
            "review_count": review_count,
            "last_reviewed": last_reviewed.isoformat(),
            "next_review": next_review.isoformat()
        })
        
        return updated_data
    
    def leitner_algorithm(self, review_data: Dict[str, Any], quality: int) -> Dict[str, Any]:
        """
        Implement the Leitner system for spaced repetition.
        
        Args:
            review_data (Dict[str, Any]): Current review data
            quality (int): Quality of recall (0-5)
            
        Returns:
            Dict[str, Any]: Updated review data
        """
        # Extract current values
        box = review_data.get("box", 0)
        review_count = review_data.get("review_count", 0)
        
        # Ensure quality is in range 0-5
        quality = max(0, min(5, quality))
        
        # Update review count
        review_count += 1
        
        # Update box based on quality
        if quality < 3:
            # If quality is less than 3, move back to box 0
            box = max(0, box - 1)
        else:
            # Otherwise, move to the next box
            box += 1
        
        # Calculate next review date based on box
        last_reviewed = datetime.now()
        
        # Box intervals: 1 day, 3 days, 7 days, 14 days, 30 days, 90 days
        intervals = [1, 3, 7, 14, 30, 90]
        
        # Ensure box is in range
        box = min(box, len(intervals) - 1)
        
        # Calculate next review date
        next_review = last_reviewed + timedelta(days=intervals[box])
        
        # Update review data
        updated_data = review_data.copy()
        updated_data.update({
            "box": box,
            "review_count": review_count,
            "last_reviewed": last_reviewed.isoformat(),
            "next_review": next_review.isoformat()
        })
        
        return updated_data
    
    def get_due_items(self, item_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get items that are due for review.
        
        Args:
            item_type (str, optional): Type of item to filter by
            limit (int): Maximum number of items to return
            
        Returns:
            List[Dict[str, Any]]: List of due items
        """
        # If database manager is available, use it
        if self.db_manager:
            return self.get_due_items_from_db(item_type, limit)
        
        # Otherwise, use a simple file-based approach
        return self.get_due_items_from_files(item_type, limit)
    
    def get_due_items_from_db(self, item_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get items that are due for review from the database.
        
        Args:
            item_type (str, optional): Type of item to filter by
            limit (int): Maximum number of items to return
            
        Returns:
            List[Dict[str, Any]]: List of due items
        """
        try:
            # This is a placeholder for database integration
            # In a real implementation, this would query the database
            
            # For now, return an empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting due items from database: {str(e)}")
            return []
    
    def get_due_items_from_files(self, item_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get items that are due for review from files.
        
        Args:
            item_type (str, optional): Type of item to filter by
            limit (int): Maximum number of items to return
            
        Returns:
            List[Dict[str, Any]]: List of due items
        """
        try:
            # Get the path to the data directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(os.path.dirname(current_dir))
            data_dir = os.path.join(project_dir, "data", "spaced_repetition")
            
            # Ensure directory exists
            if not os.path.exists(data_dir):
                return []
            
            # Get all review data files
            files = os.listdir(data_dir)
            
            # Filter by item type if specified
            if item_type:
                files = [f for f in files if f.startswith(f"{item_type}_")]
            
            # Load review data from each file
            due_items = []
            now = datetime.now()
            
            for file in files:
                file_path = os.path.join(data_dir, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Check if the item is due
                    next_review = datetime.fromisoformat(data.get("next_review", "2099-12-31T00:00:00"))
                    
                    if next_review <= now:
                        due_items.append(data)
                        
                        # Stop if we've reached the limit
                        if len(due_items) >= limit:
                            break
                
                except Exception as e:
                    logger.error(f"Error loading review data from {file_path}: {str(e)}")
                    continue
            
            # Sort by next review date
            due_items.sort(key=lambda x: x.get("next_review", "2099-12-31T00:00:00"))
            
            return due_items
            
        except Exception as e:
            logger.error(f"Error getting due items from files: {str(e)}")
            return []
    
    def calculate_mastery_score(self, review_data: Dict[str, Any]) -> float:
        """
        Calculate a mastery score based on review data.
        
        Args:
            review_data (Dict[str, Any]): Review data
            
        Returns:
            float: Mastery score (0-1)
        """
        # Extract values
        easiness_factor = review_data.get("easiness_factor", 2.5)
        repetitions = review_data.get("repetitions", 0)
        review_count = review_data.get("review_count", 0)
        box = review_data.get("box", 0)
        
        # Calculate score based on algorithm
        if "box" in review_data:
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
            
            # Combine scores
            score = (ef_score + rep_score) / 2
        
        return score

def schedule_review(
    item_id: str,
    quality: int,
    item_type: str = "note",
    algorithm: str = "SM-2",
    db_manager=None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Schedule a review for an item based on the quality of recall.
    
    Args:
        item_id (str): ID of the item to schedule
        quality (int): Quality of recall (0-5)
        item_type (str): Type of item (note, question, etc.)
        algorithm (str): Spaced repetition algorithm to use
        db_manager: Database manager instance
        metadata (Dict[str, Any], optional): Additional metadata
        
    Returns:
        Dict[str, Any]: Updated review data
    """
    sr = SpacedRepetition(db_manager)
    return sr.schedule_review(item_id, quality, item_type, algorithm, metadata)

def get_due_items(
    item_type: Optional[str] = None,
    limit: int = 100,
    db_manager=None
) -> List[Dict[str, Any]]:
    """
    Get items that are due for review.
    
    Args:
        item_type (str, optional): Type of item to filter by
        limit (int): Maximum number of items to return
        db_manager: Database manager instance
        
    Returns:
        List[Dict[str, Any]]: List of due items
    """
    sr = SpacedRepetition(db_manager)
    return sr.get_due_items(item_type, limit)

def calculate_mastery_score(
    review_data: Dict[str, Any]
) -> float:
    """
    Calculate a mastery score based on review data.
    
    Args:
        review_data (Dict[str, Any]): Review data
        
    Returns:
        float: Mastery score (0-1)
    """
    sr = SpacedRepetition()
    return sr.calculate_mastery_score(review_data)