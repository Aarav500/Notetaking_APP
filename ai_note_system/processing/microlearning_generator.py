"""
Auto-Microlearning Generator module for AI Note System.
Creates short micro-lessons from notes for learning during breaks.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import tempfile
import re

# Setup logging
logger = logging.getLogger("ai_note_system.processing.microlearning_generator")

# Import required modules
from ..api.llm_interface import get_llm_interface
from ..database.db_manager import DatabaseManager
from ..visualization.diagram_generator import DiagramGenerator

class MicrolearningGenerator:
    """
    Generates micro-lessons from notes for learning during breaks.
    """
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Microlearning Generator.
        
        Args:
            db_manager (DatabaseManager, optional): Database manager instance
            llm_provider (str): LLM provider to use for content generation
            llm_model (str): LLM model to use for content generation
            output_dir (str, optional): Directory to save generated micro-lessons
        """
        self.db_manager = db_manager
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Initialize diagram generator
        self.diagram_generator = DiagramGenerator(
            llm_provider=llm_provider,
            llm_model=llm_model,
            output_dir=output_dir
        )
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Microlearning Generator with {llm_provider} {llm_model}")
    
    def generate_microlearning(
        self,
        note_id: Optional[int] = None,
        note_text: Optional[str] = None,
        note_title: Optional[str] = None,
        topic: Optional[str] = None,
        duration_minutes: int = 3,
        include_diagram: bool = True,
        platform: str = "telegram",
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a micro-lesson from a note.
        
        Args:
            note_id (int, optional): ID of the note to use
            note_text (str, optional): Text of the note (if not using note_id)
            note_title (str, optional): Title of the note (if not using note_id)
            topic (str, optional): Topic of the micro-lesson (if not using note_id)
            duration_minutes (int): Target duration of the micro-lesson in minutes
            include_diagram (bool): Whether to include a diagram
            platform (str): Target platform (telegram, discord, slack)
            save_output (bool): Whether to save the output
            
        Returns:
            Dict[str, Any]: Generated micro-lesson
        """
        # Get note content if note_id is provided
        if note_id and self.db_manager:
            note = self.db_manager.get_note(note_id)
            if not note:
                logger.error(f"Note with ID {note_id} not found")
                return {"error": f"Note with ID {note_id} not found"}
            
            note_text = note.get("text", "")
            note_title = note.get("title", "")
            topic = note_title  # Use note title as topic if not specified
        
        # Validate inputs
        if not note_text:
            logger.error("Note text is required")
            return {"error": "Note text is required"}
        
        if not topic and not note_title:
            logger.error("Topic or note title is required")
            return {"error": "Topic or note title is required"}
        
        # Use note title as topic if not specified
        if not topic:
            topic = note_title
        
        logger.info(f"Generating micro-lesson for topic: {topic}")
        
        # Step 1: Extract key explanation
        explanation = self._extract_key_explanation(note_text, topic, duration_minutes)
        
        # Step 2: Generate question
        question = self._generate_question(explanation, topic)
        
        # Step 3: Generate diagram if requested
        diagram_path = None
        if include_diagram:
            diagram_result = self._generate_diagram(explanation, topic)
            diagram_path = diagram_result.get("output_path")
        
        # Step 4: Package for target platform
        packaged_content = self._package_for_platform(
            explanation=explanation,
            question=question,
            topic=topic,
            diagram_path=diagram_path,
            platform=platform
        )
        
        # Create micro-lesson object
        microlesson = {
            "topic": topic,
            "explanation": explanation,
            "question": question,
            "diagram_path": diagram_path,
            "platform": platform,
            "packaged_content": packaged_content,
            "duration_minutes": duration_minutes,
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to database if available
        if self.db_manager and note_id:
            self._save_microlesson(microlesson, note_id)
        
        # Save to file if requested
        if save_output and self.output_dir:
            self._save_to_file(microlesson)
        
        return microlesson
    
    def _extract_key_explanation(
        self,
        note_text: str,
        topic: str,
        duration_minutes: int
    ) -> str:
        """
        Extract a key explanation from note text.
        
        Args:
            note_text (str): Text of the note
            topic (str): Topic of the micro-lesson
            duration_minutes (int): Target duration in minutes
            
        Returns:
            str: Extracted key explanation
        """
        logger.debug(f"Extracting key explanation for topic: {topic}")
        
        # Calculate target word count based on duration
        # Assuming average reading speed of 200 words per minute
        target_word_count = duration_minutes * 200 // 2  # Half the time for reading explanation
        
        # Create prompt for extraction
        prompt = f"""
        Extract a concise, clear explanation of the key concept related to "{topic}" from the following note.
        The explanation should be approximately {target_word_count} words (about {duration_minutes//2} minutes of reading).
        
        Focus on:
        1. The most important concept or insight
        2. Clear, simple language that's easy to understand
        3. Concrete examples or analogies if helpful
        
        Note text:
        {note_text[:2000]}...  # Limit input size
        
        Extract only the explanation, without any additional commentary or meta-text.
        """
        
        try:
            # Generate explanation
            explanation = self.llm.generate_text(
                prompt=prompt,
                temperature=0.3,
                max_tokens=target_word_count * 2  # Allow some buffer
            )
            
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Error extracting key explanation: {e}")
            
            # Extract a section of the note as fallback
            sentences = re.split(r'(?<=[.!?])\s+', note_text)
            if len(sentences) > 5:
                return " ".join(sentences[:5])
            else:
                return note_text[:500]
    
    def _generate_question(self, explanation: str, topic: str) -> Dict[str, Any]:
        """
        Generate a question based on the explanation.
        
        Args:
            explanation (str): Key explanation
            topic (str): Topic of the micro-lesson
            
        Returns:
            Dict[str, Any]: Generated question with answer
        """
        logger.debug(f"Generating question for topic: {topic}")
        
        # Define the schema for structured output
        question_schema = {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "answer": {"type": "string"},
                "type": {
                    "type": "string",
                    "enum": ["multiple_choice", "true_false", "short_answer"]
                },
                "options": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["question", "answer", "type"]
        }
        
        # Create prompt for question generation
        prompt = f"""
        Generate a thought-provoking question based on the following explanation about "{topic}".
        The question should test understanding and encourage deeper thinking.
        
        Explanation:
        {explanation}
        
        Create a question that:
        1. Tests understanding of the key concept
        2. Is clear and specific
        3. Encourages application or analysis, not just recall
        
        Include the correct answer and specify the question type (multiple_choice, true_false, or short_answer).
        For multiple choice questions, provide 3-4 options including the correct answer.
        """
        
        try:
            # Generate structured question
            question_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=question_schema,
                temperature=0.7
            )
            
            return question_data
            
        except Exception as e:
            logger.error(f"Error generating question: {e}")
            
            # Create a simple question as fallback
            return {
                "question": f"What is the key insight about {topic}?",
                "answer": "The key insight can be found in the explanation.",
                "type": "short_answer"
            }
    
    def _generate_diagram(self, explanation: str, topic: str) -> Dict[str, Any]:
        """
        Generate a diagram based on the explanation.
        
        Args:
            explanation (str): Key explanation
            topic (str): Topic of the micro-lesson
            
        Returns:
            Dict[str, Any]: Generated diagram information
        """
        logger.debug(f"Generating diagram for topic: {topic}")
        
        # Create a temporary file path if output_dir is available
        diagram_path = None
        if self.output_dir:
            # Sanitize topic for filename
            safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            diagram_path = os.path.join(self.output_dir, f"{safe_topic}_diagram_{timestamp}.png")
        
        # Determine diagram type based on content
        if re.search(r'process|step|workflow|sequence|procedure', explanation, re.IGNORECASE):
            diagram_type = "algorithm"
        elif re.search(r'relation|entity|database|schema|table', explanation, re.IGNORECASE):
            diagram_type = "er"
        else:
            diagram_type = "architecture"
        
        try:
            # Generate diagram
            diagram_result = self.diagram_generator.generate_diagram(
                text=explanation,
                diagram_type=diagram_type,
                output_format="png",
                output_path=diagram_path,
                title=topic,
                editable=True
            )
            
            return diagram_result
            
        except Exception as e:
            logger.error(f"Error generating diagram: {e}")
            
            return {
                "error": f"Error generating diagram: {e}",
                "diagram_type": diagram_type
            }
    
    def _package_for_platform(
        self,
        explanation: str,
        question: Dict[str, Any],
        topic: str,
        diagram_path: Optional[str] = None,
        platform: str = "telegram"
    ) -> Dict[str, Any]:
        """
        Package the micro-lesson for the target platform.
        
        Args:
            explanation (str): Key explanation
            question (Dict[str, Any]): Generated question
            topic (str): Topic of the micro-lesson
            diagram_path (str, optional): Path to the generated diagram
            platform (str): Target platform (telegram, discord, slack)
            
        Returns:
            Dict[str, Any]: Packaged content for the platform
        """
        logger.debug(f"Packaging micro-lesson for platform: {platform}")
        
        # Format question based on type
        formatted_question = self._format_question(question, platform)
        
        # Create base content
        content = {
            "title": f"📚 Micro-Lesson: {topic}",
            "explanation": explanation,
            "question": formatted_question,
            "has_diagram": diagram_path is not None,
            "diagram_path": diagram_path,
            "platform": platform
        }
        
        # Format content based on platform
        if platform == "telegram":
            content["formatted_text"] = self._format_for_telegram(content)
        elif platform == "discord":
            content["formatted_text"] = self._format_for_discord(content)
        elif platform == "slack":
            content["formatted_text"] = self._format_for_slack(content)
        else:
            content["formatted_text"] = self._format_for_generic(content)
        
        return content
    
    def _format_question(self, question: Dict[str, Any], platform: str) -> str:
        """
        Format a question for display.
        
        Args:
            question (Dict[str, Any]): Question data
            platform (str): Target platform
            
        Returns:
            str: Formatted question
        """
        question_text = question.get("question", "")
        question_type = question.get("type", "short_answer")
        
        if question_type == "multiple_choice":
            options = question.get("options", [])
            
            if platform == "telegram":
                # Format as Telegram poll options
                return {
                    "text": question_text,
                    "options": options,
                    "correct_answer": question.get("answer", "")
                }
            else:
                # Format as text options
                formatted = f"{question_text}\n\n"
                for i, option in enumerate(options):
                    formatted += f"{chr(65+i)}. {option}\n"
                return formatted
                
        elif question_type == "true_false":
            if platform == "telegram":
                # Format as Telegram poll options
                return {
                    "text": question_text,
                    "options": ["True", "False"],
                    "correct_answer": question.get("answer", "")
                }
            else:
                # Format as text
                return f"{question_text}\n\nTrue or False?"
                
        else:  # short_answer
            return question_text
    
    def _format_for_telegram(self, content: Dict[str, Any]) -> str:
        """
        Format content for Telegram.
        
        Args:
            content (Dict[str, Any]): Content to format
            
        Returns:
            str: Formatted content
        """
        formatted = f"*{content['title']}*\n\n"
        formatted += content['explanation'] + "\n\n"
        
        # Add question
        if isinstance(content['question'], dict):
            # This is a poll question, handle separately
            formatted += f"*Question:* {content['question']['text']}\n"
            formatted += "(Poll options will be sent separately)"
        else:
            formatted += f"*Question:* {content['question']}\n"
        
        # Add diagram note if available
        if content['has_diagram']:
            formatted += "\n(Diagram attached)"
        
        return formatted
    
    def _format_for_discord(self, content: Dict[str, Any]) -> str:
        """
        Format content for Discord.
        
        Args:
            content (Dict[str, Any]): Content to format
            
        Returns:
            str: Formatted content
        """
        formatted = f"**{content['title']}**\n\n"
        formatted += content['explanation'] + "\n\n"
        
        # Add question
        formatted += f"**Question:** {content['question']}\n"
        
        # Add diagram note if available
        if content['has_diagram']:
            formatted += "\n(Diagram attached)"
        
        return formatted
    
    def _format_for_slack(self, content: Dict[str, Any]) -> str:
        """
        Format content for Slack.
        
        Args:
            content (Dict[str, Any]): Content to format
            
        Returns:
            str: Formatted content
        """
        formatted = f"*{content['title']}*\n\n"
        formatted += content['explanation'] + "\n\n"
        
        # Add question
        formatted += f"*Question:* {content['question']}\n"
        
        # Add diagram note if available
        if content['has_diagram']:
            formatted += "\n(Diagram attached)"
        
        return formatted
    
    def _format_for_generic(self, content: Dict[str, Any]) -> str:
        """
        Format content for generic platforms.
        
        Args:
            content (Dict[str, Any]): Content to format
            
        Returns:
            str: Formatted content
        """
        formatted = f"{content['title']}\n\n"
        formatted += content['explanation'] + "\n\n"
        
        # Add question
        formatted += f"Question: {content['question']}\n"
        
        # Add diagram note if available
        if content['has_diagram']:
            formatted += "\n(Diagram attached)"
        
        return formatted
    
    def _save_microlesson(self, microlesson: Dict[str, Any], note_id: int) -> int:
        """
        Save micro-lesson to database.
        
        Args:
            microlesson (Dict[str, Any]): Micro-lesson data
            note_id (int): ID of the source note
            
        Returns:
            int: ID of the saved micro-lesson
        """
        try:
            # Check if microlessons table exists, create if not
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS microlessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                topic TEXT NOT NULL,
                explanation TEXT NOT NULL,
                question TEXT NOT NULL,
                diagram_path TEXT,
                platform TEXT NOT NULL,
                packaged_content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Insert micro-lesson
            self.db_manager.cursor.execute('''
            INSERT INTO microlessons (
                note_id, topic, explanation, question, diagram_path,
                platform, packaged_content, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                note_id,
                microlesson["topic"],
                microlesson["explanation"],
                json.dumps(microlesson["question"]),
                microlesson["diagram_path"],
                microlesson["platform"],
                json.dumps(microlesson["packaged_content"]),
                datetime.now().isoformat()
            ))
            
            self.db_manager.conn.commit()
            microlesson_id = self.db_manager.cursor.lastrowid
            
            logger.info(f"Saved micro-lesson with ID {microlesson_id}: {microlesson['topic']}")
            return microlesson_id
            
        except Exception as e:
            logger.error(f"Error saving micro-lesson: {e}")
            return -1
    
    def _save_to_file(self, microlesson: Dict[str, Any]) -> str:
        """
        Save micro-lesson to file.
        
        Args:
            microlesson (Dict[str, Any]): Micro-lesson data
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Sanitize topic for filename
            safe_topic = re.sub(r'[^\w\s-]', '', microlesson["topic"]).strip().lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"microlesson_{safe_topic}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                # Create a copy without diagram path for JSON serialization
                ml_copy = microlesson.copy()
                if "diagram_path" in ml_copy and ml_copy["diagram_path"]:
                    ml_copy["diagram_filename"] = os.path.basename(ml_copy["diagram_path"])
                
                json.dump(ml_copy, f, indent=2)
            
            logger.debug(f"Saved micro-lesson to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving micro-lesson to file: {e}")
            return ""
    
    def generate_batch(
        self,
        topic: str,
        count: int = 5,
        duration_minutes: int = 3,
        include_diagram: bool = True,
        platform: str = "telegram",
        save_output: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate a batch of micro-lessons for a topic.
        
        Args:
            topic (str): Topic to generate micro-lessons for
            count (int): Number of micro-lessons to generate
            duration_minutes (int): Target duration of each micro-lesson in minutes
            include_diagram (bool): Whether to include diagrams
            platform (str): Target platform (telegram, discord, slack)
            save_output (bool): Whether to save the output
            
        Returns:
            List[Dict[str, Any]]: Generated micro-lessons
        """
        logger.info(f"Generating {count} micro-lessons for topic: {topic}")
        
        # Get relevant notes if database is available
        notes = []
        if self.db_manager:
            notes = self._get_relevant_notes(topic, count)
        
        # Generate micro-lessons
        microlessons = []
        
        if notes:
            # Generate from existing notes
            for note in notes:
                microlesson = self.generate_microlearning(
                    note_id=note.get("id"),
                    duration_minutes=duration_minutes,
                    include_diagram=include_diagram,
                    platform=platform,
                    save_output=save_output
                )
                
                if "error" not in microlesson:
                    microlessons.append(microlesson)
                
                # Stop if we have enough
                if len(microlessons) >= count:
                    break
        
        # If we don't have enough, generate from subtopics
        if len(microlessons) < count:
            # Generate subtopics
            subtopics = self._generate_subtopics(topic, count - len(microlessons))
            
            # Generate micro-lessons for each subtopic
            for subtopic in subtopics:
                # Generate content for subtopic
                content = self._generate_content_for_subtopic(subtopic, topic)
                
                microlesson = self.generate_microlearning(
                    note_text=content,
                    note_title=subtopic,
                    topic=subtopic,
                    duration_minutes=duration_minutes,
                    include_diagram=include_diagram,
                    platform=platform,
                    save_output=save_output
                )
                
                if "error" not in microlesson:
                    microlessons.append(microlesson)
        
        return microlessons
    
    def _get_relevant_notes(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """
        Get relevant notes for a topic.
        
        Args:
            topic (str): Topic to find notes for
            count (int): Maximum number of notes to return
            
        Returns:
            List[Dict[str, Any]]: Relevant notes
        """
        try:
            # Search for notes with the topic
            notes = self.db_manager.search_notes(
                query=topic,
                limit=count
            )
            
            return notes
            
        except Exception as e:
            logger.error(f"Error getting relevant notes: {e}")
            return []
    
    def _generate_subtopics(self, topic: str, count: int) -> List[str]:
        """
        Generate subtopics for a topic.
        
        Args:
            topic (str): Main topic
            count (int): Number of subtopics to generate
            
        Returns:
            List[str]: Generated subtopics
        """
        logger.debug(f"Generating {count} subtopics for topic: {topic}")
        
        # Create prompt for subtopic generation
        prompt = f"""
        Generate {count} specific subtopics or aspects of "{topic}" that would make good micro-lessons.
        
        Each subtopic should be:
        1. Focused and specific
        2. Self-contained enough for a {3}-minute micro-lesson
        3. Interesting and valuable to learn about
        
        Format each subtopic as a short, descriptive phrase (3-7 words).
        Return only the list of subtopics, one per line.
        """
        
        try:
            # Generate subtopics
            response = self.llm.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=count * 10
            )
            
            # Parse subtopics
            subtopics = []
            for line in response.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith(("•", "-", "*", "1.", "2.")):
                    subtopics.append(line)
                elif line and line[2:].strip():
                    subtopics.append(line[2:].strip())
            
            # Remove any numbering
            subtopics = [re.sub(r'^\d+\.\s*', '', topic) for topic in subtopics]
            
            # Limit to requested count
            return subtopics[:count]
            
        except Exception as e:
            logger.error(f"Error generating subtopics: {e}")
            
            # Generate simple subtopics as fallback
            return [f"{topic} - Aspect {i+1}" for i in range(count)]
    
    def _generate_content_for_subtopic(self, subtopic: str, main_topic: str) -> str:
        """
        Generate content for a subtopic.
        
        Args:
            subtopic (str): Subtopic to generate content for
            main_topic (str): Main topic
            
        Returns:
            str: Generated content
        """
        logger.debug(f"Generating content for subtopic: {subtopic}")
        
        # Create prompt for content generation
        prompt = f"""
        Generate a short educational text about "{subtopic}" (which is related to {main_topic}).
        
        The text should:
        1. Be informative and accurate
        2. Include key concepts and principles
        3. Be suitable for a 3-minute micro-lesson
        4. Include at least one example or application
        
        Write approximately 300-400 words of clear, educational content.
        """
        
        try:
            # Generate content
            content = self.llm.generate_text(
                prompt=prompt,
                temperature=0.5,
                max_tokens=500
            )
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error generating content for subtopic: {e}")
            
            # Generate simple content as fallback
            return f"This is a micro-lesson about {subtopic}, which is an important aspect of {main_topic}."


def main():
    """
    Command-line interface for the Microlearning Generator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Microlearning Generator")
    parser.add_argument("--note-id", type=int, help="ID of the note to use")
    parser.add_argument("--topic", help="Topic of the micro-lesson")
    parser.add_argument("--text", help="Text to use for generation (if not using note-id)")
    parser.add_argument("--duration", type=int, default=3, help="Target duration in minutes")
    parser.add_argument("--no-diagram", action="store_true", help="Don't include a diagram")
    parser.add_argument("--platform", choices=["telegram", "discord", "slack"], default="telegram", help="Target platform")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--batch", action="store_true", help="Generate a batch of micro-lessons")
    parser.add_argument("--count", type=int, default=5, help="Number of micro-lessons to generate in batch mode")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = MicrolearningGenerator(
        llm_provider=args.llm,
        llm_model=args.model,
        output_dir=args.output
    )
    
    if args.batch:
        if not args.topic:
            print("Error: Topic is required for batch generation")
            return
        
        # Generate batch of micro-lessons
        microlessons = generator.generate_batch(
            topic=args.topic,
            count=args.count,
            duration_minutes=args.duration,
            include_diagram=not args.no_diagram,
            platform=args.platform
        )
        
        print(f"Generated {len(microlessons)} micro-lessons for topic: {args.topic}")
        for i, ml in enumerate(microlessons):
            print(f"\n{i+1}. {ml['topic']}")
            print(f"   Platform: {ml['platform']}")
            print(f"   Diagram: {'Yes' if ml['diagram_path'] else 'No'}")
            
            if args.output:
                print(f"   Saved to: {args.output}")
    else:
        # Generate single micro-lesson
        microlesson = generator.generate_microlearning(
            note_id=args.note_id,
            note_text=args.text,
            topic=args.topic,
            duration_minutes=args.duration,
            include_diagram=not args.no_diagram,
            platform=args.platform
        )
        
        if "error" in microlesson:
            print(f"Error: {microlesson['error']}")
            return
        
        # Print micro-lesson
        print("\nMICRO-LESSON")
        print("=" * 50)
        
        print(f"\nTopic: {microlesson['topic']}")
        print(f"Platform: {microlesson['platform']}")
        print(f"Duration: {microlesson['duration_minutes']} minutes")
        
        print("\nExplanation:")
        print(microlesson['explanation'])
        
        print("\nQuestion:")
        if isinstance(microlesson['question'], dict):
            print(microlesson['question']['question'])
            if microlesson['question']['type'] == 'multiple_choice':
                for i, option in enumerate(microlesson['question'].get('options', [])):
                    print(f"  {chr(65+i)}. {option}")
            print(f"\nAnswer: {microlesson['question']['answer']}")
        else:
            print(microlesson['question'])
        
        if microlesson['diagram_path']:
            print(f"\nDiagram saved to: {microlesson['diagram_path']}")
        
        print("\nFormatted for platform:")
        print(microlesson['packaged_content']['formatted_text'])
        
        if args.output:
            print(f"\nMicro-lesson saved to: {args.output}")


if __name__ == "__main__":
    main()