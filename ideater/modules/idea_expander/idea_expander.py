"""
Idea Expander module for the Ideater application.

This module handles the expansion of initial ideas into refined statements,
value propositions, unique selling points, competitor comparisons, and
feature prioritization matrices.
"""

import logging
import json
from typing import Dict, Any, List, Optional

import openai
from pydantic import BaseModel

# Import configuration
from .config import config

# Set up logging
logger = logging.getLogger("ideater.modules.idea_expander")

class IdeaExpansionRequest(BaseModel):
    """Request model for idea expansion."""
    original_idea: str
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    constraints: Optional[List[str]] = None

class ValueProposition(BaseModel):
    """Model for a value proposition."""
    title: str
    description: str
    impact: str

class UniqueSellingPoint(BaseModel):
    """Model for a unique selling point."""
    point: str
    description: str
    differentiation: str

class CompetitorComparison(BaseModel):
    """Model for competitor comparison."""
    competitors: List[Dict[str, Any]]
    comparison_matrix: Dict[str, Dict[str, Any]]
    advantages: List[str]
    disadvantages: List[str]

class FeaturePriority(BaseModel):
    """Model for feature prioritization."""
    feature: str
    score: Dict[str, float]  # RICE or MoSCoW scores
    priority: str  # High, Medium, Low
    rationale: str

class IdeaExpansionResult(BaseModel):
    """Result model for idea expansion."""
    refined_idea: str
    value_propositions: List[ValueProposition]
    unique_selling_points: List[UniqueSellingPoint]
    competitor_comparison: Optional[CompetitorComparison] = None
    feature_prioritization: List[FeaturePriority]

