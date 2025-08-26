"""
Deep Project Integrator module for AI Note System.
Provides functionality to break down projects and map them to learning requirements.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.learning.deep_project_integrator")

class DeepProjectIntegrator:
    """
    Deep Project Integrator class for breaking down projects and mapping to knowledge.
    Maps project requirements to learning materials and tracks progress.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Deep Project Integrator.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        self.projects = {}
        
        logger.debug("Initialized DeepProjectIntegrator")
    
    def create_project(self, 
                      project_name: str,
                      project_description: str,
                      project_goals: List[str],
                      estimated_duration_weeks: int = 4,
                      difficulty_level: str = "intermediate") -> Dict[str, Any]:
        """
        Create a new project with basic information.
        
        Args:
            project_name (str): Name of the project
            project_description (str): Description of the project
            project_goals (List[str]): List of project goals
            estimated_duration_weeks (int): Estimated duration in weeks
            difficulty_level (str): Difficulty level (beginner, intermediate, advanced)
            
        Returns:
            Dict[str, Any]: Created project
        """
        project_id = f"proj_{len(self.projects) + 1}_{int(datetime.now().timestamp())}"
        
        project = {
            "id": project_id,
            "name": project_name,
            "description": project_description,
            "goals": project_goals,
            "created_at": datetime.now().isoformat(),
            "estimated_duration_weeks": estimated_duration_weeks,
            "difficulty_level": difficulty_level,
            "modules": [],
            "skills_required": [],
            "learning_checkpoints": [],
            "resources": [],
            "progress": {
                "status": "planning",
                "completion_percentage": 0,
                "modules_completed": 0
            }
        }
        
        self.projects[project_id] = project
        logger.info(f"Created project: {project_name} (ID: {project_id})")
        
        return project
    
    def break_down_project(self, 
                          project_id: str,
                          auto_generate: bool = True) -> Dict[str, Any]:
        """
        Break down a project into modules and components.
        
        Args:
            project_id (str): ID of the project
            auto_generate (bool): Whether to automatically generate modules
            
        Returns:
            Dict[str, Any]: Updated project with modules
        """
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return {"error": f"Project not found: {project_id}"}
        
        project = self.projects[project_id]
        
        # If auto-generate is enabled, generate modules based on project description
        if auto_generate:
            # This would typically use an LLM to generate modules
            # For now, we'll use a simple placeholder implementation
            project_description = project["description"]
            project_goals = project["goals"]
            
            # Simple module generation based on goals
            modules = []
            for i, goal in enumerate(project_goals):
                module_id = f"{project_id}_mod_{i+1}"
                module = {
                    "id": module_id,
                    "name": f"Module {i+1}: {goal[:30]}...",
                    "description": f"This module addresses the goal: {goal}",
                    "components": [
                        {
                            "id": f"{module_id}_comp_1",
                            "name": f"Research for {goal[:20]}...",
                            "description": "Research and gather information",
                            "estimated_hours": 4,
                            "status": "pending"
                        },
                        {
                            "id": f"{module_id}_comp_2",
                            "name": f"Implementation for {goal[:20]}...",
                            "description": "Implement the core functionality",
                            "estimated_hours": 8,
                            "status": "pending"
                        },
                        {
                            "id": f"{module_id}_comp_3",
                            "name": f"Testing for {goal[:20]}...",
                            "description": "Test and validate the implementation",
                            "estimated_hours": 4,
                            "status": "pending"
                        }
                    ],
                    "dependencies": [],
                    "estimated_hours": 16,
                    "status": "pending"
                }
                modules.append(module)
            
            # Add dependencies between modules
            for i in range(1, len(modules)):
                modules[i]["dependencies"].append(modules[i-1]["id"])
            
            project["modules"] = modules
        
        logger.info(f"Broke down project {project_id} into {len(project['modules'])} modules")
        return project
    
    def map_knowledge_to_project(self,
                               project_id: str,
                               notes: List[Dict[str, Any]],
                               auto_map: bool = True) -> Dict[str, Any]:
        """
        Map existing notes and knowledge to project requirements.
        
        Args:
            project_id (str): ID of the project
            notes (List[Dict[str, Any]]): List of notes to map
            auto_map (bool): Whether to automatically map notes to modules
            
        Returns:
            Dict[str, Any]: Knowledge mapping results
        """
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return {"error": f"Project not found: {project_id}"}
        
        project = self.projects[project_id]
        
        # Initialize knowledge mapping
        knowledge_mapping = {
            "project_id": project_id,
            "mapped_notes": [],
            "knowledge_gaps": [],
            "coverage_percentage": 0
        }
        
        # If no modules, break down the project first
        if not project["modules"]:
            self.break_down_project(project_id)
        
        # Extract skills required from modules
        skills_required = []
        for module in project["modules"]:
            # This would typically use an LLM to extract skills
            # For now, we'll use a simple placeholder implementation
            module_skills = [
                {
                    "name": f"Skill for {module['name'][:20]}...",
                    "description": f"Knowledge required for {module['name']}",
                    "level": "intermediate",
                    "module_id": module["id"]
                }
            ]
            skills_required.extend(module_skills)
        
        project["skills_required"] = skills_required
        
        # Map notes to skills
        mapped_notes = []
        for note in notes:
            # This would typically use embeddings or LLM to map notes to skills
            # For now, we'll use a simple placeholder implementation
            for skill in skills_required:
                # Simple keyword matching
                if any(keyword in note.get("content", "") for keyword in skill["name"].split()):
                    mapped_note = {
                        "note_id": note.get("id"),
                        "note_title": note.get("title"),
                        "skill_id": skill["name"],
                        "relevance_score": 0.8,  # Placeholder score
                        "module_id": skill["module_id"]
                    }
                    mapped_notes.append(mapped_note)
        
        knowledge_mapping["mapped_notes"] = mapped_notes
        
        # Identify knowledge gaps
        covered_skills = set(note["skill_id"] for note in mapped_notes)
        all_skills = set(skill["name"] for skill in skills_required)
        knowledge_gaps = list(all_skills - covered_skills)
        
        knowledge_mapping["knowledge_gaps"] = [
            {
                "skill_name": gap,
                "description": f"Missing knowledge for {gap}",
                "suggested_resources": []
            }
            for gap in knowledge_gaps
        ]
        
        # Calculate coverage percentage
        if all_skills:
            coverage_percentage = (len(covered_skills) / len(all_skills)) * 100
        else:
            coverage_percentage = 0
        
        knowledge_mapping["coverage_percentage"] = coverage_percentage
        
        logger.info(f"Mapped {len(mapped_notes)} notes to project {project_id}, identified {len(knowledge_gaps)} knowledge gaps")
        return knowledge_mapping
    
    def generate_learning_checkpoints(self,
                                    project_id: str,
                                    knowledge_mapping: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate learning checkpoints and micro-projects for mastery.
        
        Args:
            project_id (str): ID of the project
            knowledge_mapping (Dict[str, Any], optional): Knowledge mapping results
            
        Returns:
            List[Dict[str, Any]]: Generated learning checkpoints
        """
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return []
        
        project = self.projects[project_id]
        
        # If no knowledge mapping provided, generate it
        if knowledge_mapping is None:
            # This would typically use actual notes from the database
            # For now, we'll use an empty list as a placeholder
            knowledge_mapping = self.map_knowledge_to_project(project_id, [])
        
        # Generate checkpoints for each module
        checkpoints = []
        for module in project["modules"]:
            # Basic checkpoint for module completion
            module_checkpoint = {
                "id": f"{module['id']}_cp_1",
                "name": f"Complete {module['name']}",
                "description": f"Successfully complete all components of {module['name']}",
                "type": "module_completion",
                "module_id": module["id"],
                "criteria": [
                    f"All components of {module['name']} are completed",
                    f"Module functionality is tested and working"
                ],
                "status": "pending"
            }
            checkpoints.append(module_checkpoint)
            
            # Knowledge checkpoint for skills required
            skills_for_module = [s for s in project["skills_required"] if s["module_id"] == module["id"]]
            if skills_for_module:
                skill_checkpoint = {
                    "id": f"{module['id']}_cp_2",
                    "name": f"Master skills for {module['name']}",
                    "description": f"Demonstrate mastery of skills required for {module['name']}",
                    "type": "knowledge_mastery",
                    "module_id": module["id"],
                    "skills": [s["name"] for s in skills_for_module],
                    "assessment_method": "quiz",
                    "status": "pending"
                }
                checkpoints.append(skill_checkpoint)
            
            # Micro-project checkpoint
            micro_project = {
                "id": f"{module['id']}_cp_3",
                "name": f"Micro-project for {module['name']}",
                "description": f"Complete a small project demonstrating skills from {module['name']}",
                "type": "micro_project",
                "module_id": module["id"],
                "requirements": [
                    f"Implement a small feature using skills from {module['name']}",
                    "Document the implementation process",
                    "Reflect on challenges and solutions"
                ],
                "estimated_hours": 4,
                "status": "pending"
            }
            checkpoints.append(micro_project)
        
        # Add final project checkpoint
        final_checkpoint = {
            "id": f"{project_id}_final_cp",
            "name": f"Complete {project['name']}",
            "description": f"Successfully complete the entire project",
            "type": "project_completion",
            "criteria": [
                "All modules are completed",
                "Project meets all specified goals",
                "Project is documented and tested"
            ],
            "status": "pending"
        }
        checkpoints.append(final_checkpoint)
        
        # Update project with checkpoints
        project["learning_checkpoints"] = checkpoints
        
        logger.info(f"Generated {len(checkpoints)} learning checkpoints for project {project_id}")
        return checkpoints
    
    def recommend_resources(self,
                          project_id: str,
                          knowledge_gaps: Optional[List[Dict[str, Any]]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Recommend learning resources for project skills and knowledge gaps.
        
        Args:
            project_id (str): ID of the project
            knowledge_gaps (List[Dict[str, Any]], optional): List of identified knowledge gaps
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Recommended resources by category
        """
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return {"error": f"Project not found: {project_id}"}
        
        project = self.projects[project_id]
        
        # If no knowledge gaps provided, extract from project
        if knowledge_gaps is None:
            # Get knowledge mapping to extract gaps
            # This would typically use actual notes from the database
            # For now, we'll use an empty list as a placeholder
            mapping_result = self.map_knowledge_to_project(project_id, [])
            knowledge_gaps = mapping_result.get("knowledge_gaps", [])
        
        # Initialize resource categories
        resources = {
            "tutorials": [],
            "courses": [],
            "documentation": [],
            "books": [],
            "videos": [],
            "projects": []
        }
        
        # Generate recommendations for each knowledge gap
        for gap in knowledge_gaps:
            # This would typically use an LLM or recommendation system
            # For now, we'll use placeholder recommendations
            
            # Add a tutorial
            resources["tutorials"].append({
                "title": f"Tutorial on {gap['skill_name']}",
                "url": f"https://example.com/tutorials/{gap['skill_name'].lower().replace(' ', '-')}",
                "description": f"A comprehensive tutorial covering {gap['skill_name']}",
                "skill_id": gap['skill_name'],
                "difficulty": "intermediate",
                "estimated_hours": 2
            })
            
            # Add a course
            resources["courses"].append({
                "title": f"Course: Mastering {gap['skill_name']}",
                "url": f"https://example.com/courses/{gap['skill_name'].lower().replace(' ', '-')}",
                "description": f"An in-depth course on {gap['skill_name']}",
                "skill_id": gap['skill_name'],
                "difficulty": "intermediate",
                "estimated_hours": 10
            })
            
            # Add documentation
            resources["documentation"].append({
                "title": f"Official Documentation for {gap['skill_name']}",
                "url": f"https://example.com/docs/{gap['skill_name'].lower().replace(' ', '-')}",
                "description": f"Official documentation for {gap['skill_name']}",
                "skill_id": gap['skill_name'],
                "type": "reference"
            })
        
        # Update project with resources
        project["resources"] = [
            item for category in resources.values() for item in category
        ]
        
        logger.info(f"Recommended {sum(len(items) for items in resources.values())} resources for project {project_id}")
        return resources
    
    def track_project_progress(self,
                             project_id: str,
                             module_id: Optional[str] = None,
                             component_id: Optional[str] = None,
                             checkpoint_id: Optional[str] = None,
                             status: Optional[str] = None) -> Dict[str, Any]:
        """
        Track progress on project, modules, components, or checkpoints.
        
        Args:
            project_id (str): ID of the project
            module_id (str, optional): ID of the module to update
            component_id (str, optional): ID of the component to update
            checkpoint_id (str, optional): ID of the checkpoint to update
            status (str, optional): New status (pending, in_progress, completed)
            
        Returns:
            Dict[str, Any]: Updated project progress
        """
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return {"error": f"Project not found: {project_id}"}
        
        project = self.projects[project_id]
        
        # Update module status if specified
        if module_id:
            module_found = False
            for module in project["modules"]:
                if module["id"] == module_id:
                    if status:
                        module["status"] = status
                    module_found = True
                    
                    # Update component status if specified
                    if component_id:
                        component_found = False
                        for component in module["components"]:
                            if component["id"] == component_id:
                                if status:
                                    component["status"] = status
                                component_found = True
                                break
                        
                        if not component_found:
                            logger.warning(f"Component not found: {component_id}")
                    break
            
            if not module_found:
                logger.warning(f"Module not found: {module_id}")
        
        # Update checkpoint status if specified
        if checkpoint_id:
            checkpoint_found = False
            for checkpoint in project["learning_checkpoints"]:
                if checkpoint["id"] == checkpoint_id:
                    if status:
                        checkpoint["status"] = status
                    checkpoint_found = True
                    break
            
            if not checkpoint_found:
                logger.warning(f"Checkpoint not found: {checkpoint_id}")
        
        # Recalculate project progress
        self._recalculate_project_progress(project_id)
        
        logger.info(f"Updated progress for project {project_id}")
        return project["progress"]
    
    def _recalculate_project_progress(self, project_id: str) -> Dict[str, Any]:
        """
        Recalculate project progress based on modules and checkpoints.
        
        Args:
            project_id (str): ID of the project
            
        Returns:
            Dict[str, Any]: Updated progress
        """
        project = self.projects[project_id]
        
        # Count completed modules
        total_modules = len(project["modules"])
        completed_modules = sum(1 for m in project["modules"] if m["status"] == "completed")
        
        # Count completed components
        total_components = sum(len(m["components"]) for m in project["modules"])
        completed_components = sum(
            sum(1 for c in m["components"] if c["status"] == "completed")
            for m in project["modules"]
        )
        
        # Count completed checkpoints
        total_checkpoints = len(project["learning_checkpoints"])
        completed_checkpoints = sum(1 for c in project["learning_checkpoints"] if c["status"] == "completed")
        
        # Calculate overall completion percentage
        if total_modules > 0 and total_components > 0 and total_checkpoints > 0:
            module_weight = 0.4
            component_weight = 0.4
            checkpoint_weight = 0.2
            
            module_completion = (completed_modules / total_modules) if total_modules > 0 else 0
            component_completion = (completed_components / total_components) if total_components > 0 else 0
            checkpoint_completion = (completed_checkpoints / total_checkpoints) if total_checkpoints > 0 else 0
            
            completion_percentage = (
                module_weight * module_completion +
                component_weight * component_completion +
                checkpoint_weight * checkpoint_completion
            ) * 100
        else:
            completion_percentage = 0
        
        # Determine project status
        if completion_percentage == 0:
            status = "planning"
        elif completion_percentage < 100:
            status = "in_progress"
        else:
            status = "completed"
        
        # Update progress
        project["progress"] = {
            "status": status,
            "completion_percentage": round(completion_percentage, 2),
            "modules_completed": completed_modules,
            "total_modules": total_modules,
            "components_completed": completed_components,
            "total_components": total_components,
            "checkpoints_completed": completed_checkpoints,
            "total_checkpoints": total_checkpoints,
            "last_updated": datetime.now().isoformat()
        }
        
        return project["progress"]
    
    def export_project_plan(self, project_id: str, format: str = "json") -> Dict[str, Any]:
        """
        Export project plan in specified format.
        
        Args:
            project_id (str): ID of the project
            format (str): Export format (json, markdown)
            
        Returns:
            Dict[str, Any]: Export result
        """
        if project_id not in self.projects:
            logger.error(f"Project not found: {project_id}")
            return {"error": f"Project not found: {project_id}"}
        
        project = self.projects[project_id]
        
        if format == "json":
            # Return project as JSON
            return {
                "success": True,
                "format": "json",
                "data": project
            }
        elif format == "markdown":
            # Generate markdown representation
            markdown = f"# {project['name']}\n\n"
            markdown += f"## Description\n{project['description']}\n\n"
            
            markdown += "## Goals\n"
            for goal in project['goals']:
                markdown += f"- {goal}\n"
            markdown += "\n"
            
            markdown += "## Modules\n"
            for module in project['modules']:
                markdown += f"### {module['name']}\n"
                markdown += f"{module['description']}\n\n"
                
                markdown += "#### Components\n"
                for component in module['components']:
                    markdown += f"- **{component['name']}**: {component['description']} ({component['status']})\n"
                markdown += "\n"
            
            markdown += "## Learning Checkpoints\n"
            for checkpoint in project['learning_checkpoints']:
                markdown += f"### {checkpoint['name']}\n"
                markdown += f"{checkpoint['description']}\n\n"
                
                if "criteria" in checkpoint:
                    markdown += "#### Criteria\n"
                    for criterion in checkpoint['criteria']:
                        markdown += f"- {criterion}\n"
                    markdown += "\n"
            
            markdown += "## Progress\n"
            progress = project['progress']
            markdown += f"- **Status**: {progress['status']}\n"
            markdown += f"- **Completion**: {progress['completion_percentage']}%\n"
            
            return {
                "success": True,
                "format": "markdown",
                "data": markdown
            }
        else:
            return {
                "error": f"Unsupported format: {format}",
                "supported_formats": ["json", "markdown"]
            }
    
    def save_projects(self, filepath: str) -> bool:
        """
        Save all projects to a file.
        
        Args:
            filepath (str): Path to save the projects
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Convert datetime objects to strings
            serializable_projects = {}
            for project_id, project in self.projects.items():
                serializable_project = json.loads(json.dumps(project))
                serializable_projects[project_id] = serializable_project
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(serializable_projects, f, indent=2)
            
            logger.info(f"Saved {len(self.projects)} projects to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving projects: {str(e)}")
            return False
    
    def load_projects(self, filepath: str) -> bool:
        """
        Load projects from a file.
        
        Args:
            filepath (str): Path to the projects file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                self.projects = json.load(f)
            
            logger.info(f"Loaded {len(self.projects)} projects from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")
            return False