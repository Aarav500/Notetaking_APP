"""
Personal Research Summaries module for AI Note System.
Monitors specified ArXiv categories and generates personalized summaries with contextual relevance to notes.
"""

import os
import logging
import json
import tempfile
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import re

# Setup logging
logger = logging.getLogger("ai_note_system.inputs.research_monitor")

class ResearchMonitor:
    """
    Monitors research sources (primarily ArXiv) and generates personalized summaries.
    """
    
    def __init__(self, db_manager, embedder=None):
        """
        Initialize the research monitor.
        
        Args:
            db_manager: Database manager instance
            embedder: Embedder instance for finding relevant notes
        """
        self.db_manager = db_manager
        self.embedder = embedder
        self._ensure_research_tables()
    
    def _ensure_research_tables(self) -> None:
        """
        Ensure the research-related tables exist in the database.
        """
        # Create monitored_categories table
        categories_query = """
        CREATE TABLE IF NOT EXISTS monitored_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            last_checked TIMESTAMP,
            check_frequency INTEGER DEFAULT 86400,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, category)
        )
        """
        self.db_manager.execute_query(categories_query)
        
        # Create research_papers table
        papers_query = """
        CREATE TABLE IF NOT EXISTS research_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            arxiv_id TEXT UNIQUE,
            title TEXT NOT NULL,
            authors TEXT,
            abstract TEXT,
            pdf_url TEXT,
            published_date TIMESTAMP,
            categories TEXT,
            retrieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.db_manager.execute_query(papers_query)
        
        # Create paper_summaries table
        summaries_query = """
        CREATE TABLE IF NOT EXISTS paper_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            summary TEXT NOT NULL,
            relevance_score REAL,
            relevance_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES research_papers(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(paper_id, user_id)
        )
        """
        self.db_manager.execute_query(summaries_query)
        
        # Create paper_connections table
        connections_query = """
        CREATE TABLE IF NOT EXISTS paper_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            note_id INTEGER NOT NULL,
            connection_type TEXT NOT NULL,
            connection_strength REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (paper_id) REFERENCES research_papers(id) ON DELETE CASCADE,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(connections_query)
    
    def setup_monitoring(self, user_id: int, categories: List[str], check_frequency: int = 86400) -> Dict[str, Any]:
        """
        Set up monitoring for ArXiv categories.
        
        Args:
            user_id (int): ID of the user
            categories (List[str]): List of ArXiv categories to monitor
            check_frequency (int): Frequency to check for updates in seconds (default: daily)
            
        Returns:
            Dict[str, Any]: Setup result
        """
        # Validate categories
        valid_categories = self._validate_arxiv_categories(categories)
        invalid_categories = [cat for cat in categories if cat not in valid_categories]
        
        if invalid_categories:
            logger.warning(f"Invalid ArXiv categories: {', '.join(invalid_categories)}")
        
        if not valid_categories:
            return {
                "status": "error",
                "message": "No valid ArXiv categories provided",
                "invalid_categories": invalid_categories
            }
        
        # Add categories to database
        added_categories = []
        for category in valid_categories:
            try:
                query = """
                INSERT INTO monitored_categories (user_id, category, check_frequency)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, category) 
                DO UPDATE SET check_frequency = ?
                """
                
                self.db_manager.execute_query(query, (user_id, category, check_frequency, check_frequency))
                added_categories.append(category)
            except Exception as e:
                logger.error(f"Error adding category {category}: {e}")
        
        # Perform initial check for papers
        if added_categories:
            self.check_for_updates(user_id, categories=added_categories)
        
        return {
            "status": "success",
            "message": f"Monitoring set up for {len(added_categories)} categories",
            "categories": added_categories,
            "invalid_categories": invalid_categories
        }
    
    def _validate_arxiv_categories(self, categories: List[str]) -> List[str]:
        """
        Validate ArXiv categories.
        
        Args:
            categories (List[str]): List of categories to validate
            
        Returns:
            List[str]: List of valid categories
        """
        # List of valid ArXiv categories
        valid_prefixes = [
            "astro-ph", "cond-mat", "cs", "econ", "eess", "gr-qc", "hep-ex", "hep-lat", 
            "hep-ph", "hep-th", "math", "math-ph", "nlin", "nucl-ex", "nucl-th", 
            "physics", "q-bio", "q-fin", "quant-ph", "stat"
        ]
        
        # Validate each category
        valid_categories = []
        for category in categories:
            # Check if it's a valid category format
            if "." in category:
                prefix, suffix = category.split(".", 1)
                if prefix in valid_prefixes:
                    valid_categories.append(category)
            elif category in valid_prefixes:
                valid_categories.append(category)
        
        return valid_categories
    
    def list_monitored_categories(self, user_id: int) -> List[Dict[str, Any]]:
        """
        List monitored ArXiv categories for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of monitored categories
        """
        query = """
        SELECT * FROM monitored_categories
        WHERE user_id = ?
        ORDER BY category
        """
        
        results = self.db_manager.execute_query(query, (user_id,)).fetchall()
        
        categories = []
        for result in results:
            category = dict(result)
            
            # Get paper count for this category
            count_query = """
            SELECT COUNT(*) as paper_count
            FROM research_papers
            WHERE categories LIKE ?
            """
            
            count_result = self.db_manager.execute_query(count_query, (f"%{category['category']}%",)).fetchone()
            category["paper_count"] = count_result["paper_count"] if count_result else 0
            
            categories.append(category)
        
        return categories
    
    def remove_category(self, user_id: int, category: str) -> bool:
        """
        Remove a monitored category.
        
        Args:
            user_id (int): ID of the user
            category (str): Category to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        DELETE FROM monitored_categories
        WHERE user_id = ? AND category = ?
        """
        
        cursor = self.db_manager.execute_query(query, (user_id, category))
        
        if cursor.rowcount > 0:
            logger.info(f"Removed category {category} for user {user_id}")
            return True
        else:
            logger.warning(f"Category {category} not found for user {user_id}")
            return False
    
    def check_for_updates(self, user_id: int, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Check for updates in monitored categories.
        
        Args:
            user_id (int): ID of the user
            categories (List[str], optional): Specific categories to check
            
        Returns:
            Dict[str, Any]: Update result
        """
        # Get monitored categories
        if categories:
            category_list = categories
        else:
            query = """
            SELECT category, last_checked
            FROM monitored_categories
            WHERE user_id = ?
            """
            
            results = self.db_manager.execute_query(query, (user_id,)).fetchall()
            category_list = [result["category"] for result in results]
        
        if not category_list:
            return {
                "status": "error",
                "message": "No monitored categories found"
            }
        
        # Check each category for new papers
        new_papers = []
        for category in category_list:
            try:
                # Get last checked time
                last_checked_query = """
                SELECT last_checked
                FROM monitored_categories
                WHERE user_id = ? AND category = ?
                """
                
                last_checked_result = self.db_manager.execute_query(last_checked_query, (user_id, category)).fetchone()
                
                if last_checked_result and last_checked_result["last_checked"]:
                    last_checked = datetime.fromisoformat(last_checked_result["last_checked"])
                else:
                    # If never checked, use 7 days ago as default
                    last_checked = datetime.now() - timedelta(days=7)
                
                # Fetch papers from ArXiv
                category_papers = self._fetch_arxiv_papers(category, last_checked)
                
                # Store papers in database
                for paper in category_papers:
                    paper_id = self._store_paper(paper)
                    if paper_id:
                        new_papers.append({
                            "id": paper_id,
                            "arxiv_id": paper["arxiv_id"],
                            "title": paper["title"],
                            "category": category
                        })
                
                # Update last checked time
                update_query = """
                UPDATE monitored_categories
                SET last_checked = ?
                WHERE user_id = ? AND category = ?
                """
                
                self.db_manager.execute_query(update_query, (datetime.now().isoformat(), user_id, category))
                
            except Exception as e:
                logger.error(f"Error checking category {category}: {e}")
        
        return {
            "status": "success",
            "message": f"Found {len(new_papers)} new papers",
            "new_papers": new_papers
        }
    
    def _fetch_arxiv_papers(self, category: str, since: datetime) -> List[Dict[str, Any]]:
        """
        Fetch papers from ArXiv API.
        
        Args:
            category (str): ArXiv category
            since (datetime): Fetch papers published since this date
            
        Returns:
            List[Dict[str, Any]]: List of papers
        """
        # Format date for ArXiv query
        since_str = since.strftime("%Y%m%d%H%M%S")
        
        # Construct ArXiv API URL
        url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&sortBy=submittedDate&sortOrder=descending&max_results=50"
        
        try:
            # Make request to ArXiv API
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Extract papers
            papers = []
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                # Get publication date
                published = entry.find("{http://www.w3.org/2005/Atom}published")
                if published is None:
                    continue
                
                published_date = datetime.fromisoformat(published.text.replace("Z", "+00:00"))
                
                # Skip papers published before the since date
                if published_date < since:
                    continue
                
                # Extract paper details
                paper = {
                    "arxiv_id": entry.find("{http://www.w3.org/2005/Atom}id").text.split("/")[-1],
                    "title": entry.find("{http://www.w3.org/2005/Atom}title").text.strip(),
                    "authors": ", ".join([author.find("{http://www.w3.org/2005/Atom}name").text for author in entry.findall("{http://www.w3.org/2005/Atom}author")]),
                    "abstract": entry.find("{http://www.w3.org/2005/Atom}summary").text.strip(),
                    "pdf_url": next((link.get("href") for link in entry.findall("{http://www.w3.org/2005/Atom}link") if link.get("title") == "pdf"), ""),
                    "published_date": published_date.isoformat(),
                    "categories": ", ".join([cat.get("term") for cat in entry.findall("{http://www.w3.org/2005/Atom}category")])
                }
                
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error fetching papers from ArXiv: {e}")
            return []
    
    def _store_paper(self, paper: Dict[str, Any]) -> Optional[int]:
        """
        Store a paper in the database.
        
        Args:
            paper (Dict[str, Any]): Paper details
            
        Returns:
            Optional[int]: ID of the stored paper, or None if failed
        """
        try:
            # Check if paper already exists
            check_query = """
            SELECT id FROM research_papers
            WHERE arxiv_id = ?
            """
            
            existing = self.db_manager.execute_query(check_query, (paper["arxiv_id"],)).fetchone()
            if existing:
                return existing["id"]
            
            # Insert paper
            query = """
            INSERT INTO research_papers (arxiv_id, title, authors, abstract, pdf_url, published_date, categories)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor = self.db_manager.execute_query(query, (
                paper["arxiv_id"],
                paper["title"],
                paper["authors"],
                paper["abstract"],
                paper["pdf_url"],
                paper["published_date"],
                paper["categories"]
            ))
            
            return cursor.lastrowid
            
        except Exception as e:
            logger.error(f"Error storing paper: {e}")
            return None
    
    def list_papers(self, user_id: int, category: Optional[str] = None, limit: int = 50, min_relevance: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        List papers from monitored categories.
        
        Args:
            user_id (int): ID of the user
            category (str, optional): Filter by category
            limit (int): Maximum number of papers to return
            min_relevance (float, optional): Minimum relevance score
            
        Returns:
            List[Dict[str, Any]]: List of papers
        """
        # Build query
        query_parts = ["SELECT rp.*, ps.summary, ps.relevance_score, ps.relevance_notes"]
        from_parts = ["FROM research_papers rp"]
        where_parts = []
        params = []
        
        # Join with summaries if available
        from_parts.append("LEFT JOIN paper_summaries ps ON rp.id = ps.paper_id AND ps.user_id = ?")
        params.append(user_id)
        
        # Filter by category if provided
        if category:
            where_parts.append("rp.categories LIKE ?")
            params.append(f"%{category}%")
        else:
            # Only show papers from monitored categories
            from_parts.append("JOIN monitored_categories mc ON mc.user_id = ? AND rp.categories LIKE '%' || mc.category || '%'")
            params.append(user_id)
        
        # Filter by relevance if provided
        if min_relevance is not None:
            where_parts.append("(ps.relevance_score IS NULL OR ps.relevance_score >= ?)")
            params.append(min_relevance)
        
        # Combine query parts
        query = " ".join(query_parts) + " " + " ".join(from_parts)
        if where_parts:
            query += " WHERE " + " AND ".join(where_parts)
        
        # Add order and limit
        query += " ORDER BY rp.published_date DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        papers = [dict(result) for result in results]
        return papers
    
    def generate_summary(self, user_id: int, paper_id: int, with_relevance: bool = True) -> Dict[str, Any]:
        """
        Generate a personalized summary for a paper.
        
        Args:
            user_id (int): ID of the user
            paper_id (int): ID of the paper
            with_relevance (bool): Whether to include relevance to user's notes
            
        Returns:
            Dict[str, Any]: Generated summary
        """
        # Get paper details
        paper_query = """
        SELECT * FROM research_papers
        WHERE id = ?
        """
        
        paper = self.db_manager.execute_query(paper_query, (paper_id,)).fetchone()
        if not paper:
            return {
                "status": "error",
                "message": f"Paper with ID {paper_id} not found"
            }
        
        # Check if summary already exists
        summary_query = """
        SELECT * FROM paper_summaries
        WHERE paper_id = ? AND user_id = ?
        """
        
        existing_summary = self.db_manager.execute_query(summary_query, (paper_id, user_id)).fetchone()
        if existing_summary:
            return {
                "status": "success",
                "message": "Summary already exists",
                "paper": dict(paper),
                "summary": existing_summary["summary"],
                "relevance_score": existing_summary["relevance_score"],
                "relevance_notes": existing_summary["relevance_notes"]
            }
        
        # Get relevant notes if requested
        relevant_notes = []
        if with_relevance and self.embedder:
            # Use abstract as query
            abstract = paper["abstract"]
            
            # Get relevant notes
            relevant_notes = self.embedder.search_notes_by_embedding(
                query_text=abstract,
                limit=5,
                threshold=0.6
            )
            
            # Fetch full note content
            for i, note in enumerate(relevant_notes):
                note_id = note["id"]
                full_note = self.db_manager.get_note(note_id)
                if full_note:
                    relevant_notes[i] = full_note
        
        # Generate summary
        from ai_note_system.api.llm_interface import get_llm_interface
        
        # Get LLM interface
        llm = get_llm_interface("openai", model="gpt-4")
        
        # Create prompt
        if with_relevance and relevant_notes:
            # Create context from relevant notes
            notes_context = "\n\n".join([
                f"Note {i+1}: {note.get('title', 'Untitled')}\n{note.get('summary', note.get('text', ''))[:500]}..."
                for i, note in enumerate(relevant_notes)
            ])
            
            prompt = f"""
            Generate a personalized research summary for the following paper, highlighting its relevance to the user's existing notes.
            
            Paper Title: {paper["title"]}
            Authors: {paper["authors"]}
            Abstract: {paper["abstract"]}
            
            User's relevant notes:
            {notes_context}
            
            Your summary should include:
            1. A concise summary of the paper's key contributions and findings
            2. How this paper relates to the user's existing notes
            3. Potential applications or extensions relevant to the user's interests
            4. Key takeaways that would be most valuable for the user
            
            Also provide a relevance score from 0.0 to 1.0 indicating how relevant this paper is to the user's notes,
            and brief notes explaining the relevance score.
            
            Format your response as a JSON object with the following fields:
            - summary: The personalized summary
            - relevance_score: A float from 0.0 to 1.0
            - relevance_notes: Brief explanation of the relevance
            """
        else:
            prompt = f"""
            Generate a concise research summary for the following paper:
            
            Paper Title: {paper["title"]}
            Authors: {paper["authors"]}
            Abstract: {paper["abstract"]}
            
            Your summary should include:
            1. The paper's key contributions and findings
            2. The significance of this research
            3. Potential applications or implications
            4. Key takeaways for someone interested in this field
            
            Format your response as a JSON object with the following fields:
            - summary: The research summary
            - relevance_score: null
            - relevance_notes: null
            """
        
        # Generate summary
        response = llm.generate_text(prompt)
        
        try:
            # Parse response
            summary_data = json.loads(response)
            
            # Extract fields
            summary = summary_data.get("summary", "")
            relevance_score = summary_data.get("relevance_score")
            relevance_notes = summary_data.get("relevance_notes")
            
            # Store summary
            store_query = """
            INSERT INTO paper_summaries (paper_id, user_id, summary, relevance_score, relevance_notes)
            VALUES (?, ?, ?, ?, ?)
            """
            
            self.db_manager.execute_query(store_query, (paper_id, user_id, summary, relevance_score, relevance_notes))
            
            # Store connections to relevant notes
            if with_relevance and relevant_notes:
                for note in relevant_notes:
                    note_id = note["id"]
                    
                    # Calculate connection strength based on similarity
                    connection_strength = note.get("similarity", 0.5)
                    
                    # Store connection
                    connection_query = """
                    INSERT INTO paper_connections (paper_id, note_id, connection_type, connection_strength, description)
                    VALUES (?, ?, ?, ?, ?)
                    """
                    
                    self.db_manager.execute_query(connection_query, (
                        paper_id,
                        note_id,
                        "relevant",
                        connection_strength,
                        f"Automatically detected relevance between paper and note"
                    ))
            
            return {
                "status": "success",
                "message": "Summary generated",
                "paper": dict(paper),
                "summary": summary,
                "relevance_score": relevance_score,
                "relevance_notes": relevance_notes,
                "relevant_notes": [{"id": note["id"], "title": note.get("title", "Untitled"), "similarity": note.get("similarity", 0)} for note in relevant_notes] if with_relevance else []
            }
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {
                "status": "error",
                "message": f"Error generating summary: {e}",
                "paper": dict(paper)
            }
    
    def get_paper_connections(self, user_id: int, paper_id: Optional[int] = None, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get connections between papers and notes/projects.
        
        Args:
            user_id (int): ID of the user
            paper_id (int, optional): ID of the paper
            project_id (int, optional): ID of the project
            
        Returns:
            List[Dict[str, Any]]: List of connections
        """
        # Build query
        query_parts = ["SELECT pc.*, rp.title as paper_title, rp.arxiv_id, n.title as note_title"]
        from_parts = ["FROM paper_connections pc"]
        where_parts = []
        params = []
        
        # Join with papers and notes
        from_parts.append("JOIN research_papers rp ON pc.paper_id = rp.id")
        from_parts.append("JOIN notes n ON pc.note_id = n.id")
        
        # Filter by user
        where_parts.append("n.user_id = ?")
        params.append(user_id)
        
        # Filter by paper if provided
        if paper_id:
            where_parts.append("pc.paper_id = ?")
            params.append(paper_id)
        
        # Filter by project if provided
        if project_id:
            where_parts.append("n.project_id = ?")
            params.append(project_id)
        
        # Combine query parts
        query = " ".join(query_parts) + " " + " ".join(from_parts)
        if where_parts:
            query += " WHERE " + " AND ".join(where_parts)
        
        # Add order
        query += " ORDER BY pc.connection_strength DESC"
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        connections = [dict(result) for result in results]
        return connections
    
    def export_summaries(self, user_id: int, format: str = "markdown", output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Export research summaries.
        
        Args:
            user_id (int): ID of the user
            format (str): Export format (markdown, json)
            output_path (str, optional): Path to save the export
            
        Returns:
            Dict[str, Any]: Export result
        """
        # Get summaries
        query = """
        SELECT ps.*, rp.*
        FROM paper_summaries ps
        JOIN research_papers rp ON ps.paper_id = rp.id
        WHERE ps.user_id = ?
        ORDER BY rp.published_date DESC
        """
        
        results = self.db_manager.execute_query(query, (user_id,)).fetchall()
        
        if not results:
            return {
                "status": "error",
                "message": "No summaries found"
            }
        
        # Create output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = tempfile.gettempdir()
            output_path = os.path.join(output_dir, f"research_summaries_{timestamp}.{format}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Export based on format
        if format.lower() == "json":
            # Export as JSON
            summaries = [dict(result) for result in results]
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(summaries, f, ensure_ascii=False, indent=2)
            
        elif format.lower() == "markdown":
            # Export as Markdown
            md_content = ["# Research Summaries\n"]
            
            for result in results:
                # Add paper details
                md_content.append(f"## {result['title']}")
                md_content.append(f"**Authors:** {result['authors']}")
                md_content.append(f"**Published:** {result['published_date']}")
                md_content.append(f"**ArXiv ID:** {result['arxiv_id']}")
                md_content.append(f"**Categories:** {result['categories']}")
                md_content.append("")
                
                # Add abstract
                md_content.append("### Abstract")
                md_content.append(result["abstract"])
                md_content.append("")
                
                # Add summary
                md_content.append("### Summary")
                md_content.append(result["summary"])
                md_content.append("")
                
                # Add relevance if available
                if result["relevance_score"] is not None:
                    md_content.append(f"**Relevance Score:** {result['relevance_score']}")
                    md_content.append("")
                    md_content.append("**Relevance Notes:**")
                    md_content.append(result["relevance_notes"])
                    md_content.append("")
                
                # Add separator
                md_content.append("---")
                md_content.append("")
            
            # Write to file
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_content))
        
        else:
            return {
                "status": "error",
                "message": f"Unsupported export format: {format}"
            }
        
        return {
            "status": "success",
            "message": f"Exported {len(results)} summaries to {format}",
            "output_path": output_path
        }

def setup_monitoring(db_manager, user_id: int, categories: List[str], check_frequency: int = 86400) -> Dict[str, Any]:
    """
    Set up monitoring for ArXiv categories.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        categories (List[str]): List of ArXiv categories to monitor
        check_frequency (int): Frequency to check for updates in seconds (default: daily)
        
    Returns:
        Dict[str, Any]: Setup result
    """
    monitor = ResearchMonitor(db_manager)
    return monitor.setup_monitoring(user_id, categories, check_frequency)

def check_for_updates(db_manager, user_id: int, categories: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Check for updates in monitored categories.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        categories (List[str], optional): Specific categories to check
        
    Returns:
        Dict[str, Any]: Update result
    """
    monitor = ResearchMonitor(db_manager)
    return monitor.check_for_updates(user_id, categories)

def generate_summary(db_manager, embedder, user_id: int, paper_id: int, with_relevance: bool = True) -> Dict[str, Any]:
    """
    Generate a personalized summary for a paper.
    
    Args:
        db_manager: Database manager instance
        embedder: Embedder instance for finding relevant notes
        user_id (int): ID of the user
        paper_id (int): ID of the paper
        with_relevance (bool): Whether to include relevance to user's notes
        
    Returns:
        Dict[str, Any]: Generated summary
    """
    monitor = ResearchMonitor(db_manager, embedder)
    return monitor.generate_summary(user_id, paper_id, with_relevance)

def get_paper_connections(db_manager, user_id: int, project_id: int) -> List[Dict[str, Any]]:
    """
    Get connections between papers and notes in a project.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        project_id (int): ID of the project
        
    Returns:
        List[Dict[str, Any]]: List of connections
    """
    monitor = ResearchMonitor(db_manager)
    return monitor.get_paper_connections(user_id, project_id=project_id)

def export_summaries(db_manager, user_id: int, format: str = "markdown", output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Export research summaries.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        format (str): Export format (markdown, json)
        output_path (str, optional): Path to save the export
        
    Returns:
        Dict[str, Any]: Export result
    """
    monitor = ResearchMonitor(db_manager)
    return monitor.export_summaries(user_id, format, output_path)

def filter_papers_by_relevance(db_manager, user_id: int, min_relevance: float = 0.7) -> List[Dict[str, Any]]:
    """
    Filter papers by relevance score.
    
    Args:
        db_manager: Database manager instance
        user_id (int): ID of the user
        min_relevance (float): Minimum relevance score
        
    Returns:
        List[Dict[str, Any]]: List of papers
    """
    monitor = ResearchMonitor(db_manager)
    return monitor.list_papers(user_id, min_relevance=min_relevance)