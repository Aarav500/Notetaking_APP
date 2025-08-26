"""
Quiz Agent module for AI Note System.
Provides adaptive quiz generation capabilities based on user's knowledge level and learning progress.
"""

import os
import logging
import json
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.agents.quiz_agent")

# Import interfaces
from ..api.llm_interface import LLMInterface, get_llm_interface
from ..api.embedding_interface import EmbeddingInterface, get_embedding_interface

class QuizType:
    """
    Enum-like class for quiz types.
    """
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    CODING = "coding"
    MIXED = "mixed"

class DifficultyLevel:
    """
    Enum-like class for difficulty levels.
    """
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    ADAPTIVE = "adaptive"

class QuizAgent:
    """
    Agent that provides adaptive quiz generation capabilities.
    Generates quizzes based on user's knowledge level and learning progress.
    """
    
    def __init__(
        self,
        llm_interface: Optional[LLMInterface] = None,
        embedding_interface: Optional[EmbeddingInterface] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        embedding_provider: str = "sentence-transformers",
        embedding_model: str = "all-MiniLM-L6-v2",
        user_profile: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the quiz agent.
        
        Args:
            llm_interface (LLMInterface, optional): LLM interface to use
            embedding_interface (EmbeddingInterface, optional): Embedding interface to use
            llm_provider (str): LLM provider to use if llm_interface is not provided
            llm_model (str): LLM model to use if llm_interface is not provided
            embedding_provider (str): Embedding provider to use if embedding_interface is not provided
            embedding_model (str): Embedding model to use if embedding_interface is not provided
            user_profile (Dict[str, Any], optional): User profile with learning preferences
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
        
        # Set embedding interface
        if embedding_interface:
            self.embedding = embedding_interface
        else:
            # Get embedding interface from provider and model
            self.embedding = get_embedding_interface(
                embedding_provider,
                model_name=embedding_model
            )
        
        # Set user profile
        self.user_profile = user_profile or {}
        
        # Set configuration
        self.config = config or {}
        
        # Initialize quiz history
        self.quiz_history = []
        
        logger.info("Quiz agent initialized")
    
    def generate_quiz(
        self,
        topic: str,
        content: Optional[str] = None,
        quiz_type: str = QuizType.MIXED,
        difficulty: str = DifficultyLevel.ADAPTIVE,
        num_questions: int = 5,
        time_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a quiz on a topic.
        
        Args:
            topic (str): Topic for the quiz
            content (str, optional): Content to generate quiz from
            quiz_type (str): Type of quiz to generate
            difficulty (str): Difficulty level of the quiz
            num_questions (int): Number of questions to generate
            time_limit (int, optional): Time limit for the quiz in minutes
            
        Returns:
            Dict[str, Any]: Generated quiz
        """
        logger.info(f"Generating {quiz_type} quiz on {topic} with {num_questions} questions")
        
        # Adjust difficulty based on user profile if adaptive
        if difficulty == DifficultyLevel.ADAPTIVE:
            difficulty = self._determine_adaptive_difficulty(topic)
        
        # Determine quiz types to include if mixed
        quiz_types = self._determine_quiz_types(quiz_type, num_questions)
        
        # Generate questions for each quiz type
        questions = []
        for q_type, count in quiz_types.items():
            if count > 0:
                type_questions = self._generate_questions_by_type(
                    topic=topic,
                    content=content,
                    quiz_type=q_type,
                    difficulty=difficulty,
                    num_questions=count
                )
                questions.extend(type_questions)
        
        # Shuffle questions
        random.shuffle(questions)
        
        # Create quiz
        quiz = {
            "id": f"quiz_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": f"Quiz on {topic}",
            "topic": topic,
            "difficulty": difficulty,
            "time_limit": time_limit,
            "questions": questions,
            "created_at": datetime.now().isoformat(),
            "metadata": {
                "quiz_type": quiz_type,
                "num_questions": len(questions),
                "types_distribution": quiz_types
            }
        }
        
        # Add to history
        self.quiz_history.append({
            "quiz_id": quiz["id"],
            "topic": topic,
            "difficulty": difficulty,
            "num_questions": len(questions),
            "created_at": quiz["created_at"]
        })
        
        return quiz
    
    def _determine_adaptive_difficulty(self, topic: str) -> str:
        """
        Determine the appropriate difficulty level based on user's history.
        
        Args:
            topic (str): Topic for the quiz
            
        Returns:
            str: Appropriate difficulty level
        """
        # Get user's knowledge level
        knowledge_level = self.user_profile.get("knowledge_level", "intermediate")
        
        # Get user's quiz history for this topic
        topic_history = [
            h for h in self.quiz_history 
            if h["topic"].lower() == topic.lower() or topic.lower() in h["topic"].lower()
        ]
        
        # If no history, base on knowledge level
        if not topic_history:
            if knowledge_level == "beginner":
                return DifficultyLevel.EASY
            elif knowledge_level == "intermediate":
                return DifficultyLevel.MEDIUM
            else:
                return DifficultyLevel.HARD
        
        # Calculate performance on previous quizzes
        # This is a placeholder - in a real implementation, we would use actual quiz results
        # For now, we'll just progress difficulty over time
        if len(topic_history) <= 2:
            return DifficultyLevel.EASY
        elif len(topic_history) <= 5:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _determine_quiz_types(self, quiz_type: str, num_questions: int) -> Dict[str, int]:
        """
        Determine the distribution of question types.
        
        Args:
            quiz_type (str): Type of quiz to generate
            num_questions (int): Number of questions to generate
            
        Returns:
            Dict[str, int]: Distribution of question types
        """
        if quiz_type != QuizType.MIXED:
            return {quiz_type: num_questions}
        
        # For mixed quizzes, distribute questions among types
        # Prioritize multiple choice and short answer
        distribution = {
            QuizType.MULTIPLE_CHOICE: max(1, int(num_questions * 0.4)),
            QuizType.SHORT_ANSWER: max(1, int(num_questions * 0.3)),
            QuizType.TRUE_FALSE: max(1, int(num_questions * 0.15)),
            QuizType.FILL_IN_BLANK: max(1, int(num_questions * 0.15))
        }
        
        # Adjust to match total
        total = sum(distribution.values())
        if total < num_questions:
            distribution[QuizType.MULTIPLE_CHOICE] += (num_questions - total)
        elif total > num_questions:
            # Remove excess questions from each type
            excess = total - num_questions
            for q_type in list(distribution.keys()):
                if excess <= 0:
                    break
                if distribution[q_type] > 1:
                    reduction = min(distribution[q_type] - 1, excess)
                    distribution[q_type] -= reduction
                    excess -= reduction
        
        return distribution
    
    def _generate_questions_by_type(
        self,
        topic: str,
        content: Optional[str],
        quiz_type: str,
        difficulty: str,
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """
        Generate questions of a specific type.
        
        Args:
            topic (str): Topic for the questions
            content (str, optional): Content to generate questions from
            quiz_type (str): Type of questions to generate
            difficulty (str): Difficulty level of the questions
            num_questions (int): Number of questions to generate
            
        Returns:
            List[Dict[str, Any]]: Generated questions
        """
        # Create prompt based on quiz type and difficulty
        prompt = f"Generate {num_questions} {difficulty} {quiz_type} questions about {topic}."
        
        if content:
            prompt += f" Base the questions on the following content:\n\n{content}\n\n"
        
        # Add specific instructions based on quiz type
        if quiz_type == QuizType.MULTIPLE_CHOICE:
            prompt += " For each question, provide 4 options with exactly one correct answer."
            output_schema = {
                "questions": [
                    {
                        "question": "The question text",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "The correct option (exactly as it appears in options)",
                        "explanation": "Explanation of why this is the correct answer"
                    }
                ]
            }
        elif quiz_type == QuizType.TRUE_FALSE:
            prompt += " For each statement, indicate whether it is true or false and provide an explanation."
            output_schema = {
                "questions": [
                    {
                        "statement": "The statement to evaluate as true or false",
                        "correct_answer": "true or false",
                        "explanation": "Explanation of why this is true or false"
                    }
                ]
            }
        elif quiz_type == QuizType.SHORT_ANSWER:
            prompt += " For each question, provide a model answer and key points that should be included in a correct response."
            output_schema = {
                "questions": [
                    {
                        "question": "The question text",
                        "model_answer": "A model answer to the question",
                        "key_points": ["Key point 1", "Key point 2", "Key point 3"],
                        "grading_rubric": "Guidelines for grading responses"
                    }
                ]
            }
        elif quiz_type == QuizType.FILL_IN_BLANK:
            prompt += " For each question, provide a sentence with a blank (indicated by ___) and the correct word or phrase to fill in."
            output_schema = {
                "questions": [
                    {
                        "text": "Sentence with ___ for the blank",
                        "correct_answer": "The word or phrase that correctly fills the blank",
                        "explanation": "Explanation of why this is the correct answer"
                    }
                ]
            }
        elif quiz_type == QuizType.MATCHING:
            prompt += " Create a matching exercise with terms and their definitions or related concepts."
            output_schema = {
                "questions": [
                    {
                        "instructions": "Match the items in Column A with their corresponding items in Column B",
                        "column_a": ["Item A1", "Item A2", "Item A3", "Item A4"],
                        "column_b": ["Item B1", "Item B2", "Item B3", "Item B4"],
                        "correct_matches": [
                            {"a": "Item A1", "b": "Item B3"},
                            {"a": "Item A2", "b": "Item B1"},
                            {"a": "Item A3", "b": "Item B4"},
                            {"a": "Item A4", "b": "Item B2"}
                        ]
                    }
                ]
            }
        elif quiz_type == QuizType.CODING:
            prompt += " Create coding exercises that test understanding of programming concepts. Include starter code, instructions, and expected output."
            output_schema = {
                "questions": [
                    {
                        "instructions": "The problem description and requirements",
                        "starter_code": "Code template to start with",
                        "expected_output": "Expected output or behavior",
                        "solution": "A working solution",
                        "hints": ["Hint 1", "Hint 2"],
                        "test_cases": [
                            {"input": "Test input 1", "expected": "Expected output 1"},
                            {"input": "Test input 2", "expected": "Expected output 2"}
                        ]
                    }
                ]
            }
        else:
            # Default schema for other types
            output_schema = {
                "questions": [
                    {
                        "question": "The question text",
                        "answer": "The answer",
                        "explanation": "Explanation of the answer"
                    }
                ]
            }
        
        # Add difficulty-specific instructions
        if difficulty == DifficultyLevel.EASY:
            prompt += " Make the questions straightforward and test basic understanding of the topic."
        elif difficulty == DifficultyLevel.MEDIUM:
            prompt += " Make the questions moderately challenging, testing deeper understanding and application of concepts."
        elif difficulty == DifficultyLevel.HARD:
            prompt += " Make the questions challenging, testing advanced understanding, analysis, and synthesis of concepts."
        
        # Generate questions using LLM
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.7
        )
        
        # Process and format questions
        questions = result.get("questions", [])
        
        # Add metadata to each question
        for i, question in enumerate(questions):
            question["id"] = f"q_{i+1}"
            question["type"] = quiz_type
            question["difficulty"] = difficulty
        
        return questions
    
    def grade_quiz(
        self,
        quiz_id: str,
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Grade a completed quiz.
        
        Args:
            quiz_id (str): ID of the quiz to grade
            answers (List[Dict[str, Any]]): User's answers to the quiz
            
        Returns:
            Dict[str, Any]: Grading results
        """
        # Find the quiz in history
        quiz = None
        for h in self.quiz_history:
            if h["quiz_id"] == quiz_id:
                quiz = h
                break
        
        if not quiz:
            logger.error(f"Quiz with ID {quiz_id} not found")
            return {"error": f"Quiz with ID {quiz_id} not found"}
        
        # Grade each answer
        graded_answers = []
        total_score = 0
        max_score = len(answers)
        
        for answer in answers:
            question_id = answer.get("question_id")
            user_answer = answer.get("answer")
            question_type = answer.get("type")
            
            # Grade based on question type
            if question_type == QuizType.MULTIPLE_CHOICE or question_type == QuizType.TRUE_FALSE:
                # Direct comparison with correct answer
                correct_answer = answer.get("correct_answer")
                is_correct = user_answer == correct_answer
                score = 1 if is_correct else 0
                
                graded_answers.append({
                    "question_id": question_id,
                    "is_correct": is_correct,
                    "score": score,
                    "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}"
                })
                
                total_score += score
                
            elif question_type == QuizType.FILL_IN_BLANK:
                # Check if answer matches exactly or is close enough
                correct_answer = answer.get("correct_answer")
                is_correct = user_answer.lower() == correct_answer.lower()
                score = 1 if is_correct else 0
                
                graded_answers.append({
                    "question_id": question_id,
                    "is_correct": is_correct,
                    "score": score,
                    "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}"
                })
                
                total_score += score
                
            elif question_type == QuizType.SHORT_ANSWER:
                # Use LLM to evaluate short answer
                key_points = answer.get("key_points", [])
                model_answer = answer.get("model_answer", "")
                
                evaluation = self._evaluate_short_answer(
                    question=answer.get("question", ""),
                    user_answer=user_answer,
                    model_answer=model_answer,
                    key_points=key_points
                )
                
                graded_answers.append({
                    "question_id": question_id,
                    "score": evaluation["score"],
                    "feedback": evaluation["feedback"],
                    "key_points_covered": evaluation["key_points_covered"],
                    "key_points_missed": evaluation["key_points_missed"]
                })
                
                total_score += evaluation["score"]
                
            elif question_type == QuizType.MATCHING:
                # Check matching pairs
                correct_matches = answer.get("correct_matches", [])
                user_matches = user_answer
                
                correct_count = 0
                for user_match in user_matches:
                    if any(m["a"] == user_match["a"] and m["b"] == user_match["b"] for m in correct_matches):
                        correct_count += 1
                
                score = correct_count / len(correct_matches) if correct_matches else 0
                
                graded_answers.append({
                    "question_id": question_id,
                    "score": score,
                    "correct_count": correct_count,
                    "total_matches": len(correct_matches),
                    "feedback": f"You matched {correct_count} out of {len(correct_matches)} items correctly."
                })
                
                total_score += score
                
            elif question_type == QuizType.CODING:
                # Evaluate code solution
                # This would typically involve running tests, but for simplicity,
                # we'll use LLM to evaluate the code
                evaluation = self._evaluate_code_solution(
                    instructions=answer.get("instructions", ""),
                    user_code=user_answer,
                    solution_code=answer.get("solution", ""),
                    test_cases=answer.get("test_cases", [])
                )
                
                graded_answers.append({
                    "question_id": question_id,
                    "score": evaluation["score"],
                    "feedback": evaluation["feedback"],
                    "test_results": evaluation["test_results"]
                })
                
                total_score += evaluation["score"]
                
            else:
                # Default grading for other types
                graded_answers.append({
                    "question_id": question_id,
                    "score": 0,
                    "feedback": "Unable to grade this question type automatically."
                })
        
        # Calculate percentage score
        percentage_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Determine grade
        grade = self._determine_grade(percentage_score)
        
        # Create grading result
        grading_result = {
            "quiz_id": quiz_id,
            "total_score": total_score,
            "max_score": max_score,
            "percentage_score": percentage_score,
            "grade": grade,
            "graded_answers": graded_answers,
            "graded_at": datetime.now().isoformat()
        }
        
        # Update quiz history with results
        for h in self.quiz_history:
            if h["quiz_id"] == quiz_id:
                h["results"] = {
                    "total_score": total_score,
                    "max_score": max_score,
                    "percentage_score": percentage_score,
                    "grade": grade,
                    "graded_at": grading_result["graded_at"]
                }
                break
        
        return grading_result
    
    def _evaluate_short_answer(
        self,
        question: str,
        user_answer: str,
        model_answer: str,
        key_points: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate a short answer response.
        
        Args:
            question (str): The question
            user_answer (str): User's answer
            model_answer (str): Model answer
            key_points (List[str]): Key points that should be covered
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Create prompt for evaluation
        prompt = f"""
        Evaluate the following short answer response:
        
        Question: {question}
        
        Model Answer: {model_answer}
        
        Key Points that should be covered:
        {', '.join(key_points)}
        
        User's Answer: {user_answer}
        
        Please evaluate the user's answer based on:
        1. Coverage of key points
        2. Accuracy of information
        3. Clarity and coherence
        
        Provide a score from 0.0 to 1.0, where 1.0 is perfect.
        """
        
        # Define output schema
        output_schema = {
            "evaluation": {
                "score": "Score from 0.0 to 1.0",
                "key_points_covered": ["Key points that were covered"],
                "key_points_missed": ["Key points that were missed"],
                "feedback": "Detailed feedback on the answer"
            }
        }
        
        # Generate evaluation
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.3
        )
        
        evaluation = result.get("evaluation", {})
        
        # Convert score to float
        try:
            score = float(evaluation.get("score", 0))
            score = max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
        except (ValueError, TypeError):
            score = 0.0
        
        evaluation["score"] = score
        
        return evaluation
    
    def _evaluate_code_solution(
        self,
        instructions: str,
        user_code: str,
        solution_code: str,
        test_cases: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Evaluate a code solution.
        
        Args:
            instructions (str): Problem instructions
            user_code (str): User's code solution
            solution_code (str): Model solution code
            test_cases (List[Dict[str, str]]): Test cases
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        # Create prompt for evaluation
        prompt = f"""
        Evaluate the following code solution:
        
        Problem Instructions: {instructions}
        
        Model Solution:
        ```
        {solution_code}
        ```
        
        User's Solution:
        ```
        {user_code}
        ```
        
        Test Cases:
        {json.dumps(test_cases, indent=2)}
        
        Please evaluate the user's solution based on:
        1. Correctness (does it produce the expected output for all test cases)
        2. Efficiency (time and space complexity)
        3. Code quality (readability, organization)
        
        Provide a score from 0.0 to 1.0, where 1.0 is perfect.
        """
        
        # Define output schema
        output_schema = {
            "evaluation": {
                "score": "Score from 0.0 to 1.0",
                "feedback": "Detailed feedback on the solution",
                "test_results": [
                    {
                        "test_case": "Description of test case",
                        "passed": "true or false",
                        "expected": "Expected output",
                        "actual": "Actual output (if determinable)",
                        "notes": "Any notes about this test case"
                    }
                ]
            }
        }
        
        # Generate evaluation
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.3
        )
        
        evaluation = result.get("evaluation", {})
        
        # Convert score to float
        try:
            score = float(evaluation.get("score", 0))
            score = max(0.0, min(1.0, score))  # Ensure score is between 0 and 1
        except (ValueError, TypeError):
            score = 0.0
        
        evaluation["score"] = score
        
        return evaluation
    
    def _determine_grade(self, percentage_score: float) -> str:
        """
        Determine the letter grade based on percentage score.
        
        Args:
            percentage_score (float): Percentage score
            
        Returns:
            str: Letter grade
        """
        if percentage_score >= 90:
            return "A"
        elif percentage_score >= 80:
            return "B"
        elif percentage_score >= 70:
            return "C"
        elif percentage_score >= 60:
            return "D"
        else:
            return "F"
    
    def generate_quiz_report(self, quiz_id: str) -> Dict[str, Any]:
        """
        Generate a report for a completed quiz.
        
        Args:
            quiz_id (str): ID of the quiz
            
        Returns:
            Dict[str, Any]: Quiz report
        """
        # Find the quiz in history
        quiz = None
        for h in self.quiz_history:
            if h["quiz_id"] == quiz_id and "results" in h:
                quiz = h
                break
        
        if not quiz:
            logger.error(f"Completed quiz with ID {quiz_id} not found")
            return {"error": f"Completed quiz with ID {quiz_id} not found"}
        
        # Create report prompt
        prompt = f"""
        Generate a comprehensive learning report based on the following quiz results:
        
        Topic: {quiz['topic']}
        Difficulty: {quiz['difficulty']}
        Score: {quiz['results']['percentage_score']}% ({quiz['results']['total_score']}/{quiz['results']['max_score']})
        Grade: {quiz['results']['grade']}
        
        Please include:
        1. A summary of performance
        2. Strengths and areas for improvement
        3. Recommended next steps for learning
        4. Suggested resources for further study
        """
        
        # Define output schema
        output_schema = {
            "report": {
                "summary": "Summary of quiz performance",
                "strengths": ["Areas of strength"],
                "areas_for_improvement": ["Areas that need improvement"],
                "next_steps": ["Recommended next steps for learning"],
                "resources": [
                    {
                        "title": "Resource title",
                        "type": "Resource type (article, video, book, etc.)",
                        "description": "Brief description of the resource"
                    }
                ]
            }
        }
        
        # Generate report
        result = self.llm.generate_structured_output(
            prompt,
            output_schema,
            temperature=0.5
        )
        
        # Create final report
        report = {
            "quiz_id": quiz_id,
            "topic": quiz["topic"],
            "difficulty": quiz["difficulty"],
            "score": quiz["results"]["percentage_score"],
            "grade": quiz["results"]["grade"],
            "report": result.get("report", {}),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def save_quiz_history(self, file_path: str) -> bool:
        """
        Save quiz history to a file.
        
        Args:
            file_path (str): Path to save the history
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.quiz_history, f, indent=2)
            
            logger.info(f"Quiz history saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving quiz history: {e}")
            return False
    
    def load_quiz_history(self, file_path: str) -> bool:
        """
        Load quiz history from a file.
        
        Args:
            file_path (str): Path to load the history from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load from file
            with open(file_path, 'r', encoding='utf-8') as f:
                self.quiz_history = json.load(f)
            
            logger.info(f"Quiz history loaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading quiz history: {e}")
            return False


def create_quiz_agent_from_config(config: Dict[str, Any]) -> QuizAgent:
    """
    Create a quiz agent from a configuration dictionary.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        QuizAgent: The quiz agent
    """
    # Get LLM provider and model
    llm_provider = config.get("LLM_PROVIDER", "openai")
    llm_model = config.get("LLM_MODEL", "gpt-4")
    
    # Get embedding provider and model
    embedding_provider = config.get("EMBEDDING_PROVIDER", "sentence-transformers")
    embedding_model = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Get user profile
    user_profile = config.get("USER_PROFILE", {})
    
    # Create quiz agent
    agent = QuizAgent(
        llm_provider=llm_provider,
        llm_model=llm_model,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        user_profile=user_profile,
        config=config
    )
    
    return agent