"""
MVP Generator module for the Ideater application.

This module handles the generation of MVP checklists, feature prioritization,
fallback logic, and boilerplate repository generation.
"""

import os
import json
import logging
import tempfile
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

try:
    import openai
except ImportError:
    openai = None

try:
    from github import Github
    from github.GithubException import GithubException
except ImportError:
    Github = None
    GithubException = Exception

try:
    from pydantic import BaseModel, Field
except ImportError:
    # Fallback for when pydantic is not available
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    def Field(**kwargs):
        return None

from .config import config

# Set up logging
logger = logging.getLogger("ideater.modules.mvp_generator")

class FeaturePriorityLevel(str, Enum):
    """Enum for feature priority levels."""
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    COULD_HAVE = "could_have"
    WONT_HAVE = "wont_have"

class FeatureCategory(str, Enum):
    """Enum for feature categories."""
    CORE = "core"
    UX = "ux"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ANALYTICS = "analytics"
    INTEGRATION = "integration"
    OTHER = "other"

class MVPChecklistRequest(BaseModel):
    """Request model for generating MVP checklist."""
    description: str
    target_audience: Optional[List[str]] = None
    business_goals: Optional[List[str]] = None
    technical_constraints: Optional[List[str]] = None
    timeline_weeks: Optional[int] = None
    team_size: Optional[int] = None
    prioritization_method: Optional[str] = "RICE"  # RICE or MoSCoW

class Feature(BaseModel):
    """Model for a feature in the MVP checklist."""
    id: str
    name: str
    description: str
    category: FeatureCategory
    priority: FeaturePriorityLevel
    effort_estimate: Optional[int] = None  # In person-days
    impact_score: Optional[float] = None  # 1-10 scale
    confidence_score: Optional[float] = None  # 1-10 scale
    reach_score: Optional[float] = None  # Number of users affected
    rice_score: Optional[float] = None  # RICE score (Reach * Impact * Confidence / Effort)
    moscow_category: Optional[str] = None  # Must, Should, Could, Won't
    include_in_mvp: bool = True
    rationale: Optional[str] = None

class FeaturePriority(BaseModel):
    """Model for feature prioritization."""
    features: List[Feature]
    prioritization_method: str
    mvp_features: List[Feature]
    future_features: List[Feature]
    rationale: str

class MVPChecklistResult(BaseModel):
    """Result model for generated MVP checklist."""
    feature_priority: FeaturePriority
    timeline_estimate: Optional[str] = None
    resource_requirements: Optional[Dict[str, Any]] = None
    success_metrics: Optional[List[str]] = None
    explanation: Optional[str] = None

class FallbackLogicRequest(BaseModel):
    """Request model for generating fallback logic."""
    description: str
    features: List[Feature]
    critical_features: Optional[List[str]] = None
    potential_challenges: Optional[List[str]] = None

class FallbackStrategy(BaseModel):
    """Model for a fallback strategy."""
    feature_id: str
    feature_name: str
    potential_issues: List[str]
    fallback_approaches: List[str]
    degraded_functionality: Optional[str] = None
    user_impact: str
    implementation_notes: Optional[str] = None

class FallbackLogicResult(BaseModel):
    """Result model for generated fallback logic."""
    strategies: List[FallbackStrategy]
    general_recommendations: List[str]
    explanation: Optional[str] = None

class BoilerplateRepoRequest(BaseModel):
    """Request model for generating boilerplate repository."""
    description: str
    features: List[Feature]
    tech_stack: Dict[str, Any]
    repo_name: str
    include_readme: bool = True
    include_license: Optional[str] = None
    include_ci_cd: bool = False
    include_docker: bool = False

class BoilerplateRepoResult(BaseModel):
    """Result model for generated boilerplate repository."""
    repo_url: Optional[str] = None
    repo_name: str
    files_created: List[str]
    setup_instructions: str
    next_steps: List[str]
    explanation: Optional[str] = None

