"""
AI Debugging & Thought Process Tracer for Code Learning

This module provides functionality for simulating debugging processes and
tracing thought processes for code learning. It helps users understand
debugging strategies and identify misconceptions in their reasoning.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
import re
import ast
import traceback
from dataclasses import dataclass, asdict, field
from enum import Enum

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface

# Set up logging
logger = logging.getLogger(__name__)

class BugType(Enum):
    """Types of bugs that can be simulated"""
    SYNTAX_ERROR = "syntax_error"
    LOGIC_ERROR = "logic_error"
    RUNTIME_ERROR = "runtime_error"
    SEMANTIC_ERROR = "semantic_error"
    PERFORMANCE_ISSUE = "performance_issue"
    EDGE_CASE = "edge_case"

@dataclass
class DebuggingStep:
    """Class representing a step in the debugging process"""
    id: Optional[int] = None
    session_id: int = 0
    step_number: int = 0
    action: str = ""
    observation: str = ""
    hypothesis: str = ""
    timestamp: str = ""

@dataclass
class TestCase:
    """Class representing a test case for debugging"""
    id: Optional[int] = None
    session_id: int = 0
    input_data: str = ""
    expected_output: str = ""
    actual_output: str = ""
    is_passing: bool = False

class CodeDebugger:
    """
    AI Debugging & Thought Process Tracer for Code Learning
    
    Features:
    - Debugging Simulation Mode: Guide users through debugging process
    - Thought Process Reflection: Identify misconceptions in user reasoning
    - Test Case Generation: Automatically generate test cases for code
    """
    
    def __init__(self, db_manager: DatabaseManager, llm_interface: Optional[LLMInterface] = None):
        """Initialize the code debugger"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create debugging sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS debugging_sessions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            code_snippet TEXT NOT NULL,
            language TEXT NOT NULL,
            bug_type TEXT,
            description TEXT,
            is_completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create debugging steps table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS debugging_steps (
            id INTEGER PRIMARY KEY,
            session_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            action TEXT NOT NULL,
            observation TEXT NOT NULL,
            hypothesis TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES debugging_sessions(id)
        )
        ''')
        
        # Create test cases table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS debugging_test_cases (
            id INTEGER PRIMARY KEY,
            session_id INTEGER NOT NULL,
            input_data TEXT NOT NULL,
            expected_output TEXT NOT NULL,
            actual_output TEXT,
            is_passing BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (session_id) REFERENCES debugging_sessions(id)
        )
        ''')
        
        # Create thought process reflections table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS thought_process_reflections (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            code_snippet TEXT NOT NULL,
            user_explanation TEXT NOT NULL,
            ai_feedback TEXT NOT NULL,
            misconceptions TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
    
    def create_debugging_session(self, user_id: int, code_snippet: str, 
                               language: str, bug_type: Optional[BugType] = None,
                               description: Optional[str] = None) -> int:
        """
        Create a new debugging session
        
        Args:
            user_id: The ID of the user
            code_snippet: The buggy code snippet
            language: The programming language of the code
            bug_type: Optional type of bug to simulate
            description: Optional description of the bug
            
        Returns:
            The ID of the created debugging session
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO debugging_sessions 
        (user_id, code_snippet, language, bug_type, description, is_completed, created_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
        ''', (user_id, code_snippet, language, 
             bug_type.value if bug_type else None, 
             description, created_at))
        
        session_id = cursor.lastrowid
        conn.commit()
        
        # Generate test cases for the debugging session
        self.generate_test_cases(session_id)
        
        return session_id
    
    def get_debugging_session(self, session_id: int) -> Dict[str, Any]:
        """
        Get a debugging session by ID
        
        Args:
            session_id: The ID of the debugging session
            
        Returns:
            Dictionary with session details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, code_snippet, language, bug_type, description, 
               is_completed, created_at, completed_at
        FROM debugging_sessions
        WHERE id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        session = {
            'id': row[0],
            'user_id': row[1],
            'code_snippet': row[2],
            'language': row[3],
            'bug_type': row[4],
            'description': row[5],
            'is_completed': bool(row[6]),
            'created_at': row[7],
            'completed_at': row[8]
        }
        
        # Get debugging steps
        cursor.execute('''
        SELECT id, step_number, action, observation, hypothesis, timestamp
        FROM debugging_steps
        WHERE session_id = ?
        ORDER BY step_number
        ''', (session_id,))
        
        steps = []
        for row in cursor.fetchall():
            step = {
                'id': row[0],
                'step_number': row[1],
                'action': row[2],
                'observation': row[3],
                'hypothesis': row[4],
                'timestamp': row[5]
            }
            steps.append(step)
        
        session['steps'] = steps
        
        # Get test cases
        cursor.execute('''
        SELECT id, input_data, expected_output, actual_output, is_passing
        FROM debugging_test_cases
        WHERE session_id = ?
        ''', (session_id,))
        
        test_cases = []
        for row in cursor.fetchall():
            test_case = {
                'id': row[0],
                'input_data': row[1],
                'expected_output': row[2],
                'actual_output': row[3],
                'is_passing': bool(row[4])
            }
            test_cases.append(test_case)
        
        session['test_cases'] = test_cases
        
        return session
    
    def add_debugging_step(self, session_id: int, action: str, 
                         observation: str, hypothesis: str) -> int:
        """
        Add a step to a debugging session
        
        Args:
            session_id: The ID of the debugging session
            action: The action taken in this step
            observation: The observation made after the action
            hypothesis: The hypothesis about the bug based on the observation
            
        Returns:
            The ID of the created debugging step
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get the next step number
        cursor.execute('''
        SELECT MAX(step_number) FROM debugging_steps WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        next_step = (row[0] or 0) + 1
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO debugging_steps 
        (session_id, step_number, action, observation, hypothesis, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, next_step, action, observation, hypothesis, timestamp))
        
        step_id = cursor.lastrowid
        conn.commit()
        
        return step_id
    
    def complete_debugging_session(self, session_id: int) -> None:
        """
        Mark a debugging session as completed
        
        Args:
            session_id: The ID of the debugging session
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime
        completed_at = datetime.now().isoformat()
        
        cursor.execute('''
        UPDATE debugging_sessions
        SET is_completed = 1, completed_at = ?
        WHERE id = ?
        ''', (completed_at, session_id))
        
        conn.commit()
    
    def generate_test_cases(self, session_id: int, num_cases: int = 3) -> List[Dict[str, Any]]:
        """
        Generate test cases for a debugging session
        
        Args:
            session_id: The ID of the debugging session
            num_cases: Number of test cases to generate
            
        Returns:
            List of generated test cases
        """
        # Get the debugging session
        session = self.get_debugging_session(session_id)
        
        if not session:
            logger.error(f"Debugging session {session_id} not found")
            return []
        
        code_snippet = session.get('code_snippet', '')
        language = session.get('language', 'python')
        bug_type = session.get('bug_type', '')
        
        # Prepare prompt for LLM
        prompt = f"""
        Generate {num_cases} test cases for the following {language} code that has a bug.
        
        Code:
        ```{language}
        {code_snippet}
        ```
        
        Bug type: {bug_type or "Unknown"}
        
        For each test case, provide:
        1. Input data
        2. Expected output (what the code should produce if it worked correctly)
        
        Format your response as JSON:
        ```json
        [
          {{
            "input_data": "Input for test case 1",
            "expected_output": "Expected output for test case 1"
          }},
          ...
        ]
        ```
        
        Include test cases that would specifically help identify the bug.
        Include at least one edge case that might trigger the bug.
        """
        
        # Generate test cases using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
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
            test_cases_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        # Store test cases in database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        stored_test_cases = []
        for tc in test_cases_data:
            input_data = tc.get('input_data', '')
            expected_output = tc.get('expected_output', '')
            
            cursor.execute('''
            INSERT INTO debugging_test_cases 
            (session_id, input_data, expected_output, is_passing)
            VALUES (?, ?, ?, 0)
            ''', (session_id, input_data, expected_output))
            
            test_case_id = cursor.lastrowid
            
            stored_test_cases.append({
                'id': test_case_id,
                'input_data': input_data,
                'expected_output': expected_output,
                'actual_output': None,
                'is_passing': False
            })
        
        conn.commit()
        
        return stored_test_cases
    
    def run_test_cases(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Run test cases for a debugging session
        
        Args:
            session_id: The ID of the debugging session
            
        Returns:
            List of updated test cases with results
        """
        # Get the debugging session
        session = self.get_debugging_session(session_id)
        
        if not session:
            logger.error(f"Debugging session {session_id} not found")
            return []
        
        code_snippet = session.get('code_snippet', '')
        language = session.get('language', 'python')
        test_cases = session.get('test_cases', [])
        
        updated_test_cases = []
        
        # Only support Python for now
        if language.lower() != 'python':
            logger.warning(f"Test case execution not supported for language: {language}")
            return test_cases
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        for tc in test_cases:
            test_case_id = tc.get('id')
            input_data = tc.get('input_data', '')
            expected_output = tc.get('expected_output', '')
            
            # Prepare code for execution with the test input
            # This is a simplified approach and might not work for all code snippets
            test_code = f"""
{code_snippet}

# Test input
test_input = {input_data}

# Run the code with the test input
try:
    result = None
    # Try to identify the main function or entry point
    import inspect
    import re
    
    # Look for function definitions
    function_matches = re.finditer(r'def\\s+([a-zA-Z0-9_]+)\\s*\\(', {repr(code_snippet)})
    functions = [match.group(1) for match in function_matches]
    
    if functions:
        # Assume the last defined function is the main one
        main_function = functions[-1]
        # Get the function from locals
        func = locals()[main_function]
        # Inspect the function signature
        sig = inspect.signature(func)
        param_count = len(sig.parameters)
        
        if param_count == 0:
            result = func()
        elif param_count == 1:
            result = func(test_input)
        else:
            # Try to unpack the input if it's a collection
            try:
                if isinstance(test_input, (list, tuple)):
                    result = func(*test_input)
                elif isinstance(test_input, dict):
                    result = func(**test_input)
                else:
                    result = func(test_input)
            except:
                result = func(test_input)
    else:
        # No functions found, try to evaluate the last expression
        lines = {repr(code_snippet)}.strip().split('\\n')
        last_line = lines[-1].strip()
        if not last_line.startswith(('def ', 'class ', 'import ', 'from ')):
            # Replace variable references with the test input
            modified_line = last_line
            # This is a very simplified approach
            if 'input(' in modified_line:
                modified_line = modified_line.replace('input()', repr(test_input))
                modified_line = modified_line.replace('input("', repr(test_input))
                modified_line = modified_line.replace("input('", repr(test_input))
            result = eval(modified_line)
        else:
            # Just try to use the test input directly
            result = test_input
    
    print(repr(result))
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
"""
            
            # Execute the test code in a safe environment
            import subprocess
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(test_code.encode('utf-8'))
            
            try:
                result = subprocess.run(
                    ['python', temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=5  # Timeout after 5 seconds
                )
                
                actual_output = result.stdout.strip() or result.stderr.strip()
                
                # Check if the test passes
                is_passing = False
                try:
                    # Try to compare as Python objects
                    expected_obj = eval(expected_output)
                    actual_obj = eval(actual_output) if 'ERROR:' not in actual_output else actual_output
                    is_passing = expected_obj == actual_obj
                except:
                    # Fall back to string comparison
                    is_passing = expected_output.strip() == actual_output.strip()
                
                # Update the test case in the database
                cursor.execute('''
                UPDATE debugging_test_cases
                SET actual_output = ?, is_passing = ?
                WHERE id = ?
                ''', (actual_output, 1 if is_passing else 0, test_case_id))
                
                updated_test_cases.append({
                    'id': test_case_id,
                    'input_data': input_data,
                    'expected_output': expected_output,
                    'actual_output': actual_output,
                    'is_passing': is_passing
                })
                
            except subprocess.TimeoutExpired:
                actual_output = "ERROR: Execution timed out"
                cursor.execute('''
                UPDATE debugging_test_cases
                SET actual_output = ?, is_passing = 0
                WHERE id = ?
                ''', (actual_output, test_case_id))
                
                updated_test_cases.append({
                    'id': test_case_id,
                    'input_data': input_data,
                    'expected_output': expected_output,
                    'actual_output': actual_output,
                    'is_passing': False
                })
            
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
        
        conn.commit()
        
        return updated_test_cases
    
    def predict_bug_causes(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Predict potential causes of the bug in a debugging session
        
        Args:
            session_id: The ID of the debugging session
            
        Returns:
            List of potential bug causes with explanations
        """
        # Get the debugging session
        session = self.get_debugging_session(session_id)
        
        if not session:
            logger.error(f"Debugging session {session_id} not found")
            return []
        
        code_snippet = session.get('code_snippet', '')
        language = session.get('language', 'python')
        bug_type = session.get('bug_type', '')
        test_cases = session.get('test_cases', [])
        
        # Format test cases for the prompt
        test_cases_text = ""
        for i, tc in enumerate(test_cases, 1):
            test_cases_text += f"Test Case {i}:\n"
            test_cases_text += f"Input: {tc.get('input_data', '')}\n"
            test_cases_text += f"Expected Output: {tc.get('expected_output', '')}\n"
            test_cases_text += f"Actual Output: {tc.get('actual_output', 'Not run yet')}\n"
            test_cases_text += f"Passing: {tc.get('is_passing', False)}\n\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        Analyze the following {language} code that has a bug and predict the most likely causes.
        
        Code:
        ```{language}
        {code_snippet}
        ```
        
        Bug type: {bug_type or "Unknown"}
        
        Test Cases:
        {test_cases_text}
        
        Predict the top 3 most likely causes of the bug, ordered by probability.
        For each cause, provide:
        1. A brief description of the cause
        2. An explanation of why this might be causing the observed behavior
        3. A suggestion for how to fix it
        
        Format your response as JSON:
        ```json
        [
          {{
            "cause": "Brief description of cause 1",
            "explanation": "Detailed explanation of why this is likely the cause",
            "fix_suggestion": "Suggestion for how to fix this issue"
          }},
          ...
        ]
        ```
        """
        
        # Generate bug causes using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
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
            causes = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        return causes
    
    def suggest_debugging_strategies(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Suggest debugging strategies for a debugging session
        
        Args:
            session_id: The ID of the debugging session
            
        Returns:
            List of suggested debugging strategies
        """
        # Get the debugging session
        session = self.get_debugging_session(session_id)
        
        if not session:
            logger.error(f"Debugging session {session_id} not found")
            return []
        
        code_snippet = session.get('code_snippet', '')
        language = session.get('language', 'python')
        bug_type = session.get('bug_type', '')
        test_cases = session.get('test_cases', [])
        
        # Format test cases for the prompt
        test_cases_text = ""
        for i, tc in enumerate(test_cases, 1):
            test_cases_text += f"Test Case {i}:\n"
            test_cases_text += f"Input: {tc.get('input_data', '')}\n"
            test_cases_text += f"Expected Output: {tc.get('expected_output', '')}\n"
            test_cases_text += f"Actual Output: {tc.get('actual_output', 'Not run yet')}\n"
            test_cases_text += f"Passing: {tc.get('is_passing', False)}\n\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        Suggest debugging strategies for the following {language} code that has a bug.
        
        Code:
        ```{language}
        {code_snippet}
        ```
        
        Bug type: {bug_type or "Unknown"}
        
        Test Cases:
        {test_cases_text}
        
        Suggest 3-5 specific debugging strategies that would be effective for this particular bug.
        For each strategy, provide:
        1. A name for the strategy
        2. A step-by-step process for applying this strategy
        3. What to look for when using this strategy
        4. Why this strategy would be effective for this type of bug
        
        Format your response as JSON:
        ```json
        [
          {{
            "strategy_name": "Name of strategy 1",
            "steps": ["Step 1", "Step 2", ...],
            "what_to_look_for": "What to look for when using this strategy",
            "why_effective": "Why this strategy would be effective for this bug"
          }},
          ...
        ]
        ```
        """
        
        # Generate debugging strategies using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
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
            strategies = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return []
        
        return strategies
    
    def analyze_thought_process(self, user_id: int, code_snippet: str, 
                              user_explanation: str) -> Dict[str, Any]:
        """
        Analyze a user's thought process about code and identify misconceptions
        
        Args:
            user_id: The ID of the user
            code_snippet: The code snippet being explained
            user_explanation: The user's explanation of what they think is happening in the code
            
        Returns:
            Dictionary with AI feedback and identified misconceptions
        """
        # Prepare prompt for LLM
        prompt = f"""
        Analyze a user's explanation of what they think is happening in the following code:
        
        Code:
        ```
        {code_snippet}
        ```
        
        User's explanation:
        "{user_explanation}"
        
        Your task is to:
        1. Identify any misconceptions in the user's understanding
        2. Provide a correct explanation of what the code actually does
        3. Suggest specific learning resources or exercises that would help clarify these concepts
        
        Format your response as JSON:
        ```json
        {{
          "misconceptions": [
            {{
              "misconception": "Description of misconception 1",
              "correction": "Correct understanding",
              "importance": "Why this misconception is important to address"
            }},
            ...
          ],
          "correct_explanation": "Detailed explanation of what the code actually does",
          "learning_resources": [
            {{
              "resource_type": "Type of resource (article, video, exercise, etc.)",
              "description": "Description of the resource",
              "why_helpful": "Why this resource would be helpful for this specific misconception"
            }},
            ...
          ]
        }}
        ```
        
        Be constructive and supportive in your feedback. Focus on helping the user build a correct mental model.
        """
        
        # Generate analysis using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without the markdown code block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                logger.error("Failed to extract JSON from LLM response")
                return {}
        
        try:
            analysis = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {}
        
        # Store the analysis in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        from datetime import datetime
        created_at = datetime.now().isoformat()
        
        # Convert misconceptions to a string for storage
        misconceptions_json = json.dumps(analysis.get('misconceptions', []))
        
        cursor.execute('''
        INSERT INTO thought_process_reflections 
        (user_id, code_snippet, user_explanation, ai_feedback, misconceptions, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, code_snippet, user_explanation, 
             analysis.get('correct_explanation', ''), 
             misconceptions_json, created_at))
        
        reflection_id = cursor.lastrowid
        conn.commit()
        
        # Add the ID to the analysis
        analysis['id'] = reflection_id
        
        return analysis
    
    def get_thought_process_reflection(self, reflection_id: int) -> Dict[str, Any]:
        """
        Get a thought process reflection by ID
        
        Args:
            reflection_id: The ID of the reflection
            
        Returns:
            Dictionary with reflection details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, code_snippet, user_explanation, ai_feedback, misconceptions, created_at
        FROM thought_process_reflections
        WHERE id = ?
        ''', (reflection_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        # Parse misconceptions from JSON
        try:
            misconceptions = json.loads(row[5]) if row[5] else []
        except json.JSONDecodeError:
            misconceptions = []
        
        reflection = {
            'id': row[0],
            'user_id': row[1],
            'code_snippet': row[2],
            'user_explanation': row[3],
            'correct_explanation': row[4],
            'misconceptions': misconceptions,
            'created_at': row[6]
        }
        
        return reflection

# Helper functions for easier access to code debugger functionality

def create_debugging_session(db_manager, user_id: int, code_snippet: str, 
                           language: str, bug_type: Optional[str] = None,
                           description: Optional[str] = None) -> int:
    """
    Create a new debugging session
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        code_snippet: The buggy code snippet
        language: The programming language of the code
        bug_type: Optional type of bug to simulate
        description: Optional description of the bug
        
    Returns:
        The ID of the created debugging session
    """
    debugger = CodeDebugger(db_manager)
    bug_type_enum = BugType(bug_type) if bug_type else None
    return debugger.create_debugging_session(user_id, code_snippet, language, bug_type_enum, description)

def analyze_thought_process(db_manager, user_id: int, code_snippet: str, 
                          user_explanation: str) -> Dict[str, Any]:
    """
    Analyze a user's thought process about code and identify misconceptions
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        code_snippet: The code snippet being explained
        user_explanation: The user's explanation of what they think is happening in the code
        
    Returns:
        Dictionary with AI feedback and identified misconceptions
    """
    debugger = CodeDebugger(db_manager)
    return debugger.analyze_thought_process(user_id, code_snippet, user_explanation)

def predict_bug_causes(db_manager, session_id: int) -> List[Dict[str, Any]]:
    """
    Predict potential causes of the bug in a debugging session
    
    Args:
        db_manager: Database manager instance
        session_id: The ID of the debugging session
        
    Returns:
        List of potential bug causes with explanations
    """
    debugger = CodeDebugger(db_manager)
    return debugger.predict_bug_causes(session_id)

def suggest_debugging_strategies(db_manager, session_id: int) -> List[Dict[str, Any]]:
    """
    Suggest debugging strategies for a debugging session
    
    Args:
        db_manager: Database manager instance
        session_id: The ID of the debugging session
        
    Returns:
        List of suggested debugging strategies
    """
    debugger = CodeDebugger(db_manager)
    return debugger.suggest_debugging_strategies(session_id)