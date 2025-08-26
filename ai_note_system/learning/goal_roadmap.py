"""
Goal-Based Roadmap Generator module for AI Note System.
Provides functionality to create personalized learning roadmaps based on goals.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import calendar
import uuid

# Setup logging
logger = logging.getLogger("ai_note_system.learning.goal_roadmap")

class GoalRoadmapGenerator:
    """
    Goal Roadmap Generator class for creating personalized learning plans.
    Generates realistic roadmaps based on goals, timeframes, and skill levels.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Goal Roadmap Generator.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Default effort estimates (hours)
        self.default_effort_estimates = {
            "beginner": {
                "concept": 2.0,
                "skill": 4.0,
                "project": 8.0
            },
            "intermediate": {
                "concept": 1.5,
                "skill": 3.0,
                "project": 6.0
            },
            "advanced": {
                "concept": 1.0,
                "skill": 2.0,
                "project": 4.0
            }
        }
        
        # Default buffer percentages
        self.buffer_percentages = {
            "revision": 0.15,  # 15% of time for revision
            "life_events": 0.10,  # 10% of time for unexpected life events
            "difficulty": 0.20  # 20% of time for unexpected difficulty
        }
        
        logger.debug("Initialized GoalRoadmapGenerator")
    
    def generate_roadmap(self, 
                        goal: str,
                        timeframe_weeks: int,
                        skill_level: str = "beginner",
                        available_hours_per_week: float = 10.0,
                        start_date: Optional[datetime] = None,
                        include_projects: bool = True,
                        include_assessments: bool = True,
                        output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a personalized learning roadmap based on the goal.
        
        Args:
            goal (str): The learning goal (e.g., "Master Linear Algebra for ML")
            timeframe_weeks (int): Timeframe in weeks
            skill_level (str): Current skill level ("beginner", "intermediate", "advanced")
            available_hours_per_week (float): Available study hours per week
            start_date (datetime, optional): Start date for the roadmap
            include_projects (bool): Whether to include projects in the roadmap
            include_assessments (bool): Whether to include assessments in the roadmap
            output_dir (str, optional): Directory to save the roadmap
            
        Returns:
            Dict[str, Any]: Generated roadmap
        """
        logger.info(f"Generating roadmap for goal: {goal}")
        
        # Validate inputs
        if timeframe_weeks <= 0:
            logger.error("Timeframe must be positive")
            return {"error": "Timeframe must be positive"}
        
        if available_hours_per_week <= 0:
            logger.error("Available hours per week must be positive")
            return {"error": "Available hours per week must be positive"}
        
        if skill_level not in ["beginner", "intermediate", "advanced"]:
            logger.warning(f"Unknown skill level: {skill_level}, defaulting to beginner")
            skill_level = "beginner"
        
        # Set start date if not provided
        if start_date is None:
            start_date = datetime.now()
        
        # Research the goal to identify learning requirements
        learning_requirements = self._research_goal(goal, skill_level)
        
        # Estimate required effort
        effort_estimate = self._estimate_effort(learning_requirements, skill_level)
        
        # Calculate total available hours
        total_available_hours = timeframe_weeks * available_hours_per_week
        
        # Apply buffer for revision and life events
        buffer_hours = self._calculate_buffer(total_available_hours)
        effective_available_hours = total_available_hours - buffer_hours
        
        # Check if the goal is achievable in the given timeframe
        achievable = effort_estimate["total_hours"] <= effective_available_hours
        
        # Adjust learning requirements if not achievable
        if not achievable:
            learning_requirements = self._adjust_requirements(
                learning_requirements, 
                effort_estimate["total_hours"], 
                effective_available_hours
            )
            # Re-estimate effort
            effort_estimate = self._estimate_effort(learning_requirements, skill_level)
        
        # Generate weekly plan
        weekly_plan = self._generate_weekly_plan(
            learning_requirements,
            start_date,
            timeframe_weeks,
            available_hours_per_week,
            skill_level
        )
        
        # Generate milestones
        milestones = self._generate_milestones(
            learning_requirements,
            start_date,
            timeframe_weeks
        )
        
        # Generate calendar events
        calendar_events = self._generate_calendar_events(
            weekly_plan,
            milestones,
            start_date
        )
        
        # Compile roadmap
        roadmap = {
            "id": str(uuid.uuid4()),
            "goal": goal,
            "skill_level": skill_level,
            "timeframe_weeks": timeframe_weeks,
            "available_hours_per_week": available_hours_per_week,
            "start_date": start_date.isoformat(),
            "end_date": (start_date + timedelta(weeks=timeframe_weeks)).isoformat(),
            "learning_requirements": learning_requirements,
            "effort_estimate": effort_estimate,
            "achievable": achievable,
            "buffer_hours": buffer_hours,
            "effective_available_hours": effective_available_hours,
            "weekly_plan": weekly_plan,
            "milestones": milestones,
            "calendar_events": calendar_events,
            "created_at": datetime.now().isoformat()
        }
        
        # Save roadmap if output directory is provided
        if output_dir:
            self._save_roadmap(roadmap, output_dir)
        
        logger.info(f"Roadmap generated for goal: {goal}")
        return roadmap
    
    def _research_goal(self, goal: str, skill_level: str) -> List[Dict[str, Any]]:
        """
        Research the goal to identify learning requirements.
        
        Args:
            goal (str): The learning goal
            skill_level (str): Current skill level
            
        Returns:
            List[Dict[str, Any]]: List of learning requirements
        """
        logger.debug(f"Researching goal: {goal}")
        
        # This is a simplified implementation
        # In a real implementation, you would use LLMs, web scraping, or a knowledge base
        
        # Extract domain from goal
        domain = self._extract_domain(goal)
        
        # Return mock learning requirements based on domain
        if "linear algebra" in goal.lower():
            return [
                {
                    "id": "la-001",
                    "title": "Vectors and Vector Spaces",
                    "type": "concept",
                    "description": "Understanding vectors, vector operations, and vector spaces",
                    "resources": [
                        {"type": "video", "title": "Introduction to Vectors", "url": "https://example.com/vectors"},
                        {"type": "book", "title": "Linear Algebra and Its Applications", "author": "Gilbert Strang"}
                    ],
                    "prerequisites": [],
                    "difficulty": "beginner",
                    "estimated_hours": 4
                },
                {
                    "id": "la-002",
                    "title": "Matrices and Matrix Operations",
                    "type": "concept",
                    "description": "Understanding matrices, matrix operations, and their properties",
                    "resources": [
                        {"type": "video", "title": "Introduction to Matrices", "url": "https://example.com/matrices"},
                        {"type": "article", "title": "Matrix Operations", "url": "https://example.com/matrix-ops"}
                    ],
                    "prerequisites": ["la-001"],
                    "difficulty": "beginner",
                    "estimated_hours": 6
                },
                {
                    "id": "la-003",
                    "title": "Matrix Transformations",
                    "type": "concept",
                    "description": "Understanding how matrices represent transformations",
                    "resources": [
                        {"type": "video", "title": "Matrix Transformations", "url": "https://example.com/transformations"},
                        {"type": "interactive", "title": "Visualizing Transformations", "url": "https://example.com/viz"}
                    ],
                    "prerequisites": ["la-002"],
                    "difficulty": "intermediate",
                    "estimated_hours": 5
                },
                {
                    "id": "la-004",
                    "title": "Eigenvalues and Eigenvectors",
                    "type": "concept",
                    "description": "Understanding eigenvalues, eigenvectors, and their applications",
                    "resources": [
                        {"type": "video", "title": "Eigenvalues and Eigenvectors", "url": "https://example.com/eigen"},
                        {"type": "article", "title": "Applications of Eigenvalues", "url": "https://example.com/eigen-apps"}
                    ],
                    "prerequisites": ["la-003"],
                    "difficulty": "advanced",
                    "estimated_hours": 8
                },
                {
                    "id": "la-005",
                    "title": "Implementing Matrix Operations",
                    "type": "skill",
                    "description": "Implementing matrix operations in Python/NumPy",
                    "resources": [
                        {"type": "tutorial", "title": "NumPy for Linear Algebra", "url": "https://example.com/numpy-la"},
                        {"type": "notebook", "title": "Matrix Operations in NumPy", "url": "https://example.com/numpy-matrix"}
                    ],
                    "prerequisites": ["la-002"],
                    "difficulty": "intermediate",
                    "estimated_hours": 4
                },
                {
                    "id": "la-006",
                    "title": "Linear Regression with Linear Algebra",
                    "type": "project",
                    "description": "Implementing linear regression using linear algebra concepts",
                    "resources": [
                        {"type": "tutorial", "title": "Linear Regression from Scratch", "url": "https://example.com/lr-scratch"},
                        {"type": "dataset", "title": "Housing Prices Dataset", "url": "https://example.com/housing"}
                    ],
                    "prerequisites": ["la-004", "la-005"],
                    "difficulty": "advanced",
                    "estimated_hours": 10
                }
            ]
        elif "machine learning" in goal.lower():
            return [
                {
                    "id": "ml-001",
                    "title": "Introduction to Machine Learning",
                    "type": "concept",
                    "description": "Understanding the basics of machine learning",
                    "resources": [
                        {"type": "course", "title": "Machine Learning Basics", "url": "https://example.com/ml-basics"},
                        {"type": "book", "title": "Introduction to Machine Learning", "author": "Ethem Alpaydin"}
                    ],
                    "prerequisites": [],
                    "difficulty": "beginner",
                    "estimated_hours": 6
                },
                # Add more ML requirements...
            ]
        else:
            # Generic learning requirements
            return [
                {
                    "id": "gen-001",
                    "title": f"Introduction to {domain}",
                    "type": "concept",
                    "description": f"Understanding the basics of {domain}",
                    "resources": [
                        {"type": "course", "title": f"{domain} Basics", "url": f"https://example.com/{domain.lower()}-basics"},
                        {"type": "book", "title": f"Introduction to {domain}", "author": "John Smith"}
                    ],
                    "prerequisites": [],
                    "difficulty": "beginner",
                    "estimated_hours": 6
                },
                {
                    "id": "gen-002",
                    "title": f"Intermediate {domain} Concepts",
                    "type": "concept",
                    "description": f"Deeper understanding of {domain} concepts",
                    "resources": [
                        {"type": "course", "title": f"Intermediate {domain}", "url": f"https://example.com/{domain.lower()}-intermediate"},
                        {"type": "article", "title": f"{domain} Concepts", "url": f"https://example.com/{domain.lower()}-concepts"}
                    ],
                    "prerequisites": ["gen-001"],
                    "difficulty": "intermediate",
                    "estimated_hours": 8
                },
                {
                    "id": "gen-003",
                    "title": f"Advanced {domain} Techniques",
                    "type": "concept",
                    "description": f"Advanced techniques in {domain}",
                    "resources": [
                        {"type": "course", "title": f"Advanced {domain}", "url": f"https://example.com/{domain.lower()}-advanced"},
                        {"type": "paper", "title": f"Recent Advances in {domain}", "url": f"https://example.com/{domain.lower()}-advances"}
                    ],
                    "prerequisites": ["gen-002"],
                    "difficulty": "advanced",
                    "estimated_hours": 10
                },
                {
                    "id": "gen-004",
                    "title": f"Practical {domain} Skills",
                    "type": "skill",
                    "description": f"Developing practical skills in {domain}",
                    "resources": [
                        {"type": "tutorial", "title": f"{domain} in Practice", "url": f"https://example.com/{domain.lower()}-practice"},
                        {"type": "workshop", "title": f"{domain} Workshop", "url": f"https://example.com/{domain.lower()}-workshop"}
                    ],
                    "prerequisites": ["gen-002"],
                    "difficulty": "intermediate",
                    "estimated_hours": 8
                },
                {
                    "id": "gen-005",
                    "title": f"{domain} Project",
                    "type": "project",
                    "description": f"Building a project using {domain} knowledge",
                    "resources": [
                        {"type": "tutorial", "title": f"{domain} Project Guide", "url": f"https://example.com/{domain.lower()}-project"},
                        {"type": "example", "title": f"Sample {domain} Project", "url": f"https://example.com/{domain.lower()}-sample"}
                    ],
                    "prerequisites": ["gen-003", "gen-004"],
                    "difficulty": "advanced",
                    "estimated_hours": 15
                }
            ]
    
    def _extract_domain(self, goal: str) -> str:
        """
        Extract the domain from the goal.
        
        Args:
            goal (str): The learning goal
            
        Returns:
            str: The extracted domain
        """
        # This is a simplified implementation
        # In a real implementation, you would use NLP techniques
        
        goal_lower = goal.lower()
        
        if "linear algebra" in goal_lower:
            return "Linear Algebra"
        elif "machine learning" in goal_lower or "ml" in goal_lower:
            return "Machine Learning"
        elif "deep learning" in goal_lower or "neural network" in goal_lower:
            return "Deep Learning"
        elif "data science" in goal_lower:
            return "Data Science"
        elif "python" in goal_lower:
            return "Python Programming"
        elif "javascript" in goal_lower or "js" in goal_lower:
            return "JavaScript"
        elif "web development" in goal_lower:
            return "Web Development"
        elif "mobile" in goal_lower or "app development" in goal_lower:
            return "Mobile Development"
        else:
            # Extract the first few words as the domain
            words = goal.split()
            if len(words) >= 3:
                return " ".join(words[:3])
            else:
                return goal
    
    def _estimate_effort(self, learning_requirements: List[Dict[str, Any]], skill_level: str) -> Dict[str, Any]:
        """
        Estimate the effort required to complete the learning requirements.
        
        Args:
            learning_requirements (List[Dict[str, Any]]): List of learning requirements
            skill_level (str): Current skill level
            
        Returns:
            Dict[str, Any]: Effort estimate
        """
        logger.debug("Estimating effort for learning requirements")
        
        # Initialize counters
        total_hours = 0
        concept_hours = 0
        skill_hours = 0
        project_hours = 0
        
        # Count requirements by type
        num_concepts = 0
        num_skills = 0
        num_projects = 0
        
        # Process each requirement
        for req in learning_requirements:
            req_type = req.get("type", "concept")
            req_hours = req.get("estimated_hours", 0)
            
            # Adjust hours based on skill level
            if req_hours == 0:
                # Use default estimates if not provided
                req_hours = self.default_effort_estimates.get(skill_level, {}).get(req_type, 2.0)
            elif skill_level == "intermediate":
                req_hours *= 0.8  # 20% faster for intermediate
            elif skill_level == "advanced":
                req_hours *= 0.6  # 40% faster for advanced
            
            # Update counters
            total_hours += req_hours
            
            if req_type == "concept":
                concept_hours += req_hours
                num_concepts += 1
            elif req_type == "skill":
                skill_hours += req_hours
                num_skills += 1
            elif req_type == "project":
                project_hours += req_hours
                num_projects += 1
        
        return {
            "total_hours": total_hours,
            "concept_hours": concept_hours,
            "skill_hours": skill_hours,
            "project_hours": project_hours,
            "num_concepts": num_concepts,
            "num_skills": num_skills,
            "num_projects": num_projects
        }
    
    def _calculate_buffer(self, total_hours: float) -> float:
        """
        Calculate buffer hours for revision and life events.
        
        Args:
            total_hours (float): Total available hours
            
        Returns:
            float: Buffer hours
        """
        # Calculate buffer based on percentages
        revision_buffer = total_hours * self.buffer_percentages.get("revision", 0.15)
        life_events_buffer = total_hours * self.buffer_percentages.get("life_events", 0.10)
        difficulty_buffer = total_hours * self.buffer_percentages.get("difficulty", 0.20)
        
        total_buffer = revision_buffer + life_events_buffer + difficulty_buffer
        
        return total_buffer
    
    def _adjust_requirements(self, 
                           learning_requirements: List[Dict[str, Any]], 
                           estimated_hours: float, 
                           available_hours: float) -> List[Dict[str, Any]]:
        """
        Adjust learning requirements to fit within available hours.
        
        Args:
            learning_requirements (List[Dict[str, Any]]): List of learning requirements
            estimated_hours (float): Estimated hours to complete all requirements
            available_hours (float): Available hours
            
        Returns:
            List[Dict[str, Any]]: Adjusted learning requirements
        """
        logger.debug(f"Adjusting requirements: estimated={estimated_hours}, available={available_hours}")
        
        if estimated_hours <= available_hours:
            # No adjustment needed
            return learning_requirements
        
        # Calculate reduction factor
        reduction_factor = available_hours / estimated_hours
        
        # Sort requirements by priority (essential first, then by difficulty)
        def get_priority(req):
            difficulty = req.get("difficulty", "beginner")
            difficulty_score = {"beginner": 0, "intermediate": 1, "advanced": 2}
            return difficulty_score.get(difficulty, 0)
        
        sorted_requirements = sorted(learning_requirements, key=get_priority)
        
        # Keep adding requirements until we reach the available hours
        adjusted_requirements = []
        current_hours = 0
        
        for req in sorted_requirements:
            req_hours = req.get("estimated_hours", 2.0)
            
            if current_hours + req_hours <= available_hours:
                # Add this requirement
                adjusted_requirements.append(req)
                current_hours += req_hours
            else:
                # Skip this requirement
                logger.debug(f"Skipping requirement: {req.get('title')}")
        
        logger.info(f"Adjusted requirements: {len(adjusted_requirements)} of {len(learning_requirements)}")
        return adjusted_requirements
    
    def _generate_weekly_plan(self, 
                            learning_requirements: List[Dict[str, Any]],
                            start_date: datetime,
                            timeframe_weeks: int,
                            hours_per_week: float,
                            skill_level: str) -> List[Dict[str, Any]]:
        """
        Generate a weekly plan based on learning requirements.
        
        Args:
            learning_requirements (List[Dict[str, Any]]): List of learning requirements
            start_date (datetime): Start date
            timeframe_weeks (int): Timeframe in weeks
            hours_per_week (float): Available hours per week
            skill_level (str): Current skill level
            
        Returns:
            List[Dict[str, Any]]: Weekly plan
        """
        logger.debug("Generating weekly plan")
        
        # Create a dependency graph
        dependency_graph = self._create_dependency_graph(learning_requirements)
        
        # Topologically sort requirements based on dependencies
        sorted_requirements = self._topological_sort(learning_requirements, dependency_graph)
        
        # Distribute requirements across weeks
        weekly_plan = []
        current_week = 1
        current_week_hours = 0
        current_week_requirements = []
        
        for req in sorted_requirements:
            req_hours = req.get("estimated_hours", 0)
            
            # Adjust hours based on skill level
            if req_hours == 0:
                # Use default estimates if not provided
                req_type = req.get("type", "concept")
                req_hours = self.default_effort_estimates.get(skill_level, {}).get(req_type, 2.0)
            elif skill_level == "intermediate":
                req_hours *= 0.8  # 20% faster for intermediate
            elif skill_level == "advanced":
                req_hours *= 0.6  # 40% faster for advanced
            
            # Check if this requirement fits in the current week
            if current_week_hours + req_hours <= hours_per_week:
                # Add to current week
                current_week_requirements.append({
                    "id": req.get("id"),
                    "title": req.get("title"),
                    "type": req.get("type"),
                    "hours": req_hours
                })
                current_week_hours += req_hours
            else:
                # Start a new week
                if current_week_requirements:
                    weekly_plan.append({
                        "week": current_week,
                        "start_date": (start_date + timedelta(weeks=current_week-1)).isoformat(),
                        "end_date": (start_date + timedelta(weeks=current_week)).isoformat(),
                        "total_hours": current_week_hours,
                        "requirements": current_week_requirements
                    })
                
                current_week += 1
                current_week_hours = req_hours
                current_week_requirements = [{
                    "id": req.get("id"),
                    "title": req.get("title"),
                    "type": req.get("type"),
                    "hours": req_hours
                }]
        
        # Add the last week if not empty
        if current_week_requirements:
            weekly_plan.append({
                "week": current_week,
                "start_date": (start_date + timedelta(weeks=current_week-1)).isoformat(),
                "end_date": (start_date + timedelta(weeks=current_week)).isoformat(),
                "total_hours": current_week_hours,
                "requirements": current_week_requirements
            })
        
        # Fill remaining weeks with revision if needed
        while current_week < timeframe_weeks:
            current_week += 1
            weekly_plan.append({
                "week": current_week,
                "start_date": (start_date + timedelta(weeks=current_week-1)).isoformat(),
                "end_date": (start_date + timedelta(weeks=current_week)).isoformat(),
                "total_hours": 0,
                "requirements": [],
                "revision": True
            })
        
        return weekly_plan
    
    def _create_dependency_graph(self, learning_requirements: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Create a dependency graph from learning requirements.
        
        Args:
            learning_requirements (List[Dict[str, Any]]): List of learning requirements
            
        Returns:
            Dict[str, List[str]]: Dependency graph
        """
        # Create a mapping of requirement IDs to their prerequisites
        dependency_graph = {}
        
        for req in learning_requirements:
            req_id = req.get("id")
            prerequisites = req.get("prerequisites", [])
            dependency_graph[req_id] = prerequisites
        
        return dependency_graph
    
    def _topological_sort(self, 
                        learning_requirements: List[Dict[str, Any]], 
                        dependency_graph: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Topologically sort learning requirements based on dependencies.
        
        Args:
            learning_requirements (List[Dict[str, Any]]): List of learning requirements
            dependency_graph (Dict[str, List[str]]): Dependency graph
            
        Returns:
            List[Dict[str, Any]]: Sorted learning requirements
        """
        # Create a mapping of requirement IDs to requirements
        req_map = {req.get("id"): req for req in learning_requirements}
        
        # Initialize variables for topological sort
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(req_id):
            if req_id in temp_visited:
                # Cyclic dependency detected
                logger.warning(f"Cyclic dependency detected for {req_id}")
                return
            
            if req_id in visited:
                return
            
            temp_visited.add(req_id)
            
            # Visit prerequisites
            for prereq_id in dependency_graph.get(req_id, []):
                visit(prereq_id)
            
            temp_visited.remove(req_id)
            visited.add(req_id)
            order.append(req_id)
        
        # Visit all requirements
        for req_id in dependency_graph:
            if req_id not in visited:
                visit(req_id)
        
        # Convert the order of IDs to the order of requirements
        sorted_requirements = [req_map.get(req_id) for req_id in order if req_id in req_map]
        
        return sorted_requirements
    
    def _generate_milestones(self, 
                           learning_requirements: List[Dict[str, Any]],
                           start_date: datetime,
                           timeframe_weeks: int) -> List[Dict[str, Any]]:
        """
        Generate milestones based on learning requirements.
        
        Args:
            learning_requirements (List[Dict[str, Any]]): List of learning requirements
            start_date (datetime): Start date
            timeframe_weeks (int): Timeframe in weeks
            
        Returns:
            List[Dict[str, Any]]: List of milestones
        """
        logger.debug("Generating milestones")
        
        milestones = []
        
        # Group requirements by type
        concepts = [req for req in learning_requirements if req.get("type") == "concept"]
        skills = [req for req in learning_requirements if req.get("type") == "skill"]
        projects = [req for req in learning_requirements if req.get("type") == "project"]
        
        # Create milestones for completing all concepts
        if concepts:
            concepts_milestone = {
                "id": str(uuid.uuid4()),
                "title": "Complete All Concept Learning",
                "description": f"Complete learning all {len(concepts)} concepts",
                "date": (start_date + timedelta(weeks=timeframe_weeks // 3)).isoformat(),
                "requirements": [req.get("id") for req in concepts],
                "type": "concept"
            }
            milestones.append(concepts_milestone)
        
        # Create milestones for completing all skills
        if skills:
            skills_milestone = {
                "id": str(uuid.uuid4()),
                "title": "Master All Skills",
                "description": f"Master all {len(skills)} skills",
                "date": (start_date + timedelta(weeks=timeframe_weeks * 2 // 3)).isoformat(),
                "requirements": [req.get("id") for req in skills],
                "type": "skill"
            }
            milestones.append(skills_milestone)
        
        # Create milestones for completing all projects
        if projects:
            projects_milestone = {
                "id": str(uuid.uuid4()),
                "title": "Complete All Projects",
                "description": f"Complete all {len(projects)} projects",
                "date": (start_date + timedelta(weeks=timeframe_weeks - 1)).isoformat(),
                "requirements": [req.get("id") for req in projects],
                "type": "project"
            }
            milestones.append(projects_milestone)
        
        # Create a final milestone
        final_milestone = {
            "id": str(uuid.uuid4()),
            "title": "Complete Learning Roadmap",
            "description": "Complete the entire learning roadmap",
            "date": (start_date + timedelta(weeks=timeframe_weeks)).isoformat(),
            "requirements": [req.get("id") for req in learning_requirements],
            "type": "final"
        }
        milestones.append(final_milestone)
        
        return milestones
    
    def _generate_calendar_events(self, 
                                weekly_plan: List[Dict[str, Any]],
                                milestones: List[Dict[str, Any]],
                                start_date: datetime) -> List[Dict[str, Any]]:
        """
        Generate calendar events based on the weekly plan and milestones.
        
        Args:
            weekly_plan (List[Dict[str, Any]]): Weekly plan
            milestones (List[Dict[str, Any]]): List of milestones
            start_date (datetime): Start date
            
        Returns:
            List[Dict[str, Any]]: List of calendar events
        """
        logger.debug("Generating calendar events")
        
        calendar_events = []
        
        # Generate events for weekly plan
        for week in weekly_plan:
            week_num = week.get("week", 0)
            week_start = start_date + timedelta(weeks=week_num - 1)
            
            # Create events for each requirement in the week
            for req in week.get("requirements", []):
                req_id = req.get("id")
                req_title = req.get("title")
                req_hours = req.get("hours", 0)
                
                # Create multiple events for requirements that take more than 2 hours
                if req_hours > 2:
                    num_sessions = int(req_hours / 2) + (1 if req_hours % 2 > 0 else 0)
                    hours_per_session = req_hours / num_sessions
                    
                    for i in range(num_sessions):
                        # Distribute sessions throughout the week
                        day_offset = i % 7
                        session_date = week_start + timedelta(days=day_offset)
                        
                        calendar_events.append({
                            "id": str(uuid.uuid4()),
                            "title": f"Study: {req_title} (Session {i+1}/{num_sessions})",
                            "description": f"Study session for {req_title}",
                            "start_date": session_date.isoformat(),
                            "end_date": (session_date + timedelta(hours=hours_per_session)).isoformat(),
                            "requirement_id": req_id,
                            "type": "study"
                        })
                else:
                    # Create a single event for short requirements
                    session_date = week_start + timedelta(days=0)  # Start on Monday
                    
                    calendar_events.append({
                        "id": str(uuid.uuid4()),
                        "title": f"Study: {req_title}",
                        "description": f"Study session for {req_title}",
                        "start_date": session_date.isoformat(),
                        "end_date": (session_date + timedelta(hours=req_hours)).isoformat(),
                        "requirement_id": req_id,
                        "type": "study"
                    })
            
            # Add a revision session at the end of the week
            if week.get("revision", False) or week_num % 4 == 0:  # Every 4 weeks or revision week
                revision_date = week_start + timedelta(days=6)  # Sunday
                
                calendar_events.append({
                    "id": str(uuid.uuid4()),
                    "title": "Weekly Revision",
                    "description": "Review and consolidate learning from previous weeks",
                    "start_date": revision_date.isoformat(),
                    "end_date": (revision_date + timedelta(hours=2)).isoformat(),
                    "type": "revision"
                })
        
        # Generate events for milestones
        for milestone in milestones:
            milestone_date = datetime.fromisoformat(milestone.get("date"))
            
            calendar_events.append({
                "id": str(uuid.uuid4()),
                "title": milestone.get("title"),
                "description": milestone.get("description"),
                "start_date": milestone_date.isoformat(),
                "end_date": (milestone_date + timedelta(hours=1)).isoformat(),
                "type": "milestone"
            })
        
        return calendar_events
    
    def _save_roadmap(self, roadmap: Dict[str, Any], output_dir: str) -> None:
        """
        Save the roadmap to a file.
        
        Args:
            roadmap (Dict[str, Any]): Generated roadmap
            output_dir (str): Output directory
        """
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        goal = roadmap.get("goal", "roadmap")
        safe_goal = "".join(c if c.isalnum() or c in " .-" else "_" for c in goal)
        safe_goal = safe_goal.strip().replace(" ", "_")
        
        filename = f"{safe_goal}_roadmap.json"
        file_path = os.path.join(output_dir, filename)
        
        # Save roadmap to file
        with open(file_path, "w") as f:
            json.dump(roadmap, f, indent=2)
        
        logger.info(f"Roadmap saved to {file_path}")
        
        # Generate calendar export if needed
        calendar_path = os.path.join(output_dir, f"{safe_goal}_calendar.ics")
        self._export_to_ical(roadmap, calendar_path)
    
    def _export_to_ical(self, roadmap: Dict[str, Any], output_path: str) -> None:
        """
        Export the roadmap to an iCalendar file.
        
        Args:
            roadmap (Dict[str, Any]): Generated roadmap
            output_path (str): Output file path
        """
        logger.debug(f"Exporting roadmap to iCalendar: {output_path}")
        
        try:
            # This is a simplified implementation
            # In a real implementation, you would use a library like icalendar
            
            # Create a basic iCalendar file
            ical_content = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "PRODID:-//AI Note System//Roadmap Generator//EN",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH"
            ]
            
            # Add events
            for event in roadmap.get("calendar_events", []):
                event_id = event.get("id", str(uuid.uuid4()))
                event_title = event.get("title", "Event")
                event_description = event.get("description", "")
                event_start = event.get("start_date", "")
                event_end = event.get("end_date", "")
                
                # Convert ISO format to iCalendar format
                try:
                    start_dt = datetime.fromisoformat(event_start)
                    end_dt = datetime.fromisoformat(event_end)
                    
                    start_str = start_dt.strftime("%Y%m%dT%H%M%SZ")
                    end_str = end_dt.strftime("%Y%m%dT%H%M%SZ")
                    
                    ical_content.extend([
                        "BEGIN:VEVENT",
                        f"UID:{event_id}",
                        f"SUMMARY:{event_title}",
                        f"DESCRIPTION:{event_description}",
                        f"DTSTART:{start_str}",
                        f"DTEND:{end_str}",
                        "END:VEVENT"
                    ])
                except Exception as e:
                    logger.error(f"Error formatting event date: {e}")
            
            # Close the calendar
            ical_content.append("END:VCALENDAR")
            
            # Write to file
            with open(output_path, "w") as f:
                f.write("\r\n".join(ical_content))
            
            logger.info(f"Calendar exported to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting to iCalendar: {e}")

# Command-line interface
def main():
    """
    Command-line interface for the Goal Roadmap Generator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Goal Roadmap Generator")
    parser.add_argument("--goal", required=True, help="Learning goal")
    parser.add_argument("--weeks", type=int, default=12, help="Timeframe in weeks")
    parser.add_argument("--level", default="beginner", choices=["beginner", "intermediate", "advanced"], help="Skill level")
    parser.add_argument("--hours", type=float, default=10.0, help="Available hours per week")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--no-projects", action="store_true", help="Exclude projects")
    parser.add_argument("--no-assessments", action="store_true", help="Exclude assessments")
    parser.add_argument("--output", default="roadmaps", help="Output directory")
    
    args = parser.parse_args()
    
    try:
        # Parse start date
        start_date = None
        if args.start_date:
            start_date = datetime.fromisoformat(args.start_date)
        
        # Create generator
        generator = GoalRoadmapGenerator()
        
        # Generate roadmap
        roadmap = generator.generate_roadmap(
            goal=args.goal,
            timeframe_weeks=args.weeks,
            skill_level=args.level,
            available_hours_per_week=args.hours,
            start_date=start_date,
            include_projects=not args.no_projects,
            include_assessments=not args.no_assessments,
            output_dir=args.output
        )
        
        # Print summary
        print(f"\nRoadmap Summary for: {args.goal}")
        print(f"{'=' * 40}")
        print(f"Timeframe: {args.weeks} weeks")
        print(f"Skill Level: {args.level}")
        print(f"Available Hours: {args.hours} per week")
        print(f"Total Learning Requirements: {len(roadmap.get('learning_requirements', []))}")
        print(f"Estimated Total Hours: {roadmap.get('effort_estimate', {}).get('total_hours', 0):.1f}")
        print(f"Goal Achievable: {'Yes' if roadmap.get('achievable', False) else 'No'}")
        print(f"Weekly Plan: {len(roadmap.get('weekly_plan', []))} weeks")
        print(f"Milestones: {len(roadmap.get('milestones', []))}")
        print(f"Calendar Events: {len(roadmap.get('calendar_events', []))}")
        print(f"\nRoadmap saved to {args.output}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()