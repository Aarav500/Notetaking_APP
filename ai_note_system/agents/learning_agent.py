"""
Learning Agent module for AI Note System.
Provides personalized tutoring capabilities that adapt to the user's learning style and knowledge level.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.agents.learning_agent")

# Import LLM interface
from ..api.llm_interface import LLMInterface, get_llm_interface

class LearningStyle:
    """
    Enum-like class for learning styles.
    """
    VISUAL = "visual"
    AUDITORY = "auditory"
    READING_WRITING = "reading_writing"
    KINESTHETIC = "kinesthetic"
    MULTIMODAL = "multimodal"

class KnowledgeLevel:
    """
    Enum-like class for knowledge levels.
    """
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningAgent:
    """
    Agent that provides personalized tutoring capabilities.
    Adapts to the user's learning style and knowledge level.
    """
    
    def __init__(
        self,
        llm_interface: Optional[LLMInterface] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        user_profile: Optional[Dict[str, Any]] = None,
        session_memory: Optional[List[Dict[str, str]]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the learning agent.
        
        Args:
            llm_interface (LLMInterface, optional): LLM interface to use
            llm_provider (str): LLM provider to use if llm_interface is not provided
            llm_model (str): LLM model to use if llm_interface is not provided
            user_profile (Dict[str, Any], optional): User profile with learning preferences
            session_memory (List[Dict[str, str]], optional): Memory of the current session
            config (Dict[str, Any], optional): Configuration dictionary
        """
        # Set LLM interface
        if llm_interface:
            self.llm = llm_interface
        else:
            # Get LLM interface from provider and model
            self.llm = get_llm_interface(
                llm_provider,
                model=llm_model
            )
        
        # Set user profile
        self.user_profile = user_profile or {}
        
        # Set session memory
        self.session_memory = session_memory or []
        
        # Set configuration
        self.config = config or {}
        
        # Initialize session if not already started
        if not self.session_memory:
            self._initialize_session()
        
        logger.info("Learning agent initialized")
    
    def _initialize_session(self) -> None:
        """
        Initialize a new tutoring session.
        """
        # Add system message
        self.session_memory.append({
            "role": "system",
            "content": self._generate_system_prompt()
        })
        
        # Add initial greeting
        greeting = self._generate_greeting()
        self.session_memory.append({
            "role": "assistant",
            "content": greeting
        })
        
        logger.debug("Session initialized")
    
    def _generate_system_prompt(self) -> str:
        """
        Generate the system prompt based on user profile.
        
        Returns:
            str: System prompt
        """
        # Get learning style
        learning_style = self.user_profile.get("learning_style", LearningStyle.MULTIMODAL)
        
        # Get knowledge level
        knowledge_level = self.user_profile.get("knowledge_level", KnowledgeLevel.INTERMEDIATE)
        
        # Get interests
        interests = self.user_profile.get("interests", [])
        interests_str = ", ".join(interests) if interests else "various topics"
        
        # Get goals
        goals = self.user_profile.get("goals", [])
        goals_str = ", ".join(goals) if goals else "learning and understanding concepts"
        
        # Generate system prompt
        system_prompt = f"""
        You are an expert tutor and learning assistant, specialized in personalized education.
        
        User Profile:
        - Learning Style: {learning_style}
        - Knowledge Level: {knowledge_level}
        - Interests: {interests_str}
        - Goals: {goals_str}
        
        Your task is to provide personalized tutoring that adapts to the user's learning style and knowledge level.
        For a {learning_style} learner at a {knowledge_level} level, you should:
        """
        
        # Add learning style specific instructions
        if learning_style == LearningStyle.VISUAL:
            system_prompt += """
            - Use visual descriptions and spatial language
            - Suggest diagrams, charts, and visual aids
            - Describe concepts in terms of visual patterns and relationships
            - Recommend visualization techniques for memorization
            """
        elif learning_style == LearningStyle.AUDITORY:
            system_prompt += """
            - Use clear explanations with rhythm and emphasis
            - Suggest verbal repetition and discussion techniques
            - Frame concepts as conversations or dialogues
            - Recommend audio resources and verbal mnemonics
            """
        elif learning_style == LearningStyle.READING_WRITING:
            system_prompt += """
            - Provide detailed written explanations
            - Suggest note-taking strategies and written exercises
            - Frame concepts with clear definitions and structured text
            - Recommend reading materials and writing exercises
            """
        elif learning_style == LearningStyle.KINESTHETIC:
            system_prompt += """
            - Suggest hands-on activities and practical applications
            - Frame concepts in terms of actions and real-world examples
            - Recommend interactive exercises and physical demonstrations
            - Use metaphors related to movement and physical sensation
            """
        else:  # MULTIMODAL
            system_prompt += """
            - Use a balanced approach combining visual, auditory, reading/writing, and kinesthetic elements
            - Provide varied explanations and learning strategies
            - Suggest multiple ways to engage with the material
            - Adapt based on the specific topic and context
            """
        
        # Add knowledge level specific instructions
        if knowledge_level == KnowledgeLevel.BEGINNER:
            system_prompt += """
            - Explain concepts from first principles with simple language
            - Avoid jargon and technical terms without explanation
            - Provide frequent summaries and check for understanding
            - Use analogies to familiar everyday concepts
            """
        elif knowledge_level == KnowledgeLevel.INTERMEDIATE:
            system_prompt += """
            - Build on fundamental concepts with more detailed explanations
            - Introduce field-specific terminology with clear definitions
            - Make connections between related concepts
            - Challenge the user with moderate complexity
            """
        elif knowledge_level == KnowledgeLevel.ADVANCED:
            system_prompt += """
            - Provide in-depth explanations with nuanced details
            - Use field-specific terminology freely
            - Discuss exceptions, edge cases, and theoretical implications
            - Challenge the user with complex problems and scenarios
            """
        elif knowledge_level == KnowledgeLevel.EXPERT:
            system_prompt += """
            - Focus on cutting-edge concepts and research
            - Engage in sophisticated analysis and critique
            - Discuss theoretical frameworks and their limitations
            - Challenge the user with expert-level problems and open questions in the field
            """
        
        # Add general tutoring guidelines
        system_prompt += """
        
        General Guidelines:
        1. Be encouraging and supportive while maintaining high standards
        2. Ask questions to check understanding and promote active learning
        3. Provide constructive feedback on the user's responses
        4. Adapt your teaching approach based on the user's responses
        5. Break down complex topics into manageable parts
        6. Use the Socratic method when appropriate to guide discovery
        7. Provide concrete examples and applications
        8. Summarize key points at appropriate intervals
        9. Suggest additional resources for further learning
        10. Maintain a conversational and engaging tone
        
        Remember that your goal is to help the user truly understand the material, not just memorize facts.
        """
        
        return system_prompt.strip()
    
    def _generate_greeting(self) -> str:
        """
        Generate a personalized greeting based on user profile.
        
        Returns:
            str: Personalized greeting
        """
        # Get user name
        user_name = self.user_profile.get("name", "there")
        
        # Get time of day
        current_hour = datetime.now().hour
        time_greeting = "Good morning" if 5 <= current_hour < 12 else "Good afternoon" if 12 <= current_hour < 18 else "Good evening"
        
        # Get learning style
        learning_style = self.user_profile.get("learning_style", LearningStyle.MULTIMODAL)
        
        # Generate greeting
        greeting = f"{time_greeting}, {user_name}! I'm your personal learning assistant, here to help you understand and master new concepts."
        
        # Add learning style specific message
        if learning_style == LearningStyle.VISUAL:
            greeting += " I'll use visual descriptions and imagery to help you see the big picture of what we're learning."
        elif learning_style == LearningStyle.AUDITORY:
            greeting += " I'll explain concepts clearly and discuss ideas in a way that's easy to follow and remember."
        elif learning_style == LearningStyle.READING_WRITING:
            greeting += " I'll provide detailed explanations and suggest effective note-taking strategies to help you process information."
        elif learning_style == LearningStyle.KINESTHETIC:
            greeting += " I'll focus on practical applications and hands-on examples to make concepts tangible and actionable."
        else:  # MULTIMODAL
            greeting += " I'll use a variety of approaches to help you engage with the material in the most effective way."
        
        greeting += " What would you like to learn about today?"
        
        return greeting
    
    def process_message(self, message: str) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message (str): User message
            
        Returns:
            str: Agent response
        """
        # Add user message to session memory
        self.session_memory.append({
            "role": "user",
            "content": message
        })
        
        # Generate response
        response = self.llm.generate_chat_response(
            self.session_memory,
            temperature=0.7
        )
        
        # Add assistant response to session memory
        self.session_memory.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def explain_concept(
        self,
        concept: str,
        context: Optional[str] = None,
        depth: str = "standard",
        format: str = "default"
    ) -> str:
        """
        Generate an explanation of a concept.
        
        Args:
            concept (str): Concept to explain
            context (str, optional): Additional context for the explanation
            depth (str): Depth of explanation ("brief", "standard", "detailed")
            format (str): Format of explanation ("default", "steps", "examples", "analogy")
            
        Returns:
            str: Explanation of the concept
        """
        # Get learning style
        learning_style = self.user_profile.get("learning_style", LearningStyle.MULTIMODAL)
        
        # Get knowledge level
        knowledge_level = self.user_profile.get("knowledge_level", KnowledgeLevel.INTERMEDIATE)
        
        # Create prompt
        prompt = f"Please explain the concept of {concept}"
        if context:
            prompt += f" in the context of {context}"
        
        # Add depth instruction
        if depth == "brief":
            prompt += ". Keep the explanation brief and focused on the core idea."
        elif depth == "detailed":
            prompt += ". Provide a detailed explanation covering nuances and implications."
        
        # Add format instruction
        if format == "steps":
            prompt += " Break down the explanation into clear, sequential steps."
        elif format == "examples":
            prompt += " Include multiple concrete examples to illustrate the concept."
        elif format == "analogy":
            prompt += " Use an analogy to make the concept more relatable."
        
        # Add learning style and knowledge level context
        prompt += f" Tailor the explanation for a {learning_style} learner at a {knowledge_level} knowledge level."
        
        # Generate explanation
        explanation = self.llm.generate_text(
            prompt,
            temperature=0.5
        )
        
        return explanation
    
    def generate_practice_exercise(
        self,
        topic: str,
        difficulty: str = "medium",
        exercise_type: str = "problem"
    ) -> Dict[str, str]:
        """
        Generate a practice exercise for a topic.
        
        Args:
            topic (str): Topic for the exercise
            difficulty (str): Difficulty level ("easy", "medium", "hard")
            exercise_type (str): Type of exercise ("problem", "question", "project")
            
        Returns:
            Dict[str, str]: Exercise with question and solution
        """
        # Get knowledge level
        knowledge_level = self.user_profile.get("knowledge_level", KnowledgeLevel.INTERMEDIATE)
        
        # Adjust difficulty based on knowledge level
        if knowledge_level == KnowledgeLevel.BEGINNER and difficulty == "hard":
            difficulty = "medium"
        elif knowledge_level == KnowledgeLevel.EXPERT and difficulty == "easy":
            difficulty = "medium"
        
        # Create prompt
        prompt = f"Create a {difficulty} {exercise_type} about {topic} for a {knowledge_level} level student."
        prompt += " Provide both the exercise and a detailed solution."
        
        # Define output schema
        output_schema = {
            "exercise": {
                "question": "The exercise question or problem statement",
                "context": "Any necessary context or setup for the exercise",
                "hints": ["Optional hints to help solve the exercise"]
            },
            "solution": {
                "answer": "The answer or solution to the exercise",
                "explanation": "Detailed explanation of how to solve the exercise",
                "key_insights": ["Key insights or learning points from this exercise"]
            }
        }
        
        # Generate exercise
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.7
        )
        
        return result
    
    def create_learning_path(
        self,
        topic: str,
        goal: str,
        estimated_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a personalized learning path for a topic.
        
        Args:
            topic (str): Main topic for the learning path
            goal (str): Learning goal or objective
            estimated_time (str, optional): Estimated time available (e.g., "2 weeks", "3 hours per day")
            
        Returns:
            Dict[str, Any]: Structured learning path
        """
        # Get knowledge level
        knowledge_level = self.user_profile.get("knowledge_level", KnowledgeLevel.INTERMEDIATE)
        
        # Create prompt
        prompt = f"Create a personalized learning path for {topic} with the goal of {goal}."
        prompt += f" The learner is at a {knowledge_level} knowledge level."
        
        if estimated_time:
            prompt += f" They have approximately {estimated_time} available for this learning journey."
        
        prompt += " The learning path should include subtopics, resources, activities, and milestones."
        
        # Define output schema
        output_schema = {
            "learning_path": {
                "title": "Title of the learning path",
                "description": "Brief description of the learning path",
                "prerequisites": ["Any prerequisites for this learning path"],
                "estimated_completion_time": "Estimated time to complete the entire path",
                "stages": [
                    {
                        "title": "Stage title",
                        "description": "Description of this stage",
                        "subtopics": ["List of subtopics to cover"],
                        "resources": [
                            {
                                "title": "Resource title",
                                "type": "Resource type (article, video, book, etc.)",
                                "description": "Brief description of the resource"
                            }
                        ],
                        "activities": [
                            {
                                "title": "Activity title",
                                "type": "Activity type (exercise, project, quiz, etc.)",
                                "description": "Description of the activity"
                            }
                        ],
                        "milestone": "Milestone to achieve at the end of this stage"
                    }
                ]
            }
        }
        
        # Generate learning path
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.7
        )
        
        return result
    
    def identify_knowledge_gaps(self, text: str) -> Dict[str, Any]:
        """
        Identify knowledge gaps in a text.
        
        Args:
            text (str): Text to analyze for knowledge gaps
            
        Returns:
            Dict[str, Any]: Identified knowledge gaps and recommendations
        """
        # Get knowledge level
        knowledge_level = self.user_profile.get("knowledge_level", KnowledgeLevel.INTERMEDIATE)
        
        # Create prompt
        prompt = f"Analyze the following text and identify potential knowledge gaps for a {knowledge_level} level learner."
        prompt += " Provide specific concepts that may need clarification and recommendations for filling these gaps."
        prompt += f"\n\nText to analyze:\n{text}"
        
        # Define output schema
        output_schema = {
            "analysis": {
                "summary": "Brief summary of the text",
                "knowledge_gaps": [
                    {
                        "concept": "Concept that may be unclear",
                        "context": "How this concept appears in the text",
                        "importance": "Why understanding this concept is important",
                        "recommendation": "Recommendation for learning this concept"
                    }
                ],
                "overall_assessment": "Overall assessment of the text's clarity and completeness"
            }
        }
        
        # Generate analysis
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.5
        )
        
        return result
    
    def generate_socratic_questions(
        self,
        topic: str,
        depth: str = "medium",
        count: int = 5
    ) -> List[Dict[str, str]]:
        """
        Generate Socratic questions for a topic.
        
        Args:
            topic (str): Topic to generate questions for
            depth (str): Depth of questions ("shallow", "medium", "deep")
            count (int): Number of questions to generate
            
        Returns:
            List[Dict[str, str]]: List of Socratic questions with context and purpose
        """
        # Create prompt
        prompt = f"Generate {count} Socratic questions about {topic} at a {depth} depth."
        prompt += " For each question, provide the context and purpose of asking it."
        
        # Define output schema
        output_schema = {
            "socratic_questions": [
                {
                    "question": "The Socratic question",
                    "context": "Context or background for this question",
                    "purpose": "Purpose or learning objective of this question",
                    "follow_up": "Potential follow-up question based on typical responses"
                }
            ]
        }
        
        # Generate questions
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.7
        )
        
        return result.get("socratic_questions", [])
    
    def simplify_explanation(self, text: str, target_level: Optional[str] = None) -> str:
        """
        Simplify an explanation to make it more accessible.
        
        Args:
            text (str): Text to simplify
            target_level (str, optional): Target knowledge level (defaults to one level below current)
            
        Returns:
            str: Simplified explanation
        """
        # Get current knowledge level
        current_level = self.user_profile.get("knowledge_level", KnowledgeLevel.INTERMEDIATE)
        
        # Determine target level if not specified
        if not target_level:
            if current_level == KnowledgeLevel.EXPERT:
                target_level = KnowledgeLevel.ADVANCED
            elif current_level == KnowledgeLevel.ADVANCED:
                target_level = KnowledgeLevel.INTERMEDIATE
            elif current_level == KnowledgeLevel.INTERMEDIATE:
                target_level = KnowledgeLevel.BEGINNER
            else:
                target_level = KnowledgeLevel.BEGINNER
        
        # Create prompt
        prompt = f"Simplify the following explanation to a {target_level} knowledge level."
        prompt += " Maintain the core meaning but use simpler language and concepts."
        prompt += f"\n\nText to simplify:\n{text}"
        
        # Generate simplified explanation
        simplified = self.llm.generate_text(
            prompt,
            temperature=0.3
        )
        
        return simplified
    
    def save_session(self, file_path: str) -> bool:
        """
        Save the current session to a file.
        
        Args:
            file_path (str): Path to save the session
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create session data
            session_data = {
                "user_profile": self.user_profile,
                "session_memory": self.session_memory,
                "timestamp": datetime.now().isoformat()
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
            
            logger.info(f"Session saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving session: {e}")
            return False
    
    def load_session(self, file_path: str) -> bool:
        """
        Load a session from a file.
        
        Args:
            file_path (str): Path to load the session from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load from file
            with open(file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Set session data
            self.user_profile = session_data.get("user_profile", {})
            self.session_memory = session_data.get("session_memory", [])
            
            logger.info(f"Session loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False
    
    def update_user_profile(self, profile_updates: Dict[str, Any]) -> None:
        """
        Update the user profile.
        
        Args:
            profile_updates (Dict[str, Any]): Updates to apply to the profile
        """
        # Update profile
        self.user_profile.update(profile_updates)
        
        logger.debug("User profile updated")
    
    def clear_session_memory(self, keep_system_prompt: bool = True) -> None:
        """
        Clear the session memory.
        
        Args:
            keep_system_prompt (bool): Whether to keep the system prompt
        """
        if keep_system_prompt and self.session_memory and self.session_memory[0]["role"] == "system":
            # Keep only the system prompt
            system_prompt = self.session_memory[0]
            self.session_memory = [system_prompt]
        else:
            # Clear all memory
            self.session_memory = []
            # Reinitialize if needed
            if not self.session_memory:
                self._initialize_session()
        
        logger.debug("Session memory cleared")


def create_learning_agent_from_config(config: Dict[str, Any]) -> LearningAgent:
    """
    Create a learning agent from a configuration dictionary.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        LearningAgent: The learning agent
    """
    # Get LLM provider and model
    llm_provider = config.get("LLM_PROVIDER", "openai")
    llm_model = config.get("LLM_MODEL", "gpt-4")
    
    # Get user profile
    user_profile = config.get("USER_PROFILE", {})
    
    # Create learning agent
    agent = LearningAgent(
        llm_provider=llm_provider,
        llm_model=llm_model,
        user_profile=user_profile,
        config=config
    )
    
    return agent
def track_learning_performance(
    self,
    content_type: str,
    score: float,
    duration_minutes: int,
    topic: str,
    difficulty: str = "medium",
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track learning performance for a specific content type.
    
    Args:
        content_type (str): Type of content (visual, text, audio, interactive)
        score (float): Performance score (0-100)
        duration_minutes (int): Time spent on the content
        topic (str): Topic of the content
        difficulty (str): Difficulty level (easy, medium, hard)
        notes (str, optional): Additional notes
        
    Returns:
        Dict[str, Any]: Performance tracking result
    """
    logger.info(f"Tracking learning performance for {content_type} content")
    
    # Validate score
    if not 0 <= score <= 100:
        logger.error(f"Invalid score: {score}. Must be between 0 and 100.")
        raise ValueError(f"Invalid score: {score}. Must be between 0 and 100.")
    
    # Validate content type
    valid_content_types = ["visual", "text", "audio", "interactive", "mixed"]
    if content_type not in valid_content_types:
        logger.error(f"Invalid content type: {content_type}. Must be one of {valid_content_types}.")
        raise ValueError(f"Invalid content type: {content_type}. Must be one of {valid_content_types}.")
    
    # Create performance entry
    performance_entry = {
        "content_type": content_type,
        "score": score,
        "duration_minutes": duration_minutes,
        "topic": topic,
        "difficulty": difficulty,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    
    # Add to user profile if not already present
    if "performance_history" not in self.user_profile:
        self.user_profile["performance_history"] = []
    
    # Add performance entry
    self.user_profile["performance_history"].append(performance_entry)
    
    # Update learning style preferences based on performance
    self._update_learning_style_preferences(performance_entry)
    
    return {
        "status": "success",
        "message": f"Performance tracked for {content_type} content",
        "entry": performance_entry
    }

def _update_learning_style_preferences(self, performance_entry: Dict[str, Any]) -> None:
    """
    Update learning style preferences based on performance.
    
    Args:
        performance_entry (Dict[str, Any]): Performance entry
    """
    # Initialize learning style preferences if not present
    if "learning_style_preferences" not in self.user_profile:
        self.user_profile["learning_style_preferences"] = {
            "visual": 0.25,
            "text": 0.25,
            "audio": 0.25,
            "interactive": 0.25,
            "preferred_style": LearningStyle.MULTIMODAL
        }
    
    # Get current preferences
    preferences = self.user_profile["learning_style_preferences"]
    
    # Get content type and score
    content_type = performance_entry["content_type"]
    score = performance_entry["score"]
    
    # Skip mixed content type
    if content_type == "mixed":
        return
    
    # Calculate performance weight (higher scores have more influence)
    weight = 0.1 * (score / 100)
    
    # Update preference for this content type
    current_value = preferences.get(content_type, 0.25)
    new_value = current_value * (1 - weight) + weight
    
    # Update preferences
    preferences[content_type] = new_value
    
    # Normalize preferences to sum to 1
    total = sum(v for k, v in preferences.items() if k != "preferred_style")
    for k in preferences:
        if k != "preferred_style":
            preferences[k] = preferences[k] / total
    
    # Determine preferred style
    max_preference = max((v, k) for k, v in preferences.items() if k != "preferred_style")
    if max_preference[0] > 0.4:  # Strong preference
        if max_preference[1] == "visual":
            preferences["preferred_style"] = LearningStyle.VISUAL
        elif max_preference[1] == "text":
            preferences["preferred_style"] = LearningStyle.READING_WRITING
        elif max_preference[1] == "audio":
            preferences["preferred_style"] = LearningStyle.AUDITORY
        elif max_preference[1] == "interactive":
            preferences["preferred_style"] = LearningStyle.KINESTHETIC
    else:
        preferences["preferred_style"] = LearningStyle.MULTIMODAL
    
    # Update user profile
    self.user_profile["learning_style"] = preferences["preferred_style"]
    
    logger.debug(f"Updated learning style preferences: {preferences}")

def analyze_learning_style(self) -> Dict[str, Any]:
    """
    Analyze learning style based on performance history.
    
    Returns:
        Dict[str, Any]: Learning style analysis
    """
    logger.info("Analyzing learning style")
    
    # Check if performance history exists
    if "performance_history" not in self.user_profile or not self.user_profile["performance_history"]:
        return {
            "status": "error",
            "message": "No performance history available for analysis",
            "learning_style": self.user_profile.get("learning_style", LearningStyle.MULTIMODAL)
        }
    
    # Get performance history
    history = self.user_profile["performance_history"]
    
    # Calculate average scores by content type
    scores_by_type = {}
    for entry in history:
        content_type = entry["content_type"]
        if content_type == "mixed":
            continue
        
        if content_type not in scores_by_type:
            scores_by_type[content_type] = []
        
        scores_by_type[content_type].append(entry["score"])
    
    # Calculate averages
    avg_scores = {}
    for content_type, scores in scores_by_type.items():
        if scores:
            avg_scores[content_type] = sum(scores) / len(scores)
    
    # Get learning style preferences
    preferences = self.user_profile.get("learning_style_preferences", {})
    if not preferences:
        preferences = {
            "visual": 0.25,
            "text": 0.25,
            "audio": 0.25,
            "interactive": 0.25,
            "preferred_style": LearningStyle.MULTIMODAL
        }
    
    # Create analysis
    analysis = {
        "status": "success",
        "message": "Learning style analysis completed",
        "learning_style": self.user_profile.get("learning_style", LearningStyle.MULTIMODAL),
        "preferences": {k: v for k, v in preferences.items() if k != "preferred_style"},
        "average_scores": avg_scores,
        "sample_size": len(history),
        "recommendations": []
    }
    
    # Generate recommendations
    if preferences.get("preferred_style") == LearningStyle.VISUAL:
        analysis["recommendations"].append("Focus on visual content like diagrams, charts, and mind maps")
        analysis["recommendations"].append("Use color coding and spatial organization in notes")
        analysis["recommendations"].append("Convert text-based information into visual formats")
    elif preferences.get("preferred_style") == LearningStyle.READING_WRITING:
        analysis["recommendations"].append("Focus on text-based content with detailed explanations")
        analysis["recommendations"].append("Take comprehensive notes and rewrite key concepts")
        analysis["recommendations"].append("Use written summaries and outlines")
    elif preferences.get("preferred_style") == LearningStyle.AUDITORY:
        analysis["recommendations"].append("Focus on audio content like lectures and discussions")
        analysis["recommendations"].append("Read content aloud or use text-to-speech")
        analysis["recommendations"].append("Discuss concepts with others to reinforce understanding")
    elif preferences.get("preferred_style") == LearningStyle.KINESTHETIC:
        analysis["recommendations"].append("Focus on interactive content with hands-on exercises")
        analysis["recommendations"].append("Use practical applications and real-world examples")
        analysis["recommendations"].append("Take breaks for physical activity during study sessions")
    else:  # MULTIMODAL
        analysis["recommendations"].append("Use a variety of content types to maintain engagement")
        analysis["recommendations"].append("Experiment with different learning approaches")
        analysis["recommendations"].append("Combine visual, text, audio, and interactive elements")
    
    return analysis

def generate_adapted_content(
    self,
    content: Dict[str, Any],
    target_style: Optional[str] = None,
    format_type: str = "default"
) -> Dict[str, Any]:
    """
    Generate content adapted to a specific learning style.
    
    Args:
        content (Dict[str, Any]): Original content
        target_style (str, optional): Target learning style (if None, uses user's preferred style)
        format_type (str): Output format (default, markdown, html)
        
    Returns:
        Dict[str, Any]: Adapted content
    """
    logger.info(f"Generating adapted content for style: {target_style or 'user preferred'}")
    
    # Get learning style
    if target_style:
        learning_style = target_style
    else:
        learning_style = self.user_profile.get("learning_style", LearningStyle.MULTIMODAL)
        
        # If user has preferences, use the preferred style
        preferences = self.user_profile.get("learning_style_preferences", {})
        if preferences and "preferred_style" in preferences:
            learning_style = preferences["preferred_style"]
    
    # Get content text
    text = content.get("text", "")
    summary = content.get("summary", "")
    title = content.get("title", "Untitled")
    
    # Use summary if available, otherwise use text
    content_text = summary if summary else text
    
    if not content_text:
        logger.error("No content text available for adaptation")
        return {
            "status": "error",
            "message": "No content text available for adaptation"
        }
    
    # Create prompt for content adaptation
    prompt = f"""
    You are adapting educational content to match a specific learning style.
    
    Original content title: {title}
    
    Original content:
    {content_text}
    
    Target learning style: {learning_style}
    
    Please adapt this content to better suit a {learning_style} learner. 
    """
    
    # Add style-specific instructions
    if learning_style == LearningStyle.VISUAL:
        prompt += """
        For VISUAL learners:
        - Describe visual elements like diagrams, charts, and mind maps
        - Use spatial language and visual metaphors
        - Organize information in a visual hierarchy
        - Suggest visual aids and visualization techniques
        - Include descriptions of colors, shapes, and patterns
        """
    elif learning_style == LearningStyle.READING_WRITING:
        prompt += """
        For READING/WRITING learners:
        - Provide detailed written explanations
        - Use clear definitions and structured text
        - Organize information in lists, outlines, and hierarchies
        - Include references to written materials
        - Focus on precise language and terminology
        """
    elif learning_style == LearningStyle.AUDITORY:
        prompt += """
        For AUDITORY learners:
        - Use conversational language and dialogue format
        - Include verbal cues and auditory descriptions
        - Suggest discussions and verbal repetition techniques
        - Frame concepts as conversations or interviews
        - Use rhythm and emphasis in explanations
        """
    elif learning_style == LearningStyle.KINESTHETIC:
        prompt += """
        For KINESTHETIC learners:
        - Focus on hands-on activities and practical applications
        - Include step-by-step instructions for exercises
        - Use action-oriented language and physical metaphors
        - Suggest interactive experiments and demonstrations
        - Connect concepts to physical sensations and movements
        """
    else:  # MULTIMODAL
        prompt += """
        For MULTIMODAL learners:
        - Combine elements from visual, reading/writing, auditory, and kinesthetic approaches
        - Provide multiple ways to engage with the material
        - Include a variety of examples and explanations
        - Suggest different learning activities for the same concept
        - Balance different learning modalities
        """
    
    # Add format instructions
    if format_type == "markdown":
        prompt += """
        Format your response in Markdown, using:
        - # for main headings
        - ## for subheadings
        - **bold** for emphasis
        - *italic* for secondary emphasis
        - - for bullet points
        - 1. for numbered lists
        - > for blockquotes
        - ``` for code blocks
        """
    elif format_type == "html":
        prompt += """
        Format your response in HTML, using:
        - <h1>, <h2>, etc. for headings
        - <p> for paragraphs
        - <strong> for emphasis
        - <em> for secondary emphasis
        - <ul> and <li> for bullet points
        - <ol> and <li> for numbered lists
        - <blockquote> for quotes
        - <pre> for code blocks
        """
    
    # Generate adapted content
    try:
        adapted_text = self.llm.generate_text(
            prompt,
            temperature=0.7
        )
        
        # Create result
        result = {
            "status": "success",
            "title": f"{title} (Adapted for {learning_style} learning)",
            "original_title": title,
            "adapted_text": adapted_text,
            "learning_style": learning_style,
            "format_type": format_type
        }
        
        return result
    except Exception as e:
        logger.error(f"Error generating adapted content: {e}")
        return {
            "status": "error",
            "message": f"Error generating adapted content: {e}"
        }