"""
Coding Theory-Practice Bridge module for AI Note System.
Provides functionality to bridge the gap between theoretical coding knowledge and practical application.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.learning.coding_bridge")

class CodingCompetencyMap:
    """
    Coding Competency Map class for categorizing coding skills and mapping them to learning resources.
    Categorizes skills as critical manual, AI-assisted, or theory-only.
    """
    
    def __init__(self, db_manager=None, embedder=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Coding Competency Map.
        
        Args:
            db_manager: Database manager instance
            embedder: Embedder instance for semantic processing
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.db_manager = db_manager
        self.embedder = embedder
        self.config = config or {}
        self._ensure_coding_tables()
        
        logger.debug("Initialized CodingCompetencyMap")
    
    def _ensure_coding_tables(self) -> None:
        """
        Ensure the coding-related tables exist in the database.
        """
        if not self.db_manager:
            logger.warning("No database manager provided, skipping table creation")
            return
            
        # Create coding_skills table
        skills_query = """
        CREATE TABLE IF NOT EXISTS coding_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            relevance_score REAL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(skills_query)
        
        # Create coding_tasks table
        tasks_query = """
        CREATE TABLE IF NOT EXISTS coding_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            description TEXT,
            difficulty TEXT,
            code_snippet TEXT,
            solution TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES coding_skills(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(tasks_query)
        
        # Create coding_notebooks table
        notebooks_query = """
        CREATE TABLE IF NOT EXISTS coding_notebooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            notebook_content TEXT NOT NULL,
            skills TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(notebooks_query)
        
        # Create ai_collaboration_tracking table
        tracking_query = """
        CREATE TABLE IF NOT EXISTS ai_collaboration_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_id INTEGER,
            task_name TEXT NOT NULL,
            completion_type TEXT NOT NULL,
            ai_assistance_level REAL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (task_id) REFERENCES coding_tasks(id) ON DELETE SET NULL
        )
        """
        self.db_manager.execute_query(tracking_query)
        
        logger.debug("Ensured coding tables exist in database")
    
    def analyze_notes_for_skills(self,
                               user_id: int,
                               notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze notes to generate a personalized coding competency map.
        
        Args:
            user_id (int): ID of the user
            notes (List[Dict[str, Any]]): List of notes to analyze
            
        Returns:
            Dict[str, Any]: Generated competency map
        """
        logger.info(f"Analyzing notes for coding skills for user {user_id}")
        
        # Extract text content from notes
        note_texts = []
        for note in notes:
            content = note.get("content", note.get("text", ""))
            title = note.get("title", "Untitled")
            note_texts.append(f"Title: {title}\n\n{content}")
        
        combined_text = "\n\n---\n\n".join(note_texts)
        
        # Generate competency map using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Analyze the following notes on programming and computer science to create a personalized coding competency map.
        
        Notes:
        {combined_text[:10000]}  # Limit text length to avoid token limits
        
        Create a comprehensive map of coding skills mentioned or implied in these notes, categorizing them into:
        
        1. Critical Manual Skills: Skills that the user must practice and master manually (e.g., data structures, debugging, system design)
        2. AI-Assisted Skills: Skills where AI can handle the heavy lifting (e.g., boilerplate code, generic API usage)
        3. Theory-Only Concepts: Concepts important for understanding but not daily coding (e.g., formal proofs, complexity analysis)
        
        For each skill, provide:
        - Skill name
        - Brief description
        - Category (critical_manual, ai_assisted, or theory_only)
        - Relevance score (0.0-1.0) indicating importance to the user's learning goals
        - Tags (comma-separated keywords)
        
        Format your response as a JSON object with the following structure:
        {{
            "critical_manual": [
                {{
                    "skill_name": "Skill name",
                    "description": "Brief description",
                    "relevance_score": 0.9,
                    "tags": "tag1, tag2, tag3"
                }},
                ...
            ],
            "ai_assisted": [
                {{
                    "skill_name": "Skill name",
                    "description": "Brief description",
                    "relevance_score": 0.7,
                    "tags": "tag1, tag2, tag3"
                }},
                ...
            ],
            "theory_only": [
                {{
                    "skill_name": "Skill name",
                    "description": "Brief description",
                    "relevance_score": 0.5,
                    "tags": "tag1, tag2, tag3"
                }},
                ...
            ]
        }}
        
        Focus on creating a balanced and comprehensive map that will help the user understand what to learn deeply vs. what AI can handle.
        """
        
        # Generate competency map
        try:
            response = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "object",
                    "properties": {
                        "critical_manual": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill_name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "relevance_score": {"type": "number"},
                                    "tags": {"type": "string"}
                                },
                                "required": ["skill_name", "description", "relevance_score", "tags"]
                            }
                        },
                        "ai_assisted": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill_name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "relevance_score": {"type": "number"},
                                    "tags": {"type": "string"}
                                },
                                "required": ["skill_name", "description", "relevance_score", "tags"]
                            }
                        },
                        "theory_only": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill_name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "relevance_score": {"type": "number"},
                                    "tags": {"type": "string"}
                                },
                                "required": ["skill_name", "description", "relevance_score", "tags"]
                            }
                        }
                    },
                    "required": ["critical_manual", "ai_assisted", "theory_only"]
                }
            )
            
            # Save skills to database
            saved_skills = self.save_skills(user_id, response)
            
            competency_map = {
                "user_id": user_id,
                "critical_manual": saved_skills.get("critical_manual", []),
                "ai_assisted": saved_skills.get("ai_assisted", []),
                "theory_only": saved_skills.get("theory_only", []),
                "created_at": datetime.now().isoformat()
            }
            
            logger.info(f"Generated coding competency map for user {user_id}")
            return competency_map
            
        except Exception as e:
            logger.error(f"Error generating coding competency map: {str(e)}")
            return {"error": f"Error generating coding competency map: {str(e)}"}
    
    def save_skills(self,
                  user_id: int,
                  competency_map: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Save skills from a competency map to the database.
        
        Args:
            user_id (int): ID of the user
            competency_map (Dict[str, List[Dict[str, Any]]]): Competency map with categorized skills
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Saved skills by category
        """
        if not self.db_manager:
            logger.warning("No database manager, returning skills without saving")
            return competency_map
        
        saved_skills = {
            "critical_manual": [],
            "ai_assisted": [],
            "theory_only": []
        }
        
        # Process each category
        for category, skills in competency_map.items():
            for skill in skills:
                # Check if skill already exists
                query = """
                SELECT * FROM coding_skills
                WHERE user_id = ? AND skill_name = ?
                """
                
                existing_skill = self.db_manager.execute_query(
                    query, 
                    (user_id, skill["skill_name"])
                ).fetchone()
                
                if existing_skill:
                    # Update existing skill
                    update_query = """
                    UPDATE coding_skills
                    SET description = ?, category = ?, relevance_score = ?, tags = ?
                    WHERE id = ?
                    """
                    
                    self.db_manager.execute_query(
                        update_query,
                        (
                            skill["description"],
                            category,
                            skill["relevance_score"],
                            skill["tags"],
                            existing_skill["id"]
                        )
                    )
                    
                    skill_id = existing_skill["id"]
                else:
                    # Insert new skill
                    insert_query = """
                    INSERT INTO coding_skills (
                        user_id, skill_name, description, category, relevance_score, tags
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """
                    
                    cursor = self.db_manager.execute_query(
                        insert_query,
                        (
                            user_id,
                            skill["skill_name"],
                            skill["description"],
                            category,
                            skill["relevance_score"],
                            skill["tags"]
                        )
                    )
                    
                    skill_id = cursor.lastrowid
                
                # Add ID to skill data
                saved_skill = {
                    "id": skill_id,
                    "skill_name": skill["skill_name"],
                    "description": skill["description"],
                    "category": category,
                    "relevance_score": skill["relevance_score"],
                    "tags": skill["tags"]
                }
                
                saved_skills[category].append(saved_skill)
        
        logger.info(f"Saved {sum(len(skills) for skills in saved_skills.values())} skills for user {user_id}")
        return saved_skills
    
    def get_skills(self,
                 user_id: int,
                 category: Optional[str] = None,
                 min_relevance: float = 0.0) -> List[Dict[str, Any]]:
        """
        Get skills for a user.
        
        Args:
            user_id (int): ID of the user
            category (str, optional): Category to filter by
            min_relevance (float): Minimum relevance score
            
        Returns:
            List[Dict[str, Any]]: List of skills
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT * FROM coding_skills
        WHERE user_id = ? AND relevance_score >= ?
        """
        
        params = [user_id, min_relevance]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY relevance_score DESC"
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def generate_practical_tasks(self,
                               user_id: int,
                               skill_id: int,
                               count: int = 3,
                               difficulty: str = "intermediate") -> List[Dict[str, Any]]:
        """
        Generate practical coding tasks for a skill.
        
        Args:
            user_id (int): ID of the user
            skill_id (int): ID of the skill
            count (int): Number of tasks to generate
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            
        Returns:
            List[Dict[str, Any]]: Generated tasks
        """
        logger.info(f"Generating {count} practical tasks for skill {skill_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Get skill information
        query = """
        SELECT * FROM coding_skills
        WHERE id = ? AND user_id = ?
        """
        
        skill = self.db_manager.execute_query(query, (skill_id, user_id)).fetchone()
        
        if not skill:
            logger.error(f"Skill not found: {skill_id}")
            return []
        
        # Generate tasks using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate {count} practical coding tasks for the skill "{skill['skill_name']}" at {difficulty} difficulty level.
        
        Skill description: {skill['description']}
        
        For each task, provide:
        1. Task name
        2. Description of the task
        3. A code snippet to start with
        4. A solution or approach (not the complete solution, but guidance)
        
        The tasks should be practical, focused on real-world application, and designed to build mastery of the skill.
        
        Format your response as a JSON array with objects containing fields:
        - task_name: Name of the task
        - description: Detailed description
        - difficulty: "{difficulty}"
        - code_snippet: Starting code
        - solution: Guidance on the solution
        """
        
        # Generate tasks
        try:
            response = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "task_name": {"type": "string"},
                            "description": {"type": "string"},
                            "difficulty": {"type": "string"},
                            "code_snippet": {"type": "string"},
                            "solution": {"type": "string"}
                        },
                        "required": ["task_name", "description", "difficulty", "code_snippet", "solution"]
                    }
                }
            )
            
            # Save tasks to database
            saved_tasks = []
            for task in response:
                saved_task = self.save_task(
                    user_id=user_id,
                    skill_id=skill_id,
                    task_name=task["task_name"],
                    description=task["description"],
                    difficulty=task["difficulty"],
                    code_snippet=task["code_snippet"],
                    solution=task["solution"]
                )
                saved_tasks.append(saved_task)
            
            logger.info(f"Generated {len(saved_tasks)} practical tasks for skill {skill_id}")
            return saved_tasks
            
        except Exception as e:
            logger.error(f"Error generating practical tasks: {str(e)}")
            return []
    
    def save_task(self,
                user_id: int,
                skill_id: int,
                task_name: str,
                description: str,
                difficulty: str,
                code_snippet: str,
                solution: str) -> Dict[str, Any]:
        """
        Save a coding task to the database.
        
        Args:
            user_id (int): ID of the user
            skill_id (int): ID of the skill
            task_name (str): Name of the task
            description (str): Description of the task
            difficulty (str): Difficulty level
            code_snippet (str): Starting code
            solution (str): Solution guidance
            
        Returns:
            Dict[str, Any]: Saved task data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning task without saving")
            return {
                "user_id": user_id,
                "skill_id": skill_id,
                "task_name": task_name,
                "description": description,
                "difficulty": difficulty,
                "code_snippet": code_snippet,
                "solution": solution,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO coding_tasks (
            user_id, skill_id, task_name, description, difficulty, code_snippet, solution
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (
                    user_id, skill_id, task_name, description,
                    difficulty, code_snippet, solution
                )
            )
            
            task_id = cursor.lastrowid
            
            logger.debug(f"Saved task {task_id} for skill {skill_id}")
            
            return {
                "id": task_id,
                "user_id": user_id,
                "skill_id": skill_id,
                "task_name": task_name,
                "description": description,
                "difficulty": difficulty,
                "code_snippet": code_snippet,
                "solution": solution,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving task: {str(e)}")
            return {
                "error": f"Error saving task: {str(e)}",
                "task_name": task_name
            }
    
    def get_tasks(self,
                user_id: int,
                skill_id: Optional[int] = None,
                difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get coding tasks for a user.
        
        Args:
            user_id (int): ID of the user
            skill_id (int, optional): ID of the skill to filter by
            difficulty (str, optional): Difficulty level to filter by
            
        Returns:
            List[Dict[str, Any]]: List of tasks
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT t.*, s.skill_name, s.category
        FROM coding_tasks t
        JOIN coding_skills s ON t.skill_id = s.id
        WHERE t.user_id = ?
        """
        
        params = [user_id]
        
        if skill_id is not None:
            query += " AND t.skill_id = ?"
            params.append(skill_id)
        
        if difficulty:
            query += " AND t.difficulty = ?"
            params.append(difficulty)
        
        query += " ORDER BY t.created_at DESC"
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def generate_jupyter_notebook(self,
                                user_id: int,
                                skill_ids: List[int],
                                title: Optional[str] = None,
                                description: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a Jupyter notebook for practicing coding skills.
        
        Args:
            user_id (int): ID of the user
            skill_ids (List[int]): IDs of the skills to include
            title (str, optional): Title of the notebook
            description (str, optional): Description of the notebook
            
        Returns:
            Dict[str, Any]: Generated notebook
        """
        logger.info(f"Generating Jupyter notebook for skills {skill_ids}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Get skills information
        skills = []
        for skill_id in skill_ids:
            query = """
            SELECT * FROM coding_skills
            WHERE id = ? AND user_id = ?
            """
            
            skill = self.db_manager.execute_query(query, (skill_id, user_id)).fetchone()
            
            if skill:
                skills.append(dict(skill))
        
        if not skills:
            logger.error(f"No valid skills found for IDs {skill_ids}")
            return {"error": "No valid skills found"}
        
        # Get tasks for each skill
        tasks_by_skill = {}
        for skill in skills:
            skill_tasks = self.get_tasks(user_id, skill["id"])
            if skill_tasks:
                tasks_by_skill[skill["id"]] = skill_tasks
        
        # Generate notebook using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Default title if not provided
        if not title:
            skill_names = [skill["skill_name"] for skill in skills]
            title = f"Practice Notebook: {', '.join(skill_names[:2])}"
            if len(skill_names) > 2:
                title += f" and {len(skill_names) - 2} more"
        
        # Default description if not provided
        if not description:
            description = f"A Jupyter notebook for practicing {len(skills)} coding skills: {', '.join(skill['skill_name'] for skill in skills)}"
        
        # Create prompt
        prompt = f"""
        Generate a Jupyter notebook for practicing the following coding skills:
        
        {', '.join(f"{i+1}. {skill['skill_name']}: {skill['description']}" for i, skill in enumerate(skills))}
        
        The notebook should include:
        1. An introduction explaining the skills and how to use the notebook
        2. Sections for each skill with:
           - Theoretical explanation
           - Code examples
           - Practice exercises
           - Solutions (in hidden cells)
        3. A final section with a mini-project that combines multiple skills
        
        Format your response as a JSON object representing a Jupyter notebook with the following structure:
        {{
            "cells": [
                {{
                    "cell_type": "markdown",
                    "metadata": {{}},
                    "source": ["# Notebook title\\n", "Introduction text..."]
                }},
                {{
                    "cell_type": "code",
                    "metadata": {{}},
                    "source": ["# Code cell\\n", "print('Hello world')"],
                    "execution_count": null,
                    "outputs": []
                }},
                ...
            ],
            "metadata": {{
                "kernelspec": {{
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }},
                ...
            }},
            "nbformat": 4,
            "nbformat_minor": 4
        }}
        
        Make sure the notebook is well-structured, educational, and includes practical exercises.
        """
        
        # If we have tasks, include them in the prompt
        if tasks_by_skill:
            tasks_text = ""
            for skill_id, tasks in tasks_by_skill.items():
                skill_name = next((s["skill_name"] for s in skills if s["id"] == skill_id), "Unknown")
                tasks_text += f"\nTasks for {skill_name}:\n"
                for i, task in enumerate(tasks[:3]):  # Limit to 3 tasks per skill
                    tasks_text += f"{i+1}. {task['task_name']}: {task['description'][:100]}...\n"
            
            prompt += f"""
            
            Include these existing tasks in the notebook:
            {tasks_text}
            
            Adapt and expand on these tasks to create comprehensive practice exercises.
            """
        
        # Generate notebook
        try:
            notebook_content = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "object",
                    "properties": {
                        "cells": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "cell_type": {"type": "string"},
                                    "metadata": {"type": "object"},
                                    "source": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["cell_type", "metadata", "source"]
                            }
                        },
                        "metadata": {"type": "object"},
                        "nbformat": {"type": "number"},
                        "nbformat_minor": {"type": "number"}
                    },
                    "required": ["cells", "metadata", "nbformat", "nbformat_minor"]
                }
            )
            
            # Save notebook to database
            notebook_data = self.save_notebook(
                user_id=user_id,
                title=title,
                description=description,
                notebook_content=json.dumps(notebook_content),
                skills=",".join(str(skill_id) for skill_id in skill_ids)
            )
            
            logger.info(f"Generated Jupyter notebook for skills {skill_ids}")
            return notebook_data
            
        except Exception as e:
            logger.error(f"Error generating Jupyter notebook: {str(e)}")
            return {"error": f"Error generating Jupyter notebook: {str(e)}"}
    
    def save_notebook(self,
                    user_id: int,
                    title: str,
                    description: str,
                    notebook_content: str,
                    skills: str) -> Dict[str, Any]:
        """
        Save a Jupyter notebook to the database.
        
        Args:
            user_id (int): ID of the user
            title (str): Title of the notebook
            description (str): Description of the notebook
            notebook_content (str): JSON string of notebook content
            skills (str): Comma-separated skill IDs
            
        Returns:
            Dict[str, Any]: Saved notebook data
        """
        if not self.db_manager:
            logger.warning("No database manager, returning notebook without saving")
            return {
                "user_id": user_id,
                "title": title,
                "description": description,
                "notebook_content": notebook_content,
                "skills": skills,
                "created_at": datetime.now().isoformat()
            }
        
        query = """
        INSERT INTO coding_notebooks (
            user_id, title, description, notebook_content, skills
        )
        VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (user_id, title, description, notebook_content, skills)
            )
            
            notebook_id = cursor.lastrowid
            
            logger.debug(f"Saved notebook {notebook_id} for user {user_id}")
            
            return {
                "id": notebook_id,
                "user_id": user_id,
                "title": title,
                "description": description,
                "skills": skills,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error saving notebook: {str(e)}")
            return {
                "error": f"Error saving notebook: {str(e)}",
                "title": title
            }
    
    def get_notebooks(self,
                    user_id: int,
                    skill_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get Jupyter notebooks for a user.
        
        Args:
            user_id (int): ID of the user
            skill_id (int, optional): ID of the skill to filter by
            
        Returns:
            List[Dict[str, Any]]: List of notebooks
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT * FROM coding_notebooks
        WHERE user_id = ?
        """
        
        params = [user_id]
        
        if skill_id is not None:
            query += " AND skills LIKE ?"
            params.append(f"%{skill_id}%")
        
        query += " ORDER BY created_at DESC"
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        return [dict(result) for result in results]
    
    def track_task_completion(self,
                            user_id: int,
                            task_id: Optional[int] = None,
                            task_name: Optional[str] = None,
                            completion_type: str = "manual",
                            ai_assistance_level: float = 0.0,
                            notes: Optional[str] = None) -> Dict[str, Any]:
        """
        Track completion of a coding task with or without AI assistance.
        
        Args:
            user_id (int): ID of the user
            task_id (int, optional): ID of the task
            task_name (str, optional): Name of the task if not from database
            completion_type (str): Type of completion (manual, ai_assisted)
            ai_assistance_level (float): Level of AI assistance (0.0-1.0)
            notes (str, optional): Additional notes
            
        Returns:
            Dict[str, Any]: Tracking data
        """
        logger.info(f"Tracking task completion for user {user_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Validate parameters
        if task_id is None and task_name is None:
            logger.error("Either task_id or task_name must be provided")
            return {"error": "Either task_id or task_name must be provided"}
        
        # If task_id is provided, get task name
        if task_id is not None:
            task_query = """
            SELECT task_name FROM coding_tasks
            WHERE id = ? AND user_id = ?
            """
            
            task = self.db_manager.execute_query(task_query, (task_id, user_id)).fetchone()
            
            if task:
                task_name = task["task_name"]
            else:
                logger.error(f"Task not found: {task_id}")
                return {"error": f"Task not found: {task_id}"}
        
        # Insert tracking data
        query = """
        INSERT INTO ai_collaboration_tracking (
            user_id, task_id, task_name, completion_type, ai_assistance_level, notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query,
                (user_id, task_id, task_name, completion_type, ai_assistance_level, notes)
            )
            
            tracking_id = cursor.lastrowid
            
            logger.debug(f"Tracked task completion {tracking_id} for user {user_id}")
            
            return {
                "id": tracking_id,
                "user_id": user_id,
                "task_id": task_id,
                "task_name": task_name,
                "completion_type": completion_type,
                "ai_assistance_level": ai_assistance_level,
                "notes": notes,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error tracking task completion: {str(e)}")
            return {"error": f"Error tracking task completion: {str(e)}"}
    
    def get_ai_collaboration_stats(self,
                                 user_id: int,
                                 days: int = 30) -> Dict[str, Any]:
        """
        Get statistics on AI collaboration for a user.
        
        Args:
            user_id (int): ID of the user
            days (int): Number of days to include in stats
            
        Returns:
            Dict[str, Any]: Collaboration statistics
        """
        logger.info(f"Getting AI collaboration stats for user {user_id}")
        
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get all tracking data in date range
        query = """
        SELECT * FROM ai_collaboration_tracking
        WHERE user_id = ? AND created_at >= ? AND created_at <= ?
        ORDER BY created_at DESC
        """
        
        results = self.db_manager.execute_query(
            query, 
            (user_id, start_date.isoformat(), end_date.isoformat())
        ).fetchall()
        
        if not results:
            logger.warning(f"No tracking data found for user {user_id} in the last {days} days")
            return {
                "user_id": user_id,
                "days": days,
                "total_tasks": 0,
                "manual_tasks": 0,
                "ai_assisted_tasks": 0,
                "average_ai_assistance": 0.0,
                "balance_score": 0.0,
                "task_history": []
            }
        
        # Convert to list of dictionaries
        tracking_data = [dict(result) for result in results]
        
        # Calculate statistics
        total_tasks = len(tracking_data)
        manual_tasks = sum(1 for t in tracking_data if t["completion_type"] == "manual")
        ai_assisted_tasks = sum(1 for t in tracking_data if t["completion_type"] == "ai_assisted")
        
        if ai_assisted_tasks > 0:
            average_ai_assistance = sum(t["ai_assistance_level"] for t in tracking_data if t["completion_type"] == "ai_assisted") / ai_assisted_tasks
        else:
            average_ai_assistance = 0.0
        
        # Calculate balance score (higher is better, max 1.0)
        # A good balance is around 70% manual, 30% AI-assisted
        if total_tasks > 0:
            manual_ratio = manual_tasks / total_tasks
            ai_ratio = ai_assisted_tasks / total_tasks
            
            # Ideal ratios
            ideal_manual = 0.7
            ideal_ai = 0.3
            
            # Calculate how close to ideal
            manual_distance = abs(manual_ratio - ideal_manual)
            ai_distance = abs(ai_ratio - ideal_ai)
            
            # Convert to a score (1.0 is perfect)
            balance_score = 1.0 - (manual_distance + ai_distance) / 2
        else:
            balance_score = 0.0
        
        # Create stats object
        stats = {
            "user_id": user_id,
            "days": days,
            "total_tasks": total_tasks,
            "manual_tasks": manual_tasks,
            "ai_assisted_tasks": ai_assisted_tasks,
            "average_ai_assistance": average_ai_assistance,
            "balance_score": balance_score,
            "task_history": tracking_data
        }
        
        logger.info(f"Generated AI collaboration stats for user {user_id}")
        return stats
    
    def generate_self_assessment(self,
                               user_id: int,
                               category: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a self-assessment for coding skills.
        
        Args:
            user_id (int): ID of the user
            category (str, optional): Category to filter by
            
        Returns:
            Dict[str, Any]: Self-assessment data
        """
        logger.info(f"Generating self-assessment for user {user_id}")
        
        # Get skills
        skills = self.get_skills(user_id, category)
        
        if not skills:
            logger.warning(f"No skills found for user {user_id}")
            return {"error": "No skills found"}
        
        # Get AI collaboration stats
        stats = self.get_ai_collaboration_stats(user_id)
        
        # Generate assessment using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        skills_text = "\n".join([
            f"{i+1}. {skill['skill_name']} ({skill['category']}, relevance: {skill['relevance_score']:.2f}): {skill['description']}"
            for i, skill in enumerate(skills)
        ])
        
        prompt = f"""
        Generate a comprehensive self-assessment for a user based on their coding skills and AI collaboration patterns.
        
        Skills:
        {skills_text}
        
        AI Collaboration Stats:
        - Total tasks completed: {stats.get('total_tasks', 0)}
        - Manual tasks: {stats.get('manual_tasks', 0)}
        - AI-assisted tasks: {stats.get('ai_assisted_tasks', 0)}
        - Average AI assistance level: {stats.get('average_ai_assistance', 0):.2f}
        - Balance score: {stats.get('balance_score', 0):.2f}
        
        The self-assessment should include:
        1. An overall assessment of the user's skill profile
        2. Strengths and areas for improvement
        3. Recommendations for skills to focus on
        4. Suggestions for balancing manual coding vs. AI assistance
        5. A personalized learning plan with specific next steps
        
        Format your response as a JSON object with the following structure:
        {{
            "overall_assessment": "Overall assessment text",
            "strengths": ["Strength 1", "Strength 2", ...],
            "improvement_areas": ["Area 1", "Area 2", ...],
            "skill_recommendations": [
                {{
                    "skill": "Skill name",
                    "reason": "Reason for recommendation",
                    "resources": ["Resource 1", "Resource 2", ...]
                }},
                ...
            ],
            "ai_balance_suggestions": ["Suggestion 1", "Suggestion 2", ...],
            "learning_plan": [
                {{
                    "step": "Step description",
                    "timeframe": "Timeframe (e.g., '1-2 weeks')",
                    "expected_outcome": "Expected outcome"
                }},
                ...
            ]
        }}
        """
        
        # Generate assessment
        try:
            assessment = llm.generate_structured_output(
                prompt=prompt,
                output_schema={
                    "type": "object",
                    "properties": {
                        "overall_assessment": {"type": "string"},
                        "strengths": {"type": "array", "items": {"type": "string"}},
                        "improvement_areas": {"type": "array", "items": {"type": "string"}},
                        "skill_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill": {"type": "string"},
                                    "reason": {"type": "string"},
                                    "resources": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["skill", "reason", "resources"]
                            }
                        },
                        "ai_balance_suggestions": {"type": "array", "items": {"type": "string"}},
                        "learning_plan": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "string"},
                                    "timeframe": {"type": "string"},
                                    "expected_outcome": {"type": "string"}
                                },
                                "required": ["step", "timeframe", "expected_outcome"]
                            }
                        }
                    },
                    "required": ["overall_assessment", "strengths", "improvement_areas", 
                                "skill_recommendations", "ai_balance_suggestions", "learning_plan"]
                }
            )
            
            # Add metadata
            assessment_data = {
                "user_id": user_id,
                "category": category,
                "skills_count": len(skills),
                "generated_at": datetime.now().isoformat(),
                "assessment": assessment
            }
            
            logger.info(f"Generated self-assessment for user {user_id}")
            return assessment_data
            
        except Exception as e:
            logger.error(f"Error generating self-assessment: {str(e)}")
            return {"error": f"Error generating self-assessment: {str(e)}"}
"""
"""