class MVPGenerator:
    """
    Main class for the Auto-MVP Generator module.
    
    This class provides methods for generating MVP checklists, feature prioritization,
    fallback logic, and boilerplate repository generation.
    """
    
    def __init__(self):
        """Initialize the MVPGenerator."""
        self.openai_api_key = config.get_openai_api_key()
        self.openai_model = config.get_openai_model()
        self.temperature = config.get_temperature()
        self.max_tokens = config.get_max_tokens()
        self.github_token = config.get_github_token()
        self.github_username = config.get_github_username()
        self.templates_dir = config.get_templates_dir()
        self.prioritization_method = config.get_prioritization_method()
        
        # Initialize OpenAI client if available
        if openai and self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.client = openai.OpenAI()
        else:
            self.client = None
            logger.warning("OpenAI client not available. Some features may not work.")
        
        # Initialize GitHub client if available
        if Github and self.github_token:
            self.github = Github(self.github_token)
        else:
            self.github = None
            logger.warning("GitHub client not available. Repository generation will be limited.")
    
    def generate_mvp_checklist(self, request: MVPChecklistRequest) -> MVPChecklistResult:
        """
        Generate MVP checklist based on the request.
        
        Args:
            request: The MVP checklist request.
            
        Returns:
            The MVP checklist result.
        """
        logger.info("Generating MVP checklist")
        
        # Check if OpenAI client is available
        if not self.client:
            logger.error("OpenAI client not available. Cannot generate MVP checklist.")
            return MVPChecklistResult(
                feature_priority=FeaturePriority(
                    features=[
                        Feature(
                            id="error",
                            name="Error",
                            description="OpenAI client not available. Please check your API key and try again.",
                            category=FeatureCategory.OTHER,
                            priority=FeaturePriorityLevel.MUST_HAVE,
                            include_in_mvp=True
                        )
                    ],
                    prioritization_method="RICE",
                    mvp_features=[],
                    future_features=[],
                    rationale="Error: OpenAI client not available."
                )
            )
        
        try:
            # Use the prioritization method from the request or the default
            prioritization_method = request.prioritization_method or self.prioritization_method
            
            # Generate features
            features = self._generate_features(
                description=request.description,
                target_audience=request.target_audience,
                business_goals=request.business_goals,
                technical_constraints=request.technical_constraints,
                prioritization_method=prioritization_method
            )
            
            # Prioritize features
            feature_priority = self._prioritize_features(
                features=features,
                prioritization_method=prioritization_method,
                timeline_weeks=request.timeline_weeks,
                team_size=request.team_size
            )
            
            # Generate timeline estimate
            timeline_estimate = self._generate_timeline_estimate(
                feature_priority=feature_priority,
                timeline_weeks=request.timeline_weeks,
                team_size=request.team_size
            )
            
            # Generate resource requirements
            resource_requirements = self._generate_resource_requirements(
                feature_priority=feature_priority,
                team_size=request.team_size
            )
            
            # Generate success metrics
            success_metrics = self._generate_success_metrics(
                description=request.description,
                feature_priority=feature_priority,
                business_goals=request.business_goals
            )
            
            # Generate explanation
            explanation = self._generate_mvp_checklist_explanation(
                description=request.description,
                feature_priority=feature_priority
            )
            
            # Create and return the result
            result = MVPChecklistResult(
                feature_priority=feature_priority,
                timeline_estimate=timeline_estimate,
                resource_requirements=resource_requirements,
                success_metrics=success_metrics,
                explanation=explanation
            )
            
            logger.info(f"Generated MVP checklist with {len(feature_priority.features)} features")
            return result
            
        except Exception as e:
            logger.error(f"Error generating MVP checklist: {str(e)}")
            return MVPChecklistResult(
                feature_priority=FeaturePriority(
                    features=[
                        Feature(
                            id="error",
                            name="Error",
                            description=f"Error generating MVP checklist: {str(e)}",
                            category=FeatureCategory.OTHER,
                            priority=FeaturePriorityLevel.MUST_HAVE,
                            include_in_mvp=True
                        )
                    ],
                    prioritization_method=prioritization_method,
                    mvp_features=[],
                    future_features=[],
                    rationale=f"Error: {str(e)}"
                )
            )
    
    def generate_fallback_logic(self, request: FallbackLogicRequest) -> FallbackLogicResult:
        """
        Generate fallback logic based on the request.
        
        Args:
            request: The fallback logic request.
            
        Returns:
            The fallback logic result.
        """
        logger.info("Generating fallback logic")
        
        # Implementation will be added in the next part
        pass
    
    def generate_boilerplate_repo(self, request: BoilerplateRepoRequest) -> BoilerplateRepoResult:
        """
        Generate boilerplate repository based on the request.
        
        Args:
            request: The boilerplate repository request.
            
        Returns:
            The boilerplate repository result.
        """
        logger.info(f"Generating boilerplate repository: {request.repo_name}")
        
        # Implementation will be added in the next part
        pass
    
    def _generate_features(
        self,
        description: str,
        target_audience: Optional[List[str]] = None,
        business_goals: Optional[List[str]] = None,
        technical_constraints: Optional[List[str]] = None,
        prioritization_method: str = "RICE"
    ) -> List[Feature]:
        """
        Generate a list of features based on the project description.
        
        Args:
            description: The project description.
            target_audience: The target audience.
            business_goals: The business goals.
            technical_constraints: The technical constraints.
            prioritization_method: The prioritization method (RICE or MoSCoW).
            
        Returns:
            A list of Feature objects.
        """
        logger.info("Generating features based on project description")
        
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            You are an expert product manager. Based on the following project description, generate a list of features for an MVP (Minimum Viable Product).
            
            Project description:
            {description}
            """
            
            if target_audience:
                audience_str = ", ".join(target_audience)
                prompt += f"\n\nTarget audience: {audience_str}"
            
            if business_goals:
                goals_str = "\n- " + "\n- ".join(business_goals)
                prompt += f"\n\nBusiness goals:{goals_str}"
            
            if technical_constraints:
                constraints_str = "\n- " + "\n- ".join(technical_constraints)
                prompt += f"\n\nTechnical constraints:{constraints_str}"
            
            prompt += f"""
            
            For each feature, provide:
            1. A unique ID (e.g., F001, F002)
            2. A short, descriptive name
            3. A detailed description
            4. The category (one of: core, ux, performance, security, analytics, integration, other)
            5. The priority level (one of: must_have, should_have, could_have, wont_have)
            """
            
            if prioritization_method == "RICE":
                prompt += """
                6. Effort estimate (in person-days)
                7. Impact score (1-10 scale)
                8. Confidence score (1-10 scale)
                9. Reach score (estimated number of users affected)
                """
            elif prioritization_method == "MoSCoW":
                prompt += """
                6. MoSCoW category (Must, Should, Could, Won't)
                """
            
            prompt += """
            10. Whether to include in MVP (true/false)
            11. Rationale for inclusion/exclusion
            
            Format your response as a JSON array with objects containing the following fields:
            {
                "id": "F001",
                "name": "Feature Name",
                "description": "Detailed description",
                "category": "core",
                "priority": "must_have",
                "effort_estimate": 5,
                "impact_score": 8,
                "confidence_score": 9,
                "reach_score": 1000,
                "moscow_category": "Must",
                "include_in_mvp": true,
                "rationale": "Rationale for inclusion/exclusion"
            }
            
            Generate 10-15 features that would be appropriate for an MVP. Include a mix of must-have, should-have, and could-have features. Ensure that the features are specific, measurable, and aligned with the project description and business goals.
            """
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert product manager."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            # Extract the features from the response
            content = response.choices[0].message.content.strip()
            features_data = json.loads(content)
            
            # Convert to Feature objects
            features = []
            for feature_data in features_data.get("features", []):
                try:
                    # Convert category string to FeatureCategory enum
                    category_str = feature_data.get("category", "other").lower()
                    try:
                        category = FeatureCategory(category_str)
                    except ValueError:
                        category = FeatureCategory.OTHER
                    
                    # Convert priority string to FeaturePriorityLevel enum
                    priority_str = feature_data.get("priority", "should_have").lower()
                    try:
                        priority = FeaturePriorityLevel(priority_str)
                    except ValueError:
                        priority = FeaturePriorityLevel.SHOULD_HAVE
                    
                    # Create Feature object
                    feature = Feature(
                        id=feature_data.get("id", f"F{len(features)+1:03d}"),
                        name=feature_data.get("name", "Unnamed Feature"),
                        description=feature_data.get("description", ""),
                        category=category,
                        priority=priority,
                        effort_estimate=feature_data.get("effort_estimate"),
                        impact_score=feature_data.get("impact_score"),
                        confidence_score=feature_data.get("confidence_score"),
                        reach_score=feature_data.get("reach_score"),
                        rice_score=self._calculate_rice_score(
                            reach=feature_data.get("reach_score"),
                            impact=feature_data.get("impact_score"),
                            confidence=feature_data.get("confidence_score"),
                            effort=feature_data.get("effort_estimate")
                        ),
                        moscow_category=feature_data.get("moscow_category"),
                        include_in_mvp=feature_data.get("include_in_mvp", True),
                        rationale=feature_data.get("rationale", "")
                    )
                    features.append(feature)
                except Exception as e:
                    logger.warning(f"Error creating feature from data: {str(e)}")
            
            logger.info(f"Generated {len(features)} features")
            return features
            
        except Exception as e:
            logger.error(f"Error generating features: {str(e)}")
            # Return a minimal set of features in case of error
            return [
                Feature(
                    id="F001",
                    name="Basic Functionality",
                    description="Core functionality of the application",
                    category=FeatureCategory.CORE,
                    priority=FeaturePriorityLevel.MUST_HAVE,
                    include_in_mvp=True,
                    rationale="Essential for the MVP"
                )
            ]
    
    def _calculate_rice_score(
        self,
        reach: Optional[float] = None,
        impact: Optional[float] = None,
        confidence: Optional[float] = None,
        effort: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate the RICE score (Reach * Impact * Confidence / Effort).
        
        Args:
            reach: The reach score.
            impact: The impact score.
            confidence: The confidence score.
            effort: The effort estimate.
            
        Returns:
            The calculated RICE score, or None if any of the inputs are None.
        """
        if reach is None or impact is None or confidence is None or effort is None or effort == 0:
            return None
        
        # Convert confidence from 1-10 scale to 0-1 scale
        confidence_decimal = confidence / 10.0
        
        # Calculate RICE score
        rice_score = (reach * impact * confidence_decimal) / effort
        
        return round(rice_score, 2)
    
    def _prioritize_features(
        self,
        features: List[Feature],
        prioritization_method: str,
        timeline_weeks: Optional[int] = None,
        team_size: Optional[int] = None
    ) -> FeaturePriority:
        """
        Prioritize features based on the specified method.
        
        Args:
            features: The list of features to prioritize.
            prioritization_method: The prioritization method (RICE or MoSCoW).
            timeline_weeks: The timeline in weeks.
            team_size: The team size.
            
        Returns:
            A FeaturePriority object.
        """
        logger.info(f"Prioritizing features using {prioritization_method} method")
        
        try:
            # Make a copy of the features list to avoid modifying the original
            features_copy = features.copy()
            
            # Calculate capacity if timeline and team size are provided
            capacity_person_days = None
            if timeline_weeks is not None and team_size is not None:
                # Assume 5 working days per week
                capacity_person_days = timeline_weeks * 5 * team_size
                logger.info(f"Calculated capacity: {capacity_person_days} person-days")
            
            # Sort features based on prioritization method
            if prioritization_method.upper() == "RICE":
                # Sort by RICE score (descending)
                features_copy.sort(key=lambda f: f.rice_score if f.rice_score is not None else 0, reverse=True)
                
                # Determine which features to include in MVP based on capacity
                mvp_features = []
                future_features = []
                
                if capacity_person_days is not None:
                    # Include features until we reach capacity
                    remaining_capacity = capacity_person_days
                    
                    for feature in features_copy:
                        # Always include MUST_HAVE features
                        if feature.priority == FeaturePriorityLevel.MUST_HAVE:
                            mvp_features.append(feature)
                            if feature.effort_estimate is not None:
                                remaining_capacity -= feature.effort_estimate
                        # Include high RICE score features if capacity allows
                        elif feature.effort_estimate is not None and feature.effort_estimate <= remaining_capacity:
                            mvp_features.append(feature)
                            remaining_capacity -= feature.effort_estimate
                        else:
                            future_features.append(feature)
                else:
                    # Without capacity, include features based on priority and RICE score
                    for feature in features_copy:
                        if feature.priority == FeaturePriorityLevel.MUST_HAVE or feature.include_in_mvp:
                            mvp_features.append(feature)
                        else:
                            future_features.append(feature)
                
                rationale = (
                    f"Features were prioritized using the RICE method (Reach, Impact, Confidence, Effort). "
                    f"MUST_HAVE features were automatically included in the MVP. "
                    f"Other features were included based on their RICE score and available capacity."
                )
                
            elif prioritization_method.upper() == "MOSCOW":
                # Sort by MoSCoW category
                moscow_order = {"Must": 0, "Should": 1, "Could": 2, "Won't": 3}
                
                # Sort first by priority level, then by moscow_category if available
                def moscow_sort_key(feature):
                    priority_order = {
                        FeaturePriorityLevel.MUST_HAVE: 0,
                        FeaturePriorityLevel.SHOULD_HAVE: 1,
                        FeaturePriorityLevel.COULD_HAVE: 2,
                        FeaturePriorityLevel.WONT_HAVE: 3
                    }
                    
                    # Primary sort by priority level
                    primary_key = priority_order.get(feature.priority, 4)
                    
                    # Secondary sort by moscow_category if available
                    secondary_key = 4  # Default high value
                    if feature.moscow_category:
                        secondary_key = moscow_order.get(feature.moscow_category, 4)
                    
                    return (primary_key, secondary_key)
                
                features_copy.sort(key=moscow_sort_key)
                
                # Determine which features to include in MVP
                mvp_features = []
                future_features = []
                
                if capacity_person_days is not None:
                    # Include features until we reach capacity
                    remaining_capacity = capacity_person_days
                    
                    for feature in features_copy:
                        # Always include MUST_HAVE features
                        if feature.priority == FeaturePriorityLevel.MUST_HAVE:
                            mvp_features.append(feature)
                            if feature.effort_estimate is not None:
                                remaining_capacity -= feature.effort_estimate
                        # Include SHOULD_HAVE features if capacity allows
                        elif feature.priority == FeaturePriorityLevel.SHOULD_HAVE and feature.effort_estimate is not None and feature.effort_estimate <= remaining_capacity:
                            mvp_features.append(feature)
                            remaining_capacity -= feature.effort_estimate
                        # Include some COULD_HAVE features if capacity allows
                        elif feature.priority == FeaturePriorityLevel.COULD_HAVE and feature.effort_estimate is not None and feature.effort_estimate <= remaining_capacity and remaining_capacity > capacity_person_days * 0.2:
                            mvp_features.append(feature)
                            remaining_capacity -= feature.effort_estimate
                        else:
                            future_features.append(feature)
                else:
                    # Without capacity, include features based on priority
                    for feature in features_copy:
                        if feature.priority in [FeaturePriorityLevel.MUST_HAVE, FeaturePriorityLevel.SHOULD_HAVE] or feature.include_in_mvp:
                            mvp_features.append(feature)
                        else:
                            future_features.append(feature)
                
                rationale = (
                    f"Features were prioritized using the MoSCoW method (Must, Should, Could, Won't). "
                    f"Must-have features were automatically included in the MVP. "
                    f"Should-have features were included if capacity allowed. "
                    f"Could-have features were included only if significant capacity remained."
                )
                
            else:
                # Default prioritization based on priority level
                features_copy.sort(key=lambda f: f.priority.value)
                
                # Determine which features to include in MVP
                mvp_features = [f for f in features_copy if f.priority in [FeaturePriorityLevel.MUST_HAVE, FeaturePriorityLevel.SHOULD_HAVE] or f.include_in_mvp]
                future_features = [f for f in features_copy if f not in mvp_features]
                
                rationale = (
                    f"Features were prioritized based on their priority level. "
                    f"MUST_HAVE and SHOULD_HAVE features were included in the MVP."
                )
            
            # Create and return FeaturePriority object
            feature_priority = FeaturePriority(
                features=features_copy,
                prioritization_method=prioritization_method,
                mvp_features=mvp_features,
                future_features=future_features,
                rationale=rationale
            )
            
            logger.info(f"Prioritized {len(mvp_features)} features for MVP and {len(future_features)} features for future releases")
            return feature_priority
            
        except Exception as e:
            logger.error(f"Error prioritizing features: {str(e)}")
            # Return a basic FeaturePriority object in case of error
            must_have_features = [f for f in features if f.priority == FeaturePriorityLevel.MUST_HAVE]
            other_features = [f for f in features if f.priority != FeaturePriorityLevel.MUST_HAVE]
            
            return FeaturePriority(
                features=features,
                prioritization_method=prioritization_method,
                mvp_features=must_have_features,
                future_features=other_features,
                rationale="Error occurred during prioritization. Only MUST_HAVE features were included in the MVP."
            )
    
    def _generate_mvp_checklist_explanation(
        self,
        description: str,
        feature_priority: FeaturePriority
    ) -> str:
        """
        Generate an explanation for the MVP checklist.
        
        Args:
            description: The project description.
            feature_priority: The feature prioritization.
            
        Returns:
            The generated explanation.
        """
        # Implementation will be added in the next part
        pass
    
    def _generate_fallback_strategies(
        self,
        description: str,
        features: List[Feature],
        critical_features: Optional[List[str]] = None,
        potential_challenges: Optional[List[str]] = None
    ) -> List[FallbackStrategy]:
        """
        Generate fallback strategies for features.
        
        Args:
            description: The project description.
            features: The list of features.
            critical_features: The list of critical feature IDs.
            potential_challenges: The list of potential challenges.
            
        Returns:
            A list of FallbackStrategy objects.
        """
        # Implementation will be added in the next part
        pass
    
    def _generate_fallback_logic_explanation(
        self,
        description: str,
        strategies: List[FallbackStrategy]
    ) -> str:
        """
        Generate an explanation for the fallback logic.
        
        Args:
            description: The project description.
            strategies: The list of fallback strategies.
            
        Returns:
            The generated explanation.
        """
        # Implementation will be added in the next part
        pass
    
    def _create_github_repo(
        self,
        repo_name: str,
        description: str,
        private: bool = False
    ) -> Optional[str]:
        """
        Create a GitHub repository.
        
        Args:
            repo_name: The repository name.
            description: The repository description.
            private: Whether the repository should be private.
            
        Returns:
            The repository URL if successful, None otherwise.
        """
        # Implementation will be added in the next part
        pass
    
    def _generate_boilerplate_files(
        self,
        description: str,
        features: List[Feature],
        tech_stack: Dict[str, Any],
        repo_name: str,
        include_readme: bool = True,
        include_license: Optional[str] = None,
        include_ci_cd: bool = False,
        include_docker: bool = False
    ) -> Dict[str, str]:
        """
        Generate boilerplate files for the repository.
        
        Args:
            description: The project description.
            features: The list of features.
            tech_stack: The technology stack.
            repo_name: The repository name.
            include_readme: Whether to include a README file.
            include_license: The license type to include.
            include_ci_cd: Whether to include CI/CD configuration.
            include_docker: Whether to include Docker configuration.
            
        Returns:
            A dictionary mapping file paths to file contents.
        """
        # Implementation will be added in the next part
        pass
    
    def _push_files_to_github(
        self,
        repo_name: str,
        files: Dict[str, str]
    ) -> List[str]:
        """
        Push files to a GitHub repository.
        
        Args:
            repo_name: The repository name.
            files: A dictionary mapping file paths to file contents.
            
        Returns:
            A list of created file paths.
        """
        # Implementation will be added in the next part
        pass
    
    def _generate_boilerplate_repo_explanation(
        self,
        description: str,
        repo_name: str,
        files_created: List[str],
        tech_stack: Dict[str, Any]
    ) -> str:
        """
        Generate an explanation for the boilerplate repository.
        
        Args:
            description: The project description.
            repo_name: The repository name.
            files_created: The list of created file paths.
            tech_stack: The technology stack.
            
        Returns:
            The generated explanation.
        """
        # Implementation will be added in the next part
        pass