"""
Time-Sensitive Knowledge Highlighting module for AI Note System.
Flags outdated notes in fast-evolving fields and suggests updated resources.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import re

# Setup logging
logger = logging.getLogger("ai_note_system.processing.knowledge_freshness")

class KnowledgeFreshness:
    """
    Manages the freshness of knowledge in notes, flagging outdated content and suggesting updates.
    """
    
    def __init__(self, db_manager, research_monitor=None):
        """
        Initialize the knowledge freshness manager.
        
        Args:
            db_manager: Database manager instance
            research_monitor: Research monitor instance for finding updated resources
        """
        self.db_manager = db_manager
        self.research_monitor = research_monitor
        self._ensure_freshness_tables()
    
    def _ensure_freshness_tables(self) -> None:
        """
        Ensure the freshness-related tables exist in the database.
        """
        # Create knowledge_half_life table
        half_life_query = """
        CREATE TABLE IF NOT EXISTS knowledge_half_life (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL UNIQUE,
            half_life_days INTEGER NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute_query(half_life_query)
        
        # Create note_freshness table
        freshness_query = """
        CREATE TABLE IF NOT EXISTS note_freshness (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            freshness_score REAL NOT NULL,
            last_updated TIMESTAMP,
            is_outdated BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
            UNIQUE(note_id)
        )
        """
        self.db_manager.execute_query(freshness_query)
        
        # Create update_suggestions table
        suggestions_query = """
        CREATE TABLE IF NOT EXISTS update_suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            suggestion_type TEXT NOT NULL,
            suggestion TEXT NOT NULL,
            resource_url TEXT,
            resource_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(suggestions_query)
        
        # Insert default half-life values if not exists
        self._insert_default_half_lives()
    
    def _insert_default_half_lives(self) -> None:
        """
        Insert default knowledge half-life values if they don't exist.
        """
        # Check if half-life values already exist
        check_query = "SELECT COUNT(*) as count FROM knowledge_half_life"
        result = self.db_manager.execute_query(check_query).fetchone()
        
        if result and result["count"] > 0:
            return
        
        # Define default half-life values for different topics
        default_half_lives = [
            {
                "topic": "generative_ai",
                "half_life_days": 90,  # 3 months
                "description": "Generative AI, LLMs, and related technologies"
            },
            {
                "topic": "machine_learning",
                "half_life_days": 180,  # 6 months
                "description": "Machine learning algorithms and techniques"
            },
            {
                "topic": "deep_learning",
                "half_life_days": 180,  # 6 months
                "description": "Deep learning architectures and methods"
            },
            {
                "topic": "web_development",
                "half_life_days": 365,  # 1 year
                "description": "Web development frameworks and technologies"
            },
            {
                "topic": "mobile_development",
                "half_life_days": 365,  # 1 year
                "description": "Mobile app development frameworks and technologies"
            },
            {
                "topic": "programming_languages",
                "half_life_days": 730,  # 2 years
                "description": "Programming languages and their features"
            },
            {
                "topic": "data_science",
                "half_life_days": 365,  # 1 year
                "description": "Data science methods and tools"
            },
            {
                "topic": "cybersecurity",
                "half_life_days": 180,  # 6 months
                "description": "Cybersecurity threats and defenses"
            },
            {
                "topic": "blockchain",
                "half_life_days": 180,  # 6 months
                "description": "Blockchain technologies and cryptocurrencies"
            },
            {
                "topic": "quantum_computing",
                "half_life_days": 365,  # 1 year
                "description": "Quantum computing algorithms and hardware"
            },
            {
                "topic": "mathematics",
                "half_life_days": 3650,  # 10 years
                "description": "Mathematical concepts and theorems"
            },
            {
                "topic": "physics",
                "half_life_days": 1825,  # 5 years
                "description": "Physics principles and theories"
            },
            {
                "topic": "biology",
                "half_life_days": 730,  # 2 years
                "description": "Biological concepts and discoveries"
            },
            {
                "topic": "medicine",
                "half_life_days": 365,  # 1 year
                "description": "Medical treatments and research"
            },
            {
                "topic": "history",
                "half_life_days": 3650,  # 10 years
                "description": "Historical events and interpretations"
            }
        ]
        
        # Insert default half-life values
        for half_life in default_half_lives:
            query = """
            INSERT INTO knowledge_half_life (topic, half_life_days, description)
            VALUES (?, ?, ?)
            """
            
            self.db_manager.execute_query(query, (
                half_life["topic"],
                half_life["half_life_days"],
                half_life["description"]
            ))
        
        logger.info(f"Inserted {len(default_half_lives)} default knowledge half-life values")
    
    def set_half_life(self, topic: str, half_life_days: int, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Set the half-life for a topic.
        
        Args:
            topic (str): Topic name
            half_life_days (int): Half-life in days
            description (str, optional): Description of the topic
            
        Returns:
            Dict[str, Any]: Result of the operation
        """
        # Validate half-life
        if half_life_days <= 0:
            return {
                "status": "error",
                "message": "Half-life must be a positive number of days"
            }
        
        # Check if topic already exists
        check_query = "SELECT id FROM knowledge_half_life WHERE topic = ?"
        existing = self.db_manager.execute_query(check_query, (topic,)).fetchone()
        
        if existing:
            # Update existing topic
            update_query = """
            UPDATE knowledge_half_life
            SET half_life_days = ?, description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE topic = ?
            """
            
            self.db_manager.execute_query(update_query, (half_life_days, description, topic))
            
            return {
                "status": "success",
                "message": f"Updated half-life for topic '{topic}' to {half_life_days} days",
                "topic": topic,
                "half_life_days": half_life_days
            }
        else:
            # Insert new topic
            insert_query = """
            INSERT INTO knowledge_half_life (topic, half_life_days, description)
            VALUES (?, ?, ?)
            """
            
            self.db_manager.execute_query(insert_query, (topic, half_life_days, description))
            
            return {
                "status": "success",
                "message": f"Set half-life for topic '{topic}' to {half_life_days} days",
                "topic": topic,
                "half_life_days": half_life_days
            }
    
    def get_half_lives(self) -> List[Dict[str, Any]]:
        """
        Get all knowledge half-life values.
        
        Returns:
            List[Dict[str, Any]]: List of half-life values
        """
        query = "SELECT * FROM knowledge_half_life ORDER BY topic"
        results = self.db_manager.execute_query(query).fetchall()
        
        half_lives = [dict(result) for result in results]
        return half_lives
    
    def calculate_note_freshness(self, note_id: int) -> Dict[str, Any]:
        """
        Calculate the freshness score for a note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            Dict[str, Any]: Freshness calculation result
        """
        # Get note
        note_query = "SELECT * FROM notes WHERE id = ?"
        note = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        
        if not note:
            return {
                "status": "error",
                "message": f"Note with ID {note_id} not found"
            }
        
        # Get note tags
        tags = note.get("tags", "").split(",") if note.get("tags") else []
        
        # Get note creation date
        created_at = datetime.fromisoformat(note["created_at"]) if note.get("created_at") else datetime.now()
        
        # Get note last updated date (if available)
        last_updated = datetime.fromisoformat(note["updated_at"]) if note.get("updated_at") else created_at
        
        # Find applicable half-life values based on tags
        applicable_half_lives = []
        
        for tag in tags:
            tag = tag.strip().lower().replace(" ", "_")
            
            # Check for exact match
            half_life_query = "SELECT * FROM knowledge_half_life WHERE topic = ?"
            half_life = self.db_manager.execute_query(half_life_query, (tag,)).fetchone()
            
            if half_life:
                applicable_half_lives.append(dict(half_life))
                continue
            
            # Check for partial matches
            partial_query = "SELECT * FROM knowledge_half_life WHERE topic LIKE ? OR ? LIKE '%' || topic || '%'"
            partial_matches = self.db_manager.execute_query(partial_query, (f"%{tag}%", tag)).fetchall()
            
            for match in partial_matches:
                applicable_half_lives.append(dict(match))
        
        # If no applicable half-lives found, use a default value
        if not applicable_half_lives:
            default_half_life = 365  # 1 year
        else:
            # Use the shortest half-life (most conservative)
            default_half_life = min(hl["half_life_days"] for hl in applicable_half_lives)
        
        # Calculate age in days
        age_days = (datetime.now() - last_updated).days
        
        # Calculate freshness score using exponential decay formula
        # freshness = 2^(-age/half_life)
        # This gives 1.0 for fresh content and approaches 0.0 as content ages
        freshness_score = 2 ** (-age_days / default_half_life)
        
        # Determine if the note is outdated (freshness below 0.5)
        is_outdated = freshness_score < 0.5
        
        # Store freshness in database
        self._store_freshness(note_id, freshness_score, last_updated, is_outdated)
        
        return {
            "status": "success",
            "note_id": note_id,
            "freshness_score": freshness_score,
            "age_days": age_days,
            "half_life_days": default_half_life,
            "last_updated": last_updated.isoformat(),
            "is_outdated": is_outdated,
            "applicable_topics": [hl["topic"] for hl in applicable_half_lives]
        }
    
    def _store_freshness(self, note_id: int, freshness_score: float, last_updated: datetime, is_outdated: bool) -> None:
        """
        Store freshness information for a note.
        
        Args:
            note_id (int): ID of the note
            freshness_score (float): Freshness score (0.0 to 1.0)
            last_updated (datetime): When the note was last updated
            is_outdated (bool): Whether the note is considered outdated
        """
        # Check if freshness record already exists
        check_query = "SELECT id FROM note_freshness WHERE note_id = ?"
        existing = self.db_manager.execute_query(check_query, (note_id,)).fetchone()
        
        if existing:
            # Update existing record
            update_query = """
            UPDATE note_freshness
            SET freshness_score = ?, last_updated = ?, is_outdated = ?, updated_at = CURRENT_TIMESTAMP
            WHERE note_id = ?
            """
            
            self.db_manager.execute_query(update_query, (
                freshness_score,
                last_updated.isoformat(),
                1 if is_outdated else 0,
                note_id
            ))
        else:
            # Insert new record
            insert_query = """
            INSERT INTO note_freshness (note_id, freshness_score, last_updated, is_outdated)
            VALUES (?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(insert_query, (
                note_id,
                freshness_score,
                last_updated.isoformat(),
                1 if is_outdated else 0
            ))
    
    def check_outdated_notes(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Check for outdated notes.
        
        Args:
            topic (str, optional): Filter by topic
            
        Returns:
            Dict[str, Any]: List of outdated notes
        """
        # Build query
        if topic:
            query = """
            SELECT n.id, n.title, n.tags, n.created_at, n.updated_at, 
                   nf.freshness_score, nf.last_updated, nf.is_outdated
            FROM notes n
            LEFT JOIN note_freshness nf ON n.id = nf.note_id
            WHERE n.tags LIKE ? OR n.title LIKE ?
            ORDER BY nf.freshness_score ASC
            """
            
            search_term = f"%{topic}%"
            notes = self.db_manager.execute_query(query, (search_term, search_term)).fetchall()
        else:
            query = """
            SELECT n.id, n.title, n.tags, n.created_at, n.updated_at, 
                   nf.freshness_score, nf.last_updated, nf.is_outdated
            FROM notes n
            LEFT JOIN note_freshness nf ON n.id = nf.note_id
            ORDER BY nf.freshness_score ASC
            """
            
            notes = self.db_manager.execute_query(query).fetchall()
        
        # Process notes
        outdated_notes = []
        unchecked_notes = []
        
        for note in notes:
            note_dict = dict(note)
            
            # If freshness hasn't been calculated yet, calculate it now
            if note_dict.get("freshness_score") is None:
                freshness_result = self.calculate_note_freshness(note_dict["id"])
                
                if freshness_result["status"] == "success":
                    note_dict["freshness_score"] = freshness_result["freshness_score"]
                    note_dict["is_outdated"] = freshness_result["is_outdated"]
                    
                    if freshness_result["is_outdated"]:
                        outdated_notes.append(note_dict)
                    
                else:
                    unchecked_notes.append(note_dict)
            
            # If note is already marked as outdated, add to outdated list
            elif note_dict.get("is_outdated"):
                outdated_notes.append(note_dict)
        
        return {
            "status": "success",
            "outdated_notes": outdated_notes,
            "unchecked_notes": unchecked_notes,
            "total_outdated": len(outdated_notes),
            "total_unchecked": len(unchecked_notes)
        }
    
    def suggest_updates(self, note_id: int) -> Dict[str, Any]:
        """
        Suggest updates for an outdated note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            Dict[str, Any]: Update suggestions
        """
        # Get note
        note_query = "SELECT * FROM notes WHERE id = ?"
        note = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        
        if not note:
            return {
                "status": "error",
                "message": f"Note with ID {note_id} not found"
            }
        
        # Get note freshness
        freshness_query = "SELECT * FROM note_freshness WHERE note_id = ?"
        freshness = self.db_manager.execute_query(freshness_query, (note_id,)).fetchone()
        
        # If freshness hasn't been calculated yet, calculate it now
        if not freshness:
            freshness_result = self.calculate_note_freshness(note_id)
            
            if freshness_result["status"] != "success":
                return freshness_result
            
            is_outdated = freshness_result["is_outdated"]
        else:
            is_outdated = freshness["is_outdated"]
        
        # If note is not outdated, return early
        if not is_outdated:
            return {
                "status": "success",
                "message": "Note is not outdated, no updates needed",
                "note_id": note_id,
                "suggestions": []
            }
        
        # Get note tags and title
        tags = note.get("tags", "").split(",") if note.get("tags") else []
        title = note.get("title", "")
        
        # Generate update suggestions
        suggestions = []
        
        # 1. Check for existing suggestions
        existing_query = "SELECT * FROM update_suggestions WHERE note_id = ?"
        existing_suggestions = self.db_manager.execute_query(existing_query, (note_id,)).fetchall()
        
        if existing_suggestions:
            for suggestion in existing_suggestions:
                suggestions.append(dict(suggestion))
        
        # 2. If research monitor is available, use it to find relevant papers
        if self.research_monitor:
            # Use tags as search terms
            for tag in tags:
                tag = tag.strip()
                if not tag:
                    continue
                
                # Find papers related to the tag
                papers = self.research_monitor.list_papers(
                    user_id=note.get("user_id", 1),
                    category=tag,
                    limit=3
                )
                
                for paper in papers:
                    # Create suggestion
                    suggestion = {
                        "suggestion_type": "research_paper",
                        "suggestion": f"Consider updating with information from this paper: {paper['title']}",
                        "resource_url": paper.get("pdf_url", ""),
                        "resource_title": paper["title"]
                    }
                    
                    # Store suggestion
                    self._store_suggestion(note_id, suggestion)
                    suggestions.append(suggestion)
        
        # 3. Generate general update suggestions using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        prompt = f"""
        Generate update suggestions for an outdated note on the following topic:
        
        Title: {title}
        Tags: {', '.join(tags)}
        
        The note content is about:
        {note.get('summary', note.get('text', ''))[:500]}...
        
        Please suggest:
        1. Specific areas that might need updating
        2. Recent developments in this field that should be incorporated
        3. Resources (books, papers, websites) that might provide updated information
        
        Format your response as a JSON array of suggestion objects with the following fields:
        - suggestion_type: "content_update", "recent_development", or "resource"
        - suggestion: The suggestion text
        - resource_url: URL of a resource (if applicable)
        - resource_title: Title of the resource (if applicable)
        
        Provide 3-5 specific, actionable suggestions.
        """
        
        # Generate suggestions
        response = llm.generate_text(prompt)
        
        try:
            # Parse response
            llm_suggestions = json.loads(response)
            
            # Store and add suggestions
            for suggestion in llm_suggestions:
                if isinstance(suggestion, dict) and "suggestion" in suggestion:
                    # Store suggestion
                    self._store_suggestion(note_id, suggestion)
                    suggestions.append(suggestion)
            
        except json.JSONDecodeError:
            logger.error(f"Error parsing LLM suggestions: {response}")
        
        return {
            "status": "success",
            "note_id": note_id,
            "title": title,
            "tags": tags,
            "suggestions": suggestions
        }
    
    def _store_suggestion(self, note_id: int, suggestion: Dict[str, Any]) -> int:
        """
        Store an update suggestion.
        
        Args:
            note_id (int): ID of the note
            suggestion (Dict[str, Any]): Suggestion data
            
        Returns:
            int: ID of the stored suggestion
        """
        # Extract suggestion data
        suggestion_type = suggestion.get("suggestion_type", "general")
        suggestion_text = suggestion.get("suggestion", "")
        resource_url = suggestion.get("resource_url", "")
        resource_title = suggestion.get("resource_title", "")
        
        # Insert suggestion
        query = """
        INSERT INTO update_suggestions (note_id, suggestion_type, suggestion, resource_url, resource_title)
        VALUES (?, ?, ?, ?, ?)
        """
        
        cursor = self.db_manager.execute_query(query, (
            note_id,
            suggestion_type,
            suggestion_text,
            resource_url,
            resource_title
        ))
        
        return cursor.lastrowid
    
    def auto_update_note(self, note_id: int) -> Dict[str, Any]:
        """
        Automatically update an outdated note.
        
        Args:
            note_id (int): ID of the note
            
        Returns:
            Dict[str, Any]: Update result
        """
        # Get note
        note_query = "SELECT * FROM notes WHERE id = ?"
        note = self.db_manager.execute_query(note_query, (note_id,)).fetchone()
        
        if not note:
            return {
                "status": "error",
                "message": f"Note with ID {note_id} not found"
            }
        
        # Get update suggestions
        suggestions_result = self.suggest_updates(note_id)
        
        if suggestions_result["status"] != "success" or not suggestions_result.get("suggestions"):
            return {
                "status": "error",
                "message": "No update suggestions available",
                "note_id": note_id
            }
        
        # Generate updated content using LLM
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        suggestions_text = "\n".join([
            f"- {suggestion['suggestion']}" 
            for suggestion in suggestions_result["suggestions"]
        ])
        
        prompt = f"""
        Update the following note with the latest information based on the provided suggestions:
        
        Title: {note.get('title', '')}
        Tags: {note.get('tags', '')}
        
        Original content:
        {note.get('text', '')}
        
        Update suggestions:
        {suggestions_text}
        
        Please provide an updated version of the note that:
        1. Preserves the original structure and key information
        2. Incorporates the suggested updates
        3. Removes any outdated information
        4. Adds references to new sources where appropriate
        
        The updated note should be comprehensive and accurate, reflecting the latest developments in the field.
        """
        
        # Generate updated content
        updated_content = llm.generate_text(prompt)
        
        # Update the note
        update_query = """
        UPDATE notes
        SET text = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        self.db_manager.execute_query(update_query, (updated_content, note_id))
        
        # Recalculate freshness
        self.calculate_note_freshness(note_id)
        
        # Clear update suggestions
        clear_query = "DELETE FROM update_suggestions WHERE note_id = ?"
        self.db_manager.execute_query(clear_query, (note_id,))
        
        return {
            "status": "success",
            "message": "Note automatically updated",
            "note_id": note_id,
            "updated_content": updated_content
        }
    
    def generate_freshness_report(self) -> Dict[str, Any]:
        """
        Generate a report on knowledge freshness across all notes.
        
        Returns:
            Dict[str, Any]: Freshness report
        """
        # Get all notes with freshness data
        query = """
        SELECT n.id, n.title, n.tags, n.created_at, n.updated_at, 
               nf.freshness_score, nf.last_updated, nf.is_outdated
        FROM notes n
        LEFT JOIN note_freshness nf ON n.id = nf.note_id
        ORDER BY nf.freshness_score ASC
        """
        
        notes = self.db_manager.execute_query(query).fetchall()
        
        # Process notes
        total_notes = len(notes)
        notes_with_freshness = 0
        outdated_notes = 0
        freshness_scores = []
        
        for note in notes:
            if note["freshness_score"] is not None:
                notes_with_freshness += 1
                freshness_scores.append(note["freshness_score"])
                
                if note["is_outdated"]:
                    outdated_notes += 1
        
        # Calculate statistics
        avg_freshness = sum(freshness_scores) / len(freshness_scores) if freshness_scores else 0
        
        # Group by tags
        tags_freshness = {}
        
        for note in notes:
            if note["freshness_score"] is None:
                continue
                
            tags = note.get("tags", "").split(",") if note.get("tags") else []
            
            for tag in tags:
                tag = tag.strip()
                if not tag:
                    continue
                
                if tag not in tags_freshness:
                    tags_freshness[tag] = {
                        "count": 0,
                        "outdated": 0,
                        "freshness_scores": []
                    }
                
                tags_freshness[tag]["count"] += 1
                tags_freshness[tag]["freshness_scores"].append(note["freshness_score"])
                
                if note["is_outdated"]:
                    tags_freshness[tag]["outdated"] += 1
        
        # Calculate average freshness by tag
        for tag, data in tags_freshness.items():
            data["avg_freshness"] = sum(data["freshness_scores"]) / len(data["freshness_scores"])
            data["outdated_percentage"] = (data["outdated"] / data["count"]) * 100 if data["count"] > 0 else 0
        
        # Sort tags by average freshness
        sorted_tags = sorted(
            tags_freshness.items(),
            key=lambda x: x[1]["avg_freshness"]
        )
        
        # Create report
        report = {
            "total_notes": total_notes,
            "notes_with_freshness": notes_with_freshness,
            "outdated_notes": outdated_notes,
            "outdated_percentage": (outdated_notes / notes_with_freshness) * 100 if notes_with_freshness > 0 else 0,
            "avg_freshness": avg_freshness,
            "tags_freshness": dict(sorted_tags)
        }
        
        return {
            "status": "success",
            "report": report
        }
    
    def export_freshness_analytics(self, format: str = "csv", output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export freshness analytics.
        
        Args:
            format (str): Export format (csv, json)
            output_path (str, optional): Path to save the export
            
        Returns:
            Dict[str, Any]: Export result
        """
        # Generate report
        report_result = self.generate_freshness_report()
        
        if report_result["status"] != "success":
            return report_result
        
        report = report_result["report"]
        
        # Create output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"freshness_analytics_{timestamp}.{format}"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Export based on format
        if format.lower() == "json":
            # Export as JSON
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
        elif format.lower() == "csv":
            # Export as CSV
            import csv
            
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                # Write summary
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                writer.writerow(["Total Notes", report["total_notes"]])
                writer.writerow(["Notes with Freshness", report["notes_with_freshness"]])
                writer.writerow(["Outdated Notes", report["outdated_notes"]])
                writer.writerow(["Outdated Percentage", f"{report['outdated_percentage']:.2f}%"])
                writer.writerow(["Average Freshness", f"{report['avg_freshness']:.2f}"])
                writer.writerow([])
                
                # Write tags freshness
                writer.writerow(["Tag", "Count", "Outdated", "Outdated Percentage", "Average Freshness"])
                
                for tag, data in report["tags_freshness"].items():
                    writer.writerow([
                        tag,
                        data["count"],
                        data["outdated"],
                        f"{data['outdated_percentage']:.2f}%",
                        f"{data['avg_freshness']:.2f}"
                    ])
            
        else:
            return {
                "status": "error",
                "message": f"Unsupported export format: {format}"
            }
        
        return {
            "status": "success",
            "message": f"Exported freshness analytics to {format}",
            "output_path": output_path
        }

def check_outdated_notes(db_manager, topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Check for outdated notes.
    
    Args:
        db_manager: Database manager instance
        topic (str, optional): Filter by topic
        
    Returns:
        Dict[str, Any]: List of outdated notes
    """
    freshness = KnowledgeFreshness(db_manager)
    return freshness.check_outdated_notes(topic)

def suggest_updates(db_manager, note_id: int) -> Dict[str, Any]:
    """
    Suggest updates for an outdated note.
    
    Args:
        db_manager: Database manager instance
        note_id (int): ID of the note
        
    Returns:
        Dict[str, Any]: Update suggestions
    """
    freshness = KnowledgeFreshness(db_manager)
    return freshness.suggest_updates(note_id)

def set_half_life(db_manager, topic: str, half_life_months: int) -> Dict[str, Any]:
    """
    Set the half-life for a topic.
    
    Args:
        db_manager: Database manager instance
        topic (str): Topic name
        half_life_months (int): Half-life in months
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    freshness = KnowledgeFreshness(db_manager)
    half_life_days = half_life_months * 30  # Approximate conversion
    return freshness.set_half_life(topic, half_life_days)

def auto_update(db_manager, note_id: int) -> Dict[str, Any]:
    """
    Automatically update an outdated note.
    
    Args:
        db_manager: Database manager instance
        note_id (int): ID of the note
        
    Returns:
        Dict[str, Any]: Update result
    """
    freshness = KnowledgeFreshness(db_manager)
    return freshness.auto_update_note(note_id)

def generate_freshness_report(db_manager) -> Dict[str, Any]:
    """
    Generate a report on knowledge freshness across all notes.
    
    Args:
        db_manager: Database manager instance
        
    Returns:
        Dict[str, Any]: Freshness report
    """
    freshness = KnowledgeFreshness(db_manager)
    return freshness.generate_freshness_report()

def export_freshness_analytics(db_manager, format: str = "csv", output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Export freshness analytics.
    
    Args:
        db_manager: Database manager instance
        format (str): Export format (csv, json)
        output_path (str, optional): Path to save the export
        
    Returns:
        Dict[str, Any]: Export result
    """
    freshness = KnowledgeFreshness(db_manager)
    return freshness.export_freshness_analytics(format, output_path)