"""
Oracle Database Manager module for AI Note System.
Handles Oracle database operations for storing and retrieving notes.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

# Oracle database libraries
import oracledb
import os

# Setup logging
logger = logging.getLogger("ai_note_system.database.oracle_db_manager")

class OracleDatabaseManager:
    """
    Oracle Database manager class for AI Note System.
    Handles Oracle database operations for storing and retrieving notes.
    """
    
    def __init__(self, connection_string: str, username: str, password: str):
        """
        Initialize the OracleDatabaseManager.
        
        Args:
            connection_string (str): Oracle connection string
            username (str): Oracle database username
            password (str): Oracle database password
        """
        self.connection_string = connection_string
        self.username = username
        self.password = password
        self.conn = None
        self.cursor = None
        
        # Connect to database
        self.connect()
        
    def connect(self):
        """
        Connect to the Oracle database.
        """
        try:
            # Get wallet location from environment variable or use default
            wallet_location = os.environ.get('ORACLE_WALLET_LOCATION', '/app/wallet')
            
            # Configure the connection
            oracledb.init_oracle_client(lib_dir=os.environ.get('LD_LIBRARY_PATH', '/opt/oracle/instantclient*'))
            
            # Connect using wallet authentication
            self.conn = oracledb.connect(
                user=self.username,
                password=self.password,
                dsn=self.connection_string,
                config_dir=wallet_location,
                wallet_location=wallet_location,
                wallet_password=os.environ.get('ORACLE_WALLET_PASSWORD', '')
            )
            
            self.cursor = self.conn.cursor()
            
            logger.debug(f"Connected to Oracle database: {self.connection_string}")
        except Exception as e:
            logger.error(f"Error connecting to Oracle database: {e}")
            raise
            
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.debug("Oracle database connection closed")
            
    def __enter__(self):
        """
        Context manager entry.
        """
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        """
        self.close()
        
    # CRUD operations for users
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user in the database.
        
        Args:
            user_data (Dict[str, Any]): User data including email, password_hash, name
            
        Returns:
            str: ID of the created user
        """
        try:
            # Generate UUID for user ID
            user_id = str(uuid.uuid4())
            
            # Extract user fields
            email = user_data.get("email")
            password_hash = user_data.get("password_hash")
            name = user_data.get("name")
            
            self.cursor.execute("""
            INSERT INTO users (id, email, password_hash, name, created_at)
            VALUES (:id, :email, :password_hash, :name, CURRENT_TIMESTAMP)
            """, {
                'id': user_id,
                'email': email,
                'password_hash': password_hash,
                'name': name
            })
            
            self.conn.commit()
            
            logger.info(f"Created user with ID {user_id}: {email}")
            return user_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by ID.
        
        Args:
            user_id (str): ID of the user to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: User data or None if not found
        """
        try:
            self.cursor.execute("""
            SELECT id, email, name, created_at, last_login
            FROM users WHERE id = :id
            """, {'id': user_id})
            
            row = self.cursor.fetchone()
            if not row:
                return None
            
            # Convert to dictionary
            user_dict = {
                'id': row[0],
                'email': row[1],
                'name': row[2],
                'created_at': row[3],
                'last_login': row[4]
            }
            
            return user_dict
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    # CRUD operations for notes
    
    def create_note(self, note_data: Dict[str, Any]) -> str:
        """
        Create a new note in the database.
        
        Args:
            note_data (Dict[str, Any]): Note data including user_id, content, summary, tags
            
        Returns:
            str: ID of the created note
        """
        try:
            # Generate UUID for note ID
            note_id = str(uuid.uuid4())
            
            # Extract note fields
            user_id = note_data.get("user_id")
            content = note_data.get("content", "")
            summary = note_data.get("summary", None)
            tags = note_data.get("tags", "")
            
            self.cursor.execute("""
            INSERT INTO notes (id, user_id, content, summary, tags, created_at)
            VALUES (:id, :user_id, :content, :summary, :tags, CURRENT_TIMESTAMP)
            """, {
                'id': note_id,
                'user_id': user_id,
                'content': content,
                'summary': summary,
                'tags': tags
            })
            
            self.conn.commit()
            
            logger.info(f"Created note with ID {note_id}")
            return note_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating note: {e}")
            raise
    
    # CRUD operations for flashcards
    
    def create_flashcard(self, flashcard_data: Dict[str, Any]) -> str:
        """
        Create a new flashcard in the database.
        
        Args:
            flashcard_data (Dict[str, Any]): Flashcard data including note_id, question, answer, type
            
        Returns:
            str: ID of the created flashcard
        """
        try:
            # Generate UUID for flashcard ID
            flashcard_id = str(uuid.uuid4())
            
            # Extract flashcard fields
            note_id = flashcard_data.get("note_id")
            question = flashcard_data.get("question", "")
            answer = flashcard_data.get("answer", "")
            card_type = flashcard_data.get("type", "basic")
            
            # Uncomment when deploying to Oracle Cloud
            # self.cursor.execute("""
            # INSERT INTO flashcards (id, note_id, question, answer, type, created_at)
            # VALUES (:id, :note_id, :question, :answer, :type, CURRENT_TIMESTAMP)
            # """, {
            #     'id': flashcard_id,
            #     'note_id': note_id,
            #     'question': question,
            #     'answer': answer,
            #     'type': card_type
            # })
            # 
            # self.conn.commit()
            
            logger.info(f"Created flashcard with ID {flashcard_id}")
            return flashcard_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating flashcard: {e}")
            raise
    
    # CRUD operations for files
    
    def create_file(self, file_data: Dict[str, Any]) -> str:
        """
        Create a new file record in the database.
        
        Args:
            file_data (Dict[str, Any]): File data including user_id, filename, filepath, object_storage_url
            
        Returns:
            str: ID of the created file record
        """
        try:
            # Generate UUID for file ID
            file_id = str(uuid.uuid4())
            
            # Extract file fields
            user_id = file_data.get("user_id")
            filename = file_data.get("filename", "")
            filepath = file_data.get("filepath", "")
            object_storage_url = file_data.get("object_storage_url", "")
            
            self.cursor.execute("""
            INSERT INTO files (id, user_id, filename, filepath, object_storage_url, uploaded_at)
            VALUES (:id, :user_id, :filename, :filepath, :object_storage_url, CURRENT_TIMESTAMP)
            """, {
                'id': file_id,
                'user_id': user_id,
                'filename': filename,
                'filepath': filepath,
                'object_storage_url': object_storage_url
            })
            
            self.conn.commit()
            
            logger.info(f"Created file record with ID {file_id}: {filename}")
            return file_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating file record: {e}")
            raise
            
    # CRUD operations for study plans
    
    def create_study_plan(self, plan_data: Dict[str, Any]) -> str:
        """
        Create a new study plan in the database.
        
        Args:
            plan_data (Dict[str, Any]): Study plan data including user_id, topic, deadline
            
        Returns:
            str: ID of the created study plan
        """
        try:
            # Generate UUID for plan ID
            plan_id = str(uuid.uuid4())
            
            # Extract plan fields
            user_id = plan_data.get("user_id")
            topic = plan_data.get("topic", "")
            deadline = plan_data.get("deadline")
            
            self.cursor.execute("""
            INSERT INTO study_plans (id, user_id, topic, deadline, created_at, updated_at)
            VALUES (:id, :user_id, :topic, :deadline, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, {
                'id': plan_id,
                'user_id': user_id,
                'topic': topic,
                'deadline': deadline
            })
            
            self.conn.commit()
            
            logger.info(f"Created study plan with ID {plan_id} for user {user_id}")
            return plan_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating study plan: {e}")
            raise
            
    def get_study_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a study plan by ID.
        
        Args:
            plan_id (str): ID of the study plan to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Study plan data or None if not found
        """
        try:
            self.cursor.execute("""
            SELECT id, user_id, topic, deadline, created_at, updated_at
            FROM study_plans WHERE id = :id
            """, {'id': plan_id})
            
            row = self.cursor.fetchone()
            if not row:
                return None
            
            # Convert to dictionary
            plan_dict = {
                'id': row[0],
                'user_id': row[1],
                'topic': row[2],
                'deadline': row[3],
                'created_at': row[4],
                'updated_at': row[5]
            }
            
            # Get time blocks for this plan
            plan_dict['time_blocks'] = self.get_study_plan_blocks(plan_id)
            
            # Get goals for this plan
            plan_dict['goals'] = self.get_study_plan_goals(plan_id)
            
            return plan_dict
            
        except Exception as e:
            logger.error(f"Error getting study plan: {e}")
            return None
            
    def get_study_plans_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all study plans for a user.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of study plans
        """
        try:
            self.cursor.execute("""
            SELECT id, user_id, topic, deadline, created_at, updated_at
            FROM study_plans WHERE user_id = :user_id
            ORDER BY created_at DESC
            """, {'user_id': user_id})
            
            rows = self.cursor.fetchall()
            
            plans = []
            for row in rows:
                plan_dict = {
                    'id': row[0],
                    'user_id': row[1],
                    'topic': row[2],
                    'deadline': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
                plans.append(plan_dict)
            
            return plans
            
        except Exception as e:
            logger.error(f"Error getting study plans for user: {e}")
            return []
            
    def update_study_plan(self, plan_id: str, plan_data: Dict[str, Any]) -> bool:
        """
        Update a study plan.
        
        Args:
            plan_id (str): ID of the study plan to update
            plan_data (Dict[str, Any]): Updated study plan data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract plan fields
            topic = plan_data.get("topic")
            deadline = plan_data.get("deadline")
            
            # Build update query
            update_fields = []
            params = {'id': plan_id}
            
            if topic is not None:
                update_fields.append("topic = :topic")
                params['topic'] = topic
                
            if deadline is not None:
                update_fields.append("deadline = :deadline")
                params['deadline'] = deadline
                
            if not update_fields:
                return True  # Nothing to update
                
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            query = f"""
            UPDATE study_plans
            SET {', '.join(update_fields)}
            WHERE id = :id
            """
            
            self.cursor.execute(query, params)
            self.conn.commit()
            
            logger.info(f"Updated study plan with ID {plan_id}")
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error updating study plan: {e}")
            return False
            
    # CRUD operations for study plan blocks
    
    def create_study_plan_block(self, block_data: Dict[str, Any]) -> str:
        """
        Create a new time block for a study plan.
        
        Args:
            block_data (Dict[str, Any]): Block data including plan_id, start_time, end_time, title, description, weight
            
        Returns:
            str: ID of the created block
        """
        try:
            # Generate UUID for block ID
            block_id = str(uuid.uuid4())
            
            # Extract block fields
            plan_id = block_data.get("plan_id")
            start_time = block_data.get("start_time")
            end_time = block_data.get("end_time")
            title = block_data.get("title", "")
            description = block_data.get("description", "")
            weight = block_data.get("weight", 1.0)
            completed = block_data.get("completed", 0)
            
            self.cursor.execute("""
            INSERT INTO study_plan_blocks (id, plan_id, start_time, end_time, title, description, weight, completed)
            VALUES (:id, :plan_id, :start_time, :end_time, :title, :description, :weight, :completed)
            """, {
                'id': block_id,
                'plan_id': plan_id,
                'start_time': start_time,
                'end_time': end_time,
                'title': title,
                'description': description,
                'weight': weight,
                'completed': completed
            })
            
            self.conn.commit()
            
            logger.info(f"Created study plan block with ID {block_id} for plan {plan_id}")
            return block_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating study plan block: {e}")
            raise
            
    def get_study_plan_blocks(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get all time blocks for a study plan.
        
        Args:
            plan_id (str): ID of the study plan
            
        Returns:
            List[Dict[str, Any]]: List of time blocks
        """
        try:
            self.cursor.execute("""
            SELECT id, plan_id, start_time, end_time, title, description, weight, completed
            FROM study_plan_blocks WHERE plan_id = :plan_id
            ORDER BY start_time
            """, {'plan_id': plan_id})
            
            rows = self.cursor.fetchall()
            
            blocks = []
            for row in rows:
                block_dict = {
                    'id': row[0],
                    'plan_id': row[1],
                    'start_time': row[2],
                    'end_time': row[3],
                    'title': row[4],
                    'description': row[5],
                    'weight': row[6],
                    'completed': row[7]
                }
                blocks.append(block_dict)
            
            return blocks
            
        except Exception as e:
            logger.error(f"Error getting study plan blocks: {e}")
            return []
            
    def update_study_plan_block(self, block_id: str, block_data: Dict[str, Any]) -> bool:
        """
        Update a study plan time block.
        
        Args:
            block_id (str): ID of the block to update
            block_data (Dict[str, Any]): Updated block data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract block fields
            start_time = block_data.get("start_time")
            end_time = block_data.get("end_time")
            title = block_data.get("title")
            description = block_data.get("description")
            weight = block_data.get("weight")
            completed = block_data.get("completed")
            
            # Build update query
            update_fields = []
            params = {'id': block_id}
            
            if start_time is not None:
                update_fields.append("start_time = :start_time")
                params['start_time'] = start_time
                
            if end_time is not None:
                update_fields.append("end_time = :end_time")
                params['end_time'] = end_time
                
            if title is not None:
                update_fields.append("title = :title")
                params['title'] = title
                
            if description is not None:
                update_fields.append("description = :description")
                params['description'] = description
                
            if weight is not None:
                update_fields.append("weight = :weight")
                params['weight'] = weight
                
            if completed is not None:
                update_fields.append("completed = :completed")
                params['completed'] = completed
                
            if not update_fields:
                return True  # Nothing to update
                
            query = f"""
            UPDATE study_plan_blocks
            SET {', '.join(update_fields)}
            WHERE id = :id
            """
            
            self.cursor.execute(query, params)
            self.conn.commit()
            
            logger.info(f"Updated study plan block with ID {block_id}")
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error updating study plan block: {e}")
            return False
            
    # CRUD operations for study plan goals
    
    def create_study_plan_goal(self, goal_data: Dict[str, Any]) -> str:
        """
        Create a new goal for a study plan.
        
        Args:
            goal_data (Dict[str, Any]): Goal data including plan_id, title, description, deadline, priority
            
        Returns:
            str: ID of the created goal
        """
        try:
            # Generate UUID for goal ID
            goal_id = str(uuid.uuid4())
            
            # Extract goal fields
            plan_id = goal_data.get("plan_id")
            title = goal_data.get("title", "")
            description = goal_data.get("description", "")
            deadline = goal_data.get("deadline")
            priority = goal_data.get("priority", 1)
            completed = goal_data.get("completed", 0)
            
            self.cursor.execute("""
            INSERT INTO study_plan_goals (id, plan_id, title, description, deadline, priority, completed)
            VALUES (:id, :plan_id, :title, :description, :deadline, :priority, :completed)
            """, {
                'id': goal_id,
                'plan_id': plan_id,
                'title': title,
                'description': description,
                'deadline': deadline,
                'priority': priority,
                'completed': completed
            })
            
            self.conn.commit()
            
            logger.info(f"Created study plan goal with ID {goal_id} for plan {plan_id}")
            return goal_id
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error creating study plan goal: {e}")
            raise
            
    def get_study_plan_goals(self, plan_id: str) -> List[Dict[str, Any]]:
        """
        Get all goals for a study plan.
        
        Args:
            plan_id (str): ID of the study plan
            
        Returns:
            List[Dict[str, Any]]: List of goals
        """
        try:
            self.cursor.execute("""
            SELECT id, plan_id, title, description, deadline, priority, completed
            FROM study_plan_goals WHERE plan_id = :plan_id
            ORDER BY priority DESC, deadline
            """, {'plan_id': plan_id})
            
            rows = self.cursor.fetchall()
            
            goals = []
            for row in rows:
                goal_dict = {
                    'id': row[0],
                    'plan_id': row[1],
                    'title': row[2],
                    'description': row[3],
                    'deadline': row[4],
                    'priority': row[5],
                    'completed': row[6]
                }
                goals.append(goal_dict)
            
            return goals
            
        except Exception as e:
            logger.error(f"Error getting study plan goals: {e}")
            return []
            
    def update_study_plan_goal(self, goal_id: str, goal_data: Dict[str, Any]) -> bool:
        """
        Update a study plan goal.
        
        Args:
            goal_id (str): ID of the goal to update
            goal_data (Dict[str, Any]): Updated goal data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Extract goal fields
            title = goal_data.get("title")
            description = goal_data.get("description")
            deadline = goal_data.get("deadline")
            priority = goal_data.get("priority")
            completed = goal_data.get("completed")
            
            # Build update query
            update_fields = []
            params = {'id': goal_id}
            
            if title is not None:
                update_fields.append("title = :title")
                params['title'] = title
                
            if description is not None:
                update_fields.append("description = :description")
                params['description'] = description
                
            if deadline is not None:
                update_fields.append("deadline = :deadline")
                params['deadline'] = deadline
                
            if priority is not None:
                update_fields.append("priority = :priority")
                params['priority'] = priority
                
            if completed is not None:
                update_fields.append("completed = :completed")
                params['completed'] = completed
                
            if not update_fields:
                return True  # Nothing to update
                
            query = f"""
            UPDATE study_plan_goals
            SET {', '.join(update_fields)}
            WHERE id = :id
            """
            
            self.cursor.execute(query, params)
            self.conn.commit()
            
            logger.info(f"Updated study plan goal with ID {goal_id}")
            return True
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Error updating study plan goal: {e}")
            return False

def init_oracle_db(connection_string: str, username: str, password: str) -> None:
    """
    Initialize the Oracle database connection.
    
    Args:
        connection_string (str): Oracle connection string
        username (str): Oracle database username
        password (str): Oracle database password
    """
    logger.info(f"Initializing Oracle database connection")
    
    try:
        # Get wallet location from environment variable or use default
        wallet_location = os.environ.get('ORACLE_WALLET_LOCATION', '/app/wallet')
        
        # Configure the connection
        oracledb.init_oracle_client(lib_dir=os.environ.get('LD_LIBRARY_PATH', '/opt/oracle/instantclient*'))
        
        # Connect using wallet authentication
        conn = oracledb.connect(
            user=username,
            password=password,
            dsn=connection_string,
            config_dir=wallet_location,
            wallet_location=wallet_location,
            wallet_password=os.environ.get('ORACLE_WALLET_PASSWORD', '')
        )
        
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("""
        SELECT table_name 
        FROM user_tables 
        WHERE table_name IN ('USERS', 'NOTES', 'FLASHCARDS', 'FILES', 'STUDY_PLANS', 'STUDY_PLAN_BLOCKS', 'STUDY_PLAN_GOALS', 'USER_ACTIVITY')
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if len(existing_tables) < 8:
            logger.info("Some tables are missing. Creating tables...")
            
            # Read and execute the Oracle schema SQL
            script_path = os.path.join(os.path.dirname(__file__), 'oracle_schema.sql')
            with open(script_path, 'r') as f:
                sql_script = f.read()
            
            # Split the script into individual statements
            statements = sql_script.split(';')
            
            for statement in statements:
                if statement.strip():
                    cursor.execute(statement)
            
            conn.commit()
            logger.info("Oracle database tables created successfully")
        else:
            logger.info("All Oracle database tables already exist")
        
        conn.close()
        
        logger.info("Oracle database initialization completed")
        
    except Exception as e:
        logger.error(f"Error initializing Oracle database: {e}")
        raise