"""
Real-World Application Context Generator module for AI Note System.
Generates real-world use cases, industry applications, and historical context for concepts.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import re

# Setup logging
logger = logging.getLogger("ai_note_system.processing.application_context_generator")

# Import required modules
from ..api.llm_interface import get_llm_interface
from ..database.db_manager import DatabaseManager

class ApplicationContextGenerator:
    """
    Generates real-world application contexts for concepts.
    """
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Application Context Generator.
        
        Args:
            db_manager (DatabaseManager, optional): Database manager instance
            llm_provider (str): LLM provider to use for content generation
            llm_model (str): LLM model to use for content generation
            output_dir (str, optional): Directory to save generated contexts
        """
        self.db_manager = db_manager
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Application Context Generator with {llm_provider} {llm_model}")
    
    def generate_application_context(
        self,
        note_id: Optional[int] = None,
        note_text: Optional[str] = None,
        note_title: Optional[str] = None,
        concept: Optional[str] = None,
        include_use_cases: bool = True,
        include_industry_applications: bool = True,
        include_historical_context: bool = True,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Generate application context for a concept.
        
        Args:
            note_id (int, optional): ID of the note to use
            note_text (str, optional): Text of the note (if not using note_id)
            note_title (str, optional): Title of the note (if not using note_id)
            concept (str, optional): Concept to generate context for (if not using note_id)
            include_use_cases (bool): Whether to include real-world use cases
            include_industry_applications (bool): Whether to include industry applications
            include_historical_context (bool): Whether to include historical context
            save_output (bool): Whether to save the output
            
        Returns:
            Dict[str, Any]: Generated application context
        """
        # Get note content if note_id is provided
        if note_id and self.db_manager:
            note = self.db_manager.get_note(note_id)
            if not note:
                logger.error(f"Note with ID {note_id} not found")
                return {"error": f"Note with ID {note_id} not found"}
            
            note_text = note.get("text", "")
            note_title = note.get("title", "")
            concept = note_title  # Use note title as concept if not specified
        
        # Validate inputs
        if not concept and not note_title:
            logger.error("Concept or note title is required")
            return {"error": "Concept or note title is required"}
        
        # Use note title as concept if not specified
        if not concept:
            concept = note_title
        
        logger.info(f"Generating application context for concept: {concept}")
        
        # Create context object
        context = {
            "concept": concept,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate real-world use cases if requested
        if include_use_cases:
            context["use_cases"] = self._generate_use_cases(concept, note_text)
        
        # Generate industry applications if requested
        if include_industry_applications:
            context["industry_applications"] = self._generate_industry_applications(concept, note_text)
        
        # Generate historical context if requested
        if include_historical_context:
            context["historical_context"] = self._generate_historical_context(concept, note_text)
        
        # Save to database if available
        if self.db_manager and note_id:
            self._save_application_context(context, note_id)
        
        # Save to file if requested
        if save_output and self.output_dir:
            self._save_to_file(context)
        
        return context
    
    def _generate_use_cases(
        self,
        concept: str,
        note_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate real-world use cases for a concept.
        
        Args:
            concept (str): Concept to generate use cases for
            note_text (str, optional): Text of the note
            
        Returns:
            List[Dict[str, Any]]: Generated use cases
        """
        logger.debug(f"Generating use cases for concept: {concept}")
        
        # Define the schema for structured output
        use_cases_schema = {
            "type": "object",
            "properties": {
                "use_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "domain": {"type": "string"},
                            "impact": {"type": "string"},
                            "example": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create prompt for use case generation
        prompt = f"""
        Generate 3-5 specific, concrete real-world use cases for the concept of "{concept}".
        
        {f'Based on this note text: {note_text[:1000]}...' if note_text else ''}
        
        For each use case, include:
        1. A descriptive title
        2. A clear description of how the concept is applied
        3. The domain or field where it's used
        4. The impact or benefit of this application
        5. A specific example or implementation
        
        Focus on practical, current applications that demonstrate the concept's relevance and utility.
        Provide diverse use cases across different domains when possible.
        """
        
        try:
            # Generate structured use cases
            use_cases_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=use_cases_schema,
                temperature=0.7
            )
            
            return use_cases_data.get("use_cases", [])
            
        except Exception as e:
            logger.error(f"Error generating use cases: {e}")
            
            # Return simple use cases as fallback
            return [
                {
                    "title": f"{concept} in Everyday Life",
                    "description": f"How {concept} is used in common scenarios.",
                    "domain": "General",
                    "impact": "Makes tasks more efficient and accessible.",
                    "example": f"A typical example of {concept} in action."
                }
            ]
    
    def _generate_industry_applications(
        self,
        concept: str,
        note_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate industry applications for a concept.
        
        Args:
            concept (str): Concept to generate industry applications for
            note_text (str, optional): Text of the note
            
        Returns:
            List[Dict[str, Any]]: Generated industry applications
        """
        logger.debug(f"Generating industry applications for concept: {concept}")
        
        # Define the schema for structured output
        industry_schema = {
            "type": "object",
            "properties": {
                "industry_applications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "industry": {"type": "string"},
                            "application": {"type": "string"},
                            "companies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "technologies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "challenges": {"type": "string"},
                            "future_trends": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create prompt for industry application generation
        prompt = f"""
        Generate 4-6 specific industry applications for the concept of "{concept}".
        
        {f'Based on this note text: {note_text[:1000]}...' if note_text else ''}
        
        For each industry application, include:
        1. The industry or sector
        2. How the concept is specifically applied in this industry
        3. Notable companies or organizations using this application
        4. Related technologies or tools
        5. Current challenges or limitations
        6. Future trends or developments
        
        Focus on diverse industries and current, real-world implementations.
        Be specific about how the concept is actually used in professional contexts.
        """
        
        try:
            # Generate structured industry applications
            industry_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=industry_schema,
                temperature=0.7
            )
            
            return industry_data.get("industry_applications", [])
            
        except Exception as e:
            logger.error(f"Error generating industry applications: {e}")
            
            # Return simple industry applications as fallback
            return [
                {
                    "industry": "Technology",
                    "application": f"Implementation of {concept} in software development.",
                    "companies": ["Tech Company A", "Tech Company B"],
                    "technologies": ["Related Technology 1", "Related Technology 2"],
                    "challenges": f"Integration challenges with existing systems.",
                    "future_trends": f"Growing adoption of {concept} across the industry."
                }
            ]
    
    def _generate_historical_context(
        self,
        concept: str,
        note_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate historical context for a concept.
        
        Args:
            concept (str): Concept to generate historical context for
            note_text (str, optional): Text of the note
            
        Returns:
            Dict[str, Any]: Generated historical context
        """
        logger.debug(f"Generating historical context for concept: {concept}")
        
        # Define the schema for structured output
        history_schema = {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "key_developments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string"},
                            "development": {"type": "string"},
                            "significance": {"type": "string"}
                        }
                    }
                },
                "key_figures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "contribution": {"type": "string"},
                            "period": {"type": "string"}
                        }
                    }
                },
                "evolution": {"type": "string"},
                "impact_on_field": {"type": "string"}
            }
        }
        
        # Create prompt for historical context generation
        prompt = f"""
        Generate a comprehensive historical context for the concept of "{concept}".
        
        {f'Based on this note text: {note_text[:1000]}...' if note_text else ''}
        
        Include:
        1. The origin or inception of the concept
        2. Key developments in its evolution (with time periods)
        3. Key figures who contributed to its development
        4. How the concept has evolved over time
        5. Its impact on the field or discipline
        
        Focus on accuracy and educational value. Include specific dates, names, and developments.
        Provide a narrative that helps understand how the concept emerged and evolved to its current form.
        """
        
        try:
            # Generate structured historical context
            history_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=history_schema,
                temperature=0.4
            )
            
            return history_data
            
        except Exception as e:
            logger.error(f"Error generating historical context: {e}")
            
            # Return simple historical context as fallback
            return {
                "origin": f"The concept of {concept} originated in the field of study.",
                "key_developments": [
                    {
                        "period": "Early development",
                        "development": f"Initial formulation of {concept}.",
                        "significance": "Established the foundation for future work."
                    }
                ],
                "key_figures": [
                    {
                        "name": "Notable Researcher",
                        "contribution": f"Pioneered work on {concept}.",
                        "period": "20th century"
                    }
                ],
                "evolution": f"The concept of {concept} has evolved significantly over time.",
                "impact_on_field": f"{concept} has had a substantial impact on its field."
            }
    
    def _save_application_context(self, context: Dict[str, Any], note_id: int) -> int:
        """
        Save application context to database.
        
        Args:
            context (Dict[str, Any]): Application context data
            note_id (int): ID of the source note
            
        Returns:
            int: ID of the saved application context
        """
        try:
            # Check if application_contexts table exists, create if not
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                concept TEXT NOT NULL,
                use_cases TEXT,
                industry_applications TEXT,
                historical_context TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Insert application context
            self.db_manager.cursor.execute('''
            INSERT INTO application_contexts (
                note_id, concept, use_cases, industry_applications,
                historical_context, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                note_id,
                context["concept"],
                json.dumps(context.get("use_cases", [])),
                json.dumps(context.get("industry_applications", [])),
                json.dumps(context.get("historical_context", {})),
                datetime.now().isoformat()
            ))
            
            self.db_manager.conn.commit()
            context_id = self.db_manager.cursor.lastrowid
            
            logger.info(f"Saved application context with ID {context_id}: {context['concept']}")
            return context_id
            
        except Exception as e:
            logger.error(f"Error saving application context: {e}")
            return -1
    
    def _save_to_file(self, context: Dict[str, Any]) -> str:
        """
        Save application context to file.
        
        Args:
            context (Dict[str, Any]): Application context data
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Sanitize concept for filename
            safe_concept = re.sub(r'[^\w\s-]', '', context["concept"]).strip().lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"application_context_{safe_concept}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(context, f, indent=2)
            
            logger.debug(f"Saved application context to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving application context to file: {e}")
            return ""
"""
Real-World Application Context Generator module for AI Note System.
Generates real-world use cases, industry applications, and historical context for concepts.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import re

# Setup logging
logger = logging.getLogger("ai_note_system.processing.application_context_generator")

# Import required modules
from ..api.llm_interface import get_llm_interface
from ..database.db_manager import DatabaseManager

class ApplicationContextGenerator:
    """
    Generates real-world application contexts for concepts.
    """
    
    def __init__(
        self,
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4",
        output_dir: Optional[str] = None
    ):
        """
        Initialize the Application Context Generator.
        
        Args:
            db_manager (DatabaseManager, optional): Database manager instance
            llm_provider (str): LLM provider to use for content generation
            llm_model (str): LLM model to use for content generation
            output_dir (str, optional): Directory to save generated contexts
        """
        self.db_manager = db_manager
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Set output directory
        self.output_dir = output_dir
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Initialized Application Context Generator with {llm_provider} {llm_model}")
    
    def generate_application_context(
        self,
        note_id: Optional[int] = None,
        note_text: Optional[str] = None,
        note_title: Optional[str] = None,
        concept: Optional[str] = None,
        include_use_cases: bool = True,
        include_industry_applications: bool = True,
        include_historical_context: bool = True,
        save_output: bool = True
    ) -> Dict[str, Any]:
        """
        Generate application context for a concept.
        
        Args:
            note_id (int, optional): ID of the note to use
            note_text (str, optional): Text of the note (if not using note_id)
            note_title (str, optional): Title of the note (if not using note_id)
            concept (str, optional): Concept to generate context for (if not using note_id)
            include_use_cases (bool): Whether to include real-world use cases
            include_industry_applications (bool): Whether to include industry applications
            include_historical_context (bool): Whether to include historical context
            save_output (bool): Whether to save the output
            
        Returns:
            Dict[str, Any]: Generated application context
        """
        # Get note content if note_id is provided
        if note_id and self.db_manager:
            note = self.db_manager.get_note(note_id)
            if not note:
                logger.error(f"Note with ID {note_id} not found")
                return {"error": f"Note with ID {note_id} not found"}
            
            note_text = note.get("text", "")
            note_title = note.get("title", "")
            concept = note_title  # Use note title as concept if not specified
        
        # Validate inputs
        if not concept and not note_title:
            logger.error("Concept or note title is required")
            return {"error": "Concept or note title is required"}
        
        # Use note title as concept if not specified
        if not concept:
            concept = note_title
        
        logger.info(f"Generating application context for concept: {concept}")
        
        # Create context object
        context = {
            "concept": concept,
            "generated_at": datetime.now().isoformat()
        }
        
        # Generate real-world use cases if requested
        if include_use_cases:
            context["use_cases"] = self._generate_use_cases(concept, note_text)
        
        # Generate industry applications if requested
        if include_industry_applications:
            context["industry_applications"] = self._generate_industry_applications(concept, note_text)
        
        # Generate historical context if requested
        if include_historical_context:
            context["historical_context"] = self._generate_historical_context(concept, note_text)
        
        # Save to database if available
        if self.db_manager and note_id:
            self._save_application_context(context, note_id)
        
        # Save to file if requested
        if save_output and self.output_dir:
            self._save_to_file(context)
        
        return context
    
    def _generate_use_cases(
        self,
        concept: str,
        note_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate real-world use cases for a concept.
        
        Args:
            concept (str): Concept to generate use cases for
            note_text (str, optional): Text of the note
            
        Returns:
            List[Dict[str, Any]]: Generated use cases
        """
        logger.debug(f"Generating use cases for concept: {concept}")
        
        # Define the schema for structured output
        use_cases_schema = {
            "type": "object",
            "properties": {
                "use_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "domain": {"type": "string"},
                            "impact": {"type": "string"},
                            "example": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create prompt for use case generation
        prompt = f"""
        Generate 3-5 specific, concrete real-world use cases for the concept of "{concept}".
        
        {f'Based on this note text: {note_text[:1000]}...' if note_text else ''}
        
        For each use case, include:
        1. A descriptive title
        2. A clear description of how the concept is applied
        3. The domain or field where it's used
        4. The impact or benefit of this application
        5. A specific example or implementation
        
        Focus on practical, current applications that demonstrate the concept's relevance and utility.
        Provide diverse use cases across different domains when possible.
        """
        
        try:
            # Generate structured use cases
            use_cases_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=use_cases_schema,
                temperature=0.7
            )
            
            return use_cases_data.get("use_cases", [])
            
        except Exception as e:
            logger.error(f"Error generating use cases: {e}")
            
            # Return simple use cases as fallback
            return [
                {
                    "title": f"{concept} in Everyday Life",
                    "description": f"How {concept} is used in common scenarios.",
                    "domain": "General",
                    "impact": "Makes tasks more efficient and accessible.",
                    "example": f"A typical example of {concept} in action."
                }
            ]
    
    def _generate_industry_applications(
        self,
        concept: str,
        note_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate industry applications for a concept.
        
        Args:
            concept (str): Concept to generate industry applications for
            note_text (str, optional): Text of the note
            
        Returns:
            List[Dict[str, Any]]: Generated industry applications
        """
        logger.debug(f"Generating industry applications for concept: {concept}")
        
        # Define the schema for structured output
        industry_schema = {
            "type": "object",
            "properties": {
                "industry_applications": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "industry": {"type": "string"},
                            "application": {"type": "string"},
                            "companies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "technologies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "challenges": {"type": "string"},
                            "future_trends": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create prompt for industry application generation
        prompt = f"""
        Generate 4-6 specific industry applications for the concept of "{concept}".
        
        {f'Based on this note text: {note_text[:1000]}...' if note_text else ''}
        
        For each industry application, include:
        1. The industry or sector
        2. How the concept is specifically applied in this industry
        3. Notable companies or organizations using this application
        4. Related technologies or tools
        5. Current challenges or limitations
        6. Future trends or developments
        
        Focus on diverse industries and current, real-world implementations.
        Be specific about how the concept is actually used in professional contexts.
        """
        
        try:
            # Generate structured industry applications
            industry_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=industry_schema,
                temperature=0.7
            )
            
            return industry_data.get("industry_applications", [])
            
        except Exception as e:
            logger.error(f"Error generating industry applications: {e}")
            
            # Return simple industry applications as fallback
            return [
                {
                    "industry": "Technology",
                    "application": f"Implementation of {concept} in software development.",
                    "companies": ["Tech Company A", "Tech Company B"],
                    "technologies": ["Related Technology 1", "Related Technology 2"],
                    "challenges": f"Integration challenges with existing systems.",
                    "future_trends": f"Growing adoption of {concept} across the industry."
                }
            ]
    
    def _generate_historical_context(
        self,
        concept: str,
        note_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate historical context for a concept.
        
        Args:
            concept (str): Concept to generate historical context for
            note_text (str, optional): Text of the note
            
        Returns:
            Dict[str, Any]: Generated historical context
        """
        logger.debug(f"Generating historical context for concept: {concept}")
        
        # Define the schema for structured output
        history_schema = {
            "type": "object",
            "properties": {
                "origin": {"type": "string"},
                "key_developments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "string"},
                            "development": {"type": "string"},
                            "significance": {"type": "string"}
                        }
                    }
                },
                "key_figures": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "contribution": {"type": "string"},
                            "period": {"type": "string"}
                        }
                    }
                },
                "evolution": {"type": "string"},
                "impact_on_field": {"type": "string"}
            }
        }
        
        # Create prompt for historical context generation
        prompt = f"""
        Generate a comprehensive historical context for the concept of "{concept}".
        
        {f'Based on this note text: {note_text[:1000]}...' if note_text else ''}
        
        Include:
        1. The origin or inception of the concept
        2. Key developments in its evolution (with time periods)
        3. Key figures who contributed to its development
        4. How the concept has evolved over time
        5. Its impact on the field or discipline
        
        Focus on accuracy and educational value. Include specific dates, names, and developments.
        Provide a narrative that helps understand how the concept emerged and evolved to its current form.
        """
        
        try:
            # Generate structured historical context
            history_data = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=history_schema,
                temperature=0.4
            )
            
            return history_data
            
        except Exception as e:
            logger.error(f"Error generating historical context: {e}")
            
            # Return simple historical context as fallback
            return {
                "origin": f"The concept of {concept} originated in the field of study.",
                "key_developments": [
                    {
                        "period": "Early development",
                        "development": f"Initial formulation of {concept}.",
                        "significance": "Established the foundation for future work."
                    }
                ],
                "key_figures": [
                    {
                        "name": "Notable Researcher",
                        "contribution": f"Pioneered work on {concept}.",
                        "period": "20th century"
                    }
                ],
                "evolution": f"The concept of {concept} has evolved significantly over time.",
                "impact_on_field": f"{concept} has had a substantial impact on its field."
            }
    
    def _save_application_context(self, context: Dict[str, Any], note_id: int) -> int:
        """
        Save application context to database.
        
        Args:
            context (Dict[str, Any]): Application context data
            note_id (int): ID of the source note
            
        Returns:
            int: ID of the saved application context
        """
        try:
            # Check if application_contexts table exists, create if not
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_contexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                concept TEXT NOT NULL,
                use_cases TEXT,
                industry_applications TEXT,
                historical_context TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Insert application context
            self.db_manager.cursor.execute('''
            INSERT INTO application_contexts (
                note_id, concept, use_cases, industry_applications,
                historical_context, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                note_id,
                context["concept"],
                json.dumps(context.get("use_cases", [])),
                json.dumps(context.get("industry_applications", [])),
                json.dumps(context.get("historical_context", {})),
                datetime.now().isoformat()
            ))
            
            self.db_manager.conn.commit()
            context_id = self.db_manager.cursor.lastrowid
            
            logger.info(f"Saved application context with ID {context_id}: {context['concept']}")
            return context_id
            
        except Exception as e:
            logger.error(f"Error saving application context: {e}")
            return -1
    
    def _save_to_file(self, context: Dict[str, Any]) -> str:
        """
        Save application context to file.
        
        Args:
            context (Dict[str, Any]): Application context data
            
        Returns:
            str: Path to the saved file
        """
        try:
            # Sanitize concept for filename
            safe_concept = re.sub(r'[^\w\s-]', '', context["concept"]).strip().lower().replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create filename
            filename = f"application_context_{safe_concept}_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save as JSON
            with open(filepath, 'w') as f:
                json.dump(context, f, indent=2)
            
            logger.debug(f"Saved application context to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving application context to file: {e}")
            return ""
    
    def get_application_context(self, context_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve an application context by ID.
        
        Args:
            context_id (int): ID of the application context
            
        Returns:
            Optional[Dict[str, Any]]: Application context data or None if not found
        """
        if not self.db_manager:
            logger.error("Database manager is required to retrieve application contexts")
            return None
        
        try:
            self.db_manager.cursor.execute('''
            SELECT * FROM application_contexts WHERE id = ?
            ''', (context_id,))
            
            row = self.db_manager.cursor.fetchone()
            if not row:
                return None
            
            # Convert row to dictionary
            context = dict(row)
            
            # Parse JSON fields
            if "use_cases" in context and context["use_cases"]:
                context["use_cases"] = json.loads(context["use_cases"])
            else:
                context["use_cases"] = []
                
            if "industry_applications" in context and context["industry_applications"]:
                context["industry_applications"] = json.loads(context["industry_applications"])
            else:
                context["industry_applications"] = []
                
            if "historical_context" in context and context["historical_context"]:
                context["historical_context"] = json.loads(context["historical_context"])
            else:
                context["historical_context"] = {}
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving application context: {e}")
            return None
    
    def get_application_contexts_for_note(self, note_id: int) -> List[Dict[str, Any]]:
        """
        Retrieve all application contexts for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            List[Dict[str, Any]]: List of application contexts
        """
        if not self.db_manager:
            logger.error("Database manager is required to retrieve application contexts")
            return []
        
        try:
            self.db_manager.cursor.execute('''
            SELECT * FROM application_contexts WHERE note_id = ? ORDER BY timestamp DESC
            ''', (note_id,))
            
            contexts = []
            for row in self.db_manager.cursor.fetchall():
                context = dict(row)
                
                # Parse JSON fields
                if "use_cases" in context and context["use_cases"]:
                    context["use_cases"] = json.loads(context["use_cases"])
                else:
                    context["use_cases"] = []
                    
                if "industry_applications" in context and context["industry_applications"]:
                    context["industry_applications"] = json.loads(context["industry_applications"])
                else:
                    context["industry_applications"] = []
                    
                if "historical_context" in context and context["historical_context"]:
                    context["historical_context"] = json.loads(context["historical_context"])
                else:
                    context["historical_context"] = {}
                
                contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Error retrieving application contexts for note: {e}")
            return []
    
    def search_application_contexts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search application contexts by concept or content.
        
        Args:
            query (str): Search query
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of matching application contexts
        """
        if not self.db_manager:
            logger.error("Database manager is required to search application contexts")
            return []
        
        try:
            # Search by concept (simple implementation)
            self.db_manager.cursor.execute('''
            SELECT * FROM application_contexts 
            WHERE concept LIKE ? 
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (f'%{query}%', limit))
            
            contexts = []
            for row in self.db_manager.cursor.fetchall():
                context = dict(row)
                
                # Parse JSON fields
                if "use_cases" in context and context["use_cases"]:
                    context["use_cases"] = json.loads(context["use_cases"])
                else:
                    context["use_cases"] = []
                    
                if "industry_applications" in context and context["industry_applications"]:
                    context["industry_applications"] = json.loads(context["industry_applications"])
                else:
                    context["industry_applications"] = []
                    
                if "historical_context" in context and context["historical_context"]:
                    context["historical_context"] = json.loads(context["historical_context"])
                else:
                    context["historical_context"] = {}
                
                contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Error searching application contexts: {e}")
            return []
    
    def format_application_context(
        self, 
        context: Dict[str, Any],
        format_type: str = "markdown"
    ) -> str:
        """
        Format an application context for display or export.
        
        Args:
            context (Dict[str, Any]): Application context data
            format_type (str): Output format (markdown, html, text)
            
        Returns:
            str: Formatted application context
        """
        if format_type == "markdown":
            return self._format_markdown(context)
        elif format_type == "html":
            return self._format_html(context)
        else:  # Default to text
            return self._format_text(context)
    
    def _format_markdown(self, context: Dict[str, Any]) -> str:
        """
        Format application context as Markdown.
        
        Args:
            context (Dict[str, Any]): Application context data
            
        Returns:
            str: Markdown-formatted application context
        """
        md = f"# Real-World Applications: {context['concept']}\n\n"
        
        # Add use cases
        if "use_cases" in context and context["use_cases"]:
            md += "## Real-World Use Cases\n\n"
            
            for i, use_case in enumerate(context["use_cases"], 1):
                md += f"### {i}. {use_case.get('title', 'Use Case')}\n\n"
                md += f"**Domain:** {use_case.get('domain', 'N/A')}\n\n"
                md += f"{use_case.get('description', '')}\n\n"
                md += f"**Impact:** {use_case.get('impact', '')}\n\n"
                md += f"**Example:** {use_case.get('example', '')}\n\n"
        
        # Add industry applications
        if "industry_applications" in context and context["industry_applications"]:
            md += "## Industry Applications\n\n"
            
            for i, app in enumerate(context["industry_applications"], 1):
                md += f"### {i}. {app.get('industry', 'Industry')}\n\n"
                md += f"{app.get('application', '')}\n\n"
                
                if "companies" in app and app["companies"]:
                    md += "**Notable Companies:**\n"
                    for company in app["companies"]:
                        md += f"- {company}\n"
                    md += "\n"
                
                if "technologies" in app and app["technologies"]:
                    md += "**Related Technologies:**\n"
                    for tech in app["technologies"]:
                        md += f"- {tech}\n"
                    md += "\n"
                
                md += f"**Challenges:** {app.get('challenges', '')}\n\n"
                md += f"**Future Trends:** {app.get('future_trends', '')}\n\n"
        
        # Add historical context
        if "historical_context" in context and context["historical_context"]:
            hist = context["historical_context"]
            md += "## Historical Context\n\n"
            
            if "origin" in hist:
                md += f"**Origin:** {hist['origin']}\n\n"
            
            if "key_developments" in hist and hist["key_developments"]:
                md += "**Key Developments:**\n\n"
                
                for dev in hist["key_developments"]:
                    md += f"- **{dev.get('period', 'Period')}:** {dev.get('development', '')}\n"
                    md += f"  *Significance:* {dev.get('significance', '')}\n\n"
            
            if "key_figures" in hist and hist["key_figures"]:
                md += "**Key Figures:**\n\n"
                
                for fig in hist["key_figures"]:
                    md += f"- **{fig.get('name', 'Person')}** ({fig.get('period', '')}): {fig.get('contribution', '')}\n\n"
            
            if "evolution" in hist:
                md += f"**Evolution:** {hist['evolution']}\n\n"
            
            if "impact_on_field" in hist:
                md += f"**Impact on Field:** {hist['impact_on_field']}\n\n"
        
        # Add generation timestamp
        if "generated_at" in context:
            try:
                dt = datetime.fromisoformat(context["generated_at"])
                formatted_date = dt.strftime("%B %d, %Y at %H:%M")
                md += f"\n\n*Generated on {formatted_date}*"
            except:
                md += f"\n\n*Generated on {context['generated_at']}*"
        
        return md
    
    def _format_html(self, context: Dict[str, Any]) -> str:
        """
        Format application context as HTML.
        
        Args:
            context (Dict[str, Any]): Application context data
            
        Returns:
            str: HTML-formatted application context
        """
        # Convert markdown to HTML (simplified implementation)
        md = self._format_markdown(context)
        
        # Basic markdown to HTML conversion
        html = md.replace("\n\n", "</p><p>")
        html = html.replace("# ", "<h1>").replace("\n## ", "</p><h2>").replace("\n### ", "</p><h3>")
        html = re.sub(r'<h(\d)>(.*?)\n', r'<h\1>\2</h\1><p>', html)
        html = html.replace("**", "<strong>").replace("**", "</strong>")
        html = html.replace("*", "<em>").replace("*", "</em>")
        html = re.sub(r'- (.*?)\n', r'<li>\1</li>', html)
        html = html.replace("<li>", "<ul><li>").replace("</li></p>", "</li></ul></p>")
        
        # Wrap in HTML structure
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Real-World Applications: {context['concept']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #2980b9; }}
        strong {{ color: #2c3e50; }}
        ul {{ margin-left: 20px; }}
        .timestamp {{ color: #7f8c8d; font-style: italic; margin-top: 30px; }}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""
        
        return html
    
    def _format_text(self, context: Dict[str, Any]) -> str:
        """
        Format application context as plain text.
        
        Args:
            context (Dict[str, Any]): Application context data
            
        Returns:
            str: Text-formatted application context
        """
        text = f"REAL-WORLD APPLICATIONS: {context['concept']}\n"
        text += "=" * 50 + "\n\n"
        
        # Add use cases
        if "use_cases" in context and context["use_cases"]:
            text += "REAL-WORLD USE CASES\n"
            text += "-" * 20 + "\n\n"
            
            for i, use_case in enumerate(context["use_cases"], 1):
                text += f"{i}. {use_case.get('title', 'Use Case')}\n"
                text += f"   Domain: {use_case.get('domain', 'N/A')}\n"
                text += f"   {use_case.get('description', '')}\n"
                text += f"   Impact: {use_case.get('impact', '')}\n"
                text += f"   Example: {use_case.get('example', '')}\n\n"
        
        # Add industry applications
        if "industry_applications" in context and context["industry_applications"]:
            text += "INDUSTRY APPLICATIONS\n"
            text += "-" * 20 + "\n\n"
            
            for i, app in enumerate(context["industry_applications"], 1):
                text += f"{i}. {app.get('industry', 'Industry')}\n"
                text += f"   {app.get('application', '')}\n"
                
                if "companies" in app and app["companies"]:
                    text += "   Notable Companies:\n"
                    for company in app["companies"]:
                        text += f"   - {company}\n"
                
                if "technologies" in app and app["technologies"]:
                    text += "   Related Technologies:\n"
                    for tech in app["technologies"]:
                        text += f"   - {tech}\n"
                
                text += f"   Challenges: {app.get('challenges', '')}\n"
                text += f"   Future Trends: {app.get('future_trends', '')}\n\n"
        
        # Add historical context
        if "historical_context" in context and context["historical_context"]:
            hist = context["historical_context"]
            text += "HISTORICAL CONTEXT\n"
            text += "-" * 20 + "\n\n"
            
            if "origin" in hist:
                text += f"Origin: {hist['origin']}\n\n"
            
            if "key_developments" in hist and hist["key_developments"]:
                text += "Key Developments:\n"
                
                for dev in hist["key_developments"]:
                    text += f"- {dev.get('period', 'Period')}: {dev.get('development', '')}\n"
                    text += f"  Significance: {dev.get('significance', '')}\n\n"
            
            if "key_figures" in hist and hist["key_figures"]:
                text += "Key Figures:\n"
                
                for fig in hist["key_figures"]:
                    text += f"- {fig.get('name', 'Person')} ({fig.get('period', '')}): {fig.get('contribution', '')}\n\n"
            
            if "evolution" in hist:
                text += f"Evolution: {hist['evolution']}\n\n"
            
            if "impact_on_field" in hist:
                text += f"Impact on Field: {hist['impact_on_field']}\n\n"
        
        # Add generation timestamp
        if "generated_at" in context:
            try:
                dt = datetime.fromisoformat(context["generated_at"])
                formatted_date = dt.strftime("%B %d, %Y at %H:%M")
                text += f"\nGenerated on {formatted_date}"
            except:
                text += f"\nGenerated on {context['generated_at']}"
        
        return text


def main():
    """
    Command-line interface for the Application Context Generator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Real-World Application Context Generator")
    parser.add_argument("--concept", help="Concept to generate context for")
    parser.add_argument("--note-id", type=int, help="ID of the note to use")
    parser.add_argument("--note-text", help="Text of the note (if not using note-id)")
    parser.add_argument("--note-title", help="Title of the note (if not using note-id)")
    parser.add_argument("--no-use-cases", action="store_true", help="Skip generating use cases")
    parser.add_argument("--no-industry", action="store_true", help="Skip generating industry applications")
    parser.add_argument("--no-history", action="store_true", help="Skip generating historical context")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--format", choices=["markdown", "html", "text"], default="text", 
                        help="Output format for display")
    parser.add_argument("--db-path", help="Path to the database file")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.concept and not args.note_id and not args.note_title:
        print("Error: Either --concept, --note-id, or --note-title must be provided")
        return
    
    # Initialize database manager if db_path is provided
    db_manager = None
    if args.db_path:
        from ..database.db_manager import DatabaseManager
        db_manager = DatabaseManager(args.db_path)
    
    # Initialize generator
    generator = ApplicationContextGenerator(
        db_manager=db_manager,
        llm_provider=args.llm,
        llm_model=args.model,
        output_dir=args.output_dir
    )
    
    # Generate application context
    context = generator.generate_application_context(
        note_id=args.note_id,
        note_text=args.note_text,
        note_title=args.note_title,
        concept=args.concept,
        include_use_cases=not args.no_use_cases,
        include_industry_applications=not args.no_industry,
        include_historical_context=not args.no_history,
        save_output=bool(args.output_dir)
    )
    
    # Check for errors
    if "error" in context:
        print(f"Error: {context['error']}")
        return
    
    # Format and display the context
    formatted_context = generator.format_application_context(context, args.format)
    print(formatted_context)
    
    # Print output path if saved
    if args.output_dir:
        print(f"\nOutput saved to {args.output_dir}")


if __name__ == "__main__":
    main()