"""
Collaboration Mode module for AI Note System.
Enables sharing knowledge packs with classmates or team members, collaborative annotation, and change tracking.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid

# Setup logging
logger = logging.getLogger("ai_note_system.collaboration.collaboration_manager")

class CollaborationManager:
    """
    Manages collaboration features including workspaces, sharing, comments, and change tracking.
    """
    
    def __init__(self, db_manager):
        """
        Initialize the collaboration manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self._ensure_collaboration_tables()
    
    def _ensure_collaboration_tables(self) -> None:
        """
        Ensure the collaboration-related tables exist in the database.
        """
        # Create workspaces table
        workspaces_query = """
        CREATE TABLE IF NOT EXISTS workspaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(workspaces_query)
        
        # Create workspace_members table
        members_query = """
        CREATE TABLE IF NOT EXISTS workspace_members (
            workspace_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (workspace_id, user_id),
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(members_query)
        
        # Create shared_notes table
        shared_notes_query = """
        CREATE TABLE IF NOT EXISTS shared_notes (
            workspace_id INTEGER NOT NULL,
            note_id INTEGER NOT NULL,
            shared_by INTEGER NOT NULL,
            shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (workspace_id, note_id),
            FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (shared_by) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(shared_notes_query)
        
        # Create comments table
        comments_query = """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            parent_id INTEGER,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(comments_query)
        
        # Create note_changes table
        changes_query = """
        CREATE TABLE IF NOT EXISTS note_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            change_type TEXT NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(changes_query)
    
    def create_workspace(self, name: str, description: str, user_id: int) -> int:
        """
        Create a new collaborative workspace.
        
        Args:
            name (str): Name of the workspace
            description (str): Description of the workspace
            user_id (int): ID of the user creating the workspace
            
        Returns:
            int: ID of the newly created workspace
        """
        query = """
        INSERT INTO workspaces (name, description, created_by)
        VALUES (?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (name, description, user_id))
        workspace_id = cursor.lastrowid
        
        # Add creator as admin
        self.add_member(workspace_id, user_id, "admin")
        
        logger.info(f"Created workspace '{name}' with ID {workspace_id}")
        return workspace_id
    
    def get_workspace(self, workspace_id: int) -> Optional[Dict[str, Any]]:
        """
        Get workspace details.
        
        Args:
            workspace_id (int): ID of the workspace
            
        Returns:
            Optional[Dict[str, Any]]: Workspace details or None if not found
        """
        query = """
        SELECT w.*, u.username as creator_name
        FROM workspaces w
        JOIN users u ON w.created_by = u.id
        WHERE w.id = ?
        """
        
        result = self.db_manager.execute_query(query, (workspace_id,)).fetchone()
        
        if result:
            workspace = dict(result)
            
            # Get members
            members_query = """
            SELECT wm.user_id, u.username, wm.role, wm.joined_at
            FROM workspace_members wm
            JOIN users u ON wm.user_id = u.id
            WHERE wm.workspace_id = ?
            """
            
            members = self.db_manager.execute_query(members_query, (workspace_id,)).fetchall()
            workspace["members"] = [dict(member) for member in members]
            
            # Get shared notes count
            notes_query = """
            SELECT COUNT(*) as note_count
            FROM shared_notes
            WHERE workspace_id = ?
            """
            
            note_count = self.db_manager.execute_query(notes_query, (workspace_id,)).fetchone()
            workspace["note_count"] = note_count["note_count"] if note_count else 0
            
            return workspace
        
        return None
    
    def list_workspaces(self, user_id: int) -> List[Dict[str, Any]]:
        """
        List workspaces that a user is a member of.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of workspaces
        """
        query = """
        SELECT w.*, u.username as creator_name
        FROM workspaces w
        JOIN users u ON w.created_by = u.id
        JOIN workspace_members wm ON w.id = wm.workspace_id
        WHERE wm.user_id = ?
        ORDER BY w.updated_at DESC
        """
        
        results = self.db_manager.execute_query(query, (user_id,)).fetchall()
        
        workspaces = []
        for result in results:
            workspace = dict(result)
            
            # Get member count
            members_query = """
            SELECT COUNT(*) as member_count
            FROM workspace_members
            WHERE workspace_id = ?
            """
            
            member_count = self.db_manager.execute_query(members_query, (workspace["id"],)).fetchone()
            workspace["member_count"] = member_count["member_count"] if member_count else 0
            
            # Get shared notes count
            notes_query = """
            SELECT COUNT(*) as note_count
            FROM shared_notes
            WHERE workspace_id = ?
            """
            
            note_count = self.db_manager.execute_query(notes_query, (workspace["id"],)).fetchone()
            workspace["note_count"] = note_count["note_count"] if note_count else 0
            
            # Get user's role
            role_query = """
            SELECT role
            FROM workspace_members
            WHERE workspace_id = ? AND user_id = ?
            """
            
            role = self.db_manager.execute_query(role_query, (workspace["id"], user_id)).fetchone()
            workspace["role"] = role["role"] if role else None
            
            workspaces.append(workspace)
        
        return workspaces
    
    def add_member(self, workspace_id: int, user_id: int, role: str = "member") -> bool:
        """
        Add a member to a workspace.
        
        Args:
            workspace_id (int): ID of the workspace
            user_id (int): ID of the user to add
            role (str): Role of the user (admin, member)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if workspace exists
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            logger.error(f"Workspace with ID {workspace_id} not found")
            return False
        
        # Check if user is already a member
        check_query = """
        SELECT 1 FROM workspace_members
        WHERE workspace_id = ? AND user_id = ?
        """
        
        existing = self.db_manager.execute_query(check_query, (workspace_id, user_id)).fetchone()
        if existing:
            logger.warning(f"User {user_id} is already a member of workspace {workspace_id}")
            return True
        
        # Add member
        query = """
        INSERT INTO workspace_members (workspace_id, user_id, role)
        VALUES (?, ?, ?)
        """
        
        self.db_manager.execute_query(query, (workspace_id, user_id, role))
        
        # Update workspace updated_at
        update_query = """
        UPDATE workspaces
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        self.db_manager.execute_query(update_query, (workspace_id,))
        
        logger.info(f"Added user {user_id} to workspace {workspace_id} with role {role}")
        return True
    
    def remove_member(self, workspace_id: int, user_id: int) -> bool:
        """
        Remove a member from a workspace.
        
        Args:
            workspace_id (int): ID of the workspace
            user_id (int): ID of the user to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if workspace exists
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            logger.error(f"Workspace with ID {workspace_id} not found")
            return False
        
        # Check if user is a member
        check_query = """
        SELECT 1 FROM workspace_members
        WHERE workspace_id = ? AND user_id = ?
        """
        
        existing = self.db_manager.execute_query(check_query, (workspace_id, user_id)).fetchone()
        if not existing:
            logger.warning(f"User {user_id} is not a member of workspace {workspace_id}")
            return False
        
        # Check if user is the creator (cannot remove creator)
        if workspace["created_by"] == user_id:
            logger.error(f"Cannot remove creator from workspace {workspace_id}")
            return False
        
        # Remove member
        query = """
        DELETE FROM workspace_members
        WHERE workspace_id = ? AND user_id = ?
        """
        
        self.db_manager.execute_query(query, (workspace_id, user_id))
        
        # Update workspace updated_at
        update_query = """
        UPDATE workspaces
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        self.db_manager.execute_query(update_query, (workspace_id,))
        
        logger.info(f"Removed user {user_id} from workspace {workspace_id}")
        return True
    
    def share_note(self, workspace_id: int, note_id: int, user_id: int) -> bool:
        """
        Share a note with a workspace.
        
        Args:
            workspace_id (int): ID of the workspace
            note_id (int): ID of the note to share
            user_id (int): ID of the user sharing the note
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if workspace exists
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            logger.error(f"Workspace with ID {workspace_id} not found")
            return False
        
        # Check if user is a member
        check_query = """
        SELECT 1 FROM workspace_members
        WHERE workspace_id = ? AND user_id = ?
        """
        
        existing = self.db_manager.execute_query(check_query, (workspace_id, user_id)).fetchone()
        if not existing:
            logger.error(f"User {user_id} is not a member of workspace {workspace_id}")
            return False
        
        # Check if note exists
        note_query = """
        SELECT 1 FROM notes
        WHERE id = ?
        """
        
        note_exists = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        if not note_exists:
            logger.error(f"Note with ID {note_id} not found")
            return False
        
        # Check if note is already shared
        shared_query = """
        SELECT 1 FROM shared_notes
        WHERE workspace_id = ? AND note_id = ?
        """
        
        already_shared = self.db_manager.execute_query(shared_query, (workspace_id, note_id)).fetchone()
        if already_shared:
            logger.warning(f"Note {note_id} is already shared with workspace {workspace_id}")
            return True
        
        # Share note
        query = """
        INSERT INTO shared_notes (workspace_id, note_id, shared_by)
        VALUES (?, ?, ?)
        """
        
        self.db_manager.execute_query(query, (workspace_id, note_id, user_id))
        
        # Update workspace updated_at
        update_query = """
        UPDATE workspaces
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        self.db_manager.execute_query(update_query, (workspace_id,))
        
        logger.info(f"Shared note {note_id} with workspace {workspace_id}")
        return True
    
    def unshare_note(self, workspace_id: int, note_id: int, user_id: int) -> bool:
        """
        Unshare a note from a workspace.
        
        Args:
            workspace_id (int): ID of the workspace
            note_id (int): ID of the note to unshare
            user_id (int): ID of the user unsharing the note
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if workspace exists
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            logger.error(f"Workspace with ID {workspace_id} not found")
            return False
        
        # Check if user is a member with appropriate permissions
        check_query = """
        SELECT role FROM workspace_members
        WHERE workspace_id = ? AND user_id = ?
        """
        
        member = self.db_manager.execute_query(check_query, (workspace_id, user_id)).fetchone()
        if not member:
            logger.error(f"User {user_id} is not a member of workspace {workspace_id}")
            return False
        
        # Check if note is shared
        shared_query = """
        SELECT shared_by FROM shared_notes
        WHERE workspace_id = ? AND note_id = ?
        """
        
        shared = self.db_manager.execute_query(shared_query, (workspace_id, note_id)).fetchone()
        if not shared:
            logger.warning(f"Note {note_id} is not shared with workspace {workspace_id}")
            return False
        
        # Check if user has permission to unshare
        if member["role"] != "admin" and shared["shared_by"] != user_id:
            logger.error(f"User {user_id} does not have permission to unshare note {note_id}")
            return False
        
        # Unshare note
        query = """
        DELETE FROM shared_notes
        WHERE workspace_id = ? AND note_id = ?
        """
        
        self.db_manager.execute_query(query, (workspace_id, note_id))
        
        # Update workspace updated_at
        update_query = """
        UPDATE workspaces
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        self.db_manager.execute_query(update_query, (workspace_id,))
        
        logger.info(f"Unshared note {note_id} from workspace {workspace_id}")
        return True
    
    def list_shared_notes(self, workspace_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        List notes shared with a workspace.
        
        Args:
            workspace_id (int): ID of the workspace
            user_id (int): ID of the user requesting the list
            
        Returns:
            List[Dict[str, Any]]: List of shared notes
        """
        # Check if user is a member
        check_query = """
        SELECT 1 FROM workspace_members
        WHERE workspace_id = ? AND user_id = ?
        """
        
        existing = self.db_manager.execute_query(check_query, (workspace_id, user_id)).fetchone()
        if not existing:
            logger.error(f"User {user_id} is not a member of workspace {workspace_id}")
            return []
        
        # Get shared notes
        query = """
        SELECT n.*, sn.shared_by, sn.shared_at, u.username as shared_by_name
        FROM notes n
        JOIN shared_notes sn ON n.id = sn.note_id
        JOIN users u ON sn.shared_by = u.id
        WHERE sn.workspace_id = ?
        ORDER BY sn.shared_at DESC
        """
        
        results = self.db_manager.execute_query(query, (workspace_id,)).fetchall()
        
        shared_notes = []
        for result in results:
            note = dict(result)
            
            # Get comment count
            comments_query = """
            SELECT COUNT(*) as comment_count
            FROM comments
            WHERE note_id = ?
            """
            
            comment_count = self.db_manager.execute_query(comments_query, (note["id"],)).fetchone()
            note["comment_count"] = comment_count["comment_count"] if comment_count else 0
            
            shared_notes.append(note)
        
        return shared_notes
    
    def add_comment(self, note_id: int, user_id: int, text: str, parent_id: Optional[int] = None) -> int:
        """
        Add a comment to a note.
        
        Args:
            note_id (int): ID of the note
            user_id (int): ID of the user adding the comment
            text (str): Comment text
            parent_id (int, optional): ID of the parent comment (for threaded comments)
            
        Returns:
            int: ID of the newly added comment
        """
        # Check if note exists
        note_query = """
        SELECT 1 FROM notes
        WHERE id = ?
        """
        
        note_exists = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        if not note_exists:
            logger.error(f"Note with ID {note_id} not found")
            raise ValueError(f"Note with ID {note_id} not found")
        
        # Check if user has access to the note
        access_query = """
        SELECT 1 FROM shared_notes sn
        JOIN workspace_members wm ON sn.workspace_id = wm.workspace_id
        WHERE sn.note_id = ? AND wm.user_id = ?
        UNION
        SELECT 1 FROM notes
        WHERE id = ? AND user_id = ?
        """
        
        has_access = self.db_manager.execute_query(access_query, (note_id, user_id, note_id, user_id)).fetchone()
        if not has_access:
            logger.error(f"User {user_id} does not have access to note {note_id}")
            raise ValueError(f"User {user_id} does not have access to note {note_id}")
        
        # Check if parent comment exists (if provided)
        if parent_id:
            parent_query = """
            SELECT 1 FROM comments
            WHERE id = ? AND note_id = ?
            """
            
            parent_exists = self.db_manager.execute_query(parent_query, (parent_id, note_id)).fetchone()
            if not parent_exists:
                logger.error(f"Parent comment with ID {parent_id} not found for note {note_id}")
                raise ValueError(f"Parent comment with ID {parent_id} not found for note {note_id}")
        
        # Add comment
        query = """
        INSERT INTO comments (note_id, user_id, parent_id, text)
        VALUES (?, ?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (note_id, user_id, parent_id, text))
        comment_id = cursor.lastrowid
        
        logger.info(f"Added comment {comment_id} to note {note_id}")
        return comment_id
    
    def get_comments(self, note_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get comments for a note.
        
        Args:
            note_id (int): ID of the note
            user_id (int): ID of the user requesting the comments
            
        Returns:
            List[Dict[str, Any]]: List of comments
        """
        # Check if user has access to the note
        access_query = """
        SELECT 1 FROM shared_notes sn
        JOIN workspace_members wm ON sn.workspace_id = wm.workspace_id
        WHERE sn.note_id = ? AND wm.user_id = ?
        UNION
        SELECT 1 FROM notes
        WHERE id = ? AND user_id = ?
        """
        
        has_access = self.db_manager.execute_query(access_query, (note_id, user_id, note_id, user_id)).fetchone()
        if not has_access:
            logger.error(f"User {user_id} does not have access to note {note_id}")
            return []
        
        # Get comments
        query = """
        SELECT c.*, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.note_id = ?
        ORDER BY c.created_at ASC
        """
        
        results = self.db_manager.execute_query(query, (note_id,)).fetchall()
        
        # Organize comments into threads
        comments = []
        comment_map = {}
        
        for result in results:
            comment = dict(result)
            comment["replies"] = []
            comment_map[comment["id"]] = comment
            
            if comment["parent_id"] is None:
                # Top-level comment
                comments.append(comment)
            else:
                # Reply to another comment
                parent = comment_map.get(comment["parent_id"])
                if parent:
                    parent["replies"].append(comment)
        
        return comments
    
    def track_note_change(self, note_id: int, user_id: int, change_type: str, field_name: str, old_value: str, new_value: str) -> int:
        """
        Track a change to a note.
        
        Args:
            note_id (int): ID of the note
            user_id (int): ID of the user making the change
            change_type (str): Type of change (add, modify, delete)
            field_name (str): Name of the field being changed
            old_value (str): Old value of the field
            new_value (str): New value of the field
            
        Returns:
            int: ID of the tracked change
        """
        # Check if note exists
        note_query = """
        SELECT 1 FROM notes
        WHERE id = ?
        """
        
        note_exists = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        if not note_exists:
            logger.error(f"Note with ID {note_id} not found")
            raise ValueError(f"Note with ID {note_id} not found")
        
        # Check if user has access to the note
        access_query = """
        SELECT 1 FROM shared_notes sn
        JOIN workspace_members wm ON sn.workspace_id = wm.workspace_id
        WHERE sn.note_id = ? AND wm.user_id = ?
        UNION
        SELECT 1 FROM notes
        WHERE id = ? AND user_id = ?
        """
        
        has_access = self.db_manager.execute_query(access_query, (note_id, user_id, note_id, user_id)).fetchone()
        if not has_access:
            logger.error(f"User {user_id} does not have access to note {note_id}")
            raise ValueError(f"User {user_id} does not have access to note {note_id}")
        
        # Track change
        query = """
        INSERT INTO note_changes (note_id, user_id, change_type, field_name, old_value, new_value)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (note_id, user_id, change_type, field_name, old_value, new_value))
        change_id = cursor.lastrowid
        
        logger.info(f"Tracked change {change_id} to note {note_id}")
        return change_id
    
    def get_note_changes(self, note_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get change history for a note.
        
        Args:
            note_id (int): ID of the note
            user_id (int): ID of the user requesting the changes
            
        Returns:
            List[Dict[str, Any]]: List of changes
        """
        # Check if user has access to the note
        access_query = """
        SELECT 1 FROM shared_notes sn
        JOIN workspace_members wm ON sn.workspace_id = wm.workspace_id
        WHERE sn.note_id = ? AND wm.user_id = ?
        UNION
        SELECT 1 FROM notes
        WHERE id = ? AND user_id = ?
        """
        
        has_access = self.db_manager.execute_query(access_query, (note_id, user_id, note_id, user_id)).fetchone()
        if not has_access:
            logger.error(f"User {user_id} does not have access to note {note_id}")
            return []
        
        # Get changes
        query = """
        SELECT nc.*, u.username
        FROM note_changes nc
        JOIN users u ON nc.user_id = u.id
        WHERE nc.note_id = ?
        ORDER BY nc.created_at DESC
        """
        
        results = self.db_manager.execute_query(query, (note_id,)).fetchall()
        
        changes = [dict(result) for result in results]
        return changes
    
    def merge_changes(self, note_id: int, user_id: int, from_user_id: int) -> bool:
        """
        Merge changes from another user into a note.
        
        Args:
            note_id (int): ID of the note
            user_id (int): ID of the user merging changes
            from_user_id (int): ID of the user whose changes to merge
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if note exists and user is the owner
        note_query = """
        SELECT user_id FROM notes
        WHERE id = ?
        """
        
        note = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        if not note:
            logger.error(f"Note with ID {note_id} not found")
            return False
        
        if note["user_id"] != user_id:
            logger.error(f"User {user_id} is not the owner of note {note_id}")
            return False
        
        # Get changes from the other user
        changes_query = """
        SELECT * FROM note_changes
        WHERE note_id = ? AND user_id = ?
        ORDER BY created_at ASC
        """
        
        changes = self.db_manager.execute_query(changes_query, (note_id, from_user_id)).fetchall()
        
        if not changes:
            logger.warning(f"No changes found from user {from_user_id} for note {note_id}")
            return True
        
        # Apply changes
        for change in changes:
            # Update the note with the change
            if change["change_type"] == "modify":
                update_query = f"""
                UPDATE notes
                SET {change["field_name"]} = ?
                WHERE id = ?
                """
                
                self.db_manager.execute_query(update_query, (change["new_value"], note_id))
            
            # Track that we merged this change
            self.track_note_change(
                note_id=note_id,
                user_id=user_id,
                change_type="merge",
                field_name=change["field_name"],
                old_value=f"Merged change {change['id']} from user {from_user_id}",
                new_value=change["new_value"]
            )
        
        logger.info(f"Merged changes from user {from_user_id} into note {note_id}")
        return True

def create_workspace(db_manager, name: str, description: str, user_id: int) -> int:
    """
    Create a new collaborative workspace.
    
    Args:
        db_manager: Database manager instance
        name (str): Name of the workspace
        description (str): Description of the workspace
        user_id (int): ID of the user creating the workspace
        
    Returns:
        int: ID of the newly created workspace
    """
    collaboration_manager = CollaborationManager(db_manager)
    return collaboration_manager.create_workspace(name, description, user_id)

def add_member(db_manager, workspace_id: int, user_id: int, role: str = "member") -> bool:
    """
    Add a member to a workspace.
    
    Args:
        db_manager: Database manager instance
        workspace_id (int): ID of the workspace
        user_id (int): ID of the user to add
        role (str): Role of the user (admin, member)
        
    Returns:
        bool: True if successful, False otherwise
    """
    collaboration_manager = CollaborationManager(db_manager)
    return collaboration_manager.add_member(workspace_id, user_id, role)

def share_note(db_manager, workspace_id: int, note_id: int, user_id: int) -> bool:
    """
    Share a note with a workspace.
    
    Args:
        db_manager: Database manager instance
        workspace_id (int): ID of the workspace
        note_id (int): ID of the note to share
        user_id (int): ID of the user sharing the note
        
    Returns:
        bool: True if successful, False otherwise
    """
    collaboration_manager = CollaborationManager(db_manager)
    return collaboration_manager.share_note(workspace_id, note_id, user_id)

def add_comment(db_manager, note_id: int, user_id: int, text: str, parent_id: Optional[int] = None) -> int:
    """
    Add a comment to a note.
    
    Args:
        db_manager: Database manager instance
        note_id (int): ID of the note
        user_id (int): ID of the user adding the comment
        text (str): Comment text
        parent_id (int, optional): ID of the parent comment (for threaded comments)
        
    Returns:
        int: ID of the newly added comment
    """
    collaboration_manager = CollaborationManager(db_manager)
    return collaboration_manager.add_comment(note_id, user_id, text, parent_id)

def track_changes(db_manager, note_id: int, user_id: int) -> List[Dict[str, Any]]:
    """
    Get change history for a note.
    
    Args:
        db_manager: Database manager instance
        note_id (int): ID of the note
        user_id (int): ID of the user requesting the changes
        
    Returns:
        List[Dict[str, Any]]: List of changes
    """
    collaboration_manager = CollaborationManager(db_manager)
    return collaboration_manager.get_note_changes(note_id, user_id)

def merge_changes(db_manager, note_id: int, user_id: int, from_user_id: int) -> bool:
    """
    Merge changes from another user into a note.
    
    Args:
        db_manager: Database manager instance
        note_id (int): ID of the note
        user_id (int): ID of the user merging changes
        from_user_id (int): ID of the user whose changes to merge
        
    Returns:
        bool: True if successful, False otherwise
    """
    collaboration_manager = CollaborationManager(db_manager)
    return collaboration_manager.merge_changes(note_id, user_id, from_user_id)