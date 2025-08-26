"""
Automated Ethics & Bias Analyzer for Notes & Code

This module provides functionality for scanning ML projects and notes for potential
ethical issues and biases, and generating suggestions for improvements.
"""

import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import ast

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class EthicsCategory:
    """Categories of ethical issues and biases"""
    DATASET_BIAS = "dataset_bias"
    ALGORITHMIC_BIAS = "algorithmic_bias"
    PRIVACY_CONCERN = "privacy_concern"
    FAIRNESS_ISSUE = "fairness_issue"
    TRANSPARENCY_ISSUE = "transparency_issue"
    ACCOUNTABILITY_ISSUE = "accountability_issue"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    SOCIAL_IMPACT = "social_impact"
    OVERGENERALIZATION = "overgeneralization"
    MISREPRESENTATION = "misrepresentation"

class EthicsAnalyzer:
    """
    Automated Ethics & Bias Analyzer for Notes & Code
    
    Features:
    - Scan ML projects for potential dataset biases
    - Scan notes for overgeneralized statements
    - Identify ethical risks in algorithm design
    - Provide actionable suggestions for improvement
    - Link to relevant case studies
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None):
        """Initialize the ethics analyzer"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create ethics analysis table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ethics_analyses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            content_type TEXT NOT NULL,
            content_id INTEGER,
            content_text TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create ethics issues table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ethics_issues (
            id INTEGER PRIMARY KEY,
            analysis_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            severity INTEGER NOT NULL,
            description TEXT NOT NULL,
            suggestion TEXT NOT NULL,
            case_study_url TEXT,
            resolved BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (analysis_id) REFERENCES ethics_analyses(id)
        )
        ''')
        
        conn.commit()
    
    def analyze_ml_project(self, user_id: int, project_code: str, 
                         project_description: Optional[str] = None,
                         project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze an ML project for ethical issues and biases
        
        Args:
            user_id: The ID of the user
            project_code: The code of the ML project
            project_description: Optional description of the project
            project_id: Optional ID of the project in the database
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing ML project for ethical issues and biases")
        
        # Create an analysis record
        analysis_id = self._create_analysis_record(
            user_id, 
            "ml_project", 
            project_id, 
            project_code
        )
        
        # Extract dataset information from the code
        dataset_info = self._extract_dataset_info(project_code)
        
        # Extract model information from the code
        model_info = self._extract_model_info(project_code)
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert in AI ethics and bias detection. Analyze the following ML project code and description for potential ethical issues and biases.
        
        Project Description:
        {project_description or "No description provided."}
        
        Project Code:
        ```python
        {project_code}
        ```
        
        Dataset Information:
        {dataset_info}
        
        Model Information:
        {model_info}
        
        Identify potential ethical issues and biases in the following categories:
        1. Dataset Bias: Biases in the training data that could lead to unfair outcomes
        2. Algorithmic Bias: Biases in the algorithm design or implementation
        3. Privacy Concerns: Potential privacy violations or data security issues
        4. Fairness Issues: Potential unfairness in model predictions or outcomes
        5. Transparency Issues: Lack of explainability or interpretability
        6. Accountability Issues: Lack of mechanisms for addressing errors or harms
        7. Environmental Impact: Excessive computational resources or energy consumption
        8. Social Impact: Potential negative societal impacts
        
        For each issue identified, provide:
        1. Category: One of the categories listed above
        2. Severity: A rating from 1 (minor) to 5 (critical)
        3. Description: A clear description of the issue
        4. Suggestion: An actionable suggestion for addressing the issue
        5. Case Study: A reference to a relevant case study or example (if applicable)
        
        Format your response as JSON:
        ```json
        [
          {
            "category": "dataset_bias",
            "severity": 4,
            "description": "The dataset appears to lack diversity in...",
            "suggestion": "Include more diverse samples by...",
            "case_study": "https://example.com/case-study"
          },
          ...
        ]
        ```
        
        If no issues are found in a particular category, do not include it in the response.
        """
        
        # Generate analysis using LLM
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
                return {'error': 'Failed to extract analysis results'}
        
        try:
            issues = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {'error': 'Failed to parse analysis results'}
        
        # Store issues in the database
        self._store_issues(analysis_id, issues)
        
        return {
            'analysis_id': analysis_id,
            'issues': issues,
            'issues_count': len(issues),
            'highest_severity': max([issue.get('severity', 0) for issue in issues]) if issues else 0
        }
    
    def analyze_note(self, user_id: int, note_content: str, 
                   note_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze a note for ethical issues and biases
        
        Args:
            user_id: The ID of the user
            note_content: The content of the note
            note_id: Optional ID of the note in the database
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("Analyzing note for ethical issues and biases")
        
        # Create an analysis record
        analysis_id = self._create_analysis_record(
            user_id, 
            "note", 
            note_id, 
            note_content
        )
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert in identifying ethical issues, biases, and overgeneralizations in written content. Analyze the following note for potential issues.
        
        Note Content:
        {note_content}
        
        Identify potential issues in the following categories:
        1. Overgeneralization: Statements that make broad claims without sufficient evidence or nuance
        2. Misrepresentation: Inaccurate or misleading representations of concepts, groups, or ideas
        3. Bias: Language that reflects implicit or explicit bias
        4. Privacy Concern: Content that might violate privacy norms or expectations
        5. Fairness Issue: Content that might perpetuate unfair treatment or stereotypes
        6. Social Impact: Content that might have negative societal impacts
        
        For each issue identified, provide:
        1. Category: One of the categories listed above
        2. Severity: A rating from 1 (minor) to 5 (critical)
        3. Description: A clear description of the issue, including the specific text that is problematic
        4. Suggestion: An actionable suggestion for addressing the issue
        5. Case Study: A reference to a relevant case study or example (if applicable)
        
        Format your response as JSON:
        ```json
        [
          {
            "category": "overgeneralization",
            "severity": 3,
            "description": "The statement 'All machine learning models are biased' is an overgeneralization that...",
            "suggestion": "Revise to acknowledge that while many ML models can exhibit bias, the extent and nature varies...",
            "case_study": "https://example.com/case-study"
          },
          ...
        ]
        ```
        
        If no issues are found in a particular category, do not include it in the response.
        Be thoughtful and nuanced in your analysis. Focus on substantive issues rather than minor stylistic concerns.
        """
        
        # Generate analysis using LLM
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
                return {'error': 'Failed to extract analysis results'}
        
        try:
            issues = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {'error': 'Failed to parse analysis results'}
        
        # Store issues in the database
        self._store_issues(analysis_id, issues)
        
        return {
            'analysis_id': analysis_id,
            'issues': issues,
            'issues_count': len(issues),
            'highest_severity': max([issue.get('severity', 0) for issue in issues]) if issues else 0
        }
    
    def get_analysis(self, analysis_id: int) -> Dict[str, Any]:
        """
        Get an ethics analysis by ID
        
        Args:
            analysis_id: The ID of the analysis
            
        Returns:
            Dictionary with analysis details and issues
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, content_type, content_id, content_text, created_at
        FROM ethics_analyses
        WHERE id = ?
        ''', (analysis_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        analysis = {
            'id': row[0],
            'user_id': row[1],
            'content_type': row[2],
            'content_id': row[3],
            'content_text': row[4],
            'created_at': row[5],
            'issues': []
        }
        
        # Get issues for the analysis
        cursor.execute('''
        SELECT id, category, severity, description, suggestion, case_study_url, resolved
        FROM ethics_issues
        WHERE analysis_id = ?
        ORDER BY severity DESC
        ''', (analysis_id,))
        
        for row in cursor.fetchall():
            issue = {
                'id': row[0],
                'category': row[1],
                'severity': row[2],
                'description': row[3],
                'suggestion': row[4],
                'case_study': row[5],
                'resolved': bool(row[6])
            }
            analysis['issues'].append(issue)
        
        return analysis
    
    def get_user_analyses(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get ethics analyses for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of analyses to return
            
        Returns:
            List of analysis summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT a.id, a.content_type, a.content_id, a.created_at,
               COUNT(i.id) as issues_count,
               MAX(i.severity) as highest_severity
        FROM ethics_analyses a
        LEFT JOIN ethics_issues i ON a.id = i.analysis_id
        WHERE a.user_id = ?
        GROUP BY a.id
        ORDER BY a.created_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        analyses = []
        for row in cursor.fetchall():
            analysis = {
                'id': row[0],
                'content_type': row[1],
                'content_id': row[2],
                'created_at': row[3],
                'issues_count': row[4],
                'highest_severity': row[5] or 0
            }
            analyses.append(analysis)
        
        return analyses
    
    def mark_issue_resolved(self, issue_id: int, resolved: bool = True) -> bool:
        """
        Mark an ethics issue as resolved or unresolved
        
        Args:
            issue_id: The ID of the issue
            resolved: Whether the issue is resolved
            
        Returns:
            True if the issue was updated, False otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE ethics_issues
        SET resolved = ?
        WHERE id = ?
        ''', (1 if resolved else 0, issue_id))
        
        conn.commit()
        
        return cursor.rowcount > 0
    
    def generate_improvement_suggestions(self, analysis_id: int) -> Dict[str, Any]:
        """
        Generate detailed suggestions for improving a project or note based on ethics analysis
        
        Args:
            analysis_id: The ID of the analysis
            
        Returns:
            Dictionary with improvement suggestions
        """
        # Get the analysis
        analysis = self.get_analysis(analysis_id)
        
        if not analysis:
            return {'error': 'Analysis not found'}
        
        # Get unresolved issues
        unresolved_issues = [issue for issue in analysis.get('issues', []) if not issue.get('resolved', False)]
        
        if not unresolved_issues:
            return {'message': 'No unresolved issues to address'}
        
        content_type = analysis.get('content_type', '')
        content_text = analysis.get('content_text', '')
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert in AI ethics and bias mitigation. Generate detailed suggestions for improving the following {content_type} based on the identified ethical issues.
        
        {content_type.capitalize()} Content:
        ```
        {content_text[:2000]}  # Limit to first 2000 chars to avoid token limits
        ```
        
        Identified Issues:
        {json.dumps(unresolved_issues, indent=2)}
        
        For each issue, provide:
        1. A detailed explanation of why this is an issue
        2. Specific, actionable steps to address the issue
        3. Examples of how the content could be improved
        4. References to best practices or resources for further learning
        
        Format your response as markdown with clear sections for each issue.
        """
        
        # Generate suggestions using LLM
        suggestions = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        return {
            'analysis_id': analysis_id,
            'content_type': content_type,
            'issues_count': len(unresolved_issues),
            'suggestions': suggestions
        }
    
    def _create_analysis_record(self, user_id: int, content_type: str,
                              content_id: Optional[int] = None,
                              content_text: Optional[str] = None) -> int:
        """Create an ethics analysis record in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO ethics_analyses (user_id, content_type, content_id, content_text, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, content_type, content_id, content_text, created_at))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        
        return analysis_id
    
    def _store_issues(self, analysis_id: int, issues: List[Dict[str, Any]]) -> None:
        """Store ethics issues in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        for issue in issues:
            cursor.execute('''
            INSERT INTO ethics_issues (analysis_id, category, severity, description, suggestion, case_study_url, resolved)
            VALUES (?, ?, ?, ?, ?, ?, 0)
            ''', (
                analysis_id,
                issue.get('category', ''),
                issue.get('severity', 1),
                issue.get('description', ''),
                issue.get('suggestion', ''),
                issue.get('case_study', '')
            ))
        
        conn.commit()
    
    def _extract_dataset_info(self, code: str) -> str:
        """Extract dataset information from code"""
        dataset_info = "Could not extract dataset information."
        
        # Look for common dataset loading patterns
        dataset_patterns = [
            r'pd\.read_csv\([\'"](.+?)[\'"]\)',
            r'load_dataset\([\'"](.+?)[\'"]\)',
            r'datasets\.load_dataset\([\'"](.+?)[\'"]\)',
            r'ImageDataGenerator',
            r'DataLoader',
            r'TensorDataset',
            r'Dataset',
        ]
        
        matches = []
        for pattern in dataset_patterns:
            matches.extend(re.findall(pattern, code))
        
        if matches:
            dataset_info = "Potential dataset references found:\n"
            for match in matches:
                dataset_info += f"- {match}\n"
        
        # Try to parse the code and extract more information
        try:
            tree = ast.parse(code)
            
            # Look for variable assignments that might be datasets
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                            if 'data' in var_name or 'dataset' in var_name or 'corpus' in var_name:
                                dataset_info += f"- Variable '{target.id}' might be a dataset\n"
        except SyntaxError:
            # If code parsing fails, just continue with regex matches
            pass
        
        return dataset_info
    
    def _extract_model_info(self, code: str) -> str:
        """Extract model information from code"""
        model_info = "Could not extract model information."
        
        # Look for common model patterns
        model_patterns = [
            r'model\s*=\s*([A-Za-z0-9_]+)\(',
            r'([A-Za-z0-9_]+Model)\(',
            r'tf\.keras\.models\.([A-Za-z]+)\(',
            r'torch\.nn\.([A-Za-z]+)\(',
            r'nn\.([A-Za-z]+)\(',
            r'sklearn\.([A-Za-z0-9_.]+)\(',
        ]
        
        matches = []
        for pattern in model_patterns:
            matches.extend(re.findall(pattern, code))
        
        if matches:
            model_info = "Potential model references found:\n"
            for match in matches:
                model_info += f"- {match}\n"
        
        # Try to parse the code and extract more information
        try:
            tree = ast.parse(code)
            
            # Look for class definitions that might be models
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    if 'model' in class_name.lower() or 'net' in class_name.lower():
                        model_info += f"- Class '{class_name}' might be a model definition\n"
                        
                        # Check for inheritance from known model classes
                        for base in node.bases:
                            if isinstance(base, ast.Name):
                                model_info += f"  - Inherits from '{base.id}'\n"
        except SyntaxError:
            # If code parsing fails, just continue with regex matches
            pass
        
        return model_info

# Helper functions for easier access to ethics analyzer functionality

def analyze_ml_project(db_manager, user_id: int, project_code: str, 
                     project_description: Optional[str] = None,
                     project_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Analyze an ML project for ethical issues and biases
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        project_code: The code of the ML project
        project_description: Optional description of the project
        project_id: Optional ID of the project in the database
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = EthicsAnalyzer(db_manager)
    return analyzer.analyze_ml_project(user_id, project_code, project_description, project_id)

def analyze_note(db_manager, user_id: int, note_content: str, 
               note_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Analyze a note for ethical issues and biases
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        note_content: The content of the note
        note_id: Optional ID of the note in the database
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = EthicsAnalyzer(db_manager)
    return analyzer.analyze_note(user_id, note_content, note_id)

def generate_improvement_suggestions(db_manager, analysis_id: int) -> Dict[str, Any]:
    """
    Generate detailed suggestions for improving a project or note based on ethics analysis
    
    Args:
        db_manager: Database manager instance
        analysis_id: The ID of the analysis
        
    Returns:
        Dictionary with improvement suggestions
    """
    analyzer = EthicsAnalyzer(db_manager)
    return analyzer.generate_improvement_suggestions(analysis_id)