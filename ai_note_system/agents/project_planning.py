"""
Multi-Agent Cooperative Project Planning module for AI Note System.
Deploys multiple specialized agents to generate project execution plans.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.agents.project_planning")

# Import required modules
from ..api.llm_interface import get_llm_interface
from ..database.db_manager import DatabaseManager

class ProjectPlanningCoordinator:
    """
    Coordinates multiple specialized agents to generate project execution plans.
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        db_manager: Optional[DatabaseManager] = None,
        llm_provider: str = "openai",
        llm_model: str = "gpt-4"
    ):
        """
        Initialize the Project Planning Coordinator.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            db_manager (DatabaseManager, optional): Database manager instance
            llm_provider (str): LLM provider to use for agents
            llm_model (str): LLM model to use for agents
        """
        self.config = config
        self.db_manager = db_manager
        
        # Initialize LLM interface
        self.llm = get_llm_interface(llm_provider, model=llm_model)
        
        # Initialize specialized agents
        self.roadmapper_agent = RoadmapperAgent(config, self.llm)
        self.resource_scout_agent = ResourceScoutAgent(config, self.llm)
        self.test_builder_agent = TestBuilderAgent(config, self.llm)
        self.debugging_agent = DebuggingAgent(config, self.llm)
        
        logger.info("Initialized Project Planning Coordinator")
    
    def generate_project_plan(
        self,
        project_name: str,
        project_description: str,
        project_goals: List[str],
        project_constraints: Optional[List[str]] = None,
        project_timeline: Optional[str] = None,
        project_skills: Optional[List[str]] = None,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive project execution plan.
        
        Args:
            project_name (str): Name of the project
            project_description (str): Description of the project
            project_goals (List[str]): List of project goals
            project_constraints (List[str], optional): List of project constraints
            project_timeline (str, optional): Timeline for the project
            project_skills (List[str], optional): List of skills available for the project
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Comprehensive project execution plan
        """
        logger.info(f"Generating project plan for: {project_name}")
        
        # Create project context
        project_context = {
            "name": project_name,
            "description": project_description,
            "goals": project_goals,
            "constraints": project_constraints or [],
            "timeline": project_timeline,
            "skills": project_skills or [],
            "timestamp": datetime.now().isoformat()
        }
        
        if verbose:
            print(f"Generating project plan for: {project_name}")
            print("Step 1: Breaking down project milestones...")
        
        # Step 1: Use Roadmapper Agent to break down project milestones
        milestones = self.roadmapper_agent.generate_milestones(
            project_context=project_context,
            verbose=verbose
        )
        
        if verbose:
            print("Step 2: Finding resources for each milestone...")
        
        # Step 2: Use Resource Scout Agent to find resources for each milestone
        resources = self.resource_scout_agent.find_resources(
            project_context=project_context,
            milestones=milestones,
            verbose=verbose
        )
        
        if verbose:
            print("Step 3: Generating test cases...")
        
        # Step 3: Use Test Builder Agent to generate test cases
        test_cases = self.test_builder_agent.generate_test_cases(
            project_context=project_context,
            milestones=milestones,
            verbose=verbose
        )
        
        if verbose:
            print("Step 4: Predicting common pitfalls...")
        
        # Step 4: Use Debugging Agent to predict common pitfalls
        pitfalls = self.debugging_agent.predict_pitfalls(
            project_context=project_context,
            milestones=milestones,
            verbose=verbose
        )
        
        if verbose:
            print("Step 5: Generating comprehensive project execution plan...")
        
        # Step 5: Combine all outputs into a comprehensive project execution plan
        project_plan = self._generate_execution_plan(
            project_context=project_context,
            milestones=milestones,
            resources=resources,
            test_cases=test_cases,
            pitfalls=pitfalls,
            verbose=verbose
        )
        
        # Step 6: Save project plan to database if db_manager is available
        if self.db_manager:
            self._save_project_plan(project_plan)
        
        if verbose:
            print("Project plan generation completed!")
        
        return project_plan
    
    def _generate_execution_plan(
        self,
        project_context: Dict[str, Any],
        milestones: Dict[str, Any],
        resources: Dict[str, Any],
        test_cases: Dict[str, Any],
        pitfalls: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive project execution plan.
        
        Args:
            project_context (Dict[str, Any]): Project context
            milestones (Dict[str, Any]): Milestones from Roadmapper Agent
            resources (Dict[str, Any]): Resources from Resource Scout Agent
            test_cases (Dict[str, Any]): Test cases from Test Builder Agent
            pitfalls (Dict[str, Any]): Pitfalls from Debugging Agent
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Comprehensive project execution plan
        """
        # Create execution plan
        execution_plan = {
            "project": project_context,
            "milestones": milestones,
            "resources": resources,
            "test_cases": test_cases,
            "pitfalls": pitfalls,
            "generated_at": datetime.now().isoformat()
        }
        
        # Use LLM to generate executive summary
        execution_plan["executive_summary"] = self._generate_executive_summary(execution_plan)
        
        # Use LLM to generate recommendations
        execution_plan["recommendations"] = self._generate_recommendations(execution_plan)
        
        return execution_plan
    
    def _generate_executive_summary(self, execution_plan: Dict[str, Any]) -> str:
        """
        Generate an executive summary of the project execution plan.
        
        Args:
            execution_plan (Dict[str, Any]): Project execution plan
            
        Returns:
            str: Executive summary
        """
        # Create prompt for executive summary
        prompt = f"""
        Generate a concise executive summary for the following project execution plan:
        
        Project: {execution_plan['project']['name']}
        Description: {execution_plan['project']['description']}
        Goals: {', '.join(execution_plan['project']['goals'])}
        
        The plan includes {len(execution_plan['milestones'].get('milestones', []))} milestones, 
        {len(execution_plan['resources'].get('resources', []))} resources, 
        {len(execution_plan['test_cases'].get('test_cases', []))} test cases, and 
        {len(execution_plan['pitfalls'].get('pitfalls', []))} potential pitfalls.
        
        The executive summary should be 3-4 paragraphs and highlight the key aspects of the plan,
        including the approach, timeline, key resources, and critical success factors.
        """
        
        # Generate executive summary
        try:
            summary = self.llm.generate_text(
                prompt=prompt,
                temperature=0.5,
                max_tokens=500
            )
            return summary
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "Executive summary generation failed."
    
    def _generate_recommendations(self, execution_plan: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations for the project execution plan.
        
        Args:
            execution_plan (Dict[str, Any]): Project execution plan
            
        Returns:
            List[str]: List of recommendations
        """
        # Create prompt for recommendations
        prompt = f"""
        Generate a list of 5-7 specific recommendations for the following project execution plan:
        
        Project: {execution_plan['project']['name']}
        Description: {execution_plan['project']['description']}
        Goals: {', '.join(execution_plan['project']['goals'])}
        
        Key milestones:
        {json.dumps(execution_plan['milestones'].get('milestones', [])[:3], indent=2)}
        
        Key pitfalls:
        {json.dumps(execution_plan['pitfalls'].get('pitfalls', [])[:3], indent=2)}
        
        The recommendations should be actionable, specific, and focused on ensuring project success.
        Each recommendation should be 1-2 sentences.
        """
        
        # Generate recommendations
        try:
            recommendations_text = self.llm.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse recommendations into a list
            recommendations = []
            for line in recommendations_text.split("\n"):
                line = line.strip()
                if line and (line.startswith("-") or line.startswith("*") or 
                           (line[0].isdigit() and line[1:3] in [". ", ") "])):
                    # Remove leading markers
                    recommendation = line[2:] if line.startswith(("- ", "* ")) else line[line.index(" ")+1:]
                    recommendations.append(recommendation)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Recommendations generation failed."]
    
    def _save_project_plan(self, project_plan: Dict[str, Any]) -> int:
        """
        Save project plan to database.
        
        Args:
            project_plan (Dict[str, Any]): Project execution plan
            
        Returns:
            int: ID of the saved project plan
        """
        try:
            # Check if project_plans table exists, create if not
            self.db_manager.cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                plan_data TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            ''')
            
            # Insert project plan
            self.db_manager.cursor.execute('''
            INSERT INTO project_plans (
                name, description, plan_data, timestamp
            ) VALUES (?, ?, ?, ?)
            ''', (
                project_plan['project']['name'],
                project_plan['project']['description'],
                json.dumps(project_plan),
                datetime.now().isoformat()
            ))
            
            self.db_manager.conn.commit()
            plan_id = self.db_manager.cursor.lastrowid
            
            logger.info(f"Saved project plan with ID {plan_id}: {project_plan['project']['name']}")
            return plan_id
            
        except Exception as e:
            logger.error(f"Error saving project plan: {e}")
            return -1


class RoadmapperAgent:
    """
    Agent that breaks down project milestones.
    """
    
    def __init__(self, config: Dict[str, Any], llm):
        """
        Initialize the Roadmapper Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            llm: LLM interface
        """
        self.config = config
        self.llm = llm
        
        logger.info("Initialized Roadmapper Agent")
    
    def generate_milestones(
        self,
        project_context: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Generate milestones for a project.
        
        Args:
            project_context (Dict[str, Any]): Project context
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Generated milestones
        """
        logger.info(f"Generating milestones for project: {project_context['name']}")
        
        # Define the schema for structured output
        milestones_schema = {
            "type": "object",
            "properties": {
                "milestones": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "estimated_duration": {"type": "string"},
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "deliverables": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "estimated_hours": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                },
                "timeline": {
                    "type": "object",
                    "properties": {
                        "estimated_total_duration": {"type": "string"},
                        "critical_path": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create prompt for milestone generation
        prompt = f"""
        Generate a detailed project roadmap with milestones for the following project:
        
        Project Name: {project_context['name']}
        Description: {project_context['description']}
        Goals: {', '.join(project_context['goals'])}
        Constraints: {', '.join(project_context['constraints'])}
        Timeline: {project_context['timeline'] or 'Not specified'}
        
        For each milestone, include:
        1. A unique ID (e.g., M1, M2, etc.)
        2. A clear name and description
        3. Estimated duration
        4. Dependencies on other milestones (if any)
        5. Deliverables
        6. Detailed tasks with estimated hours
        
        Also include an overall timeline with estimated total duration and critical path.
        
        The roadmap should be comprehensive, realistic, and aligned with the project goals.
        """
        
        try:
            # Generate structured milestones
            milestones = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=milestones_schema,
                temperature=0.4
            )
            
            if verbose:
                print(f"Generated {len(milestones.get('milestones', []))} milestones")
            
            # Add metadata
            milestones["generated_at"] = datetime.now().isoformat()
            milestones["project_name"] = project_context["name"]
            
            return milestones
            
        except Exception as e:
            logger.error(f"Error generating milestones: {e}")
            
            # Return empty milestones as fallback
            return {
                "milestones": [],
                "timeline": {
                    "estimated_total_duration": "Unknown",
                    "critical_path": []
                },
                "generated_at": datetime.now().isoformat(),
                "project_name": project_context["name"],
                "error": str(e)
            }


class ResourceScoutAgent:
    """
    Agent that finds resources for project milestones.
    """
    
    def __init__(self, config: Dict[str, Any], llm):
        """
        Initialize the Resource Scout Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            llm: LLM interface
        """
        self.config = config
        self.llm = llm
        
        logger.info("Initialized Resource Scout Agent")
    
    def find_resources(
        self,
        project_context: Dict[str, Any],
        milestones: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Find resources for project milestones.
        
        Args:
            project_context (Dict[str, Any]): Project context
            milestones (Dict[str, Any]): Project milestones
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Resources for project milestones
        """
        logger.info(f"Finding resources for project: {project_context['name']}")
        
        # Define the schema for structured output
        resources_schema = {
            "type": "object",
            "properties": {
                "resources": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "description": {"type": "string"},
                            "url": {"type": "string"},
                            "relevance": {"type": "string"},
                            "applicable_milestones": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "resource_categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "resource_ids": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
        
        # Create prompt for resource finding
        prompt = f"""
        Find and recommend resources for the following project and its milestones:
        
        Project Name: {project_context['name']}
        Description: {project_context['description']}
        Goals: {', '.join(project_context['goals'])}
        Skills Available: {', '.join(project_context['skills'])}
        
        Milestones:
        {json.dumps([{
            "id": m.get("id", ""),
            "name": m.get("name", ""),
            "description": m.get("description", ""),
            "deliverables": m.get("deliverables", [])
        } for m in milestones.get("milestones", [])], indent=2)}
        
        For each resource, include:
        1. A unique ID (e.g., R1, R2, etc.)
        2. A name and type (e.g., tutorial, documentation, library, tool, etc.)
        3. A description of the resource
        4. A URL (if applicable)
        5. Relevance to the project
        6. Applicable milestones (using milestone IDs)
        
        Also categorize resources by type.
        
        The resources should be specific, relevant, and high-quality.
        """
        
        try:
            # Generate structured resources
            resources = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=resources_schema,
                temperature=0.4
            )
            
            if verbose:
                print(f"Found {len(resources.get('resources', []))} resources")
            
            # Add metadata
            resources["generated_at"] = datetime.now().isoformat()
            resources["project_name"] = project_context["name"]
            
            return resources
            
        except Exception as e:
            logger.error(f"Error finding resources: {e}")
            
            # Return empty resources as fallback
            return {
                "resources": [],
                "resource_categories": [],
                "generated_at": datetime.now().isoformat(),
                "project_name": project_context["name"],
                "error": str(e)
            }


class TestBuilderAgent:
    """
    Agent that generates test cases for project milestones.
    """
    
    def __init__(self, config: Dict[str, Any], llm):
        """
        Initialize the Test Builder Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            llm: LLM interface
        """
        self.config = config
        self.llm = llm
        
        logger.info("Initialized Test Builder Agent")
    
    def generate_test_cases(
        self,
        project_context: Dict[str, Any],
        milestones: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Generate test cases for project milestones.
        
        Args:
            project_context (Dict[str, Any]): Project context
            milestones (Dict[str, Any]): Project milestones
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Test cases for project milestones
        """
        logger.info(f"Generating test cases for project: {project_context['name']}")
        
        # Define the schema for structured output
        test_cases_schema = {
            "type": "object",
            "properties": {
                "test_cases": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "type": {"type": "string"},
                            "milestone_id": {"type": "string"},
                            "preconditions": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "steps": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "expected_results": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "priority": {"type": "string"}
                        }
                    }
                },
                "test_coverage": {
                    "type": "object",
                    "properties": {
                        "milestone_coverage": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "milestone_id": {"type": "string"},
                                    "test_case_ids": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "coverage_percentage": {"type": "number"}
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Create prompt for test case generation
        prompt = f"""
        Generate comprehensive test cases for the following project and its milestones:
        
        Project Name: {project_context['name']}
        Description: {project_context['description']}
        Goals: {', '.join(project_context['goals'])}
        
        Milestones:
        {json.dumps([{
            "id": m.get("id", ""),
            "name": m.get("name", ""),
            "description": m.get("description", ""),
            "deliverables": m.get("deliverables", [])
        } for m in milestones.get("milestones", [])], indent=2)}
        
        For each test case, include:
        1. A unique ID (e.g., TC1, TC2, etc.)
        2. A name and description
        3. The type of test (e.g., functional, performance, security, etc.)
        4. The milestone it applies to (using milestone ID)
        5. Preconditions
        6. Test steps
        7. Expected results
        8. Priority (high, medium, low)
        
        Also include test coverage information for each milestone.
        
        The test cases should be comprehensive, specific, and focused on validating the deliverables.
        """
        
        try:
            # Generate structured test cases
            test_cases = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=test_cases_schema,
                temperature=0.4
            )
            
            if verbose:
                print(f"Generated {len(test_cases.get('test_cases', []))} test cases")
            
            # Add metadata
            test_cases["generated_at"] = datetime.now().isoformat()
            test_cases["project_name"] = project_context["name"]
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            
            # Return empty test cases as fallback
            return {
                "test_cases": [],
                "test_coverage": {
                    "milestone_coverage": []
                },
                "generated_at": datetime.now().isoformat(),
                "project_name": project_context["name"],
                "error": str(e)
            }


class DebuggingAgent:
    """
    Agent that predicts common pitfalls for project milestones.
    """
    
    def __init__(self, config: Dict[str, Any], llm):
        """
        Initialize the Debugging Agent.
        
        Args:
            config (Dict[str, Any]): Configuration dictionary
            llm: LLM interface
        """
        self.config = config
        self.llm = llm
        
        logger.info("Initialized Debugging Agent")
    
    def predict_pitfalls(
        self,
        project_context: Dict[str, Any],
        milestones: Dict[str, Any],
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Predict common pitfalls for project milestones.
        
        Args:
            project_context (Dict[str, Any]): Project context
            milestones (Dict[str, Any]): Project milestones
            verbose (bool): Whether to print verbose output
            
        Returns:
            Dict[str, Any]: Predicted pitfalls for project milestones
        """
        logger.info(f"Predicting pitfalls for project: {project_context['name']}")
        
        # Define the schema for structured output
        pitfalls_schema = {
            "type": "object",
            "properties": {
                "pitfalls": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "impact": {"type": "string"},
                            "likelihood": {"type": "string"},
                            "milestone_ids": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "prevention_strategies": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "mitigation_strategies": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "risk_assessment": {
                    "type": "object",
                    "properties": {
                        "high_risk_pitfalls": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "medium_risk_pitfalls": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "low_risk_pitfalls": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Create prompt for pitfall prediction
        prompt = f"""
        Predict common pitfalls and challenges for the following project and its milestones:
        
        Project Name: {project_context['name']}
        Description: {project_context['description']}
        Goals: {', '.join(project_context['goals'])}
        Constraints: {', '.join(project_context['constraints'])}
        
        Milestones:
        {json.dumps([{
            "id": m.get("id", ""),
            "name": m.get("name", ""),
            "description": m.get("description", ""),
            "dependencies": m.get("dependencies", []),
            "deliverables": m.get("deliverables", [])
        } for m in milestones.get("milestones", [])], indent=2)}
        
        For each pitfall, include:
        1. A unique ID (e.g., P1, P2, etc.)
        2. A name and description
        3. The potential impact
        4. The likelihood of occurrence (high, medium, low)
        5. The milestones it applies to (using milestone IDs)
        6. Prevention strategies
        7. Mitigation strategies if it occurs
        
        Also categorize pitfalls by risk level (high, medium, low).
        
        The pitfalls should be specific, realistic, and based on common challenges in similar projects.
        """
        
        try:
            # Generate structured pitfalls
            pitfalls = self.llm.generate_structured_output(
                prompt=prompt,
                output_schema=pitfalls_schema,
                temperature=0.4
            )
            
            if verbose:
                print(f"Predicted {len(pitfalls.get('pitfalls', []))} pitfalls")
            
            # Add metadata
            pitfalls["generated_at"] = datetime.now().isoformat()
            pitfalls["project_name"] = project_context["name"]
            
            return pitfalls
            
        except Exception as e:
            logger.error(f"Error predicting pitfalls: {e}")
            
            # Return empty pitfalls as fallback
            return {
                "pitfalls": [],
                "risk_assessment": {
                    "high_risk_pitfalls": [],
                    "medium_risk_pitfalls": [],
                    "low_risk_pitfalls": []
                },
                "generated_at": datetime.now().isoformat(),
                "project_name": project_context["name"],
                "error": str(e)
            }


def main():
    """
    Command-line interface for the Project Planning Coordinator.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Cooperative Project Planning")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--description", required=True, help="Project description")
    parser.add_argument("--goals", required=True, nargs="+", help="Project goals")
    parser.add_argument("--constraints", nargs="+", help="Project constraints")
    parser.add_argument("--timeline", help="Project timeline")
    parser.add_argument("--skills", nargs="+", help="Available skills")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("--llm", default="openai", help="LLM provider")
    parser.add_argument("--model", default="gpt-4", help="LLM model")
    
    args = parser.parse_args()
    
    # Initialize coordinator
    coordinator = ProjectPlanningCoordinator(
        config={},
        llm_provider=args.llm,
        llm_model=args.model
    )
    
    # Generate project plan
    project_plan = coordinator.generate_project_plan(
        project_name=args.name,
        project_description=args.description,
        project_goals=args.goals,
        project_constraints=args.constraints,
        project_timeline=args.timeline,
        project_skills=args.skills,
        verbose=args.verbose
    )
    
    # Save to file if output path provided
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(project_plan, f, indent=2)
        print(f"Project plan saved to {args.output}")
    else:
        # Print summary
        print("\nPROJECT EXECUTION PLAN")
        print("=" * 50)
        
        print(f"\nProject: {project_plan['project']['name']}")
        print(f"Description: {project_plan['project']['description']}")
        
        print("\nExecutive Summary:")
        print(project_plan['executive_summary'])
        
        print("\nMilestones:")
        for milestone in project_plan['milestones'].get('milestones', []):
            print(f"\n{milestone.get('id', '')}: {milestone.get('name', '')}")
            print(f"  Duration: {milestone.get('estimated_duration', '')}")
            print(f"  Dependencies: {', '.join(milestone.get('dependencies', []))}")
        
        print("\nKey Resources:")
        for resource in project_plan['resources'].get('resources', [])[:5]:
            print(f"\n{resource.get('id', '')}: {resource.get('name', '')}")
            print(f"  Type: {resource.get('type', '')}")
            print(f"  URL: {resource.get('url', '')}")
        
        print("\nKey Pitfalls:")
        for pitfall in project_plan['pitfalls'].get('pitfalls', [])[:5]:
            print(f"\n{pitfall.get('id', '')}: {pitfall.get('name', '')}")
            print(f"  Impact: {pitfall.get('impact', '')}")
            print(f"  Likelihood: {pitfall.get('likelihood', '')}")
        
        print("\nRecommendations:")
        for recommendation in project_plan.get('recommendations', []):
            print(f"- {recommendation}")


if __name__ == "__main__":
    main()