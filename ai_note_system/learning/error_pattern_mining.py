"""
Error Pattern Mining module for AI Note System.
Tracks mistakes across different learning activities, identifies patterns,
and suggests targeted interventions.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Setup logging
logger = logging.getLogger("ai_note_system.learning.error_pattern_mining")

# Import required modules
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import get_llm_interface

class ErrorPatternMiner:
    """
    Mines error patterns across different learning activities.
    Identifies recurring conceptual gaps and suggests targeted interventions.
    """
    
    def __init__(
        self,
        user_id: str,
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4"
    ):
        """
        Initialize the Error Pattern Miner.
        
        Args:
            user_id (str): ID of the user
            db_manager (DatabaseManager, optional): Database manager instance
            llm_provider (str): LLM provider to use for analysis
            llm_model (str): LLM model to use for analysis
        """
        self.user_id = user_id
        self.db_manager = db_manager
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Create directory for storing error data if it doesn't exist
        self.data_dir = os.path.join("data", "error_patterns", user_id)
        os.makedirs(self.data_dir, exist_ok=True)
        
        logger.info(f"Initialized Error Pattern Miner for user {user_id}")
    
    def track_error(
        self,
        activity_type: str,
        topic: str,
        error_description: str,
        context: Optional[Dict[str, Any]] = None,
        severity: int = 1,
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track an error or mistake.
        
        Args:
            activity_type (str): Type of learning activity (quiz, recall, explanation, etc.)
            topic (str): Topic or subject area
            error_description (str): Description of the error or mistake
            context (Dict[str, Any], optional): Additional context about the error
            severity (int): Severity of the error (1-5)
            timestamp (str, optional): Timestamp of the error (ISO format)
            
        Returns:
            Dict[str, Any]: The tracked error data
        """
        logger.info(f"Tracking error in {activity_type} for topic: {topic}")
        
        # Create error data
        error_data = {
            "user_id": self.user_id,
            "activity_type": activity_type,
            "topic": topic,
            "error_description": error_description,
            "context": context or {},
            "severity": max(1, min(5, severity)),  # Ensure severity is between 1-5
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        # Save error data
        self._save_error(error_data)
        
        return error_data
    
    def _save_error(self, error_data: Dict[str, Any]) -> None:
        """
        Save error data to storage.
        
        Args:
            error_data (Dict[str, Any]): Error data to save
        """
        try:
            # Generate a unique filename
            timestamp = datetime.fromisoformat(error_data["timestamp"])
            filename = f"error_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(error_data, f, indent=2)
            
            logger.debug(f"Saved error data to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving error data: {e}")
    
    def get_errors(
        self,
        activity_type: Optional[str] = None,
        topic: Optional[str] = None,
        days: int = 30,
        min_severity: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get errors matching the specified criteria.
        
        Args:
            activity_type (str, optional): Filter by activity type
            topic (str, optional): Filter by topic
            days (int): Number of days to look back
            min_severity (int): Minimum severity level
            
        Returns:
            List[Dict[str, Any]]: List of matching errors
        """
        try:
            # Calculate cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get all error files
            errors = []
            for filename in os.listdir(self.data_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.data_dir, filename)
                
                try:
                    with open(filepath, 'r') as f:
                        error_data = json.load(f)
                    
                    # Apply filters
                    if error_data.get("timestamp", "") < cutoff_date:
                        continue
                    
                    if activity_type and error_data.get("activity_type") != activity_type:
                        continue
                    
                    if topic and error_data.get("topic") != topic:
                        continue
                    
                    if error_data.get("severity", 0) < min_severity:
                        continue
                    
                    errors.append(error_data)
                    
                except Exception as e:
                    logger.error(f"Error reading file {filepath}: {e}")
            
            # Sort by timestamp (newest first)
            errors.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return errors
            
        except Exception as e:
            logger.error(f"Error getting errors: {e}")
            return []
    
    def mine_patterns(
        self,
        days: int = 90,
        min_cluster_size: int = 3,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Mine patterns in errors using clustering.
        
        Args:
            days (int): Number of days to look back
            min_cluster_size (int): Minimum number of errors to form a cluster
            min_similarity (float): Minimum similarity threshold (0-1)
            
        Returns:
            List[Dict[str, Any]]: List of identified error patterns
        """
        logger.info(f"Mining error patterns for user {self.user_id}")
        
        # Get all errors within the time period
        errors = self.get_errors(days=days)
        
        if len(errors) < min_cluster_size:
            logger.info(f"Not enough errors to mine patterns (found {len(errors)}, need at least {min_cluster_size})")
            return []
        
        # Extract features for clustering
        features = self._extract_features(errors)
        
        # Perform clustering
        clusters = self._cluster_errors(errors, features, min_cluster_size, min_similarity)
        
        # Analyze clusters to identify patterns
        patterns = self._analyze_clusters(clusters)
        
        return patterns
    
    def _extract_features(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract features from errors for clustering.
        
        Args:
            errors (List[Dict[str, Any]]): List of errors
            
        Returns:
            List[Dict[str, Any]]: List of feature dictionaries
        """
        features = []
        
        for error in errors:
            # Extract basic features
            feature = {
                "activity_type": error.get("activity_type", ""),
                "topic": error.get("topic", ""),
                "severity": error.get("severity", 1),
                "error_text": error.get("error_description", ""),
                "timestamp": error.get("timestamp", "")
            }
            
            # Add context features if available
            context = error.get("context", {})
            if context:
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        feature[f"context_{key}"] = value
            
            features.append(feature)
        
        return features
    
    def _cluster_errors(
        self,
        errors: List[Dict[str, Any]],
        features: List[Dict[str, Any]],
        min_cluster_size: int,
        min_similarity: float
    ) -> List[Dict[str, Any]]:
        """
        Cluster errors based on features.
        
        Args:
            errors (List[Dict[str, Any]]): List of errors
            features (List[Dict[str, Any]]): List of feature dictionaries
            min_cluster_size (int): Minimum number of errors to form a cluster
            min_similarity (float): Minimum similarity threshold (0-1)
            
        Returns:
            List[Dict[str, Any]]: List of clusters
        """
        # This is a simplified clustering implementation
        # In a real implementation, you would use a more sophisticated algorithm
        # such as DBSCAN, HDBSCAN, or a semantic clustering approach with embeddings
        
        # Group by topic and activity type first
        groups = defaultdict(list)
        for i, feature in enumerate(features):
            key = (feature.get("topic", ""), feature.get("activity_type", ""))
            groups[key].append((i, feature, errors[i]))
        
        # For each group, cluster by error similarity
        clusters = []
        
        for (topic, activity_type), group in groups.items():
            if len(group) < min_cluster_size:
                continue
            
            # Simple clustering based on text similarity
            # In a real implementation, you would use embeddings and proper clustering
            remaining = set(range(len(group)))
            
            while remaining:
                # Start a new cluster
                seed_idx = next(iter(remaining))
                seed_error_text = group[seed_idx][1].get("error_text", "")
                
                # Find similar errors
                cluster_indices = {seed_idx}
                for i in remaining - {seed_idx}:
                    error_text = group[i][1].get("error_text", "")
                    similarity = self._text_similarity(seed_error_text, error_text)
                    
                    if similarity >= min_similarity:
                        cluster_indices.add(i)
                
                # If cluster is large enough, add it
                if len(cluster_indices) >= min_cluster_size:
                    cluster_errors = [group[i][2] for i in cluster_indices]
                    clusters.append({
                        "topic": topic,
                        "activity_type": activity_type,
                        "errors": cluster_errors,
                        "size": len(cluster_errors)
                    })
                
                # Remove processed indices
                remaining -= cluster_indices
        
        return clusters
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        # This is a very simple similarity measure
        # In a real implementation, you would use embeddings or a more sophisticated approach
        
        # Convert to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Calculate Jaccard similarity
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union
    
    def _analyze_clusters(self, clusters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze clusters to identify patterns and suggest interventions.
        
        Args:
            clusters (List[Dict[str, Any]]): List of error clusters
            
        Returns:
            List[Dict[str, Any]]: List of identified patterns with interventions
        """
        patterns = []
        
        for i, cluster in enumerate(clusters):
            # Extract key information from the cluster
            topic = cluster.get("topic", "")
            activity_type = cluster.get("activity_type", "")
            errors = cluster.get("errors", [])
            
            # Combine error descriptions for analysis
            error_descriptions = [error.get("error_description", "") for error in errors]
            combined_description = "\n".join(error_descriptions)
            
            # Use LLM to analyze the pattern
            pattern_analysis = self._analyze_pattern_with_llm(
                topic=topic,
                activity_type=activity_type,
                error_descriptions=error_descriptions
            )
            
            # Create pattern object
            pattern = {
                "id": i + 1,
                "topic": topic,
                "activity_type": activity_type,
                "error_count": len(errors),
                "pattern_name": pattern_analysis.get("pattern_name", f"Pattern {i+1}"),
                "description": pattern_analysis.get("description", ""),
                "root_causes": pattern_analysis.get("root_causes", []),
                "interventions": pattern_analysis.get("interventions", []),
                "false_fluency": pattern_analysis.get("false_fluency", False),
                "sample_errors": error_descriptions[:3]  # Include a few sample errors
            }
            
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_pattern_with_llm(
        self,
        topic: str,
        activity_type: str,
        error_descriptions: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze an error pattern using LLM.
        
        Args:
            topic (str): Topic of the errors
            activity_type (str): Type of learning activity
            error_descriptions (List[str]): List of error descriptions
            
        Returns:
            Dict[str, Any]: Analysis of the pattern
        """
        logger.info(f"Analyzing error pattern in {topic} ({activity_type})")
        
        # Define the schema for structured output
        analysis_schema = {
            "type": "object",
            "properties": {
                "pattern_name": {
                    "type": "string",
                    "description": "A concise, descriptive name for this error pattern"
                },
                "description": {
                    "type": "string",
                    "description": "A detailed description of the error pattern"
                },
                "root_causes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of potential root causes for this error pattern"
                },
                "conceptual_gaps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific conceptual gaps or misunderstandings"
                },
                "false_fluency": {
                    "type": "boolean",
                    "description": "Whether this pattern indicates false fluency (content the user thinks they know but fails in application)"
                },
                "interventions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of targeted interventions to address this error pattern"
                }
            }
        }
        
        # Create the prompt for analysis
        sample_errors = "\n".join([f"- {desc}" for desc in error_descriptions[:5]])
        
        analysis_prompt = f"""
        Analyze the following pattern of errors made by a learner in the topic of {topic} during {activity_type} activities.
        
        SAMPLE ERRORS:
        {sample_errors}
        
        Identify the underlying pattern, potential root causes, and suggest targeted interventions.
        Consider whether this pattern indicates "false fluency" - where the learner thinks they understand a concept but fails when applying it.
        
        Provide a concise name for this error pattern, a detailed description, root causes, conceptual gaps, and specific interventions.
        """
        
        try:
            # Generate structured analysis
            analysis = self.llm.generate_structured_output(
                prompt=analysis_prompt,
                output_schema=analysis_schema,
                temperature=0.3
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing pattern: {e}")
            return {
                "pattern_name": f"Error Pattern in {topic}",
                "description": "Could not analyze pattern due to an error.",
                "root_causes": [],
                "conceptual_gaps": [],
                "false_fluency": False,
                "interventions": []
            }
    
    def suggest_interventions(
        self,
        topic: Optional[str] = None,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Suggest interventions based on error patterns.
        
        Args:
            topic (str, optional): Filter by topic
            days (int): Number of days to look back
            
        Returns:
            Dict[str, Any]: Suggested interventions
        """
        logger.info(f"Suggesting interventions for user {self.user_id}")
        
        # Mine patterns
        patterns = self.mine_patterns(days=days)
        
        # Filter by topic if specified
        if topic:
            patterns = [p for p in patterns if p.get("topic") == topic]
        
        if not patterns:
            return {
                "user_id": self.user_id,
                "timestamp": datetime.now().isoformat(),
                "patterns": [],
                "interventions": []
            }
        
        # Extract interventions from patterns
        all_interventions = []
        for pattern in patterns:
            interventions = pattern.get("interventions", [])
            for intervention in interventions:
                all_interventions.append({
                    "pattern_name": pattern.get("pattern_name", ""),
                    "topic": pattern.get("topic", ""),
                    "intervention": intervention
                })
        
        # Prioritize interventions
        prioritized_interventions = self._prioritize_interventions(all_interventions)
        
        return {
            "user_id": self.user_id,
            "timestamp": datetime.now().isoformat(),
            "patterns": patterns,
            "interventions": prioritized_interventions
        }
    
    def _prioritize_interventions(
        self,
        interventions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize interventions based on relevance and impact.
        
        Args:
            interventions (List[Dict[str, Any]]): List of interventions
            
        Returns:
            List[Dict[str, Any]]: Prioritized interventions
        """
        # This is a simplified implementation
        # In a real implementation, you would use a more sophisticated approach
        
        # Group by topic
        topic_interventions = defaultdict(list)
        for intervention in interventions:
            topic = intervention.get("topic", "")
            topic_interventions[topic].append(intervention)
        
        # Take top interventions from each topic
        prioritized = []
        for topic, topic_list in topic_interventions.items():
            # Add up to 3 interventions per topic
            prioritized.extend(topic_list[:3])
        
        return prioritized


def main():
    """
    Command-line interface for the Error Pattern Miner.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Error Pattern Mining")
    parser.add_argument("--user", required=True, help="User ID")
    parser.add_argument("--action", choices=["track", "mine", "suggest"], required=True, help="Action to perform")
    parser.add_argument("--activity", help="Activity type (for track action)")
    parser.add_argument("--topic", help="Topic (for track action)")
    parser.add_argument("--error", help="Error description (for track action)")
    parser.add_argument("--severity", type=int, default=1, help="Error severity (1-5, for track action)")
    parser.add_argument("--days", type=int, default=90, help="Number of days to look back (for mine and suggest actions)")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Initialize miner
    miner = ErrorPatternMiner(
        user_id=args.user,
        llm_provider=args.llm,
        llm_model=args.model
    )
    
    # Perform action
    if args.action == "track":
        if not args.activity or not args.topic or not args.error:
            print("Error: activity, topic, and error are required for track action")
            return
        
        result = miner.track_error(
            activity_type=args.activity,
            topic=args.topic,
            error_description=args.error,
            severity=args.severity
        )
        
        print(f"Tracked error: {result}")
        
    elif args.action == "mine":
        patterns = miner.mine_patterns(days=args.days)
        
        print(f"Found {len(patterns)} error patterns:")
        for pattern in patterns:
            print(f"\n{pattern['pattern_name']} ({pattern['topic']}, {pattern['error_count']} errors)")
            print(f"Description: {pattern['description']}")
            print("Root causes:")
            for cause in pattern['root_causes']:
                print(f"- {cause}")
            print("Interventions:")
            for intervention in pattern['interventions']:
                print(f"- {intervention}")
        
    elif args.action == "suggest":
        result = miner.suggest_interventions(topic=args.topic, days=args.days)
        
        print(f"Suggested interventions based on {len(result['patterns'])} patterns:")
        for intervention in result['interventions']:
            print(f"\n[{intervention['topic']}] {intervention['pattern_name']}")
            print(f"- {intervention['intervention']}")


if __name__ == "__main__":
    main()