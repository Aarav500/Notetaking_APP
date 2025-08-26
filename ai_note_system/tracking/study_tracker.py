"""
Study Tracker module for AI Note System.
Handles tracking study sessions, including Pomodoro timers and note reviews.
"""

import os
import logging
import json
import sqlite3
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field

# Setup logging
logger = logging.getLogger("ai_note_system.tracking.study_tracker")

class SessionType(Enum):
    """Enum for study session types."""
    POMODORO = "pomodoro"
    CONTINUOUS = "continuous"
    REVIEW = "review"

class SessionStatus(Enum):
    """Enum for study session status."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class StudySession:
    """Class for tracking a study session."""
    id: Optional[int] = None
    session_type: SessionType = SessionType.POMODORO
    status: SessionStatus = SessionStatus.ACTIVE
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: int = 0  # Duration in seconds
    breaks: int = 0  # Number of breaks taken
    break_duration: int = 0  # Total break duration in seconds
    notes: List[int] = field(default_factory=list)  # List of note IDs reviewed
    tags: List[str] = field(default_factory=list)  # List of tags for the session
    pomodoro_length: int = 25  # Length of Pomodoro in minutes
    break_length: int = 5  # Length of break in minutes
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the session to a dictionary."""
        result = asdict(self)
        # Convert enums to strings
        result["session_type"] = self.session_type.value
        result["status"] = self.status.value
        # Convert datetimes to ISO format
        result["start_time"] = self.start_time.isoformat() if self.start_time else None
        result["end_time"] = self.end_time.isoformat() if self.end_time else None
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudySession":
        """Create a session from a dictionary."""
        # Convert string values to enums
        if "session_type" in data:
            data["session_type"] = SessionType(data["session_type"])
        if "status" in data:
            data["status"] = SessionStatus(data["status"])
        # Convert ISO format to datetimes
        if "start_time" in data and data["start_time"]:
            data["start_time"] = datetime.fromisoformat(data["start_time"])
        if "end_time" in data and data["end_time"]:
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        return cls(**data)

