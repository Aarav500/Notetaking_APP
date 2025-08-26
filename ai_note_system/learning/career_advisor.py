"""
Long-Term Career & Research Path Advisor

This module provides functionality for mapping potential career paths,
creating layered plans, and suggesting mentors and communities based on user interests.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import re

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class TimeFrame:
    """Time frames for career planning"""
    SHORT_TERM = "short_term"  # 0-6 months
    MID_TERM = "mid_term"      # 6-18 months
    LONG_TERM = "long_term"    # 18+ months

class CareerAdvisor:
    """
    Long-Term Career & Research Path Advisor
    
    Features:
    - Map potential career paths based on goals
    - Create layered plans (short-term, mid-term, long-term)
    - Suggest mentors, communities, and internships
    - Identify required skills and knowledge
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None):
        """Initialize the career advisor"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create career goals table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_goals (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            field TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create career paths table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_paths (
            id INTEGER PRIMARY KEY,
            goal_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            probability REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (goal_id) REFERENCES career_goals(id)
        )
        ''')
        
        # Create career milestones table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS career_milestones (
            id INTEGER PRIMARY KEY,
            path_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            time_frame TEXT NOT NULL,
            target_date TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0,
            completion_date TEXT,
            FOREIGN KEY (path_id) REFERENCES career_paths(id)
        )
        ''')
        
        # Create required skills table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS required_skills (
            id INTEGER PRIMARY KEY,
            path_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            importance INTEGER NOT NULL,
            current_level INTEGER,
            target_level INTEGER NOT NULL,
            resources TEXT,
            FOREIGN KEY (path_id) REFERENCES career_paths(id)
        )
        ''')
        
        # Create mentor suggestions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentor_suggestions (
            id INTEGER PRIMARY KEY,
            path_id INTEGER NOT NULL,
            name TEXT,
            role TEXT,
            organization TEXT,
            contact_info TEXT,
            why_relevant TEXT NOT NULL,
            FOREIGN KEY (path_id) REFERENCES career_paths(id)
        )
        ''')
        
        # Create community suggestions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_suggestions (
            id INTEGER PRIMARY KEY,
            path_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT,
            description TEXT,
            why_relevant TEXT NOT NULL,
            FOREIGN KEY (path_id) REFERENCES career_paths(id)
        )
        ''')
        
        conn.commit()
    
    def create_career_goal(self, user_id: int, title: str, 
                         description: Optional[str], field: str) -> int:
        """
        Create a new career goal
        
        Args:
            user_id: The ID of the user
            title: The title of the career goal
            description: Optional description of the career goal
            field: The field or domain of the career goal
            
        Returns:
            The ID of the created career goal
        """
        logger.info(f"Creating career goal: {title}")
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO career_goals (user_id, title, description, field, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, title, description, field, now, now))
        
        goal_id = cursor.lastrowid
        conn.commit()
        
        return goal_id
    
    def get_career_goal(self, goal_id: int) -> Dict[str, Any]:
        """
        Get a career goal by ID
        
        Args:
            goal_id: The ID of the career goal
            
        Returns:
            Dictionary with career goal details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, title, description, field, created_at, updated_at
        FROM career_goals
        WHERE id = ?
        ''', (goal_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        career_goal = {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'description': row[3],
            'field': row[4],
            'created_at': row[5],
            'updated_at': row[6],
            'paths': []
        }
        
        # Get paths for the career goal
        cursor.execute('''
        SELECT id, title, description, probability, created_at
        FROM career_paths
        WHERE goal_id = ?
        ORDER BY probability DESC
        ''', (goal_id,))
        
        for row in cursor.fetchall():
            path = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'probability': row[3],
                'created_at': row[4]
            }
            career_goal['paths'].append(path)
        
        return career_goal
    
    def get_user_career_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get career goals for a user
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List of career goal summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, description, field, created_at, updated_at
        FROM career_goals
        WHERE user_id = ?
        ORDER BY updated_at DESC
        ''', (user_id,))
        
        goals = []
        for row in cursor.fetchall():
            goal = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'field': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            }
            goals.append(goal)
        
        return goals
    
    def generate_career_paths(self, goal_id: int, user_notes: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Generate potential career paths based on a career goal
        
        Args:
            goal_id: The ID of the career goal
            user_notes: Optional list of user notes to consider
            
        Returns:
            List of generated career paths
        """
        logger.info(f"Generating career paths for goal {goal_id}")
        
        # Get the career goal
        career_goal = self.get_career_goal(goal_id)
        
        if not career_goal:
            return []
        
        # Prepare context from user notes if provided
        notes_context = ""
        if user_notes:
            notes_context = "User's relevant notes:\n"
            for i, note in enumerate(user_notes, 1):
                notes_context += f"Note {i}: {note.get('title', 'Untitled')}\n"
                notes_context += f"Content: {note.get('content', '')[:300]}...\n\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert career advisor with deep knowledge of various professional fields and career trajectories.
        
        Career Goal:
        Title: {career_goal['title']}
        Description: {career_goal['description'] or 'No description provided.'}
        Field: {career_goal['field']}
        
        {notes_context}
        
        Based on this career goal, generate 3-5 potential career paths that could lead to achieving this goal.
        For each path:
        1. Provide a clear title/role
        2. Write a detailed description of the path
        3. Assign a probability score (0.0 to 1.0) indicating how well this path aligns with the stated goal
        
        Format your response as JSON:
        ```json
        [
          {{
            "title": "Research Engineer in GenAI",
            "description": "This path involves focusing on the engineering aspects of generative AI systems, building and optimizing models for production environments...",
            "probability": 0.85
          }},
          ...
        ]
        ```
        
        Ensure the paths are diverse yet realistic, and provide specific details about each path rather than generic advice.
        """
        
        # Generate paths using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        # Extract JSON from response
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
            paths_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        # Store paths in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        stored_paths = []
        for path_data in paths_data:
            cursor.execute('''
            INSERT INTO career_paths (goal_id, title, description, probability, created_at)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                goal_id,
                path_data.get('title', ''),
                path_data.get('description', ''),
                path_data.get('probability', 0.5),
                now
            ))
            
            path_id = cursor.lastrowid
            
            path_data['id'] = path_id
            path_data['created_at'] = now
            
            stored_paths.append(path_data)
        
        conn.commit()
        
        return stored_paths
    
    def get_career_path(self, path_id: int) -> Dict[str, Any]:
        """
        Get a career path by ID with all its details
        
        Args:
            path_id: The ID of the career path
            
        Returns:
            Dictionary with career path details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT cp.id, cp.goal_id, cp.title, cp.description, cp.probability, cp.created_at,
               cg.title as goal_title, cg.field as goal_field
        FROM career_paths cp
        JOIN career_goals cg ON cp.goal_id = cg.id
        WHERE cp.id = ?
        ''', (path_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        career_path = {
            'id': row[0],
            'goal_id': row[1],
            'title': row[2],
            'description': row[3],
            'probability': row[4],
            'created_at': row[5],
            'goal_title': row[6],
            'goal_field': row[7],
            'milestones': [],
            'required_skills': [],
            'mentor_suggestions': [],
            'community_suggestions': []
        }
        
        # Get milestones for the career path
        cursor.execute('''
        SELECT id, title, description, time_frame, target_date, completed, completion_date
        FROM career_milestones
        WHERE path_id = ?
        ORDER BY 
            CASE time_frame 
                WHEN 'short_term' THEN 1 
                WHEN 'mid_term' THEN 2 
                WHEN 'long_term' THEN 3 
                ELSE 4 
            END,
            target_date
        ''', (path_id,))
        
        for row in cursor.fetchall():
            milestone = {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'time_frame': row[3],
                'target_date': row[4],
                'completed': bool(row[5]),
                'completion_date': row[6]
            }
            career_path['milestones'].append(milestone)
        
        # Get required skills for the career path
        cursor.execute('''
        SELECT id, skill, importance, current_level, target_level, resources
        FROM required_skills
        WHERE path_id = ?
        ORDER BY importance DESC
        ''', (path_id,))
        
        for row in cursor.fetchall():
            skill = {
                'id': row[0],
                'skill': row[1],
                'importance': row[2],
                'current_level': row[3],
                'target_level': row[4],
                'resources': row[5]
            }
            career_path['required_skills'].append(skill)
        
        # Get mentor suggestions for the career path
        cursor.execute('''
        SELECT id, name, role, organization, contact_info, why_relevant
        FROM mentor_suggestions
        WHERE path_id = ?
        ''', (path_id,))
        
        for row in cursor.fetchall():
            mentor = {
                'id': row[0],
                'name': row[1],
                'role': row[2],
                'organization': row[3],
                'contact_info': row[4],
                'why_relevant': row[5]
            }
            career_path['mentor_suggestions'].append(mentor)
        
        # Get community suggestions for the career path
        cursor.execute('''
        SELECT id, name, type, url, description, why_relevant
        FROM community_suggestions
        WHERE path_id = ?
        ''', (path_id,))
        
        for row in cursor.fetchall():
            community = {
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'url': row[3],
                'description': row[4],
                'why_relevant': row[5]
            }
            career_path['community_suggestions'].append(community)
        
        return career_path
    
    def generate_layered_plan(self, path_id: int) -> List[Dict[str, Any]]:
        """
        Generate a layered plan (short-term, mid-term, long-term) for a career path
        
        Args:
            path_id: The ID of the career path
            
        Returns:
            List of generated milestones
        """
        logger.info(f"Generating layered plan for career path {path_id}")
        
        # Get the career path
        career_path = self.get_career_path(path_id)
        
        if not career_path:
            return []
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert career advisor creating a detailed, layered plan for a specific career path.
        
        Career Goal: {career_path['goal_title']}
        Field: {career_path['goal_field']}
        
        Career Path:
        Title: {career_path['title']}
        Description: {career_path['description']}
        
        Create a layered plan with specific milestones divided into three time frames:
        1. Short-term (0-6 months): Immediate actions and quick wins
        2. Mid-term (6-18 months): Intermediate goals and skill development
        3. Long-term (18+ months): Major achievements and career transitions
        
        For each milestone:
        - Provide a clear, specific title
        - Include a detailed description of what needs to be accomplished
        - Assign a realistic target date
        
        Format your response as JSON:
        ```json
        [
          {{
            "title": "Complete Stanford's CS224N NLP Course",
            "description": "Finish the online course to build foundational knowledge in NLP techniques...",
            "time_frame": "short_term",
            "target_date": "2025-10-15"
          }},
          ...
        ]
        ```
        
        Include at least 3 milestones for each time frame (short-term, mid-term, long-term).
        Ensure the milestones are specific, measurable, achievable, relevant, and time-bound (SMART).
        """
        
        # Generate milestones using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        # Extract JSON from response
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
            milestones_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        # Store milestones in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # First, delete any existing milestones for this path
        cursor.execute('''
        DELETE FROM career_milestones
        WHERE path_id = ?
        ''', (path_id,))
        
        stored_milestones = []
        for milestone_data in milestones_data:
            cursor.execute('''
            INSERT INTO career_milestones (
                path_id, title, description, time_frame, target_date, completed
            )
            VALUES (?, ?, ?, ?, ?, 0)
            ''', (
                path_id,
                milestone_data.get('title', ''),
                milestone_data.get('description', ''),
                milestone_data.get('time_frame', ''),
                milestone_data.get('target_date', '')
            ))
            
            milestone_id = cursor.lastrowid
            
            milestone_data['id'] = milestone_id
            milestone_data['completed'] = False
            milestone_data['completion_date'] = None
            
            stored_milestones.append(milestone_data)
        
        conn.commit()
        
        return stored_milestones
    
    def identify_required_skills(self, path_id: int) -> List[Dict[str, Any]]:
        """
        Identify required skills and knowledge for a career path
        
        Args:
            path_id: The ID of the career path
            
        Returns:
            List of identified required skills
        """
        logger.info(f"Identifying required skills for career path {path_id}")
        
        # Get the career path
        career_path = self.get_career_path(path_id)
        
        if not career_path:
            return []
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert career advisor identifying the key skills and knowledge required for a specific career path.
        
        Career Goal: {career_path['goal_title']}
        Field: {career_path['goal_field']}
        
        Career Path:
        Title: {career_path['title']}
        Description: {career_path['description']}
        
        Identify the most important skills and knowledge areas required for success in this career path.
        For each skill:
        - Provide a clear, specific name
        - Rate its importance on a scale of 1-10
        - Specify the target proficiency level needed (1-5)
        - Suggest resources for developing this skill (courses, books, projects, etc.)
        
        Format your response as JSON:
        ```json
        [
          {{
            "skill": "Deep Learning with PyTorch",
            "importance": 9,
            "target_level": 4,
            "resources": "1. Deep Learning with PyTorch by Eli Stevens, 2. Fast.ai course, 3. Build a recommendation system project"
          }},
          ...
        ]
        ```
        
        Include at least 10 skills, ranging from technical skills to soft skills, depending on what's most relevant for this career path.
        Be specific rather than generic (e.g., "TensorFlow for Computer Vision" rather than just "Machine Learning").
        """
        
        # Generate skills using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        # Extract JSON from response
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
            skills_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        # Store skills in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # First, delete any existing skills for this path
        cursor.execute('''
        DELETE FROM required_skills
        WHERE path_id = ?
        ''', (path_id,))
        
        stored_skills = []
        for skill_data in skills_data:
            cursor.execute('''
            INSERT INTO required_skills (
                path_id, skill, importance, current_level, target_level, resources
            )
            VALUES (?, ?, ?, NULL, ?, ?)
            ''', (
                path_id,
                skill_data.get('skill', ''),
                skill_data.get('importance', 5),
                skill_data.get('target_level', 3),
                skill_data.get('resources', '')
            ))
            
            skill_id = cursor.lastrowid
            
            skill_data['id'] = skill_id
            skill_data['current_level'] = None
            
            stored_skills.append(skill_data)
        
        conn.commit()
        
        return stored_skills
    
    def update_skill_level(self, skill_id: int, current_level: int) -> bool:
        """
        Update the current level of a required skill
        
        Args:
            skill_id: The ID of the skill
            current_level: The current level of proficiency (1-5)
            
        Returns:
            True if the update was successful, False otherwise
        """
        if not 1 <= current_level <= 5:
            return False
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE required_skills
        SET current_level = ?
        WHERE id = ?
        ''', (current_level, skill_id))
        
        conn.commit()
        
        return cursor.rowcount > 0
    
    def suggest_mentors_and_communities(self, path_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        Suggest potential mentors and communities for a career path
        
        Args:
            path_id: The ID of the career path
            
        Returns:
            Dictionary with mentor and community suggestions
        """
        logger.info(f"Suggesting mentors and communities for career path {path_id}")
        
        # Get the career path
        career_path = self.get_career_path(path_id)
        
        if not career_path:
            return {'mentors': [], 'communities': []}
        
        # Get the required skills for context
        required_skills = []
        for skill in career_path.get('required_skills', []):
            required_skills.append(skill.get('skill', ''))
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert career advisor suggesting mentors and communities for someone pursuing a specific career path.
        
        Career Goal: {career_path['goal_title']}
        Field: {career_path['goal_field']}
        
        Career Path:
        Title: {career_path['title']}
        Description: {career_path['description']}
        
        Key Skills Required:
        {', '.join(required_skills)}
        
        Part 1: Suggest 3-5 potential mentors or mentor types who could help with this career path.
        For each mentor:
        - Provide a name or role description
        - Include their role/position
        - Mention their organization (if applicable)
        - Explain why they would be relevant to this career path
        
        Part 2: Suggest 5-7 communities, groups, or organizations that would be valuable for networking and learning.
        For each community:
        - Provide the name
        - Specify the type (online forum, professional organization, conference, etc.)
        - Include a URL if applicable
        - Add a brief description
        - Explain why it's relevant to this career path
        
        Format your response as JSON:
        ```json
        {{
          "mentors": [
            {{
              "name": "Dr. Jane Smith",
              "role": "Senior Research Scientist",
              "organization": "Google DeepMind",
              "contact_info": "",
              "why_relevant": "Dr. Smith is a leading researcher in generative AI with numerous publications on transformer architectures..."
            }},
            ...
          ],
          "communities": [
            {{
              "name": "Machine Learning Mastery",
              "type": "Online forum and learning community",
              "url": "https://machinelearningmastery.com/community/",
              "description": "A community focused on practical implementation of ML algorithms...",
              "why_relevant": "This community has a strong focus on applied ML in industry settings..."
            }},
            ...
          ]
        }}
        ```
        
        For mentors, you can suggest specific individuals who are well-known in the field, or describe types of mentors to seek out.
        For communities, focus on specific, active groups rather than generic platforms.
        """
        
        # Generate suggestions using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without the markdown code block
            json_match = re.search(r'\{.*"mentors".*"communities".*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                logger.error("Failed to extract JSON from LLM response")
                return {'mentors': [], 'communities': []}
        
        try:
            suggestions_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {'mentors': [], 'communities': []}
        
        # Store suggestions in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # First, delete any existing suggestions for this path
        cursor.execute('''
        DELETE FROM mentor_suggestions
        WHERE path_id = ?
        ''', (path_id,))
        
        cursor.execute('''
        DELETE FROM community_suggestions
        WHERE path_id = ?
        ''', (path_id,))
        
        # Store mentor suggestions
        stored_mentors = []
        for mentor_data in suggestions_data.get('mentors', []):
            cursor.execute('''
            INSERT INTO mentor_suggestions (
                path_id, name, role, organization, contact_info, why_relevant
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                path_id,
                mentor_data.get('name', ''),
                mentor_data.get('role', ''),
                mentor_data.get('organization', ''),
                mentor_data.get('contact_info', ''),
                mentor_data.get('why_relevant', '')
            ))
            
            mentor_id = cursor.lastrowid
            mentor_data['id'] = mentor_id
            stored_mentors.append(mentor_data)
        
        # Store community suggestions
        stored_communities = []
        for community_data in suggestions_data.get('communities', []):
            cursor.execute('''
            INSERT INTO community_suggestions (
                path_id, name, type, url, description, why_relevant
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                path_id,
                community_data.get('name', ''),
                community_data.get('type', ''),
                community_data.get('url', ''),
                community_data.get('description', ''),
                community_data.get('why_relevant', '')
            ))
            
            community_id = cursor.lastrowid
            community_data['id'] = community_id
            stored_communities.append(community_data)
        
        conn.commit()
        
        return {
            'mentors': stored_mentors,
            'communities': stored_communities
        }
    
    def mark_milestone_completed(self, milestone_id: int, completed: bool = True) -> bool:
        """
        Mark a career milestone as completed or not completed
        
        Args:
            milestone_id: The ID of the milestone
            completed: Whether the milestone is completed
            
        Returns:
            True if the update was successful, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        completion_date = datetime.now().isoformat() if completed else None
        
        cursor.execute('''
        UPDATE career_milestones
        SET completed = ?, completion_date = ?
        WHERE id = ?
        ''', (1 if completed else 0, completion_date, milestone_id))
        
        conn.commit()
        
        return cursor.rowcount > 0
    
    def generate_complete_career_plan(self, goal_id: int, user_notes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a complete career plan including paths, milestones, skills, and suggestions
        
        Args:
            goal_id: The ID of the career goal
            user_notes: Optional list of user notes to consider
            
        Returns:
            Dictionary with the complete career plan
        """
        logger.info(f"Generating complete career plan for goal {goal_id}")
        
        # Generate career paths
        paths = self.generate_career_paths(goal_id, user_notes)
        
        if not paths:
            return {'error': 'Failed to generate career paths'}
        
        # Get the top path (highest probability)
        top_path = max(paths, key=lambda x: x.get('probability', 0))
        path_id = top_path['id']
        
        # Generate layered plan
        milestones = self.generate_layered_plan(path_id)
        
        # Identify required skills
        skills = self.identify_required_skills(path_id)
        
        # Suggest mentors and communities
        suggestions = self.suggest_mentors_and_communities(path_id)
        
        # Get the complete career path with all details
        complete_path = self.get_career_path(path_id)
        
        return {
            'goal_id': goal_id,
            'path': complete_path,
            'alternative_paths': [p for p in paths if p['id'] != path_id],
            'milestones': milestones,
            'skills': skills,
            'mentors': suggestions.get('mentors', []),
            'communities': suggestions.get('communities', [])
        }

# Helper functions for easier access to career advisor functionality

def create_career_goal(db_manager, user_id: int, title: str, 
                     field: str, description: Optional[str] = None) -> int:
    """
    Create a new career goal
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        title: The title of the career goal
        field: The field or domain of the career goal
        description: Optional description of the career goal
        
    Returns:
        The ID of the created career goal
    """
    advisor = CareerAdvisor(db_manager)
    return advisor.create_career_goal(user_id, title, description, field)

def generate_career_paths(db_manager, goal_id: int, user_notes: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Generate potential career paths based on a career goal
    
    Args:
        db_manager: Database manager instance
        goal_id: The ID of the career goal
        user_notes: Optional list of user notes to consider
        
    Returns:
        List of generated career paths
    """
    advisor = CareerAdvisor(db_manager)
    return advisor.generate_career_paths(goal_id, user_notes)

def generate_complete_career_plan(db_manager, goal_id: int, user_notes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Generate a complete career plan including paths, milestones, skills, and suggestions
    
    Args:
        db_manager: Database manager instance
        goal_id: The ID of the career goal
        user_notes: Optional list of user notes to consider
        
    Returns:
        Dictionary with the complete career plan
    """
    advisor = CareerAdvisor(db_manager)
    return advisor.generate_complete_career_plan(goal_id, user_notes)