"""
Learning Agent with Accountability Mode module for AI Note System.
Creates a bot that checks in daily, sends personalized micro-quizzes, and generates quick voice notes for on-the-go learning.
"""

import os
import logging
import json
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import time
import threading

# Setup logging
logger = logging.getLogger("ai_note_system.agents.accountability_agent")

class AccountabilityAgent:
    """
    Agent that provides accountability features to help users maintain consistent learning habits.
    """
    
    def __init__(self, db_manager, quiz_agent=None, llm_interface=None):
        """
        Initialize the accountability agent.
        
        Args:
            db_manager: Database manager instance
            quiz_agent: Quiz agent instance for generating quizzes
            llm_interface: LLM interface for generating content
        """
        self.db_manager = db_manager
        self.quiz_agent = quiz_agent
        self.llm_interface = llm_interface
        self._ensure_accountability_tables()
        self.scheduler_thread = None
        self.stop_scheduler = False
    
    def _ensure_accountability_tables(self) -> None:
        """
        Ensure the accountability-related tables exist in the database.
        """
        # Create accountability_settings table
        settings_query = """
        CREATE TABLE IF NOT EXISTS accountability_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            username TEXT NOT NULL,
            check_in_time TEXT,
            check_in_days TEXT,
            quiz_frequency TEXT,
            quiz_topics TEXT,
            strictness TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, platform)
        )
        """
        self.db_manager.execute_query(settings_query)
        
        # Create check_ins table
        check_ins_query = """
        CREATE TABLE IF NOT EXISTS check_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT NOT NULL,
            response TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(check_ins_query)
        
        # Create accountability_quizzes table
        quizzes_query = """
        CREATE TABLE IF NOT EXISTS accountability_quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            topic TEXT,
            questions TEXT,
            responses TEXT,
            score REAL,
            completed BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(quizzes_query)
        
        # Create voice_notes table
        voice_notes_query = """
        CREATE TABLE IF NOT EXISTS voice_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            topic TEXT,
            duration_seconds INTEGER,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(voice_notes_query)
    
    def setup(self, user_id: int, platform: str, username: str) -> Dict[str, Any]:
        """
        Set up accountability agent for a user.
        
        Args:
            user_id (int): ID of the user
            platform (str): Platform for notifications (telegram, discord, slack)
            username (str): Username on the platform
            
        Returns:
            Dict[str, Any]: Setup result
        """
        # Validate platform
        valid_platforms = ["telegram", "discord", "slack", "email"]
        if platform.lower() not in valid_platforms:
            return {
                "status": "error",
                "message": f"Invalid platform. Supported platforms: {', '.join(valid_platforms)}"
            }
        
        # Check if setup already exists
        check_query = """
        SELECT id FROM accountability_settings
        WHERE user_id = ? AND platform = ?
        """
        
        existing = self.db_manager.execute_query(check_query, (user_id, platform)).fetchone()
        
        if existing:
            # Update existing setup
            update_query = """
            UPDATE accountability_settings
            SET username = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND platform = ?
            """
            
            self.db_manager.execute_query(update_query, (username, user_id, platform))
            
            return {
                "status": "success",
                "message": f"Updated accountability setup for {platform}",
                "settings_id": existing["id"]
            }
        else:
            # Create new setup
            insert_query = """
            INSERT INTO accountability_settings (user_id, platform, username)
            VALUES (?, ?, ?)
            """
            
            cursor = self.db_manager.execute_query(insert_query, (user_id, platform, username))
            
            return {
                "status": "success",
                "message": f"Set up accountability agent for {platform}",
                "settings_id": cursor.lastrowid
            }
    
    def schedule_check_ins(self, user_id: int, time: str, days: List[str]) -> Dict[str, Any]:
        """
        Configure daily check-ins.
        
        Args:
            user_id (int): ID of the user
            time (str): Time for check-ins (HH:MM format)
            days (List[str]): Days for check-ins (mon, tue, wed, thu, fri, sat, sun)
            
        Returns:
            Dict[str, Any]: Schedule result
        """
        # Validate time format
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid time format. Use HH:MM (24-hour format)"
            }
        
        # Validate days
        valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        days = [day.lower() for day in days]
        invalid_days = [day for day in days if day not in valid_days]
        
        if invalid_days:
            return {
                "status": "error",
                "message": f"Invalid days: {', '.join(invalid_days)}. Valid days: {', '.join(valid_days)}"
            }
        
        # Update settings
        update_query = """
        UPDATE accountability_settings
        SET check_in_time = ?, check_in_days = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """
        
        days_str = ",".join(days)
        self.db_manager.execute_query(update_query, (time, days_str, user_id))
        
        # Start scheduler if not already running
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            self.start_scheduler()
        
        return {
            "status": "success",
            "message": f"Scheduled check-ins for {days_str} at {time}",
            "time": time,
            "days": days
        }
    
    def configure_quizzes(self, user_id: int, frequency: str, topics: List[str]) -> Dict[str, Any]:
        """
        Configure micro-quizzes.
        
        Args:
            user_id (int): ID of the user
            frequency (str): Frequency for quizzes (daily, weekly)
            topics (List[str]): Topics for quizzes
            
        Returns:
            Dict[str, Any]: Configuration result
        """
        # Validate frequency
        valid_frequencies = ["daily", "weekly", "biweekly"]
        if frequency.lower() not in valid_frequencies:
            return {
                "status": "error",
                "message": f"Invalid frequency. Supported frequencies: {', '.join(valid_frequencies)}"
            }
        
        # Update settings
        update_query = """
        UPDATE accountability_settings
        SET quiz_frequency = ?, quiz_topics = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """
        
        topics_str = ",".join(topics)
        self.db_manager.execute_query(update_query, (frequency.lower(), topics_str, user_id))
        
        return {
            "status": "success",
            "message": f"Configured {frequency} quizzes for topics: {topics_str}",
            "frequency": frequency,
            "topics": topics
        }
    
    def adjust_settings(self, user_id: int, strictness: str) -> Dict[str, Any]:
        """
        Adjust accountability settings.
        
        Args:
            user_id (int): ID of the user
            strictness (str): Strictness level (low, medium, high)
            
        Returns:
            Dict[str, Any]: Adjustment result
        """
        # Validate strictness
        valid_strictness = ["low", "medium", "high"]
        if strictness.lower() not in valid_strictness:
            return {
                "status": "error",
                "message": f"Invalid strictness level. Supported levels: {', '.join(valid_strictness)}"
            }
        
        # Update settings
        update_query = """
        UPDATE accountability_settings
        SET strictness = ?, updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """
        
        self.db_manager.execute_query(update_query, (strictness.lower(), user_id))
        
        return {
            "status": "success",
            "message": f"Adjusted accountability strictness to {strictness}",
            "strictness": strictness
        }
    
    def get_settings(self, user_id: int) -> Dict[str, Any]:
        """
        Get accountability settings for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: User's accountability settings
        """
        query = """
        SELECT * FROM accountability_settings
        WHERE user_id = ?
        """
        
        result = self.db_manager.execute_query(query, (user_id,)).fetchone()
        
        if not result:
            return {
                "status": "error",
                "message": "No accountability settings found for this user"
            }
        
        settings = dict(result)
        
        # Parse days and topics
        if settings.get("check_in_days"):
            settings["check_in_days"] = settings["check_in_days"].split(",")
        else:
            settings["check_in_days"] = []
        
        if settings.get("quiz_topics"):
            settings["quiz_topics"] = settings["quiz_topics"].split(",")
        else:
            settings["quiz_topics"] = []
        
        return {
            "status": "success",
            "settings": settings
        }
    
    def generate_check_in(self, user_id: int) -> Dict[str, Any]:
        """
        Generate a check-in message for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: Check-in message
        """
        # Get user settings
        settings_result = self.get_settings(user_id)
        if settings_result["status"] == "error":
            return settings_result
        
        settings = settings_result["settings"]
        
        # Get user's recent activity
        recent_activity = self._get_user_recent_activity(user_id)
        
        # Generate check-in message
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface if not provided
        if not self.llm_interface:
            self.llm_interface = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        strictness = settings.get("strictness", "medium")
        
        prompt = f"""
        Generate a friendly but {strictness} accountability check-in message for a user's learning journey.
        
        User's recent activity:
        - Notes created in the last 7 days: {recent_activity['notes_created']}
        - Quizzes taken in the last 7 days: {recent_activity['quizzes_taken']}
        - Last check-in: {recent_activity['last_check_in']}
        
        The message should:
        1. Greet the user
        2. Mention their recent activity (or lack thereof)
        3. Ask about their learning progress
        4. Provide a specific question about one of their topics
        5. Encourage them to set a small, achievable learning goal for today
        
        Keep the tone supportive but with {strictness} accountability (more strict = more direct about missed goals).
        """
        
        # Generate message
        check_in_message = self.llm_interface.generate_text(prompt)
        
        # Record check-in
        self._record_check_in(user_id, "generated")
        
        return {
            "status": "success",
            "message": check_in_message,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_user_recent_activity(self, user_id: int) -> Dict[str, Any]:
        """
        Get user's recent activity.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            Dict[str, Any]: Recent activity data
        """
        # Get notes created in the last 7 days
        notes_query = """
        SELECT COUNT(*) as count
        FROM notes
        WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
        """
        
        notes_result = self.db_manager.execute_query(notes_query, (user_id,)).fetchone()
        notes_created = notes_result["count"] if notes_result else 0
        
        # Get quizzes taken in the last 7 days
        quizzes_query = """
        SELECT COUNT(*) as count
        FROM accountability_quizzes
        WHERE user_id = ? AND completed = 1 AND quiz_time >= datetime('now', '-7 days')
        """
        
        quizzes_result = self.db_manager.execute_query(quizzes_query, (user_id,)).fetchone()
        quizzes_taken = quizzes_result["count"] if quizzes_result else 0
        
        # Get last check-in
        check_in_query = """
        SELECT check_in_time
        FROM check_ins
        WHERE user_id = ?
        ORDER BY check_in_time DESC
        LIMIT 1
        """
        
        check_in_result = self.db_manager.execute_query(check_in_query, (user_id,)).fetchone()
        last_check_in = check_in_result["check_in_time"] if check_in_result else "Never"
        
        return {
            "notes_created": notes_created,
            "quizzes_taken": quizzes_taken,
            "last_check_in": last_check_in
        }
    
    def _record_check_in(self, user_id: int, status: str, response: Optional[str] = None) -> int:
        """
        Record a check-in.
        
        Args:
            user_id (int): ID of the user
            status (str): Check-in status (generated, sent, responded)
            response (str, optional): User's response
            
        Returns:
            int: ID of the recorded check-in
        """
        query = """
        INSERT INTO check_ins (user_id, status, response)
        VALUES (?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (user_id, status, response))
        return cursor.lastrowid
    
    def generate_micro_quiz(self, user_id: int, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a micro-quiz for a user.
        
        Args:
            user_id (int): ID of the user
            topic (str, optional): Specific topic for the quiz
            
        Returns:
            Dict[str, Any]: Generated quiz
        """
        # Get user settings
        settings_result = self.get_settings(user_id)
        if settings_result["status"] == "error":
            return settings_result
        
        settings = settings_result["settings"]
        
        # Determine topic if not provided
        if not topic:
            if settings.get("quiz_topics"):
                topics = settings["quiz_topics"]
                topic = random.choice(topics)
            else:
                # Get a random topic from user's notes
                topic_query = """
                SELECT DISTINCT tags
                FROM notes
                WHERE user_id = ?
                """
                
                topic_results = self.db_manager.execute_query(topic_query, (user_id,)).fetchall()
                all_tags = []
                
                for result in topic_results:
                    if result["tags"]:
                        tags = result["tags"].split(",")
                        all_tags.extend(tags)
                
                if all_tags:
                    topic = random.choice(all_tags)
                else:
                    topic = "general knowledge"
        
        # Generate quiz
        if self.quiz_agent:
            # Use quiz agent if available
            quiz = self.quiz_agent.generate_quiz(
                topic=topic,
                quiz_type="mixed",
                difficulty="adaptive",
                num_questions=3  # Micro-quiz with just 3 questions
            )
            
            questions = quiz.get("questions", [])
        else:
            # Generate simple quiz using LLM
            from ai_note_system.api.llm_interface import get_llm_interface
            
            # Get LLM interface if not provided
            if not self.llm_interface:
                self.llm_interface = get_llm_interface("openai", model="gpt-4")
            
            # Create prompt
            prompt = f"""
            Generate a micro-quiz with 3 questions about {topic}.
            
            Include a mix of:
            - 1 multiple-choice question
            - 1 true/false question
            - 1 short answer question
            
            Format your response as a JSON array of question objects with the following structure:
            [
                {{
                    "type": "multiple_choice",
                    "question": "The question text",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "The correct option"
                }},
                {{
                    "type": "true_false",
                    "question": "The statement to evaluate",
                    "correct_answer": true or false
                }},
                {{
                    "type": "short_answer",
                    "question": "The question text",
                    "correct_answer": "The answer"
                }}
            ]
            """
            
            # Generate quiz
            response = self.llm_interface.generate_text(prompt)
            
            try:
                questions = json.loads(response)
            except json.JSONDecodeError:
                logger.error(f"Error parsing quiz response: {response}")
                questions = []
        
        # Store quiz
        quiz_json = json.dumps(questions)
        
        query = """
        INSERT INTO accountability_quizzes (user_id, topic, questions)
        VALUES (?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (user_id, topic, quiz_json))
        quiz_id = cursor.lastrowid
        
        return {
            "status": "success",
            "quiz_id": quiz_id,
            "topic": topic,
            "questions": questions,
            "timestamp": datetime.now().isoformat()
        }
    
    def submit_quiz_answers(self, user_id: int, quiz_id: int, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Submit answers to a quiz.
        
        Args:
            user_id (int): ID of the user
            quiz_id (int): ID of the quiz
            answers (List[Dict[str, Any]]): User's answers
            
        Returns:
            Dict[str, Any]: Quiz results
        """
        # Get quiz
        query = """
        SELECT * FROM accountability_quizzes
        WHERE id = ? AND user_id = ?
        """
        
        quiz = self.db_manager.execute_query(query, (quiz_id, user_id)).fetchone()
        
        if not quiz:
            return {
                "status": "error",
                "message": "Quiz not found"
            }
        
        # Parse questions
        try:
            questions = json.loads(quiz["questions"])
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Error parsing quiz questions"
            }
        
        # Grade answers
        correct_count = 0
        total_questions = len(questions)
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            question_type = question.get("type")
            
            if question_type == "multiple_choice":
                if answer.get("answer") == question.get("correct_answer"):
                    correct_count += 1
            elif question_type == "true_false":
                if answer.get("answer") == question.get("correct_answer"):
                    correct_count += 1
            elif question_type == "short_answer":
                # Simple string matching for short answers
                user_answer = answer.get("answer", "").lower().strip()
                correct_answer = question.get("correct_answer", "").lower().strip()
                
                if user_answer == correct_answer:
                    correct_count += 1
        
        # Calculate score
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        
        # Update quiz
        update_query = """
        UPDATE accountability_quizzes
        SET responses = ?, score = ?, completed = 1
        WHERE id = ?
        """
        
        responses_json = json.dumps(answers)
        self.db_manager.execute_query(update_query, (responses_json, score, quiz_id))
        
        return {
            "status": "success",
            "quiz_id": quiz_id,
            "score": score,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_voice_note(self, user_id: int, topic: str, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Generate a voice note for on-the-go learning.
        
        Args:
            user_id (int): ID of the user
            topic (str): Topic for the voice note
            duration_minutes (int): Duration in minutes
            
        Returns:
            Dict[str, Any]: Generated voice note
        """
        # Get user's notes on the topic
        query = """
        SELECT * FROM notes
        WHERE user_id = ? AND (tags LIKE ? OR title LIKE ?)
        ORDER BY created_at DESC
        LIMIT 5
        """
        
        search_term = f"%{topic}%"
        notes = self.db_manager.execute_query(query, (user_id, search_term, search_term)).fetchall()
        
        # Generate voice note content
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface if not provided
        if not self.llm_interface:
            self.llm_interface = get_llm_interface("openai", model="gpt-4")
        
        # Create context from notes
        notes_context = ""
        for note in notes:
            title = note["title"]
            summary = note.get("summary", "")
            text = note.get("text", "")
            
            content = summary if summary else text
            notes_context += f"Note: {title}\n{content[:500]}...\n\n"
        
        # Create prompt
        prompt = f"""
        Create a {duration_minutes}-minute voice note script about {topic}.
        
        User's notes on this topic:
        {notes_context}
        
        The voice note should:
        1. Start with a brief introduction to the topic
        2. Cover 3-5 key points or concepts
        3. Include practical examples or applications
        4. End with a summary and a thought-provoking question
        
        The script should be conversational, clear, and designed for listening rather than reading.
        Aim for approximately {duration_minutes * 150} words (about 150 words per minute).
        """
        
        # Generate voice note script
        script = self.llm_interface.generate_text(prompt)
        
        # Convert to speech (mock implementation)
        # In a real implementation, this would use a text-to-speech service
        duration_seconds = duration_minutes * 60
        file_path = f"voice_notes/{user_id}_{topic.replace(' ', '_')}_{int(time.time())}.mp3"
        
        # Store voice note
        query = """
        INSERT INTO voice_notes (user_id, topic, duration_seconds, file_path)
        VALUES (?, ?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (user_id, topic, duration_seconds, file_path))
        voice_note_id = cursor.lastrowid
        
        return {
            "status": "success",
            "voice_note_id": voice_note_id,
            "topic": topic,
            "duration_minutes": duration_minutes,
            "script": script,
            "file_path": file_path,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_accountability_stats(self, user_id: int, period_days: int = 30) -> Dict[str, Any]:
        """
        Get accountability statistics for a user.
        
        Args:
            user_id (int): ID of the user
            period_days (int): Number of days to look back
            
        Returns:
            Dict[str, Any]: Accountability statistics
        """
        # Calculate start date
        start_date = datetime.now() - timedelta(days=period_days)
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get check-in stats
        check_in_query = """
        SELECT status, COUNT(*) as count
        FROM check_ins
        WHERE user_id = ? AND check_in_time >= ?
        GROUP BY status
        """
        
        check_in_results = self.db_manager.execute_query(check_in_query, (user_id, start_date_str)).fetchall()
        
        check_in_stats = {
            "generated": 0,
            "sent": 0,
            "responded": 0
        }
        
        for result in check_in_results:
            status = result["status"]
            count = result["count"]
            
            if status in check_in_stats:
                check_in_stats[status] = count
        
        # Get quiz stats
        quiz_query = """
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed,
               AVG(CASE WHEN completed = 1 THEN score ELSE NULL END) as avg_score
        FROM accountability_quizzes
        WHERE user_id = ? AND quiz_time >= ?
        """
        
        quiz_result = self.db_manager.execute_query(quiz_query, (user_id, start_date_str)).fetchone()
        
        quiz_stats = {
            "total": quiz_result["total"] if quiz_result else 0,
            "completed": quiz_result["completed"] if quiz_result else 0,
            "avg_score": quiz_result["avg_score"] if quiz_result and quiz_result["avg_score"] is not None else 0
        }
        
        # Get voice note stats
        voice_note_query = """
        SELECT COUNT(*) as count, AVG(duration_seconds) as avg_duration
        FROM voice_notes
        WHERE user_id = ? AND created_at >= ?
        """
        
        voice_note_result = self.db_manager.execute_query(voice_note_query, (user_id, start_date_str)).fetchone()
        
        voice_note_stats = {
            "count": voice_note_result["count"] if voice_note_result else 0,
            "avg_duration_minutes": round(voice_note_result["avg_duration"] / 60, 1) if voice_note_result and voice_note_result["avg_duration"] is not None else 0
        }
        
        # Calculate consistency score
        # This is a simple metric based on check-in response rate and quiz completion rate
        check_in_rate = check_in_stats["responded"] / check_in_stats["sent"] if check_in_stats["sent"] > 0 else 0
        quiz_completion_rate = quiz_stats["completed"] / quiz_stats["total"] if quiz_stats["total"] > 0 else 0
        
        consistency_score = (check_in_rate * 0.6 + quiz_completion_rate * 0.4) * 100
        
        return {
            "status": "success",
            "period_days": period_days,
            "check_in_stats": check_in_stats,
            "quiz_stats": quiz_stats,
            "voice_note_stats": voice_note_stats,
            "consistency_score": round(consistency_score, 1)
        }
    
    def start_scheduler(self) -> None:
        """
        Start the scheduler thread for automated check-ins and quizzes.
        """
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.info("Scheduler already running")
            return
        
        self.stop_scheduler = False
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Started accountability scheduler")
    
    def stop_scheduler(self) -> None:
        """
        Stop the scheduler thread.
        """
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.stop_scheduler = True
            self.scheduler_thread.join(timeout=5)
            logger.info("Stopped accountability scheduler")
    
    def _scheduler_loop(self) -> None:
        """
        Main loop for the scheduler thread.
        """
        while not self.stop_scheduler:
            try:
                # Get current time
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                current_day = now.strftime("%a").lower()[:3]  # mon, tue, wed, etc.
                
                # Find users with check-ins scheduled for now
                query = """
                SELECT user_id, platform, username
                FROM accountability_settings
                WHERE check_in_time = ? AND check_in_days LIKE ?
                """
                
                results = self.db_manager.execute_query(query, (current_time, f"%{current_day}%")).fetchall()
                
                for result in results:
                    user_id = result["user_id"]
                    platform = result["platform"]
                    username = result["username"]
                    
                    # Generate check-in
                    check_in_result = self.generate_check_in(user_id)
                    
                    if check_in_result["status"] == "success":
                        # Send check-in (mock implementation)
                        # In a real implementation, this would use the appropriate platform's API
                        logger.info(f"Sending check-in to {username} on {platform}: {check_in_result['message'][:50]}...")
                        
                        # Record as sent
                        self._record_check_in(user_id, "sent")
                
                # Find users with quizzes scheduled for now
                quiz_query = """
                SELECT user_id, quiz_frequency, quiz_topics
                FROM accountability_settings
                WHERE (
                    (quiz_frequency = 'daily' AND strftime('%H:%M', 'now') = check_in_time) OR
                    (quiz_frequency = 'weekly' AND strftime('%w', 'now') = '1' AND strftime('%H:%M', 'now') = check_in_time) OR
                    (quiz_frequency = 'biweekly' AND strftime('%w', 'now') IN ('1', '4') AND strftime('%H:%M', 'now') = check_in_time)
                )
                """
                
                quiz_results = self.db_manager.execute_query(quiz_query).fetchall()
                
                for result in quiz_results:
                    user_id = result["user_id"]
                    
                    # Generate quiz
                    self.generate_micro_quiz(user_id)
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Sleep and try again

def setup_accountability(db_manager, user_id: int, platform: str, username: str) -> Dict[str, Any]:
    """
    Set up accountability agent for a user.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        platform (str): Platform for notifications (telegram, discord, slack)
        username (str): Username on the platform
        
    Returns:
        Dict[str, Any]: Setup result
    """
    agent = AccountabilityAgent(db_manager)
    return agent.setup(user_id, platform, username)

def schedule_check_ins(db_manager, user_id: int, time: str, days: List[str]) -> Dict[str, Any]:
    """
    Configure daily check-ins.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        time (str): Time for check-ins (HH:MM format)
        days (List[str]): Days for check-ins (mon, tue, wed, thu, fri, sat, sun)
        
    Returns:
        Dict[str, Any]: Schedule result
    """
    agent = AccountabilityAgent(db_manager)
    return agent.schedule_check_ins(user_id, time, days)

def configure_quizzes(db_manager, user_id: int, frequency: str, topics: List[str]) -> Dict[str, Any]:
    """
    Configure micro-quizzes.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        frequency (str): Frequency for quizzes (daily, weekly)
        topics (List[str]): Topics for quizzes
        
    Returns:
        Dict[str, Any]: Configuration result
    """
    agent = AccountabilityAgent(db_manager)
    return agent.configure_quizzes(user_id, frequency, topics)

def generate_voice_note(db_manager, user_id: int, topic: str, duration_minutes: int = 5) -> Dict[str, Any]:
    """
    Generate a voice note for on-the-go learning.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        topic (str): Topic for the voice note
        duration_minutes (int): Duration in minutes
        
    Returns:
        Dict[str, Any]: Generated voice note
    """
    agent = AccountabilityAgent(db_manager)
    return agent.generate_voice_note(user_id, topic, duration_minutes)

def accountability_stats(db_manager, user_id: int, period_days: int = 30) -> Dict[str, Any]:
    """
    Get accountability statistics for a user.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        period_days (int): Number of days to look back
        
    Returns:
        Dict[str, Any]: Accountability statistics
    """
    agent = AccountabilityAgent(db_manager)
    return agent.get_accountability_stats(user_id, period_days)