class IdeaExpander:
    """
    Idea Expander class that handles the expansion of initial ideas.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the Idea Expander.
        
        Args:
            openai_api_key: OpenAI API key (optional, can be set via environment variable)
        """
        # Use provided API key or get from config
        self.openai_api_key = openai_api_key or config.get_openai_api_key()
        
        # Set OpenAI API key
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("No OpenAI API key provided. API calls will fail.")
        
        # Get other configuration settings
        self.model = config.get_openai_model()
        self.temperature = config.get_temperature()
        self.max_tokens = config.get_max_tokens()
        
        logger.info(f"Initialized Idea Expander with model: {self.model}")
    
    def expand_idea(self, request: IdeaExpansionRequest) -> IdeaExpansionResult:
        """
        Expand an initial idea into a comprehensive result.
        
        Args:
            request: The idea expansion request
            
        Returns:
            The expanded idea result
        """
        logger.info(f"Expanding idea: {request.original_idea}")
        
        # Generate refined idea
        refined_idea = self._generate_refined_idea(request)
        
        # Generate value propositions
        value_propositions = self._generate_value_propositions(request, refined_idea)
        
        # Generate unique selling points
        unique_selling_points = self._generate_unique_selling_points(request, refined_idea)
        
        # Generate competitor comparison
        competitor_comparison = self._generate_competitor_comparison(request, refined_idea)
        
        # Generate feature prioritization
        feature_prioritization = self._generate_feature_prioritization(request, refined_idea)
        
        # Create and return the result
        result = IdeaExpansionResult(
            refined_idea=refined_idea,
            value_propositions=value_propositions,
            unique_selling_points=unique_selling_points,
            competitor_comparison=competitor_comparison,
            feature_prioritization=feature_prioritization
        )
        
        logger.info(f"Idea expansion completed for: {request.original_idea}")
        return result
    
    def _generate_refined_idea(self, request: IdeaExpansionRequest) -> str:
        """Generate a refined idea statement."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            I have an initial idea for a software application: "{request.original_idea}"
            
            Please refine this idea into a clear, concise statement that explains:
            1. What the application does
            2. Who it's for
            3. What problem it solves
            4. How it's different from existing solutions
            
            The refined idea should be 2-3 sentences long and easy to understand.
            """
            
            if request.industry:
                prompt += f"\nThe target industry is: {request.industry}"
                
            if request.target_audience:
                prompt += f"\nThe target audience is: {request.target_audience}"
                
            if request.constraints:
                constraints_str = ", ".join(request.constraints)
                prompt += f"\nThe constraints to consider are: {constraints_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert product manager and idea refiner."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=min(self.max_tokens, 200)  # Limit to 200 tokens for refined idea
            )
            
            # Extract the refined idea from the response
            refined_idea = response.choices[0].message.content.strip()
            logger.info(f"Generated refined idea: {refined_idea}")
            
            return refined_idea
            
        except Exception as e:
            logger.error(f"Error generating refined idea: {str(e)}")
            # Fallback to a simple refinement
            return f"Refined version of: {request.original_idea}"
    
    def _generate_value_propositions(self, request: IdeaExpansionRequest, refined_idea: str) -> List[ValueProposition]:
        """Generate value propositions."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this refined software application idea: "{refined_idea}"
            
            Generate 3 compelling value propositions for this application. Each value proposition should include:
            1. A clear title (1-5 words)
            2. A detailed description (1-2 sentences)
            3. The potential impact for users (1 sentence)
            
            Format your response as a JSON array with objects containing "title", "description", and "impact" fields.
            Example:
            [
                {{
                    "title": "Time Savings",
                    "description": "Reduces task completion time by 40% through automated workflows and intelligent suggestions.",
                    "impact": "Users can focus on creative work instead of repetitive tasks."
                }},
                ...
            ]
            """
            
            if request.industry:
                prompt += f"\nThe target industry is: {request.industry}"
                
            if request.target_audience:
                prompt += f"\nThe target audience is: {request.target_audience}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert product manager and marketing strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=min(self.max_tokens, 500),  # Limit to 500 tokens for value propositions
                response_format={"type": "json_object"}
            )
            
            # Extract the value propositions from the response
            import json
            content = response.choices[0].message.content.strip()
            value_props_data = json.loads(content)
            
            # Convert to ValueProposition objects
            value_propositions = []
            for prop in value_props_data:
                value_propositions.append(
                    ValueProposition(
                        title=prop.get("title", ""),
                        description=prop.get("description", ""),
                        impact=prop.get("impact", "")
                    )
                )
            
            logger.info(f"Generated {len(value_propositions)} value propositions")
            return value_propositions
            
        except Exception as e:
            logger.error(f"Error generating value propositions: {str(e)}")
            # Fallback to default value propositions
            return [
                ValueProposition(
                    title="Efficiency",
                    description=f"This solution streamlines processes related to {request.original_idea}.",
                    impact="Users save time and reduce errors."
                ),
                ValueProposition(
                    title="Innovation",
                    description=f"A novel approach to {request.original_idea} that breaks new ground.",
                    impact="Users gain competitive advantage through cutting-edge technology."
                ),
                ValueProposition(
                    title="Accessibility",
                    description=f"Makes {request.original_idea} more accessible to a wider audience.",
                    impact="More users can benefit from this solution."
                )
            ]
    
    def _generate_unique_selling_points(self, request: IdeaExpansionRequest, refined_idea: str) -> List[UniqueSellingPoint]:
        """Generate unique selling points."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this refined software application idea: "{refined_idea}"
            
            Generate 5 unique selling points (USPs) that differentiate this application from competitors.
            Each USP should include:
            1. A concise point (3-7 words)
            2. A detailed description (1-2 sentences)
            3. How it differentiates from competitors (1 sentence)
            
            Format your response as a JSON array with objects containing "point", "description", and "differentiation" fields.
            Example:
            [
                {{
                    "point": "AI-Powered Personalization",
                    "description": "The application uses advanced AI algorithms to personalize the experience for each user based on their behavior and preferences.",
                    "differentiation": "Unlike competitors who offer generic experiences, our solution adapts to individual user needs."
                }},
                ...
            ]
            """
            
            if request.industry:
                prompt += f"\nThe target industry is: {request.industry}"
                
            if request.target_audience:
                prompt += f"\nThe target audience is: {request.target_audience}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert product strategist and marketing specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=min(self.max_tokens, 800),  # Limit to 800 tokens for USPs
                response_format={"type": "json_object"}
            )
            
            # Extract the USPs from the response
            import json
            content = response.choices[0].message.content.strip()
            usps_data = json.loads(content)
            
            # Convert to UniqueSellingPoint objects
            usps = []
            for usp in usps_data:
                usps.append(
                    UniqueSellingPoint(
                        point=usp.get("point", ""),
                        description=usp.get("description", ""),
                        differentiation=usp.get("differentiation", "")
                    )
                )
            
            logger.info(f"Generated {len(usps)} unique selling points")
            return usps
            
        except Exception as e:
            logger.error(f"Error generating unique selling points: {str(e)}")
            # Fallback to default USPs
            return [
                UniqueSellingPoint(
                    point="Innovative Approach",
                    description=f"A groundbreaking approach to {request.original_idea} that hasn't been seen before.",
                    differentiation="Competitors use conventional methods while we reimagine the solution."
                ),
                UniqueSellingPoint(
                    point="User-Centric Design",
                    description=f"Designed with the user's needs at the forefront for {request.original_idea}.",
                    differentiation="Unlike competitors who prioritize features over usability."
                ),
                UniqueSellingPoint(
                    point="Seamless Integration",
                    description=f"Integrates smoothly with existing workflows for {request.original_idea}.",
                    differentiation="Competitors require significant changes to current processes."
                ),
                UniqueSellingPoint(
                    point="Scalable Solution",
                    description=f"Scales effortlessly from small teams to enterprise for {request.original_idea}.",
                    differentiation="Competitors' solutions break down at scale."
                ),
                UniqueSellingPoint(
                    point="Data-Driven Insights",
                    description=f"Provides actionable insights based on user data for {request.original_idea}.",
                    differentiation="Competitors offer raw data without meaningful analysis."
                )
            ]
    
    def _generate_competitor_comparison(self, request: IdeaExpansionRequest, refined_idea: str) -> CompetitorComparison:
        """Generate competitor comparison."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this refined software application idea: "{refined_idea}"
            
            Generate a comprehensive competitor comparison analysis. Include:
            
            1. Identify 3-5 main competitors in this space
            2. Create a feature comparison matrix between the proposed idea and competitors
            3. List key advantages of the proposed idea over competitors
            4. List potential disadvantages or challenges the proposed idea might face
            
            Format your response as a JSON object with the following structure:
            {{
                "competitors": [
                    {{"name": "Competitor Name", "description": "Brief description of competitor"}},
                    ...
                ],
                "comparison_matrix": {{
                    "Feature 1": {{"Your Idea": "Yes/No/Partial", "Competitor 1": "Yes/No/Partial", ...}},
                    "Feature 2": {{"Your Idea": "Yes/No/Partial", "Competitor 1": "Yes/No/Partial", ...}},
                    ...
                }},
                "advantages": ["Advantage 1", "Advantage 2", ...],
                "disadvantages": ["Disadvantage 1", "Disadvantage 2", ...]
            }}
            """
            
            if request.industry:
                prompt += f"\nThe target industry is: {request.industry}"
                
            if request.target_audience:
                prompt += f"\nThe target audience is: {request.target_audience}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert market analyst and competitive intelligence specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,  # Use full max_tokens for competitor comparison
                response_format={"type": "json_object"}
            )
            
            # Extract the competitor comparison from the response
            import json
            content = response.choices[0].message.content.strip()
            comparison_data = json.loads(content)
            
            # Convert to CompetitorComparison object
            competitor_comparison = CompetitorComparison(
                competitors=comparison_data.get("competitors", []),
                comparison_matrix=comparison_data.get("comparison_matrix", {}),
                advantages=comparison_data.get("advantages", []),
                disadvantages=comparison_data.get("disadvantages", [])
            )
            
            logger.info(f"Generated competitor comparison with {len(competitor_comparison.competitors)} competitors")
            return competitor_comparison
            
        except Exception as e:
            logger.error(f"Error generating competitor comparison: {str(e)}")
            # Fallback to default competitor comparison
            return CompetitorComparison(
                competitors=[
                    {"name": f"Leading {request.original_idea} Solution", "description": "Current market leader with established presence"},
                    {"name": "Traditional Alternative", "description": "Conventional approach to solving the problem"},
                    {"name": "Emerging Competitor", "description": "New entrant with innovative but limited features"}
                ],
                comparison_matrix={
                    "User Experience": {"Your Idea": "Yes", "Leading Solution": "Partial", "Traditional Alternative": "No", "Emerging Competitor": "Yes"},
                    "Feature Completeness": {"Your Idea": "Yes", "Leading Solution": "Yes", "Traditional Alternative": "Yes", "Emerging Competitor": "No"},
                    "Innovation": {"Your Idea": "Yes", "Leading Solution": "No", "Traditional Alternative": "No", "Emerging Competitor": "Yes"},
                    "Scalability": {"Your Idea": "Yes", "Leading Solution": "Yes", "Traditional Alternative": "No", "Emerging Competitor": "Partial"},
                    "Cost Efficiency": {"Your Idea": "Yes", "Leading Solution": "No", "Traditional Alternative": "Yes", "Emerging Competitor": "Partial"}
                },
                advantages=[
                    "More intuitive user experience",
                    "Innovative approach to problem-solving",
                    "Better price-to-value ratio",
                    "More scalable architecture"
                ],
                disadvantages=[
                    "New entrant in established market",
                    "Less brand recognition",
                    "Potential initial feature gaps"
                ]
            )
    
    def _generate_feature_prioritization(self, request: IdeaExpansionRequest, refined_idea: str) -> List[FeaturePriority]:
        """Generate feature prioritization."""
        try:
            # Create a prompt for the OpenAI API
            prompt = f"""
            Based on this refined software application idea: "{refined_idea}"
            
            Generate a feature prioritization matrix using the RICE scoring model (Reach, Impact, Confidence, Effort).
            Identify 5-8 key features for this application and prioritize them.
            
            For each feature:
            1. Provide a clear feature name
            2. Score each dimension (Reach, Impact, Confidence, Effort) on a scale of 1-10
               - Reach: How many users will this feature affect? (1=very few, 10=almost all)
               - Impact: How much will this feature impact those users? (1=minimal, 10=transformative)
               - Confidence: How confident are you in these estimates? (1=very unsure, 10=very confident)
               - Effort: How much effort would it take to implement? (1=very little, 10=enormous)
            3. Calculate priority (High, Medium, Low) based on the RICE score
            4. Provide a rationale for this prioritization
            
            Format your response as a JSON array with objects containing "feature", "score", "priority", and "rationale" fields.
            Example:
            [
                {{
                    "feature": "User Authentication",
                    "score": {{"Reach": 10, "Impact": 8, "Confidence": 9, "Effort": 4}},
                    "priority": "High",
                    "rationale": "Essential security feature that affects all users and builds trust in the platform."
                }},
                ...
            ]
            """
            
            if request.industry:
                prompt += f"\nThe target industry is: {request.industry}"
                
            if request.target_audience:
                prompt += f"\nThe target audience is: {request.target_audience}"
                
            if request.constraints:
                constraints_str = ", ".join(request.constraints)
                prompt += f"\nThe constraints to consider are: {constraints_str}"
            
            # Call the OpenAI API
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert product manager and feature prioritization specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,  # Use full max_tokens for feature prioritization
                response_format={"type": "json_object"}
            )
            
            # Extract the feature prioritization from the response
            import json
            content = response.choices[0].message.content.strip()
            features_data = json.loads(content)
            
            # Convert to FeaturePriority objects
            feature_priorities = []
            for feature in features_data:
                feature_priorities.append(
                    FeaturePriority(
                        feature=feature.get("feature", ""),
                        score=feature.get("score", {}),
                        priority=feature.get("priority", ""),
                        rationale=feature.get("rationale", "")
                    )
                )
            
            logger.info(f"Generated {len(feature_priorities)} feature priorities")
            return feature_priorities
            
        except Exception as e:
            logger.error(f"Error generating feature prioritization: {str(e)}")
            # Fallback to default feature prioritization
            return [
                FeaturePriority(
                    feature="User Authentication & Authorization",
                    score={"Reach": 10, "Impact": 9, "Confidence": 10, "Effort": 5},
                    priority="High",
                    rationale="Essential security feature that affects all users and is fundamental to the application."
                ),
                FeaturePriority(
                    feature="Core Functionality",
                    score={"Reach": 10, "Impact": 10, "Confidence": 9, "Effort": 7},
                    priority="High",
                    rationale=f"The primary value proposition of {request.original_idea} that users will directly interact with."
                ),
                FeaturePriority(
                    feature="User Dashboard",
                    score={"Reach": 9, "Impact": 7, "Confidence": 8, "Effort": 4},
                    priority="High",
                    rationale="Central interface for users to access all features and visualize their data."
                ),
                FeaturePriority(
                    feature="Data Export/Import",
                    score={"Reach": 6, "Impact": 7, "Confidence": 8, "Effort": 5},
                    priority="Medium",
                    rationale="Important for data portability but not immediately essential for core functionality."
                ),
                FeaturePriority(
                    feature="Advanced Analytics",
                    score={"Reach": 5, "Impact": 8, "Confidence": 7, "Effort": 8},
                    priority="Medium",
                    rationale="Provides significant value to power users but requires substantial development effort."
                ),
                FeaturePriority(
                    feature="Mobile Application",
                    score={"Reach": 7, "Impact": 6, "Confidence": 7, "Effort": 9},
                    priority="Low",
                    rationale="Expands accessibility but can be developed after web version is established."
                ),
                FeaturePriority(
                    feature="Third-party Integrations",
                    score={"Reach": 4, "Impact": 6, "Confidence": 6, "Effort": 7},
                    priority="Low",
                    rationale="Enhances functionality but not critical for initial MVP launch."
                )
            ]