"""
Focused Expression Trainer module for AI Note System.
Provides functionality to analyze and improve written expression.
"""

import os
import json
import logging
import re
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.learning.focused_expression_trainer")

class FocusedExpressionTrainer:
    """
    Focused Expression Trainer class for analyzing and improving written expression.
    Analyzes coherence, structure, depth, and completeness of written answers.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Focused Expression Trainer.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Analysis history
        self.analysis_history = []
        
        # Default evaluation criteria
        self.default_criteria = {
            "coherence": {
                "weight": 0.25,
                "description": "Logical flow and connection between ideas",
                "aspects": [
                    "Clear transitions between ideas",
                    "Consistent argument or narrative",
                    "Logical progression of thoughts"
                ]
            },
            "structure": {
                "weight": 0.20,
                "description": "Organization and formatting of the response",
                "aspects": [
                    "Clear introduction and conclusion",
                    "Appropriate paragraphing",
                    "Use of headings or sections when appropriate"
                ]
            },
            "depth": {
                "weight": 0.30,
                "description": "Level of detail and exploration of the topic",
                "aspects": [
                    "Thorough explanation of concepts",
                    "Use of examples and illustrations",
                    "Consideration of multiple perspectives"
                ]
            },
            "completeness": {
                "weight": 0.25,
                "description": "Coverage of all required aspects of the topic",
                "aspects": [
                    "Addresses all parts of the question",
                    "Includes all key concepts",
                    "No significant omissions"
                ]
            }
        }
        
        logger.debug("Initialized FocusedExpressionTrainer")
    
    def analyze_expression(self, 
                          question: str,
                          answer: str,
                          expected_key_points: Optional[List[str]] = None,
                          custom_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a written answer for expression quality.
        
        Args:
            question (str): The question or prompt
            answer (str): The written answer to analyze
            expected_key_points (List[str], optional): Expected key points to be covered
            custom_criteria (Dict[str, Any], optional): Custom evaluation criteria
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        logger.info("Analyzing written expression")
        
        # Use custom criteria if provided, otherwise use defaults
        criteria = custom_criteria or self.default_criteria
        
        # Initialize analysis result
        analysis = {
            "id": f"analysis_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer_length": len(answer),
            "scores": {},
            "feedback": {},
            "missing_key_points": [],
            "overall_score": 0.0,
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # This would typically use an LLM or NLP model for analysis
        # For now, we'll use a simple rule-based approach
        
        # Analyze coherence
        coherence_score, coherence_feedback = self._analyze_coherence(answer)
        analysis["scores"]["coherence"] = coherence_score
        analysis["feedback"]["coherence"] = coherence_feedback
        
        # Analyze structure
        structure_score, structure_feedback = self._analyze_structure(answer)
        analysis["scores"]["structure"] = structure_score
        analysis["feedback"]["structure"] = structure_feedback
        
        # Analyze depth
        depth_score, depth_feedback = self._analyze_depth(answer)
        analysis["scores"]["depth"] = depth_score
        analysis["feedback"]["depth"] = depth_feedback
        
        # Analyze completeness
        completeness_score, completeness_feedback, missing_points = self._analyze_completeness(
            question, answer, expected_key_points
        )
        analysis["scores"]["completeness"] = completeness_score
        analysis["feedback"]["completeness"] = completeness_feedback
        analysis["missing_key_points"] = missing_points
        
        # Calculate overall score
        overall_score = 0.0
        for criterion, details in criteria.items():
            if criterion in analysis["scores"]:
                overall_score += analysis["scores"][criterion] * details["weight"]
        
        analysis["overall_score"] = round(overall_score, 2)
        
        # Identify strengths and areas for improvement
        for criterion, score in analysis["scores"].items():
            if score >= 0.8:
                analysis["strengths"].append(criterion)
            elif score <= 0.6:
                analysis["areas_for_improvement"].append(criterion)
        
        # Add to history
        self.analysis_history.append({
            "id": analysis["id"],
            "question": question[:50] + "..." if len(question) > 50 else question,
            "timestamp": analysis["timestamp"],
            "overall_score": analysis["overall_score"]
        })
        
        return analysis
    
    def _analyze_coherence(self, text: str) -> tuple:
        """
        Analyze the coherence of a text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            tuple: (score, feedback)
        """
        # This would typically use an LLM or NLP model
        # For now, we'll use simple heuristics
        
        # Count transition words as a simple proxy for coherence
        transition_words = [
            "however", "therefore", "thus", "consequently", "furthermore",
            "moreover", "in addition", "nevertheless", "nonetheless",
            "in contrast", "on the other hand", "similarly", "likewise",
            "for example", "for instance", "specifically", "in particular",
            "in conclusion", "to summarize", "finally"
        ]
        
        # Count paragraphs
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        
        # Count transition words
        transition_count = 0
        for word in transition_words:
            transition_count += len(re.findall(r'\b' + word + r'\b', text.lower()))
        
        # Calculate transition density (transitions per paragraph)
        if len(paragraphs) > 1:
            transition_density = transition_count / (len(paragraphs) - 1)
        else:
            transition_density = 0
        
        # Score based on transition density
        if transition_density >= 1.5:
            score = 0.9
            feedback = "Excellent use of transition words to connect ideas."
        elif transition_density >= 1.0:
            score = 0.8
            feedback = "Good use of transition words, but could be more consistent."
        elif transition_density >= 0.5:
            score = 0.6
            feedback = "Some transitions present, but more needed to improve flow."
        else:
            score = 0.4
            feedback = "Few transitions between ideas. Consider adding more transition words to improve coherence."
        
        return score, feedback
    
    def _analyze_structure(self, text: str) -> tuple:
        """
        Analyze the structure of a text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            tuple: (score, feedback)
        """
        # Count paragraphs
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        
        # Check for headings (lines that end with a colon or are all caps)
        heading_pattern = r'^[A-Z][^a-z]*:|^[A-Z][^a-z]*$'
        headings = [line for line in text.split("\n") if re.match(heading_pattern, line.strip())]
        
        # Check for introduction and conclusion
        has_intro = False
        has_conclusion = False
        
        intro_phrases = ["introduction", "begin", "start", "first", "initially"]
        conclusion_phrases = ["conclusion", "summary", "finally", "in summary", "to conclude", "in conclusion"]
        
        first_paragraph = paragraphs[0].lower() if paragraphs else ""
        last_paragraph = paragraphs[-1].lower() if paragraphs else ""
        
        for phrase in intro_phrases:
            if phrase in first_paragraph:
                has_intro = True
                break
        
        for phrase in conclusion_phrases:
            if phrase in last_paragraph:
                has_conclusion = True
                break
        
        # Score based on structure elements
        score = 0.5  # Base score
        
        # Adjust score based on paragraphing
        if len(paragraphs) >= 3:
            score += 0.2
        elif len(paragraphs) >= 2:
            score += 0.1
        
        # Adjust score based on headings
        if len(headings) >= 2:
            score += 0.1
        
        # Adjust score based on intro/conclusion
        if has_intro:
            score += 0.1
        
        if has_conclusion:
            score += 0.1
        
        # Cap score at 1.0
        score = min(1.0, score)
        
        # Generate feedback
        feedback = []
        
        if len(paragraphs) < 2:
            feedback.append("Consider breaking your answer into multiple paragraphs for better readability.")
        
        if not has_intro:
            feedback.append("Consider adding a clear introduction to set the context.")
        
        if not has_conclusion:
            feedback.append("Consider adding a conclusion to summarize your main points.")
        
        if len(headings) == 0 and len(text) > 500:
            feedback.append("For longer answers, consider using headings to organize your content.")
        
        if not feedback:
            feedback.append("Good structure with appropriate paragraphing and organization.")
        
        return score, " ".join(feedback)
    
    def _analyze_depth(self, text: str) -> tuple:
        """
        Analyze the depth of a text.
        
        Args:
            text (str): The text to analyze
            
        Returns:
            tuple: (score, feedback)
        """
        # This would typically use an LLM or NLP model
        # For now, we'll use simple heuristics
        
        # Count length as a simple proxy for depth
        word_count = len(text.split())
        
        # Check for examples
        example_phrases = ["for example", "for instance", "such as", "e.g.", "to illustrate"]
        has_examples = any(phrase in text.lower() for phrase in example_phrases)
        
        # Check for multiple perspectives
        perspective_phrases = ["on the other hand", "alternatively", "another view", "some argue", "others believe"]
        has_perspectives = any(phrase in text.lower() for phrase in perspective_phrases)
        
        # Check for citations or references
        citation_pattern = r'\([^)]*\d{4}[^)]*\)|\[[^\]]*\d+[^\]]*\]'
        has_citations = bool(re.search(citation_pattern, text))
        
        # Score based on depth elements
        score = 0.3  # Base score
        
        # Adjust score based on length
        if word_count >= 500:
            score += 0.3
        elif word_count >= 300:
            score += 0.2
        elif word_count >= 150:
            score += 0.1
        
        # Adjust score based on examples
        if has_examples:
            score += 0.1
        
        # Adjust score based on perspectives
        if has_perspectives:
            score += 0.1
        
        # Adjust score based on citations
        if has_citations:
            score += 0.1
        
        # Cap score at 1.0
        score = min(1.0, score)
        
        # Generate feedback
        feedback = []
        
        if word_count < 150:
            feedback.append("Your answer is quite brief. Consider expanding with more details and explanation.")
        
        if not has_examples:
            feedback.append("Consider including specific examples to illustrate your points.")
        
        if not has_perspectives:
            feedback.append("Consider discussing alternative perspectives or approaches.")
        
        if not has_citations and word_count >= 300:
            feedback.append("Consider citing sources or references to support your points.")
        
        if not feedback:
            feedback.append("Good depth with detailed explanations and supporting evidence.")
        
        return score, " ".join(feedback)
    
    def _analyze_completeness(self, 
                             question: str, 
                             answer: str, 
                             expected_key_points: Optional[List[str]] = None) -> tuple:
        """
        Analyze the completeness of an answer.
        
        Args:
            question (str): The question or prompt
            answer (str): The answer to analyze
            expected_key_points (List[str], optional): Expected key points
            
        Returns:
            tuple: (score, feedback, missing_points)
        """
        # This would typically use an LLM or NLP model
        # For now, we'll use simple keyword matching
        
        # Default key points if none provided
        if not expected_key_points:
            # Extract potential key points from the question
            question_words = question.lower().split()
            key_nouns = [word for word in question_words if len(word) > 4 and word.isalpha()]
            expected_key_points = key_nouns[:5]  # Use up to 5 key nouns from the question
        
        # Check which key points are covered
        covered_points = []
        missing_points = []
        
        for point in expected_key_points:
            if point.lower() in answer.lower():
                covered_points.append(point)
            else:
                missing_points.append(point)
        
        # Calculate coverage percentage
        if expected_key_points:
            coverage = len(covered_points) / len(expected_key_points)
        else:
            coverage = 1.0
        
        # Score based on coverage
        score = coverage
        
        # Generate feedback
        if coverage == 1.0:
            feedback = "Excellent coverage of all key points."
        elif coverage >= 0.8:
            feedback = "Good coverage of most key points, with minor omissions."
        elif coverage >= 0.6:
            feedback = "Adequate coverage, but several key points are missing."
        else:
            feedback = "Significant gaps in coverage. Many key points are not addressed."
        
        if missing_points:
            feedback += f" Consider addressing: {', '.join(missing_points)}."
        
        return score, feedback, missing_points
    
    def generate_model_answer(self, 
                             question: str,
                             expected_key_points: Optional[List[str]] = None,
                             style: str = "academic") -> Dict[str, Any]:
        """
        Generate a model answer for a question.
        
        Args:
            question (str): The question or prompt
            expected_key_points (List[str], optional): Key points to include
            style (str): Writing style (academic, concise, detailed)
            
        Returns:
            Dict[str, Any]: Generated model answer
        """
        logger.info(f"Generating model answer for question in {style} style")
        
        # This would typically use an LLM to generate a model answer
        # For now, we'll use a template-based approach
        
        # Default key points if none provided
        if not expected_key_points:
            # Extract potential key points from the question
            question_words = question.lower().split()
            key_nouns = [word for word in question_words if len(word) > 4 and word.isalpha()]
            expected_key_points = key_nouns[:5]  # Use up to 5 key nouns from the question
        
        # Generate introduction
        if style == "academic":
            introduction = f"This essay addresses the question of {question} by examining several key aspects. "
            introduction += f"The analysis will focus on {', '.join(expected_key_points[:-1])} and {expected_key_points[-1] if expected_key_points else ''}."
        elif style == "concise":
            introduction = f"In response to '{question}', the key points to consider are:"
        else:  # detailed
            introduction = f"To thoroughly answer the question '{question}', we need to explore multiple facets in detail. "
            introduction += f"This response will provide a comprehensive analysis of {', '.join(expected_key_points[:-1])} and {expected_key_points[-1] if expected_key_points else ''}."
        
        # Generate body paragraphs
        body = ""
        for i, point in enumerate(expected_key_points):
            if style == "academic":
                body += f"\n\nRegarding {point}, it is important to consider its significance in the context of the question. "
                body += f"Several aspects of {point} merit discussion. First, ... Second, ... Finally, ..."
            elif style == "concise":
                body += f"\n\n{i+1}. {point.capitalize()}: Key information about this point. Brief explanation and relevance."
            else:  # detailed
                body += f"\n\n{point.capitalize()} represents a critical element in addressing this question. "
                body += f"When analyzing {point}, we must consider multiple perspectives. From one viewpoint, ... "
                body += f"Alternatively, ... The evidence suggests that ... For example, ..."
        
        # Generate conclusion
        if style == "academic":
            conclusion = "\n\nIn conclusion, the analysis of the aforementioned aspects provides a comprehensive answer to the question. "
            conclusion += f"The key points of {', '.join(expected_key_points[:-1])} and {expected_key_points[-1] if expected_key_points else ''} all contribute to our understanding of the topic."
        elif style == "concise":
            conclusion = "\n\nIn summary, these key points address the core aspects of the question."
        else:  # detailed
            conclusion = "\n\nTo conclude this detailed analysis, we can synthesize the insights gained from examining each key aspect. "
            conclusion += f"The interrelationships between {', '.join(expected_key_points[:-1])} and {expected_key_points[-1] if expected_key_points else ''} reveal a complex picture. "
            conclusion += "This comprehensive understanding allows us to fully address the original question with nuance and depth."
        
        # Combine all parts
        model_answer = introduction + body + conclusion
        
        return {
            "id": f"model_{int(datetime.now().timestamp())}",
            "question": question,
            "style": style,
            "key_points": expected_key_points,
            "model_answer": model_answer,
            "timestamp": datetime.now().isoformat()
        }
    
    def track_improvement(self, user_id: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Track improvement in expressive capability over time.
        
        Args:
            user_id (str): ID of the user
            topic (str, optional): Filter by topic
            
        Returns:
            Dict[str, Any]: Improvement metrics
        """
        logger.info(f"Tracking improvement for user {user_id}")
        
        # This would typically query a database for historical analysis results
        # For now, we'll use the in-memory history
        
        # Filter history by user (not implemented in this simplified version)
        # In a real implementation, each analysis would include a user_id
        
        if not self.analysis_history:
            return {
                "user_id": user_id,
                "improvement_metrics": {},
                "message": "Not enough data to track improvement"
            }
        
        # Sort analyses by timestamp
        sorted_analyses = sorted(self.analysis_history, key=lambda x: x["timestamp"])
        
        # Group by time periods (e.g., weeks)
        # For simplicity, we'll just divide the history into three equal parts
        if len(sorted_analyses) >= 3:
            chunk_size = len(sorted_analyses) // 3
            early_period = sorted_analyses[:chunk_size]
            mid_period = sorted_analyses[chunk_size:2*chunk_size]
            recent_period = sorted_analyses[2*chunk_size:]
        else:
            # Not enough data for meaningful periods
            early_period = sorted_analyses[:1] if sorted_analyses else []
            mid_period = []
            recent_period = sorted_analyses[1:] if len(sorted_analyses) > 1 else []
        
        # Calculate average scores for each period
        early_avg = sum(a["overall_score"] for a in early_period) / len(early_period) if early_period else 0
        mid_avg = sum(a["overall_score"] for a in mid_period) / len(mid_period) if mid_period else 0
        recent_avg = sum(a["overall_score"] for a in recent_period) / len(recent_period) if recent_period else 0
        
        # Calculate improvement percentages
        early_to_mid = ((mid_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        mid_to_recent = ((recent_avg - mid_avg) / mid_avg * 100) if mid_avg > 0 else 0
        overall_improvement = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        
        # Generate improvement metrics
        improvement_metrics = {
            "total_analyses": len(sorted_analyses),
            "earliest_date": sorted_analyses[0]["timestamp"] if sorted_analyses else None,
            "latest_date": sorted_analyses[-1]["timestamp"] if sorted_analyses else None,
            "average_scores": {
                "early_period": round(early_avg, 2),
                "mid_period": round(mid_avg, 2),
                "recent_period": round(recent_avg, 2)
            },
            "improvement_percentages": {
                "early_to_mid": round(early_to_mid, 1),
                "mid_to_recent": round(mid_to_recent, 1),
                "overall": round(overall_improvement, 1)
            }
        }
        
        # Generate improvement message
        if overall_improvement >= 20:
            message = "Significant improvement in expression skills over time."
        elif overall_improvement >= 10:
            message = "Moderate improvement in expression skills over time."
        elif overall_improvement >= 5:
            message = "Slight improvement in expression skills over time."
        elif overall_improvement >= -5:
            message = "Consistent expression skills with little change over time."
        else:
            message = "Declining trend in expression skills. Consider reviewing feedback more carefully."
        
        return {
            "user_id": user_id,
            "improvement_metrics": improvement_metrics,
            "message": message
        }
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the expression trainer to a file.
        
        Args:
            filepath (str): Path to save the state
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            state = {
                "analysis_history": self.analysis_history,
                "criteria": self.default_criteria
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Saved expression trainer state to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving expression trainer state: {str(e)}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the expression trainer state from a file.
        
        Args:
            filepath (str): Path to the state file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.analysis_history = state.get("analysis_history", [])
            
            # Only update criteria if they exist in the state
            if "criteria" in state:
                self.default_criteria = state["criteria"]
            
            logger.info(f"Loaded expression trainer state from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading expression trainer state: {str(e)}")
            return False