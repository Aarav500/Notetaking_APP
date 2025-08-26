"""
Socratic Self-Explanation Trainer module for AI Note System.
Prompts learners to verbally explain concepts, records and transcribes explanations,
and provides feedback on conceptual understanding and clarity.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import tempfile

# Setup logging
logger = logging.getLogger("ai_note_system.learning.socratic_explanation_trainer")

# Import required modules
from ..inputs.speech_input import record_audio, transcribe_audio
from ..api.llm_interface import get_llm_interface
from ..database.explanation_db import get_db_manager

class SocraticExplanationTrainer:
    """
    Trainer that guides users through Socratic self-explanation exercises.
    Records verbal explanations, analyzes them, and provides feedback.
    """
    
    def __init__(
        self,
        user_id: str,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        speech_engine: str = "whisper",
        db_manager = None
    ):
        """
        Initialize the Socratic Explanation Trainer.
        
        Args:
            user_id (str): ID of the user
            llm_provider (str): LLM provider to use for analysis
            llm_model (str): LLM model to use for analysis
            speech_engine (str): Engine to use for speech transcription
            db_manager: Database manager instance
        """
        self.user_id = user_id
        self.speech_engine = speech_engine
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Initialize database manager
        self.db_manager = db_manager or get_db_manager()
        
        # Create directory for storing recordings if it doesn't exist
        self.recordings_dir = os.path.join("data", "recordings", user_id)
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        logger.info(f"Initialized Socratic Explanation Trainer for user {user_id}")
    
    def prompt_explanation(
        self,
        topic: str,
        concept: str,
        context: Optional[str] = None,
        duration: int = 60,
        save_recording: bool = True
    ) -> Dict[str, Any]:
        """
        Prompt the user to explain a concept and record their explanation.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to explain
            context (str, optional): Additional context or instructions
            duration (int): Maximum duration for recording in seconds
            save_recording (bool): Whether to save the recording
            
        Returns:
            Dict[str, Any]: Result containing the recorded explanation and analysis
        """
        logger.info(f"Prompting explanation for concept: {concept}")
        
        # Generate a prompt for the explanation
        prompt = self._generate_explanation_prompt(topic, concept, context)
        
        # Display the prompt to the user
        print("\n" + "="*50)
        print("SOCRATIC EXPLANATION EXERCISE")
        print("="*50)
        print(prompt)
        print("\nPress Enter to start recording your explanation...")
        input()
        
        # Record the explanation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recording_path = os.path.join(self.recordings_dir, f"explanation_{timestamp}.wav") if save_recording else None
        
        print(f"Recording started (max {duration} seconds). Press Ctrl+C to stop...")
        try:
            audio_path = record_audio(recording_path, duration)
            print("Recording complete!")
        except KeyboardInterrupt:
            print("\nRecording stopped by user.")
            return {"error": "Recording stopped by user"}
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            print(f"\nError recording audio: {e}")
            return {"error": f"Error recording audio: {e}"}
        
        # Transcribe the explanation
        print("Transcribing your explanation...")
        transcription_result = transcribe_audio(
            audio_path=audio_path,
            engine=self.speech_engine,
            save_raw=True
        )
        
        if "error" in transcription_result:
            logger.error(f"Error transcribing audio: {transcription_result['error']}")
            print(f"Error transcribing audio: {transcription_result['error']}")
            return transcription_result
        
        explanation_text = transcription_result.get("text", "")
        print("\nYour explanation has been transcribed. Analyzing...")
        
        # Analyze the explanation
        analysis = self._analyze_explanation(topic, concept, context, explanation_text)
        
        # Create the result
        result = {
            "user_id": self.user_id,
            "timestamp": timestamp,
            "topic": topic,
            "concept": concept,
            "context": context,
            "audio_path": audio_path,
            "explanation_text": explanation_text,
            "word_count": transcription_result.get("word_count", 0),
            "duration": transcription_result.get("duration", 0),
            "analysis": analysis
        }
        
        # Save the result to the database
        self._save_explanation_result(result)
        
        # Display the analysis to the user
        self._display_analysis(analysis)
        
        return result
    
    def _generate_explanation_prompt(
        self,
        topic: str,
        concept: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a prompt for the explanation.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to explain
            context (str, optional): Additional context or instructions
            
        Returns:
            str: The generated prompt
        """
        prompt = f"Please explain the concept of '{concept}' in the field of {topic}."
        
        if context:
            prompt += f"\n\nAdditional context: {context}"
        
        prompt += "\n\nIn your explanation, try to:"
        prompt += "\n- Define the concept clearly"
        prompt += "\n- Explain its significance or importance"
        prompt += "\n- Provide examples or applications if relevant"
        prompt += "\n- Connect it to related concepts you know"
        
        return prompt
    
    def _analyze_explanation(
        self,
        topic: str,
        concept: str,
        context: Optional[str],
        explanation_text: str
    ) -> Dict[str, Any]:
        """
        Analyze the explanation using LLM.
        
        Args:
            topic (str): The general topic area
            concept (str): The specific concept to explain
            context (str, optional): Additional context or instructions
            explanation_text (str): The transcribed explanation
            
        Returns:
            Dict[str, Any]: Analysis of the explanation
        """
        logger.info(f"Analyzing explanation for concept: {concept}")
        
        # Define the schema for structured output
        analysis_schema = {
            "type": "object",
            "properties": {
                "conceptual_understanding": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "description": "Score from 0-10 indicating overall conceptual understanding"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "description": "List of conceptual strengths in the explanation"},
                        "gaps": {"type": "array", "items": {"type": "string"}, "description": "List of conceptual gaps or misunderstandings"},
                        "misconceptions": {"type": "array", "items": {"type": "string"}, "description": "List of specific misconceptions or errors"}
                    }
                },
                "explanation_clarity": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "number", "description": "Score from 0-10 indicating clarity of explanation"},
                        "strengths": {"type": "array", "items": {"type": "string"}, "description": "List of strengths in explanation clarity"},
                        "areas_for_improvement": {"type": "array", "items": {"type": "string"}, "description": "List of areas where clarity could be improved"}
                    }
                },
                "suggested_improvements": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of specific suggestions to improve the explanation"
                },
                "follow_up_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of Socratic questions to deepen understanding"
                },
                "additional_resources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Suggested resources to address gaps in understanding"
                }
            }
        }
        
        # Create the prompt for analysis
        analysis_prompt = f"""
        Analyze the following verbal explanation of the concept '{concept}' in the field of {topic}.
        
        CONCEPT TO EXPLAIN: {concept}
        
        LEARNER'S EXPLANATION:
        {explanation_text}
        
        Provide a detailed analysis of the explanation, including:
        1. Assessment of conceptual understanding (strengths, gaps, misconceptions)
        2. Evaluation of explanation clarity (organization, precision, examples)
        3. Specific suggestions for improvement
        4. Follow-up Socratic questions to deepen understanding
        5. Recommended resources to address any gaps
        
        Be constructive but thorough in identifying areas for improvement.
        """
        
        try:
            # Generate structured analysis
            analysis = self.llm.generate_structured_output(
                prompt=analysis_prompt,
                output_schema=analysis_schema,
                temperature=0.3
            )
            
            # Add timestamp
            analysis["timestamp"] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing explanation: {e}")
            return {
                "error": f"Error analyzing explanation: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _save_explanation_result(self, result: Dict[str, Any]) -> bool:
        """
        Save the explanation result to the database.
        
        Args:
            result (Dict[str, Any]): The explanation result
            
        Returns:
            bool: Whether the save was successful
        """
        try:
            # Save to database
            explanation_id = self.db_manager.add_explanation(
                user_id=result["user_id"],
                topic=result["topic"],
                concept=result["concept"],
                explanation_text=result["explanation_text"],
                audio_path=result["audio_path"],
                analysis=json.dumps(result["analysis"]),
                clarity_score=result["analysis"].get("explanation_clarity", {}).get("score", 0),
                understanding_score=result["analysis"].get("conceptual_understanding", {}).get("score", 0)
            )
            
            logger.info(f"Saved explanation result with ID: {explanation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving explanation result: {e}")
            return False
    
    def _display_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Display the analysis to the user in a readable format.
        
        Args:
            analysis (Dict[str, Any]): The analysis to display
        """
        print("\n" + "="*50)
        print("EXPLANATION ANALYSIS")
        print("="*50)
        
        # Check if there was an error
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
            return
        
        # Display conceptual understanding
        understanding = analysis.get("conceptual_understanding", {})
        understanding_score = understanding.get("score", 0)
        print(f"\nConceptual Understanding: {understanding_score}/10")
        
        if understanding.get("strengths"):
            print("\nStrengths:")
            for strength in understanding["strengths"]:
                print(f"  ✓ {strength}")
        
        if understanding.get("gaps"):
            print("\nGaps in Understanding:")
            for gap in understanding["gaps"]:
                print(f"  ! {gap}")
        
        if understanding.get("misconceptions"):
            print("\nMisconceptions:")
            for misconception in understanding["misconceptions"]:
                print(f"  ✗ {misconception}")
        
        # Display explanation clarity
        clarity = analysis.get("explanation_clarity", {})
        clarity_score = clarity.get("score", 0)
        print(f"\nExplanation Clarity: {clarity_score}/10")
        
        if clarity.get("strengths"):
            print("\nClarity Strengths:")
            for strength in clarity["strengths"]:
                print(f"  ✓ {strength}")
        
        if clarity.get("areas_for_improvement"):
            print("\nAreas to Improve Clarity:")
            for area in clarity["areas_for_improvement"]:
                print(f"  ! {area}")
        
        # Display suggestions
        if analysis.get("suggested_improvements"):
            print("\nSuggested Improvements:")
            for suggestion in analysis["suggested_improvements"]:
                print(f"  → {suggestion}")
        
        # Display follow-up questions
        if analysis.get("follow_up_questions"):
            print("\nFollow-up Questions to Consider:")
            for question in analysis["follow_up_questions"]:
                print(f"  ? {question}")
        
        # Display additional resources
        if analysis.get("additional_resources"):
            print("\nRecommended Resources:")
            for resource in analysis["additional_resources"]:
                print(f"  • {resource}")
        
        print("\n" + "="*50)
    
    def get_explanation_history(
        self,
        limit: int = 10,
        topic: Optional[str] = None,
        concept: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the user's explanation history.
        
        Args:
            limit (int): Maximum number of results to return
            topic (str, optional): Filter by topic
            concept (str, optional): Filter by concept
            
        Returns:
            List[Dict[str, Any]]: List of explanation results
        """
        try:
            # Get explanation history from database
            history = self.db_manager.get_explanations(
                user_id=self.user_id,
                limit=limit,
                topic=topic,
                concept=concept
            )
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting explanation history: {e}")
            return []
    
    def get_clarity_progress(
        self,
        topic: Optional[str] = None,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get the user's progress in explanation clarity over time.
        
        Args:
            topic (str, optional): Filter by topic
            period_days (int): Number of days to look back
            
        Returns:
            Dict[str, Any]: Clarity progress data
        """
        try:
            # Get clarity scores from database
            scores = self.db_manager.get_clarity_scores(
                user_id=self.user_id,
                topic=topic,
                days=period_days
            )
            
            # Calculate average scores by date
            dates = {}
            for score in scores:
                date = score["timestamp"].split("T")[0]
                if date not in dates:
                    dates[date] = {"total": 0, "count": 0}
                
                dates[date]["total"] += score["clarity_score"]
                dates[date]["count"] += 1
            
            # Calculate averages
            progress = [
                {
                    "date": date,
                    "average_score": data["total"] / data["count"]
                }
                for date, data in dates.items()
            ]
            
            # Sort by date
            progress.sort(key=lambda x: x["date"])
            
            return {
                "user_id": self.user_id,
                "topic": topic,
                "period_days": period_days,
                "progress": progress
            }
            
        except Exception as e:
            logger.error(f"Error getting clarity progress: {e}")
            return {
                "user_id": self.user_id,
                "topic": topic,
                "period_days": period_days,
                "progress": [],
                "error": str(e)
            }


def main():
    """
    Command-line interface for the Socratic Explanation Trainer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Socratic Self-Explanation Trainer")
    parser.add_argument("--user", required=True, help="User ID")
    parser.add_argument("--topic", required=True, help="Topic area")
    parser.add_argument("--concept", required=True, help="Concept to explain")
    parser.add_argument("--context", help="Additional context or instructions")
    parser.add_argument("--duration", type=int, default=60, help="Maximum recording duration in seconds")
    parser.add_argument("--llm", default="openai", help="LLM provider (openai, huggingface, etc.)")
    parser.add_argument("--model", default="gpt-4", help="LLM model to use")
    parser.add_argument("--speech", default="whisper", help="Speech recognition engine (whisper or speechrecognition)")
    
    args = parser.parse_args()
    
    # Initialize trainer
    trainer = SocraticExplanationTrainer(
        user_id=args.user,
        llm_provider=args.llm,
        llm_model=args.model,
        speech_engine=args.speech
    )
    
    # Prompt explanation
    result = trainer.prompt_explanation(
        topic=args.topic,
        concept=args.concept,
        context=args.context,
        duration=args.duration
    )
    
    # Check for errors
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print("\nExplanation exercise completed!")


if __name__ == "__main__":
    main()