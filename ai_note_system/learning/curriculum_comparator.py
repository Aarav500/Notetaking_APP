"""
Automated Curriculum Comparator module for AI Note System.
Provides functionality to compare learning roadmaps with standard curricula.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Setup logging
logger = logging.getLogger("ai_note_system.learning.curriculum_comparator")

class CurriculumComparator:
    """
    Curriculum Comparator class for comparing learning roadmaps with standard curricula.
    Compares user roadmaps with top educational institutions and industry certifications.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Curriculum Comparator.
        
        Args:
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Default curriculum sources
        self.default_sources = {
            "academic": [
                "MIT OpenCourseWare",
                "Stanford Online",
                "Harvard Online Learning",
                "Berkeley EECS",
                "Princeton Computer Science"
            ],
            "industry": [
                "AWS Certifications",
                "Google Cloud Certifications",
                "Microsoft Certifications",
                "Cisco Certifications",
                "CompTIA Certifications"
            ]
        }
        
        # Curriculum database (would typically be loaded from a file or database)
        self.curriculum_database = self._initialize_curriculum_database()
        
        # Comparison history
        self.comparison_history = []
        
        logger.debug("Initialized CurriculumComparator")
    
    def _initialize_curriculum_database(self) -> Dict[str, Any]:
        """
        Initialize the curriculum database with standard curricula.
        
        Returns:
            Dict[str, Any]: Curriculum database
        """
        # This would typically load from a file or database
        # For now, we'll use a simplified in-memory database
        
        database = {
            "academic": {
                "computer_science": {
                    "MIT": {
                        "name": "MIT Computer Science Curriculum",
                        "source": "MIT OpenCourseWare",
                        "url": "https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/",
                        "core_topics": [
                            "Introduction to Computer Science and Programming",
                            "Mathematics for Computer Science",
                            "Introduction to Algorithms",
                            "Data Structures",
                            "Computer Systems Engineering",
                            "Artificial Intelligence",
                            "Computer Networks",
                            "Database Systems",
                            "Computer Graphics",
                            "Theory of Computation"
                        ],
                        "electives": [
                            "Machine Learning",
                            "Natural Language Processing",
                            "Computer Vision",
                            "Distributed Systems",
                            "Cryptography and Security"
                        ]
                    },
                    "Stanford": {
                        "name": "Stanford Computer Science Curriculum",
                        "source": "Stanford University",
                        "url": "https://cs.stanford.edu/degrees/undergrad/",
                        "core_topics": [
                            "Computer Organization and Systems",
                            "Design and Analysis of Algorithms",
                            "Programming Abstractions",
                            "Logic, Automata, and Complexity",
                            "Probability Theory",
                            "Computer Networks",
                            "Database Systems",
                            "Artificial Intelligence"
                        ],
                        "electives": [
                            "Human-Computer Interaction",
                            "Natural Language Processing",
                            "Reinforcement Learning",
                            "Computer Vision",
                            "Robotics"
                        ]
                    }
                },
                "data_science": {
                    "Berkeley": {
                        "name": "Berkeley Data Science Curriculum",
                        "source": "UC Berkeley",
                        "url": "https://data.berkeley.edu/academics/undergraduate-programs/data-science-major",
                        "core_topics": [
                            "Foundations of Data Science",
                            "Linear Algebra",
                            "Probability and Statistics",
                            "Principles and Techniques of Data Science",
                            "Database Systems",
                            "Machine Learning",
                            "Data Visualization",
                            "Ethics in Data Science"
                        ],
                        "electives": [
                            "Natural Language Processing",
                            "Computer Vision",
                            "Deep Learning",
                            "Causal Inference",
                            "Time Series Analysis"
                        ]
                    }
                },
                "machine_learning": {
                    "Stanford": {
                        "name": "Stanford Machine Learning Curriculum",
                        "source": "Stanford University",
                        "url": "https://ai.stanford.edu/courses/",
                        "core_topics": [
                            "Linear Algebra",
                            "Probability Theory",
                            "Optimization",
                            "Machine Learning",
                            "Deep Learning",
                            "Natural Language Processing",
                            "Computer Vision",
                            "Reinforcement Learning"
                        ],
                        "electives": [
                            "Robotics",
                            "Generative Models",
                            "AI Ethics",
                            "Multi-agent Systems",
                            "Meta-Learning"
                        ]
                    }
                }
            },
            "industry": {
                "cloud_computing": {
                    "AWS": {
                        "name": "AWS Certification Path",
                        "source": "Amazon Web Services",
                        "url": "https://aws.amazon.com/certification/",
                        "certifications": [
                            "AWS Certified Cloud Practitioner",
                            "AWS Certified Solutions Architect - Associate",
                            "AWS Certified Developer - Associate",
                            "AWS Certified SysOps Administrator - Associate",
                            "AWS Certified Solutions Architect - Professional",
                            "AWS Certified DevOps Engineer - Professional"
                        ],
                        "core_topics": [
                            "Cloud Concepts",
                            "Security and Compliance",
                            "Technology",
                            "Billing and Pricing",
                            "EC2 and Compute Services",
                            "S3 and Storage Services",
                            "VPC and Networking",
                            "IAM and Security",
                            "Databases",
                            "Serverless"
                        ]
                    },
                    "Google Cloud": {
                        "name": "Google Cloud Certification Path",
                        "source": "Google Cloud Platform",
                        "url": "https://cloud.google.com/certification",
                        "certifications": [
                            "Google Cloud Digital Leader",
                            "Google Cloud Associate Engineer",
                            "Google Cloud Professional Cloud Architect",
                            "Google Cloud Professional Data Engineer",
                            "Google Cloud Professional DevOps Engineer",
                            "Google Cloud Professional Security Engineer"
                        ],
                        "core_topics": [
                            "Cloud Computing Fundamentals",
                            "Google Cloud Platform Services",
                            "Security, Privacy, and Compliance",
                            "Networking and VPC",
                            "Compute Options",
                            "Storage Options",
                            "Database Services",
                            "Identity and Access Management",
                            "Monitoring and Logging",
                            "Serverless and Containers"
                        ]
                    }
                },
                "data_science": {
                    "Microsoft": {
                        "name": "Microsoft Data Science Certification Path",
                        "source": "Microsoft",
                        "url": "https://docs.microsoft.com/en-us/learn/certifications/",
                        "certifications": [
                            "Microsoft Certified: Azure Data Fundamentals",
                            "Microsoft Certified: Azure Data Scientist Associate",
                            "Microsoft Certified: Azure Data Engineer Associate",
                            "Microsoft Certified: Azure Database Administrator Associate"
                        ],
                        "core_topics": [
                            "Data Concepts",
                            "Azure Data Services",
                            "Data Processing",
                            "Data Visualization",
                            "Data Analysis",
                            "Machine Learning",
                            "Big Data",
                            "Data Warehousing",
                            "Data Governance",
                            "Ethics and Privacy"
                        ]
                    }
                }
            }
        }
        
        return database
    
    def compare_with_standard_curriculum(self,
                                       user_roadmap: Dict[str, Any],
                                       field: str,
                                       institution: Optional[str] = None,
                                       detailed: bool = True) -> Dict[str, Any]:
        """
        Compare a user's learning roadmap with a standard curriculum.
        
        Args:
            user_roadmap (Dict[str, Any]): User's learning roadmap
            field (str): Field of study (e.g., "computer_science", "data_science")
            institution (str, optional): Specific institution to compare with
            detailed (bool): Whether to include detailed topic-by-topic comparison
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        logger.info(f"Comparing roadmap with standard curriculum for field: {field}")
        
        # Extract user topics from roadmap
        user_topics = self._extract_topics_from_roadmap(user_roadmap)
        
        # Find matching curricula in the database
        matching_curricula = self._find_matching_curricula(field, institution)
        
        if not matching_curricula:
            logger.warning(f"No matching curricula found for field: {field}")
            return {
                "success": False,
                "message": f"No matching curricula found for field: {field}",
                "field": field,
                "institution": institution
            }
        
        # Initialize comparison results
        comparison_id = f"comp_{int(datetime.now().timestamp())}"
        comparison_results = {
            "id": comparison_id,
            "timestamp": datetime.now().isoformat(),
            "field": field,
            "user_roadmap_name": user_roadmap.get("name", "User Roadmap"),
            "comparisons": [],
            "overall_coverage": 0.0,
            "missing_topics": [],
            "recommendations": []
        }
        
        # Compare with each matching curriculum
        for curriculum in matching_curricula:
            curriculum_name = curriculum.get("name", "Unknown Curriculum")
            curriculum_source = curriculum.get("source", "Unknown Source")
            
            # Get standard topics
            standard_topics = curriculum.get("core_topics", []) + curriculum.get("electives", [])
            if "certifications" in curriculum:
                standard_topics.extend(curriculum["certifications"])
            
            # Compare topics
            covered_topics = []
            missing_topics = []
            
            for topic in standard_topics:
                # Check if the topic is covered in the user roadmap
                if self._is_topic_covered(topic, user_topics):
                    covered_topics.append(topic)
                else:
                    missing_topics.append(topic)
            
            # Calculate coverage percentage
            coverage_percentage = (len(covered_topics) / len(standard_topics) * 100) if standard_topics else 0
            
            # Create comparison result for this curriculum
            comparison = {
                "curriculum_name": curriculum_name,
                "source": curriculum_source,
                "total_topics": len(standard_topics),
                "covered_topics": len(covered_topics),
                "coverage_percentage": round(coverage_percentage, 2),
                "missing_topics": missing_topics
            }
            
            # Add detailed comparison if requested
            if detailed:
                comparison["detailed_comparison"] = {
                    "covered_topics": covered_topics,
                    "missing_topics": missing_topics
                }
            
            comparison_results["comparisons"].append(comparison)
            comparison_results["missing_topics"].extend(missing_topics)
        
        # Remove duplicate missing topics
        comparison_results["missing_topics"] = list(set(comparison_results["missing_topics"]))
        
        # Calculate overall coverage
        if comparison_results["comparisons"]:
            overall_coverage = sum(comp["coverage_percentage"] for comp in comparison_results["comparisons"]) / len(comparison_results["comparisons"])
            comparison_results["overall_coverage"] = round(overall_coverage, 2)
        
        # Generate recommendations
        comparison_results["recommendations"] = self._generate_recommendations(comparison_results)
        
        # Add to history
        self.comparison_history.append({
            "id": comparison_id,
            "field": field,
            "institution": institution,
            "timestamp": comparison_results["timestamp"],
            "overall_coverage": comparison_results["overall_coverage"]
        })
        
        return comparison_results
    
    def _extract_topics_from_roadmap(self, roadmap: Dict[str, Any]) -> List[str]:
        """
        Extract topics from a user's learning roadmap.
        
        Args:
            roadmap (Dict[str, Any]): User's learning roadmap
            
        Returns:
            List[str]: List of topics in the roadmap
        """
        topics = []
        
        # Extract from learning requirements
        if "learning_requirements" in roadmap:
            for req in roadmap["learning_requirements"]:
                if isinstance(req, dict) and "name" in req:
                    topics.append(req["name"])
                elif isinstance(req, str):
                    topics.append(req)
        
        # Extract from modules
        if "modules" in roadmap:
            for module in roadmap["modules"]:
                if isinstance(module, dict) and "name" in module:
                    topics.append(module["name"])
                elif isinstance(module, str):
                    topics.append(module)
        
        # Extract from schedule
        if "schedule" in roadmap:
            for date, tasks in roadmap["schedule"].items():
                for task in tasks:
                    if isinstance(task, dict) and "name" in task:
                        topics.append(task["name"])
                    elif isinstance(task, str):
                        topics.append(task)
        
        # Extract from goals
        if "goals" in roadmap:
            for goal in roadmap["goals"]:
                if isinstance(goal, dict) and "name" in goal:
                    topics.append(goal["name"])
                elif isinstance(goal, str):
                    topics.append(goal)
        
        return topics
    
    def _find_matching_curricula(self, field: str, institution: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find matching curricula in the database.
        
        Args:
            field (str): Field of study
            institution (str, optional): Specific institution
            
        Returns:
            List[Dict[str, Any]]: List of matching curricula
        """
        matching_curricula = []
        
        # Search in academic curricula
        if field.lower() in self.curriculum_database.get("academic", {}):
            field_curricula = self.curriculum_database["academic"][field.lower()]
            
            if institution:
                # Look for specific institution
                for inst, curriculum in field_curricula.items():
                    if institution.lower() in inst.lower():
                        matching_curricula.append(curriculum)
            else:
                # Include all institutions for this field
                matching_curricula.extend(field_curricula.values())
        
        # Search in industry curricula
        if field.lower() in self.curriculum_database.get("industry", {}):
            field_curricula = self.curriculum_database["industry"][field.lower()]
            
            if institution:
                # Look for specific institution
                for inst, curriculum in field_curricula.items():
                    if institution.lower() in inst.lower():
                        matching_curricula.append(curriculum)
            else:
                # Include all institutions for this field
                matching_curricula.extend(field_curricula.values())
        
        return matching_curricula
    
    def _is_topic_covered(self, standard_topic: str, user_topics: List[str]) -> bool:
        """
        Check if a standard topic is covered in the user's topics.
        
        Args:
            standard_topic (str): Standard curriculum topic
            user_topics (List[str]): User's topics
            
        Returns:
            bool: True if the topic is covered, False otherwise
        """
        # This would typically use semantic similarity or an LLM
        # For now, we'll use simple keyword matching
        
        standard_keywords = set(standard_topic.lower().split())
        
        for user_topic in user_topics:
            user_keywords = set(user_topic.lower().split())
            
            # Check for significant overlap
            common_keywords = standard_keywords.intersection(user_keywords)
            if len(common_keywords) >= 2 or (len(common_keywords) == 1 and len(standard_keywords) == 1):
                return True
            
            # Check for substring match
            if standard_topic.lower() in user_topic.lower() or user_topic.lower() in standard_topic.lower():
                return True
        
        return False
    
    def _generate_recommendations(self, comparison_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on comparison results.
        
        Args:
            comparison_results (Dict[str, Any]): Comparison results
            
        Returns:
            List[Dict[str, Any]]: List of recommendations
        """
        recommendations = []
        
        # Recommend missing topics
        if comparison_results["missing_topics"]:
            # Group missing topics by importance
            critical_topics = []
            important_topics = []
            optional_topics = []
            
            # This would typically use a more sophisticated algorithm
            # For now, we'll use a simple heuristic based on frequency
            topic_frequency = {}
            for comp in comparison_results["comparisons"]:
                for topic in comp["missing_topics"]:
                    topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
            
            # Categorize by frequency
            for topic, freq in topic_frequency.items():
                if freq == len(comparison_results["comparisons"]):
                    critical_topics.append(topic)
                elif freq > len(comparison_results["comparisons"]) / 2:
                    important_topics.append(topic)
                else:
                    optional_topics.append(topic)
            
            # Add recommendations for critical topics
            if critical_topics:
                recommendations.append({
                    "type": "missing_critical_topics",
                    "priority": "high",
                    "message": "These topics are missing from your roadmap but are considered essential in all standard curricula",
                    "topics": critical_topics
                })
            
            # Add recommendations for important topics
            if important_topics:
                recommendations.append({
                    "type": "missing_important_topics",
                    "priority": "medium",
                    "message": "These topics are missing from your roadmap but are included in most standard curricula",
                    "topics": important_topics
                })
            
            # Add recommendations for optional topics
            if optional_topics:
                recommendations.append({
                    "type": "missing_optional_topics",
                    "priority": "low",
                    "message": "These topics are missing from your roadmap but are included in some standard curricula",
                    "topics": optional_topics
                })
        
        # Recommend based on overall coverage
        overall_coverage = comparison_results["overall_coverage"]
        if overall_coverage < 50:
            recommendations.append({
                "type": "low_coverage",
                "priority": "high",
                "message": f"Your roadmap covers only {overall_coverage}% of standard curricula. Consider adding more core topics."
            })
        elif overall_coverage < 70:
            recommendations.append({
                "type": "medium_coverage",
                "priority": "medium",
                "message": f"Your roadmap covers {overall_coverage}% of standard curricula. Consider adding some important missing topics."
            })
        elif overall_coverage < 90:
            recommendations.append({
                "type": "good_coverage",
                "priority": "low",
                "message": f"Your roadmap has good coverage ({overall_coverage}%) of standard curricula. Consider adding a few missing topics for completeness."
            })
        else:
            recommendations.append({
                "type": "excellent_coverage",
                "priority": "info",
                "message": f"Your roadmap has excellent coverage ({overall_coverage}%) of standard curricula."
            })
        
        return recommendations
    
    def compare_with_industry_certification(self,
                                          user_roadmap: Dict[str, Any],
                                          certification_path: str,
                                          provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare a user's learning roadmap with an industry certification path.
        
        Args:
            user_roadmap (Dict[str, Any]): User's learning roadmap
            certification_path (str): Certification path (e.g., "cloud_computing", "data_science")
            provider (str, optional): Specific certification provider
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        logger.info(f"Comparing roadmap with industry certification path: {certification_path}")
        
        # This is similar to compare_with_standard_curriculum but focused on industry certifications
        # For simplicity, we'll reuse the same method with the field parameter set to the certification path
        return self.compare_with_standard_curriculum(
            user_roadmap=user_roadmap,
            field=certification_path,
            institution=provider,
            detailed=True
        )
    
    def get_curriculum_sources(self, field: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available curriculum sources for comparison.
        
        Args:
            field (str, optional): Filter by field of study
            
        Returns:
            Dict[str, Any]: Available curriculum sources
        """
        sources = {
            "academic": [],
            "industry": []
        }
        
        # Get academic sources
        for field_name, field_data in self.curriculum_database.get("academic", {}).items():
            if field and field.lower() != field_name.lower():
                continue
            
            for institution, curriculum in field_data.items():
                sources["academic"].append({
                    "field": field_name,
                    "institution": institution,
                    "name": curriculum.get("name", f"{institution} {field_name.capitalize()} Curriculum"),
                    "url": curriculum.get("url", "")
                })
        
        # Get industry sources
        for field_name, field_data in self.curriculum_database.get("industry", {}).items():
            if field and field.lower() != field_name.lower():
                continue
            
            for provider, certification in field_data.items():
                sources["industry"].append({
                    "field": field_name,
                    "provider": provider,
                    "name": certification.get("name", f"{provider} {field_name.capitalize()} Certification"),
                    "url": certification.get("url", "")
                })
        
        return sources
    
    def get_comparison_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get history of curriculum comparisons.
        
        Args:
            limit (int): Maximum number of entries to return
            
        Returns:
            List[Dict[str, Any]]: Comparison history
        """
        # Sort by timestamp (newest first)
        sorted_history = sorted(self.comparison_history, key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        limited_history = sorted_history[:limit]
        
        return limited_history
    
    def add_custom_curriculum(self,
                            field: str,
                            institution: str,
                            curriculum_data: Dict[str, Any],
                            category: str = "academic") -> bool:
        """
        Add a custom curriculum to the database.
        
        Args:
            field (str): Field of study
            institution (str): Institution or provider name
            curriculum_data (Dict[str, Any]): Curriculum data
            category (str): Category (academic or industry)
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Adding custom curriculum for {institution} in {field}")
        
        try:
            # Validate category
            if category not in ["academic", "industry"]:
                logger.error(f"Invalid category: {category}")
                return False
            
            # Ensure field exists in the database
            if field.lower() not in self.curriculum_database.get(category, {}):
                self.curriculum_database[category][field.lower()] = {}
            
            # Add or update curriculum
            self.curriculum_database[category][field.lower()][institution] = curriculum_data
            
            logger.info(f"Successfully added custom curriculum for {institution} in {field}")
            return True
        except Exception as e:
            logger.error(f"Error adding custom curriculum: {str(e)}")
            return False
    
    def save_database(self, filepath: str) -> bool:
        """
        Save the curriculum database to a file.
        
        Args:
            filepath (str): Path to save the database
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(self.curriculum_database, f, indent=2)
            
            logger.info(f"Saved curriculum database to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving curriculum database: {str(e)}")
            return False
    
    def load_database(self, filepath: str) -> bool:
        """
        Load the curriculum database from a file.
        
        Args:
            filepath (str): Path to the database file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                self.curriculum_database = json.load(f)
            
            logger.info(f"Loaded curriculum database from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading curriculum database: {str(e)}")
            return False
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state of the curriculum comparator to a file.
        
        Args:
            filepath (str): Path to save the state
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            state = {
                "curriculum_database": self.curriculum_database,
                "comparison_history": self.comparison_history
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"Saved curriculum comparator state to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving curriculum comparator state: {str(e)}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load the curriculum comparator state from a file.
        
        Args:
            filepath (str): Path to the state file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.curriculum_database = state.get("curriculum_database", self._initialize_curriculum_database())
            self.comparison_history = state.get("comparison_history", [])
            
            logger.info(f"Loaded curriculum comparator state from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading curriculum comparator state: {str(e)}")
            return False