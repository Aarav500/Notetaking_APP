"""
Simulation Mode module for AI Note System.
Provides functionality to generate practical learning exercises and simulations.
"""

import os
import json
import logging
import random
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.learning.simulation_mode")

class SimulationMode:
    """
    Simulation Mode class for generating practical learning exercises.
    Creates mini-cases, simulation exercises, and real-world data interpretation tasks.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Simulation Mode.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Default simulation templates
        self.default_templates = {
            "mini_case": [
                "You are tasked with {task}. How would you approach this problem?",
                "A client has requested {request}. Design a solution that addresses their needs.",
                "Your team needs to {goal}. What strategy would you implement?"
            ],
            "debugging": [
                "You're debugging a {system_type} that {issue}. Identify potential causes and solutions.",
                "A {component} is producing {error}. How would you troubleshoot this issue?",
                "Your {application} is {behavior} when it should be {expected_behavior}. Find and fix the issue."
            ],
            "system_design": [
                "Design a system that can {requirement} with {constraint}.",
                "Create an architecture for {system_type} that optimizes for {optimization_goal}.",
                "Develop a {system_type} that handles {scenario} efficiently."
            ],
            "data_interpretation": [
                "Analyze the following {data_type} data and draw conclusions about {topic}.",
                "Interpret these {data_type} results and explain what they indicate about {phenomenon}.",
                "Review this {visualization_type} and explain the patterns you observe related to {topic}."
            ]
        }
        
        # Simulation history
        self.simulation_history = []
        
        logger.debug("Initialized SimulationMode")
    
    def generate_mini_case(self, 
                          topic: str,
                          difficulty: str = "intermediate",
                          context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a domain-specific mini-case for practical learning.
        
        Args:
            topic (str): The topic for the mini-case
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            context (Dict[str, Any], optional): Additional context for generation
            
        Returns:
            Dict[str, Any]: Generated mini-case
        """
        logger.info(f"Generating mini-case for topic: {topic}, difficulty: {difficulty}")
        
        # This would typically use an LLM to generate a case
        # For now, we'll use a template-based approach
        
        # Select a template
        templates = self.default_templates.get("mini_case", [])
        template = random.choice(templates)
        
        # Generate case details based on topic and difficulty
        if topic.lower() == "machine learning":
            if difficulty == "beginner":
                case_details = {
                    "task": "building a simple classification model for customer churn prediction",
                    "request": "a recommendation system for an e-commerce website",
                    "goal": "implement a basic sentiment analysis system for customer reviews"
                }
            elif difficulty == "advanced":
                case_details = {
                    "task": "designing a multi-modal deep learning system for medical image analysis",
                    "request": "an anomaly detection system for manufacturing defects that works in real-time",
                    "goal": "implement a reinforcement learning agent for optimizing energy consumption"
                }
            else:  # intermediate
                case_details = {
                    "task": "implementing a neural network for time series forecasting",
                    "request": "a clustering algorithm to segment customers based on behavior",
                    "goal": "build a model to detect fraudulent transactions with high precision"
                }
        elif topic.lower() == "web development":
            if difficulty == "beginner":
                case_details = {
                    "task": "creating a responsive landing page for a local business",
                    "request": "a simple contact form with validation",
                    "goal": "implement a basic user authentication system"
                }
            elif difficulty == "advanced":
                case_details = {
                    "task": "building a real-time collaborative editing platform",
                    "request": "a high-performance e-commerce site with microservices architecture",
                    "goal": "implement a progressive web app with offline capabilities"
                }
            else:  # intermediate
                case_details = {
                    "task": "creating a dashboard with interactive data visualizations",
                    "request": "a content management system with role-based access control",
                    "goal": "implement a RESTful API with proper authentication and rate limiting"
                }
        else:
            # Generic case details for other topics
            case_details = {
                "task": f"solving a complex problem related to {topic}",
                "request": f"a solution that addresses key challenges in {topic}",
                "goal": f"implement a system that demonstrates mastery of {topic} concepts"
            }
        
        # Format the template with appropriate details
        for key, value in case_details.items():
            if key in template:
                template = template.replace(f"{{{key}}}", value)
        
        # Create the mini-case
        mini_case = {
            "id": f"case_{int(datetime.now().timestamp())}",
            "type": "mini_case",
            "topic": topic,
            "difficulty": difficulty,
            "scenario": template,
            "created_at": datetime.now().isoformat(),
            "learning_objectives": [
                f"Apply {topic} concepts to a realistic scenario",
                "Develop problem-solving skills in a practical context",
                "Practice decision-making with constraints"
            ],
            "suggested_approach": "Analyze the problem, identify key requirements, develop a solution strategy, and outline implementation steps."
        }
        
        # Add to history
        self.simulation_history.append({
            "id": mini_case["id"],
            "type": "mini_case",
            "topic": topic,
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat()
        })
        
        return mini_case
    
    def generate_debugging_exercise(self,
                                  topic: str,
                                  difficulty: str = "intermediate",
                                  system_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a debugging exercise for practical problem-solving.
        
        Args:
            topic (str): The topic for the debugging exercise
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            system_type (str, optional): Type of system to debug
            
        Returns:
            Dict[str, Any]: Generated debugging exercise
        """
        logger.info(f"Generating debugging exercise for topic: {topic}, difficulty: {difficulty}")
        
        # Determine system type if not provided
        if not system_type:
            if "machine learning" in topic.lower() or "ml" in topic.lower() or "ai" in topic.lower():
                system_type = "machine learning model"
            elif "web" in topic.lower() or "frontend" in topic.lower() or "backend" in topic.lower():
                system_type = "web application"
            elif "database" in topic.lower() or "sql" in topic.lower():
                system_type = "database system"
            elif "network" in topic.lower():
                system_type = "network configuration"
            else:
                system_type = "software system"
        
        # Select a template
        templates = self.default_templates.get("debugging", [])
        template = random.choice(templates)
        
        # Generate debugging details based on topic and difficulty
        if "machine learning" in topic.lower() or "ml" in topic.lower():
            if difficulty == "beginner":
                debug_details = {
                    "system_type": "classification model",
                    "issue": "is underfitting the training data",
                    "component": "data preprocessing pipeline",
                    "error": "inconsistent results",
                    "application": "linear regression model",
                    "behavior": "producing negative predictions for positive-only outputs",
                    "expected_behavior": "producing values in the correct range"
                }
            elif difficulty == "advanced":
                debug_details = {
                    "system_type": "deep neural network",
                    "issue": "exhibits catastrophic forgetting during transfer learning",
                    "component": "attention mechanism",
                    "error": "gradient explosion",
                    "application": "reinforcement learning agent",
                    "behavior": "getting stuck in a local optimum",
                    "expected_behavior": "exploring the environment effectively"
                }
            else:  # intermediate
                debug_details = {
                    "system_type": "recommendation system",
                    "issue": "shows strong bias toward popular items",
                    "component": "feature extraction module",
                    "error": "high dimensionality issues",
                    "application": "clustering algorithm",
                    "behavior": "creating imbalanced clusters",
                    "expected_behavior": "creating well-balanced clusters"
                }
        elif "web" in topic.lower():
            if difficulty == "beginner":
                debug_details = {
                    "system_type": "static website",
                    "issue": "has layout issues on mobile devices",
                    "component": "contact form",
                    "error": "validation errors",
                    "application": "navigation menu",
                    "behavior": "not displaying correctly on small screens",
                    "expected_behavior": "being responsive on all devices"
                }
            elif difficulty == "advanced":
                debug_details = {
                    "system_type": "single-page application",
                    "issue": "has memory leaks causing performance degradation",
                    "component": "authentication service",
                    "error": "intermittent token validation failures",
                    "application": "real-time data dashboard",
                    "behavior": "showing stale data after long periods of use",
                    "expected_behavior": "consistently showing real-time updates"
                }
            else:  # intermediate
                debug_details = {
                    "system_type": "e-commerce platform",
                    "issue": "has inconsistent state between client and server",
                    "component": "shopping cart module",
                    "error": "race conditions during checkout",
                    "application": "user profile system",
                    "behavior": "losing user preferences after updates",
                    "expected_behavior": "maintaining user settings consistently"
                }
        else:
            # Generic debugging details for other topics
            debug_details = {
                "system_type": system_type,
                "issue": "is not functioning as expected",
                "component": f"{topic} module",
                "error": "unexpected behavior",
                "application": f"{topic} system",
                "behavior": "producing incorrect results",
                "expected_behavior": "working according to specifications"
            }
        
        # Format the template with appropriate details
        for key, value in debug_details.items():
            if key in template:
                template = template.replace(f"{{{key}}}", value)
        
        # Create the debugging exercise
        debugging_exercise = {
            "id": f"debug_{int(datetime.now().timestamp())}",
            "type": "debugging_exercise",
            "topic": topic,
            "difficulty": difficulty,
            "scenario": template,
            "created_at": datetime.now().isoformat(),
            "system_type": system_type,
            "learning_objectives": [
                "Practice systematic debugging approaches",
                f"Apply {topic} knowledge to identify root causes",
                "Develop solutions to fix technical issues"
            ],
            "hints": [
                "Start by reproducing the issue consistently",
                "Check for common pitfalls in this type of system",
                "Use appropriate diagnostic tools"
            ]
        }
        
        # Add to history
        self.simulation_history.append({
            "id": debugging_exercise["id"],
            "type": "debugging_exercise",
            "topic": topic,
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat()
        })
        
        return debugging_exercise
    
    def generate_system_design_challenge(self,
                                       topic: str,
                                       difficulty: str = "intermediate",
                                       constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a system design challenge for practical learning.
        
        Args:
            topic (str): The topic for the system design challenge
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            constraints (List[str], optional): List of design constraints
            
        Returns:
            Dict[str, Any]: Generated system design challenge
        """
        logger.info(f"Generating system design challenge for topic: {topic}, difficulty: {difficulty}")
        
        # Select a template
        templates = self.default_templates.get("system_design", [])
        template = random.choice(templates)
        
        # Default constraints if not provided
        if not constraints:
            constraints = [
                "scalability",
                "performance",
                "cost-effectiveness",
                "security",
                "maintainability"
            ]
        
        # Generate system design details based on topic and difficulty
        if "distributed" in topic.lower() or "cloud" in topic.lower():
            if difficulty == "beginner":
                design_details = {
                    "requirement": "store and retrieve user profiles",
                    "constraint": f"a focus on {random.choice(constraints)}",
                    "system_type": "cloud-based storage service",
                    "optimization_goal": "minimal latency",
                    "scenario": "sudden traffic spikes"
                }
            elif difficulty == "advanced":
                design_details = {
                    "requirement": "process millions of events per second with sub-second latency",
                    "constraint": f"strict {random.choice(constraints)} requirements",
                    "system_type": "globally distributed data processing pipeline",
                    "optimization_goal": "fault tolerance and consistency",
                    "scenario": "network partitions and node failures"
                }
            else:  # intermediate
                design_details = {
                    "requirement": "synchronize data across multiple regions",
                    "constraint": f"emphasis on {random.choice(constraints)}",
                    "system_type": "multi-region database system",
                    "optimization_goal": "consistency and availability",
                    "scenario": "regional outages"
                }
        elif "web" in topic.lower() or "frontend" in topic.lower() or "backend" in topic.lower():
            if difficulty == "beginner":
                design_details = {
                    "requirement": "allow users to create and share content",
                    "constraint": f"a focus on {random.choice(constraints)}",
                    "system_type": "content management system",
                    "optimization_goal": "ease of use",
                    "scenario": "content moderation"
                }
            elif difficulty == "advanced":
                design_details = {
                    "requirement": "support real-time collaboration for thousands of concurrent users",
                    "constraint": f"strict {random.choice(constraints)} requirements",
                    "system_type": "collaborative editing platform",
                    "optimization_goal": "low latency and consistency",
                    "scenario": "conflict resolution"
                }
            else:  # intermediate
                design_details = {
                    "requirement": "handle authentication and authorization for multiple services",
                    "constraint": f"emphasis on {random.choice(constraints)}",
                    "system_type": "identity management service",
                    "optimization_goal": "security and user experience",
                    "scenario": "single sign-on"
                }
        elif "machine learning" in topic.lower() or "ml" in topic.lower() or "ai" in topic.lower():
            if difficulty == "beginner":
                design_details = {
                    "requirement": "classify customer feedback",
                    "constraint": f"a focus on {random.choice(constraints)}",
                    "system_type": "sentiment analysis pipeline",
                    "optimization_goal": "accuracy",
                    "scenario": "handling multilingual input"
                }
            elif difficulty == "advanced":
                design_details = {
                    "requirement": "provide real-time recommendations based on user behavior",
                    "constraint": f"strict {random.choice(constraints)} requirements",
                    "system_type": "recommendation engine",
                    "optimization_goal": "personalization and freshness",
                    "scenario": "cold start problems"
                }
            else:  # intermediate
                design_details = {
                    "requirement": "detect anomalies in system metrics",
                    "constraint": f"emphasis on {random.choice(constraints)}",
                    "system_type": "monitoring system with ML capabilities",
                    "optimization_goal": "low false positive rate",
                    "scenario": "concept drift"
                }
        else:
            # Generic system design details for other topics
            design_details = {
                "requirement": f"solve key challenges in {topic}",
                "constraint": f"a focus on {random.choice(constraints)}",
                "system_type": f"{topic} system",
                "optimization_goal": "efficiency and reliability",
                "scenario": "typical use cases"
            }
        
        # Format the template with appropriate details
        for key, value in design_details.items():
            if key in template:
                template = template.replace(f"{{{key}}}", value)
        
        # Create the system design challenge
        design_challenge = {
            "id": f"design_{int(datetime.now().timestamp())}",
            "type": "system_design_challenge",
            "topic": topic,
            "difficulty": difficulty,
            "scenario": template,
            "created_at": datetime.now().isoformat(),
            "constraints": constraints,
            "learning_objectives": [
                "Practice system architecture design",
                "Apply theoretical knowledge to practical design decisions",
                "Consider trade-offs between different design goals"
            ],
            "deliverables": [
                "High-level architecture diagram",
                "Component descriptions and interactions",
                "Discussion of design decisions and trade-offs",
                "Approach to addressing the specified constraints"
            ]
        }
        
        # Add to history
        self.simulation_history.append({
            "id": design_challenge["id"],
            "type": "system_design_challenge",
            "topic": topic,
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat()
        })
        
        return design_challenge
    
    def generate_data_interpretation_task(self,
                                        topic: str,
                                        data_type: str = "statistical",
                                        difficulty: str = "intermediate",
                                        data_source: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a data interpretation task with real-world data.
        
        Args:
            topic (str): The topic for the data interpretation task
            data_type (str): Type of data (statistical, time_series, categorical, etc.)
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            data_source (str, optional): Source of the data
            
        Returns:
            Dict[str, Any]: Generated data interpretation task
        """
        logger.info(f"Generating data interpretation task for topic: {topic}, data_type: {data_type}")
        
        # Select a template
        templates = self.default_templates.get("data_interpretation", [])
        template = random.choice(templates)
        
        # Generate data interpretation details based on topic and data type
        if data_type == "statistical":
            interpretation_details = {
                "data_type": "statistical",
                "topic": topic,
                "phenomenon": f"trends in {topic}",
                "visualization_type": "statistical summary"
            }
        elif data_type == "time_series":
            interpretation_details = {
                "data_type": "time series",
                "topic": topic,
                "phenomenon": f"temporal patterns in {topic}",
                "visualization_type": "line chart"
            }
        elif data_type == "categorical":
            interpretation_details = {
                "data_type": "categorical",
                "topic": topic,
                "phenomenon": f"distribution of {topic} categories",
                "visualization_type": "bar chart"
            }
        elif data_type == "geospatial":
            interpretation_details = {
                "data_type": "geospatial",
                "topic": topic,
                "phenomenon": f"geographic distribution of {topic}",
                "visualization_type": "map visualization"
            }
        else:
            interpretation_details = {
                "data_type": data_type,
                "topic": topic,
                "phenomenon": f"patterns in {topic}",
                "visualization_type": "data visualization"
            }
        
        # Format the template with appropriate details
        for key, value in interpretation_details.items():
            if key in template:
                template = template.replace(f"{{{key}}}", value)
        
        # Create the data interpretation task
        interpretation_task = {
            "id": f"interpret_{int(datetime.now().timestamp())}",
            "type": "data_interpretation_task",
            "topic": topic,
            "data_type": data_type,
            "difficulty": difficulty,
            "scenario": template,
            "created_at": datetime.now().isoformat(),
            "learning_objectives": [
                f"Practice interpreting {data_type} data",
                "Draw meaningful conclusions from data analysis",
                "Connect data patterns to real-world implications"
            ],
            "guiding_questions": [
                "What are the main patterns or trends in the data?",
                "What might explain these patterns?",
                "What decisions or actions would you recommend based on this analysis?",
                "What additional data would be helpful to have?"
            ]
        }
        
        # Add data source if provided
        if data_source:
            interpretation_task["data_source"] = data_source
        
        # Add to history
        self.simulation_history.append({
            "id": interpretation_task["id"],
            "type": "data_interpretation_task",
            "topic": topic,
            "data_type": data_type,
            "difficulty": difficulty,
            "timestamp": datetime.now().isoformat()
        })
        
        return interpretation_task
    
    def generate_simulation_set(self,
                              topic: str,
                              difficulty: str = "intermediate",
                              count: int = 3,
                              simulation_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate a set of simulations for a topic.
        
        Args:
            topic (str): The topic for the simulations
            difficulty (str): Difficulty level (beginner, intermediate, advanced)
            count (int): Number of simulations to generate
            simulation_types (List[str], optional): Types of simulations to include
            
        Returns:
            List[Dict[str, Any]]: Generated simulations
        """
        logger.info(f"Generating simulation set for topic: {topic}, count: {count}")
        
        # Default simulation types if not provided
        if not simulation_types:
            simulation_types = ["mini_case", "debugging_exercise", "system_design_challenge", "data_interpretation_task"]
        
        simulations = []
        
        # Generate requested number of simulations
        for i in range(count):
            # Select a simulation type
            sim_type = random.choice(simulation_types)
            
            # Generate simulation based on type
            if sim_type == "mini_case":
                simulation = self.generate_mini_case(topic, difficulty)
            elif sim_type == "debugging_exercise":
                simulation = self.generate_debugging_exercise(topic, difficulty)
            elif sim_type == "system_design_challenge":
                simulation = self.generate_system_design_challenge(topic, difficulty)
            elif sim_type == "data_interpretation_task":
                simulation = self.generate_data_interpretation_task(topic, "statistical", difficulty)
            else:
                logger.warning(f"Unknown simulation type: {sim_type}")
                continue
            
            simulations.append(simulation)
        
        return simulations
    
    def adjust_difficulty(self,
                        simulation_id: str,
                        new_difficulty: str) -> Dict[str, Any]:
        """
        Adjust the difficulty of an existing simulation.
        
        Args:
            simulation_id (str): ID of the simulation to adjust
            new_difficulty (str): New difficulty level
            
        Returns:
            Dict[str, Any]: Adjusted simulation
        """
        logger.info(f"Adjusting difficulty of simulation {simulation_id} to {new_difficulty}")
        
        # Find the simulation in history
        simulation_info = None
        for entry in self.simulation_history:
            if entry["id"] == simulation_id:
                simulation_info = entry
                break
        
        if not simulation_info:
            logger.error(f"Simulation not found: {simulation_id}")
            return {"error": f"Simulation not found: {simulation_id}"}
        
        # Generate a new simulation with the same parameters but different difficulty
        if simulation_info["type"] == "mini_case":
            adjusted_simulation = self.generate_mini_case(
                simulation_info["topic"],
                new_difficulty
            )
        elif simulation_info["type"] == "debugging_exercise":
            adjusted_simulation = self.generate_debugging_exercise(
                simulation_info["topic"],
                new_difficulty
            )
        elif simulation_info["type"] == "system_design_challenge":
            adjusted_simulation = self.generate_system_design_challenge(
                simulation_info["topic"],
                new_difficulty
            )
        elif simulation_info["type"] == "data_interpretation_task":
            adjusted_simulation = self.generate_data_interpretation_task(
                simulation_info["topic"],
                simulation_info.get("data_type", "statistical"),
                new_difficulty
            )
        else:
            logger.error(f"Unknown simulation type: {simulation_info['type']}")
            return {"error": f"Unknown simulation type: {simulation_info['type']}"}
        
        # Preserve the original ID
        adjusted_simulation["id"] = simulation_id
        
        # Update history
        for entry in self.simulation_history:
            if entry["id"] == simulation_id:
                entry["difficulty"] = new_difficulty
                break
        
        return adjusted_simulation
    
    def get_simulation_history(self,
                             topic: Optional[str] = None,
                             simulation_type: Optional[str] = None,
                             limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get history of generated simulations with optional filtering.
        
        Args:
            topic (str, optional): Filter by topic
            simulation_type (str, optional): Filter by simulation type
            limit (int): Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Filtered simulation history
        """
        # Apply filters
        filtered_history = self.simulation_history
        
        if topic:
            filtered_history = [entry for entry in filtered_history if entry.get("topic") == topic]
        
        if simulation_type:
            filtered_history = [entry for entry in filtered_history if entry.get("type") == simulation_type]
        
        # Sort by timestamp (newest first)
        sorted_history = sorted(filtered_history, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply limit
        limited_history = sorted_history[:limit]
        
        return limited_history
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the simulation mode to a file.
        
        Args:
            filepath (str): Path to save the state
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            state = {
                "simulation_history": self.simulation_history,
                "templates": self.default_templates
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Saved simulation mode state to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving simulation mode state: {str(e)}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the simulation mode state from a file.
        
        Args:
            filepath (str): Path to the state file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.simulation_history = state.get("simulation_history", [])
            
            # Only update templates if they exist in the state
            if "templates" in state:
                self.default_templates = state["templates"]
            
            logger.info(f"Loaded simulation mode state from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading simulation mode state: {str(e)}")
            return False