class StudyTracker:
    """
    Study Tracker class for AI Note System.
    Handles tracking study sessions, including Pomodoro timers and note reviews.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the StudyTracker.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Connect to database
        self.connect()
        
        # Ensure tables exist
        self._ensure_tables()
        
        # Current active session
        self.current_session = None
        
    def connect(self):
        """
        Connect to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            logger.debug(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
            
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")
            
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
        
    def _ensure_tables(self):
        """
        Ensure that the necessary tables exist in the database.
        """
        try:
            # Create study_sessions table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration INTEGER DEFAULT 0,
                breaks INTEGER DEFAULT 0,
                break_duration INTEGER DEFAULT 0,
                pomodoro_length INTEGER DEFAULT 25,
                break_length INTEGER DEFAULT 5,
                description TEXT
            )
            ''')
            
            # Create session_notes table (many-to-many relationship)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_notes (
                session_id INTEGER,
                note_id INTEGER,
                review_time TEXT,
                duration INTEGER DEFAULT 0,
                PRIMARY KEY (session_id, note_id),
                FOREIGN KEY (session_id) REFERENCES study_sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
            )
            ''')
            
            # Create session_tags table (many-to-many relationship)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_tags (
                session_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (session_id, tag_id),
                FOREIGN KEY (session_id) REFERENCES study_sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
            ''')
            
            self.conn.commit()
            logger.debug("Study tracker tables created successfully")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error creating study tracker tables: {e}")
            raise
    
    def start_session(
        self,
        session_type: SessionType = SessionType.POMODORO,
        pomodoro_length: int = 25,
        break_length: int = 5,
        tags: List[str] = None,
        description: str = ""
    ) -> StudySession:
        """
        Start a new study session.
        
        Args:
            session_type (SessionType): Type of session (pomodoro, continuous, review)
            pomodoro_length (int): Length of Pomodoro in minutes
            break_length (int): Length of break in minutes
            tags (List[str], optional): List of tags for the session
            description (str, optional): Description of the session
            
        Returns:
            StudySession: The created study session
        """
        # Check if there's already an active session
        if self.current_session and self.current_session.status == SessionStatus.ACTIVE:
            logger.warning("There is already an active session. Please end it before starting a new one.")
            return self.current_session
        
        # Create a new session
        session = StudySession(
            session_type=session_type,
            status=SessionStatus.ACTIVE,
            start_time=datetime.now(),
            pomodoro_length=pomodoro_length,
            break_length=break_length,
            tags=tags or [],
            description=description
        )
        
        # Save to database
        try:
            # Insert session
            self.cursor.execute('''
            INSERT INTO study_sessions (
                session_type, status, start_time, pomodoro_length, break_length, description
            ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session.session_type.value,
                session.status.value,
                session.start_time.isoformat(),
                session.pomodoro_length,
                session.break_length,
                session.description
            ))
            
            session.id = self.cursor.lastrowid
            
            # Add tags if provided
            if tags:
                self._add_tags_to_session(session.id, tags)
            
            self.conn.commit()
            logger.info(f"Started {session_type.value} session (ID: {session.id})")
            
            # Set as current session
            self.current_session = session
            
            return session
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error starting session: {e}")
            raise
    
    def pause_session(self) -> Optional[StudySession]:
        """
        Pause the current study session.
        
        Returns:
            Optional[StudySession]: The updated session, or None if no active session
        """
        if not self.current_session or self.current_session.status != SessionStatus.ACTIVE:
            logger.warning("No active session to pause")
            return None
        
        # Update session
        self.current_session.status = SessionStatus.PAUSED
        
        # Save to database
        try:
            self.cursor.execute('''
            UPDATE study_sessions
            SET status = ?
            WHERE id = ?
            ''', (
                self.current_session.status.value,
                self.current_session.id
            ))
            
            self.conn.commit()
            logger.info(f"Paused session (ID: {self.current_session.id})")
            
            return self.current_session
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error pausing session: {e}")
            raise
    
    def resume_session(self) -> Optional[StudySession]:
        """
        Resume a paused study session.
        
        Returns:
            Optional[StudySession]: The updated session, or None if no paused session
        """
        if not self.current_session or self.current_session.status != SessionStatus.PAUSED:
            logger.warning("No paused session to resume")
            return None
        
        # Update session
        self.current_session.status = SessionStatus.ACTIVE
        
        # Save to database
        try:
            self.cursor.execute('''
            UPDATE study_sessions
            SET status = ?
            WHERE id = ?
            ''', (
                self.current_session.status.value,
                self.current_session.id
            ))
            
            self.conn.commit()
            logger.info(f"Resumed session (ID: {self.current_session.id})")
            
            return self.current_session
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error resuming session: {e}")
            raise
    
    def end_session(self, status: SessionStatus = SessionStatus.COMPLETED) -> Optional[StudySession]:
        """
        End the current study session.
        
        Args:
            status (SessionStatus): Final status of the session
            
        Returns:
            Optional[StudySession]: The completed session, or None if no active session
        """
        if not self.current_session or self.current_session.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            logger.warning("No active or paused session to end")
            return None
        
        # Update session
        self.current_session.status = status
        self.current_session.end_time = datetime.now()
        
        # Calculate duration
        if self.current_session.start_time:
            duration = (self.current_session.end_time - self.current_session.start_time).total_seconds()
            self.current_session.duration = int(duration)
        
        # Save to database
        try:
            self.cursor.execute('''
            UPDATE study_sessions
            SET status = ?, end_time = ?, duration = ?
            WHERE id = ?
            ''', (
                self.current_session.status.value,
                self.current_session.end_time.isoformat(),
                self.current_session.duration,
                self.current_session.id
            ))
            
            self.conn.commit()
            logger.info(f"Ended session (ID: {self.current_session.id}) with status {status.value}")
            
            completed_session = self.current_session
            self.current_session = None
            
            return completed_session
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error ending session: {e}")
            raise
    
    def add_break(self, duration: int) -> Optional[StudySession]:
        """
        Add a break to the current study session.
        
        Args:
            duration (int): Duration of the break in seconds
            
        Returns:
            Optional[StudySession]: The updated session, or None if no active session
        """
        if not self.current_session or self.current_session.status != SessionStatus.ACTIVE:
            logger.warning("No active session to add break to")
            return None
        
        # Update session
        self.current_session.breaks += 1
        self.current_session.break_duration += duration
        
        # Save to database
        try:
            self.cursor.execute('''
            UPDATE study_sessions
            SET breaks = ?, break_duration = ?
            WHERE id = ?
            ''', (
                self.current_session.breaks,
                self.current_session.break_duration,
                self.current_session.id
            ))
            
            self.conn.commit()
            logger.info(f"Added break to session (ID: {self.current_session.id})")
            
            return self.current_session
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error adding break to session: {e}")
            raise
    
    def add_note_to_session(self, note_id: int, duration: int = 0) -> bool:
        """
        Add a note to the current study session.
        
        Args:
            note_id (int): ID of the note
            duration (int): Duration spent on the note in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.current_session or self.current_session.status != SessionStatus.ACTIVE:
            logger.warning("No active session to add note to")
            return False
        
        # Add note to session
        if note_id not in self.current_session.notes:
            self.current_session.notes.append(note_id)
        
        # Save to database
        try:
            self.cursor.execute('''
            INSERT OR REPLACE INTO session_notes (
                session_id, note_id, review_time, duration
            ) VALUES (?, ?, ?, ?)
            ''', (
                self.current_session.id,
                note_id,
                datetime.now().isoformat(),
                duration
            ))
            
            self.conn.commit()
            logger.info(f"Added note {note_id} to session (ID: {self.current_session.id})")
            
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error adding note to session: {e}")
            return False
    
    def get_session(self, session_id: int) -> Optional[StudySession]:
        """
        Get a study session by ID.
        
        Args:
            session_id (int): ID of the session
            
        Returns:
            Optional[StudySession]: The session, or None if not found
        """
        try:
            # Get session
            self.cursor.execute('''
            SELECT * FROM study_sessions
            WHERE id = ?
            ''', (session_id,))
            
            row = self.cursor.fetchone()
            if not row:
                return None
            
            # Convert to dictionary
            session_dict = dict(row)
            
            # Get notes
            self.cursor.execute('''
            SELECT note_id FROM session_notes
            WHERE session_id = ?
            ''', (session_id,))
            
            notes = [row["note_id"] for row in self.cursor.fetchall()]
            session_dict["notes"] = notes
            
            # Get tags
            self.cursor.execute('''
            SELECT tags.name FROM tags
            JOIN session_tags ON tags.id = session_tags.tag_id
            WHERE session_tags.session_id = ?
            ''', (session_id,))
            
            tags = [row["name"] for row in self.cursor.fetchall()]
            session_dict["tags"] = tags
            
            # Create session object
            return StudySession.from_dict(session_dict)
            
        except sqlite3.Error as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def get_sessions(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[SessionStatus] = None,
        session_type: Optional[SessionType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tags: List[str] = None
    ) -> List[StudySession]:
        """
        Get study sessions.
        
        Args:
            limit (int): Maximum number of sessions to return
            offset (int): Offset for pagination
            status (SessionStatus, optional): Filter by status
            session_type (SessionType, optional): Filter by session type
            start_date (datetime, optional): Filter by start date
            end_date (datetime, optional): Filter by end date
            tags (List[str], optional): Filter by tags
            
        Returns:
            List[StudySession]: List of study sessions
        """
        try:
            # Build query
            sql = "SELECT id FROM study_sessions"
            params = []
            
            # Add WHERE clause if needed
            where_clauses = []
            
            if status:
                where_clauses.append("status = ?")
                params.append(status.value)
            
            if session_type:
                where_clauses.append("session_type = ?")
                params.append(session_type.value)
            
            if start_date:
                where_clauses.append("start_time >= ?")
                params.append(start_date.isoformat())
            
            if end_date:
                where_clauses.append("end_time <= ?")
                params.append(end_date.isoformat())
            
            if tags:
                placeholders = ", ".join(["?"] * len(tags))
                where_clauses.append(f"""
                id IN (
                    SELECT session_id FROM session_tags 
                    JOIN tags ON session_tags.tag_id = tags.id 
                    WHERE tags.name IN ({placeholders})
                    GROUP BY session_id
                    HAVING COUNT(DISTINCT tags.name) = ?
                )
                """)
                params.extend(tags)
                params.append(len(tags))  # Ensure all tags are matched
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # Add ORDER BY, LIMIT, and OFFSET
            sql += " ORDER BY start_time DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Execute query
            self.cursor.execute(sql, params)
            
            # Fetch results
            session_ids = [row["id"] for row in self.cursor.fetchall()]
            
            # Get full sessions
            sessions = []
            for session_id in session_ids:
                session = self.get_session(session_id)
                if session:
                    sessions.append(session)
            
            return sessions
            
        except sqlite3.Error as e:
            logger.error(f"Error getting sessions: {e}")
            return []
    
    def get_current_session(self) -> Optional[StudySession]:
        """
        Get the current study session.
        
        Returns:
            Optional[StudySession]: The current session, or None if no active session
        """
        if not self.current_session:
            # Try to find an active session in the database
            try:
                self.cursor.execute('''
                SELECT id FROM study_sessions
                WHERE status IN (?, ?)
                ORDER BY start_time DESC
                LIMIT 1
                ''', (SessionStatus.ACTIVE.value, SessionStatus.PAUSED.value))
                
                row = self.cursor.fetchone()
                if row:
                    self.current_session = self.get_session(row["id"])
            except sqlite3.Error as e:
                logger.error(f"Error getting current session: {e}")
        
        return self.current_session
    
    def get_session_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        session_type: Optional[SessionType] = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for study sessions.
        
        Args:
            start_date (datetime, optional): Start date for the statistics
            end_date (datetime, optional): End date for the statistics
            session_type (SessionType, optional): Filter by session type
            tags (List[str], optional): Filter by tags
            
        Returns:
            Dict[str, Any]: Dictionary of statistics
        """
        try:
            # Build query
            sql = """
            SELECT 
                COUNT(*) as session_count,
                SUM(duration) as total_duration,
                SUM(breaks) as total_breaks,
                SUM(break_duration) as total_break_duration,
                AVG(duration) as avg_duration,
                MAX(duration) as max_duration,
                MIN(duration) as min_duration
            FROM study_sessions
            """
            params = []
            
            # Add WHERE clause if needed
            where_clauses = []
            
            if start_date:
                where_clauses.append("start_time >= ?")
                params.append(start_date.isoformat())
            
            if end_date:
                where_clauses.append("end_time <= ?")
                params.append(end_date.isoformat())
            
            if session_type:
                where_clauses.append("session_type = ?")
                params.append(session_type.value)
            
            if tags:
                placeholders = ", ".join(["?"] * len(tags))
                where_clauses.append(f"""
                id IN (
                    SELECT session_id FROM session_tags 
                    JOIN tags ON session_tags.tag_id = tags.id 
                    WHERE tags.name IN ({placeholders})
                    GROUP BY session_id
                    HAVING COUNT(DISTINCT tags.name) = ?
                )
                """)
                params.extend(tags)
                params.append(len(tags))  # Ensure all tags are matched
            
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            
            # Execute query
            self.cursor.execute(sql, params)
            
            # Fetch results
            stats = dict(self.cursor.fetchone())
            
            # Get note count
            note_sql = """
            SELECT COUNT(DISTINCT note_id) as note_count
            FROM session_notes
            WHERE session_id IN (
                SELECT id FROM study_sessions
            """
            
            if where_clauses:
                note_sql += " WHERE " + " AND ".join(where_clauses)
            
            note_sql += ")"
            
            self.cursor.execute(note_sql, params)
            note_stats = dict(self.cursor.fetchone())
            
            # Merge stats
            stats.update(note_stats)
            
            # Convert to appropriate types
            for key in stats:
                if stats[key] is None:
                    stats[key] = 0
            
            return stats
            
        except sqlite3.Error as e:
            logger.error(f"Error getting session stats: {e}")
            return {}
    
    def _add_tags_to_session(self, session_id: int, tags: List[str]) -> None:
        """
        Add tags to a session.
        
        Args:
            session_id (int): ID of the session
            tags (List[str]): List of tag names
        """
        for tag in tags:
            # Get or create tag
            self.cursor.execute(
                "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                (tag,)
            )
            
            self.cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
            tag_id = self.cursor.fetchone()["id"]
            
            # Link tag to session
            self.cursor.execute(
                "INSERT OR IGNORE INTO session_tags (session_id, tag_id) VALUES (?, ?)",
                (session_id, tag_id)
            )