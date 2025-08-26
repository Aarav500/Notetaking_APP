"""
Voice-Based Conversational Agent with Semantic Memory

This module provides functionality for a voice-based conversational agent
that can answer questions, conduct flashcard drills, and remember context
from previous conversations using semantic memory.
"""

import os
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import threading
import queue
import tempfile
import uuid

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface
from ..embeddings.embedder import Embedder
from ..outputs.speech_generator import generate_speech_from_text, available_voices

# Set up logging
logger = logging.getLogger(__name__)

# Try to import speech recognition libraries
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    logger.warning("speech_recognition library not available. Voice input will be disabled.")
    SPEECH_RECOGNITION_AVAILABLE = False

class VoiceAgent:
    """
    Voice-Based Conversational Agent with Semantic Memory
    
    Features:
    - Voice-based Q&A using semantic search across notes
    - Voice-based flashcard drills
    - Semantic memory of conversation history
    - Hands-free learning during walks or other activities
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None,
                 embedder: Optional[Embedder] = None):
        """Initialize the voice agent"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        self.embedder = embedder or Embedder(db_manager.db_path)
        
        # Initialize speech recognition if available
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
        
        # Default voice settings
        self.voice_settings = {
            'engine': 'gtts',  # Default to Google Text-to-Speech
            'voice': 'en',     # Default to English
            'rate': 1.0,       # Normal speed
            'volume': 1.0      # Normal volume
        }
        
        # Ensure database tables exist
        self._ensure_tables()
        
        # Initialize conversation memory
        self.current_conversation_id = None
        
        # Initialize audio queue for background processing
        self.audio_queue = queue.Queue()
        self.processing_thread = None
        self.is_processing = False
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_conversations (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT,
            created_at TEXT NOT NULL,
            last_updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create conversation messages table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_messages (
            id INTEGER PRIMARY KEY,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            embedding_id INTEGER,
            FOREIGN KEY (conversation_id) REFERENCES voice_conversations(id),
            FOREIGN KEY (embedding_id) REFERENCES note_embeddings(id)
        )
        ''')
        
        # Create flashcard sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_flashcard_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            topic TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            total_cards INTEGER NOT NULL DEFAULT 0,
            correct_cards INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    
    def start_conversation(self, user_id: int, title: Optional[str] = None) -> int:
        """
        Start a new conversation
        
        Args:
            user_id: The ID of the user
            title: Optional title for the conversation
            
        Returns:
            The ID of the created conversation
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO voice_conversations (user_id, title, created_at, last_updated_at)
        VALUES (?, ?, ?, ?)
        ''', (user_id, title or f"Conversation {now}", now, now))
        
        conversation_id = cursor.lastrowid
        conn.commit()
        
        self.current_conversation_id = conversation_id
        
        # Add a system message to start the conversation
        self.add_message(conversation_id, "system", 
                        "This is a voice-based conversation with semantic memory. " +
                        "The agent can answer questions based on the user's notes and remember previous context.")
        
        return conversation_id
    
    def add_message(self, conversation_id: int, role: str, content: str) -> int:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: The ID of the conversation
            role: The role of the message sender (user, assistant, system)
            content: The content of the message
            
        Returns:
            The ID of the created message
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO voice_messages (conversation_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (conversation_id, role, content, timestamp))
        
        message_id = cursor.lastrowid
        
        # Update the conversation's last_updated_at timestamp
        cursor.execute('''
        UPDATE voice_conversations
        SET last_updated_at = ?
        WHERE id = ?
        ''', (timestamp, conversation_id))
        
        conn.commit()
        
        # Generate embedding for the message if it's not a system message
        if role != "system" and len(content) > 10:
            try:
                # Store the embedding in the database
                embedding_id = self.embedder.store_note_embedding(message_id, content)
                
                # Update the message with the embedding ID
                cursor.execute('''
                UPDATE voice_messages
                SET embedding_id = ?
                WHERE id = ?
                ''', (embedding_id, message_id))
                
                conn.commit()
            except Exception as e:
                logger.error(f"Failed to generate embedding for message: {e}")
        
        return message_id
    
    def get_conversation(self, conversation_id: int) -> Dict[str, Any]:
        """
        Get a conversation by ID
        
        Args:
            conversation_id: The ID of the conversation
            
        Returns:
            Dictionary with conversation details and messages
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, title, created_at, last_updated_at
        FROM voice_conversations
        WHERE id = ?
        ''', (conversation_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        conversation = {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'created_at': row[3],
            'last_updated_at': row[4],
            'messages': []
        }
        
        # Get messages for the conversation
        cursor.execute('''
        SELECT id, role, content, timestamp
        FROM voice_messages
        WHERE conversation_id = ?
        ORDER BY timestamp
        ''', (conversation_id,))
        
        for row in cursor.fetchall():
            message = {
                'id': row[0],
                'role': row[1],
                'content': row[2],
                'timestamp': row[3]
            }
            conversation['messages'].append(message)
        
        return conversation
    
    def get_recent_conversations(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent conversations for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, created_at, last_updated_at
        FROM voice_conversations
        WHERE user_id = ?
        ORDER BY last_updated_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        conversations = []
        for row in cursor.fetchall():
            conversation = {
                'id': row[0],
                'title': row[1],
                'created_at': row[2],
                'last_updated_at': row[3]
            }
            conversations.append(conversation)
        
        return conversations
    
    def search_conversation_history(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search conversation history using semantic search
        
        Args:
            query: The search query
            limit: Maximum number of results to return
            
        Returns:
            List of relevant messages with conversation context
        """
        # Generate embedding for the query
        results = self.embedder.search_notes_by_embedding(query, limit=limit)
        
        # Filter results to only include voice messages
        voice_message_results = []
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        for result in results:
            note_id = result['note_id']
            
            # Check if this is a voice message
            cursor.execute('''
            SELECT vm.id, vm.conversation_id, vm.role, vm.content, vm.timestamp,
                   vc.title as conversation_title
            FROM voice_messages vm
            JOIN voice_conversations vc ON vm.conversation_id = vc.id
            WHERE vm.id = ?
            ''', (note_id,))
            
            row = cursor.fetchone()
            if row:
                voice_message_results.append({
                    'message_id': row[0],
                    'conversation_id': row[1],
                    'role': row[2],
                    'content': row[3],
                    'timestamp': row[4],
                    'conversation_title': row[5],
                    'similarity': result['similarity']
                })
        
        return voice_message_results
    
    def ask_question(self, user_id: int, question: str, 
                   conversation_id: Optional[int] = None,
                   use_voice_input: bool = False,
                   use_voice_output: bool = True) -> Dict[str, Any]:
        """
        Ask a question and get an answer
        
        Args:
            user_id: The ID of the user
            question: The question to ask
            conversation_id: Optional ID of an existing conversation
            use_voice_input: Whether to use voice input for the question
            use_voice_output: Whether to use voice output for the answer
            
        Returns:
            Dictionary with the answer and conversation details
        """
        # If using voice input, record and transcribe the question
        if use_voice_input and SPEECH_RECOGNITION_AVAILABLE:
            question = self._record_and_transcribe()
            if not question:
                return {'error': 'Failed to transcribe voice input'}
        
        # Start a new conversation if needed
        if not conversation_id:
            conversation_id = self.start_conversation(user_id, f"Question: {question[:30]}...")
        else:
            self.current_conversation_id = conversation_id
        
        # Add the user's question to the conversation
        self.add_message(conversation_id, "user", question)
        
        # Get conversation history for context
        conversation = self.get_conversation(conversation_id)
        messages = conversation.get('messages', [])
        
        # Prepare context from recent messages (last 10)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        # Search for relevant information in notes and previous conversations
        note_results = self.embedder.search_notes_by_embedding(question, limit=5)
        conversation_results = self.search_conversation_history(question, limit=3)
        
        # Format search results for the prompt
        notes_context = ""
        if note_results:
            notes_context = "Relevant information from notes:\n"
            for i, result in enumerate(note_results, 1):
                notes_context += f"{i}. {result['content']}\n"
        
        conversation_context = ""
        if conversation_results:
            conversation_context = "Relevant information from previous conversations:\n"
            for i, result in enumerate(conversation_results, 1):
                conversation_context += f"{i}. From '{result['conversation_title']}': {result['content']}\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        You are a voice-based conversational agent with semantic memory.
        
        Current conversation:
        {context}
        
        {notes_context}
        
        {conversation_context}
        
        Based on the above information, provide a helpful, accurate, and concise answer to the user's question.
        If you don't know the answer, say so honestly and suggest how the user might find the information.
        
        User's question: {question}
        """
        
        # Generate answer using LLM
        answer = self.llm_interface.generate_text(prompt, max_tokens=500)
        
        # Add the assistant's answer to the conversation
        message_id = self.add_message(conversation_id, "assistant", answer)
        
        # Generate speech if requested
        audio_path = None
        if use_voice_output:
            try:
                audio_path = self._generate_speech(answer)
            except Exception as e:
                logger.error(f"Failed to generate speech: {e}")
        
        return {
            'conversation_id': conversation_id,
            'message_id': message_id,
            'question': question,
            'answer': answer,
            'audio_path': audio_path
        }
    
    def start_flashcard_session(self, user_id: int, topic: Optional[str] = None) -> int:
        """
        Start a new flashcard session
        
        Args:
            user_id: The ID of the user
            topic: Optional topic for the flashcards
            
        Returns:
            The ID of the created flashcard session
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO voice_flashcard_sessions (user_id, topic, created_at, total_cards, correct_cards)
        VALUES (?, ?, ?, 0, 0)
        ''', (user_id, topic, created_at))
        
        session_id = cursor.lastrowid
        conn.commit()
        
        return session_id
    
    def generate_flashcards(self, user_id: int, topic: Optional[str] = None, 
                          count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate flashcards based on notes
        
        Args:
            user_id: The ID of the user
            topic: Optional topic to focus on
            count: Number of flashcards to generate
            
        Returns:
            List of flashcards with questions and answers
        """
        # Search for notes related to the topic
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT n.id, n.title, n.content
        FROM notes n
        JOIN users u ON n.user_id = u.id
        """
        
        params = []
        
        if topic:
            query += """
            JOIN note_tags nt ON n.id = nt.note_id
            JOIN tags t ON nt.tag_id = t.id
            WHERE u.id = ? AND (t.name LIKE ? OR n.title LIKE ? OR n.content LIKE ?)
            """
            search_term = f"%{topic}%"
            params = [user_id, search_term, search_term, search_term]
        else:
            query += "WHERE u.id = ?"
            params = [user_id]
        
        query += " ORDER BY n.created_at DESC LIMIT 20"
        
        cursor.execute(query, params)
        notes = cursor.fetchall()
        
        if not notes:
            return []
        
        # Combine note content for context
        notes_content = ""
        for note in notes:
            notes_content += f"Note: {note[1]}\n{note[2]}\n\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        Generate {count} flashcards based on the following notes:
        
        {notes_content}
        
        For each flashcard, provide:
        1. A question that tests understanding of a key concept
        2. The correct answer to the question
        
        Format your response as JSON:
        ```json
        [
          {{
            "question": "Question 1",
            "answer": "Answer 1"
          }},
          ...
        ]
        ```
        
        Make the questions challenging but answerable based on the provided notes.
        If a specific topic was requested ({topic or 'none'}), focus on that topic.
        """
        
        # Generate flashcards using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
        # Extract JSON from response
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without the markdown code block
            json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                logger.error("Failed to extract JSON from LLM response")
                return []
        
        try:
            flashcards = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        return flashcards
    
    def conduct_flashcard_drill(self, user_id: int, topic: Optional[str] = None,
                              count: int = 5, use_voice: bool = True) -> Dict[str, Any]:
        """
        Conduct a flashcard drill session
        
        Args:
            user_id: The ID of the user
            topic: Optional topic to focus on
            count: Number of flashcards to use
            use_voice: Whether to use voice input/output
            
        Returns:
            Dictionary with session results
        """
        # Start a flashcard session
        session_id = self.start_flashcard_session(user_id, topic)
        
        # Generate flashcards
        flashcards = self.generate_flashcards(user_id, topic, count)
        
        if not flashcards:
            return {'error': 'Failed to generate flashcards'}
        
        results = {
            'session_id': session_id,
            'total_cards': len(flashcards),
            'correct_cards': 0,
            'cards': []
        }
        
        # Process each flashcard
        for i, card in enumerate(flashcards, 1):
            question = card['question']
            correct_answer = card['answer']
            
            # Present the question
            print(f"\nFlashcard {i}/{len(flashcards)}:")
            print(f"Question: {question}")
            
            if use_voice:
                self._generate_and_play_speech(f"Flashcard {i}. {question}")
            
            # Get the user's answer
            if use_voice and SPEECH_RECOGNITION_AVAILABLE:
                print("Please speak your answer...")
                user_answer = self._record_and_transcribe()
                if not user_answer:
                    user_answer = "No answer provided"
                print(f"Your answer: {user_answer}")
            else:
                user_answer = input("Your answer: ")
            
            # Evaluate the answer
            evaluation_prompt = f"""
            Evaluate if the user's answer is correct for the given flashcard question.
            
            Question: {question}
            Correct answer: {correct_answer}
            User's answer: {user_answer}
            
            Evaluate the user's answer on a scale of 0 to 1, where:
            - 0 means completely incorrect
            - 0.5 means partially correct
            - 1 means correct
            
            Also provide brief feedback explaining why the answer is correct or incorrect.
            
            Format your response as JSON:
            ```json
            {{
              "score": 0.5,
              "feedback": "Your feedback here"
            }}
            ```
            """
            
            evaluation_response = self.llm_interface.generate_text(evaluation_prompt, max_tokens=300)
            
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', evaluation_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r'\{\s*"score".*\}', evaluation_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    logger.error("Failed to extract JSON from evaluation response")
                    continue
            
            try:
                evaluation = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from evaluation response: {e}")
                continue
            
            score = evaluation.get('score', 0)
            feedback = evaluation.get('feedback', '')
            
            # Update results
            if score >= 0.8:  # Consider it correct if score is 0.8 or higher
                results['correct_cards'] += 1
            
            card_result = {
                'question': question,
                'correct_answer': correct_answer,
                'user_answer': user_answer,
                'score': score,
                'feedback': feedback
            }
            
            results['cards'].append(card_result)
            
            # Provide feedback
            print(f"Feedback: {feedback}")
            print(f"Correct answer: {correct_answer}")
            
            if use_voice:
                self._generate_and_play_speech(f"Feedback: {feedback}. The correct answer is: {correct_answer}")
        
        # Update the session in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now().isoformat()
        
        cursor.execute('''
        UPDATE voice_flashcard_sessions
        SET completed_at = ?, total_cards = ?, correct_cards = ?
        WHERE id = ?
        ''', (completed_at, results['total_cards'], results['correct_cards'], session_id))
        
        conn.commit()
        
        # Provide summary
        summary = f"Session complete. You got {results['correct_cards']} out of {results['total_cards']} correct."
        print(f"\n{summary}")
        
        if use_voice:
            self._generate_and_play_speech(summary)
        
        return results
    
    def _record_and_transcribe(self, timeout: int = 10) -> str:
        """
        Record audio and transcribe it to text
        
        Args:
            timeout: Maximum recording time in seconds
            
        Returns:
            Transcribed text or empty string if failed
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.error("Speech recognition is not available")
            return ""
        
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("Transcribing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return ""
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return ""
    
    def _generate_speech(self, text: str) -> str:
        """
        Generate speech from text
        
        Args:
            text: Text to convert to speech
            
        Returns:
            Path to the generated audio file
        """
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(tempfile.gettempdir(), 'ai_note_system', 'voice_agent')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a unique filename
        filename = f"speech_{uuid.uuid4().hex}.mp3"
        output_path = os.path.join(temp_dir, filename)
        
        # Generate speech
        generate_speech_from_text(
            text=text,
            output_path=output_path,
            engine=self.voice_settings['engine'],
            voice=self.voice_settings['voice'],
            rate=self.voice_settings['rate'],
            volume=self.voice_settings['volume']
        )
        
        return output_path
    
    def _generate_and_play_speech(self, text: str) -> None:
        """
        Generate speech and play it
        
        Args:
            text: Text to convert to speech and play
        """
        try:
            audio_path = self._generate_speech(text)
            
            # Play the audio
            import platform
            if platform.system() == 'Windows':
                os.system(f'start {audio_path}')
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'afplay {audio_path}')
            else:  # Linux
                os.system(f'mpg123 {audio_path}')
        except Exception as e:
            logger.error(f"Failed to generate or play speech: {e}")
    
    def set_voice_settings(self, engine: str, voice: str, 
                         rate: float = 1.0, volume: float = 1.0) -> None:
        """
        Set voice settings for speech generation
        
        Args:
            engine: Speech engine to use (gtts, pyttsx3, azure)
            voice: Voice to use
            rate: Speech rate (0.5 to 2.0)
            volume: Volume (0.0 to 1.0)
        """
        self.voice_settings = {
            'engine': engine,
            'voice': voice,
            'rate': max(0.5, min(2.0, rate)),
            'volume': max(0.0, min(1.0, volume))
        }
    
    def get_available_voices(self) -> Dict[str, List[str]]:
        """
        Get available voices for speech generation
        
        Returns:
            Dictionary of available voices by engine
        """
        return available_voices()
    
    def start_background_processing(self) -> None:
        """Start background processing of audio"""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_audio_queue)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def stop_background_processing(self) -> None:
        """Stop background processing of audio"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
    
    def _process_audio_queue(self) -> None:
        """Process audio queue in background"""
        while self.is_processing:
            try:
                if not self.audio_queue.empty():
                    audio_item = self.audio_queue.get()
                    
                    if audio_item['type'] == 'transcribe':
                        # Transcribe audio
                        text = self._transcribe_audio(audio_item['audio_data'])
                        if audio_item['callback']:
                            audio_item['callback'](text)
                    
                    elif audio_item['type'] == 'generate':
                        # Generate speech
                        audio_path = self._generate_speech(audio_item['text'])
                        if audio_item['callback']:
                            audio_item['callback'](audio_path)
                    
                    self.audio_queue.task_done()
                else:
                    # Sleep briefly to avoid busy waiting
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in audio processing thread: {e}")
                time.sleep(1.0)
    
    def _transcribe_audio(self, audio_data) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: Audio data to transcribe
            
        Returns:
            Transcribed text
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return ""
        
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""

# Helper functions for easier access to voice agent functionality

def ask_question(db_manager, user_id: int, question: str, 
               conversation_id: Optional[int] = None,
               use_voice: bool = True) -> Dict[str, Any]:
    """
    Ask a question and get an answer
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        question: The question to ask
        conversation_id: Optional ID of an existing conversation
        use_voice: Whether to use voice input/output
        
    Returns:
        Dictionary with the answer and conversation details
    """
    agent = VoiceAgent(db_manager)
    return agent.ask_question(user_id, question, conversation_id, 
                             use_voice_input=False, use_voice_output=use_voice)

def conduct_flashcard_drill(db_manager, user_id: int, topic: Optional[str] = None,
                          count: int = 5, use_voice: bool = True) -> Dict[str, Any]:
    """
    Conduct a flashcard drill session
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        topic: Optional topic to focus on
        count: Number of flashcards to use
        use_voice: Whether to use voice input/output
        
    Returns:
        Dictionary with session results
    """
    agent = VoiceAgent(db_manager)
    return agent.conduct_flashcard_drill(user_id, topic, count, use_voice)

def search_conversation_history(db_manager, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Search conversation history using semantic search
    
    Args:
        db_manager: Database manager instance
        query: The search query
        limit: Maximum number of results to return
        
    Returns:
        List of relevant messages with conversation context
    """
    agent = VoiceAgent(db_manager)
    return agent.search_conversation_history(query, limit)