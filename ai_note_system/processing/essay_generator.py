"""
Automatic Essay & Report Draft Generator

This module provides functionality for generating structured essay and report drafts
with proper citations based on notes and specified preferences.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import re

# Import related components
from ..database.db_manager import DatabaseManager
from ..api.llm_interface import LLMInterface, get_llm_interface
from ..embeddings.embedder import Embedder

# Set up logging
logger = logging.getLogger(__name__)

class CitationStyle:
    """Citation style formats"""
    APA = "apa"
    MLA = "mla"
    IEEE = "ieee"
    CHICAGO = "chicago"
    HARVARD = "harvard"

class EssayGenerator:
    """
    Automatic Essay & Report Draft Generator
    
    Features:
    - Generate structured essay and report drafts
    - Include proper citations in various formats
    - Create summary tables for quick review
    - Support refinement loop for improving drafts
    """
    
    def __init__(self, db_manager: DatabaseManager, 
                 llm_interface: Optional[LLMInterface] = None,
                 embedder: Optional[Embedder] = None):
        """Initialize the essay generator"""
        self.db_manager = db_manager
        self.llm_interface = llm_interface or get_llm_interface()
        self.embedder = embedder or Embedder(db_manager.db_path)
        
        # Ensure database tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Ensure that all required tables exist in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Create essay drafts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS essay_drafts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            content TEXT NOT NULL,
            citation_style TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_updated_at TEXT NOT NULL,
            version INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Create essay sources table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS essay_sources (
            id INTEGER PRIMARY KEY,
            essay_id INTEGER NOT NULL,
            note_id INTEGER,
            source_type TEXT NOT NULL,
            title TEXT,
            authors TEXT,
            year TEXT,
            url TEXT,
            publisher TEXT,
            journal TEXT,
            volume TEXT,
            issue TEXT,
            pages TEXT,
            doi TEXT,
            citation_text TEXT,
            FOREIGN KEY (essay_id) REFERENCES essay_drafts(id),
            FOREIGN KEY (note_id) REFERENCES notes(id)
        )
        ''')
        
        # Create essay feedback table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS essay_feedback (
            id INTEGER PRIMARY KEY,
            essay_id INTEGER NOT NULL,
            feedback_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (essay_id) REFERENCES essay_drafts(id)
        )
        ''')
        
        conn.commit()
    
    def generate_essay_draft(self, user_id: int, topic: str, 
                           notes_ids: List[int] = None,
                           citation_style: str = CitationStyle.APA,
                           word_count: int = 1500,
                           include_summary_table: bool = True) -> Dict[str, Any]:
        """
        Generate an essay draft based on a topic and notes
        
        Args:
            user_id: The ID of the user
            topic: The topic of the essay
            notes_ids: Optional list of note IDs to use as sources
            citation_style: The citation style to use
            word_count: Target word count for the essay
            include_summary_table: Whether to include a summary table
            
        Returns:
            Dictionary with the generated essay draft
        """
        logger.info(f"Generating essay draft on topic: {topic}")
        
        # Get relevant notes if note_ids not provided
        if not notes_ids:
            notes_ids = self._find_relevant_notes(user_id, topic)
        
        # Get notes content
        notes_content = self._get_notes_content(notes_ids)
        
        if not notes_content:
            return {"error": "No relevant notes found for the topic"}
        
        # Generate essay structure
        essay_structure = self._generate_essay_structure(topic, notes_content, word_count)
        
        # Generate essay content
        essay_content = self._generate_essay_content(
            topic, 
            essay_structure, 
            notes_content, 
            citation_style, 
            word_count
        )
        
        # Generate summary table if requested
        summary_table = None
        if include_summary_table:
            summary_table = self._generate_summary_table(topic, essay_content, notes_content)
            essay_content += f"\n\n## Summary Table\n\n{summary_table}"
        
        # Store the essay draft in the database
        essay_id = self._store_essay_draft(user_id, topic, essay_content, citation_style)
        
        # Store sources
        self._store_essay_sources(essay_id, notes_ids, notes_content, citation_style)
        
        return {
            "id": essay_id,
            "title": self._generate_title(topic, essay_content),
            "topic": topic,
            "content": essay_content,
            "structure": essay_structure,
            "summary_table": summary_table,
            "word_count": len(essay_content.split()),
            "citation_style": citation_style,
            "sources_count": len(notes_ids)
        }
    
    def refine_essay_draft(self, essay_id: int, feedback: str) -> Dict[str, Any]:
        """
        Refine an essay draft based on feedback
        
        Args:
            essay_id: The ID of the essay draft
            feedback: Feedback for improving the essay
            
        Returns:
            Dictionary with the refined essay draft
        """
        logger.info(f"Refining essay draft {essay_id} based on feedback")
        
        # Get the current essay draft
        essay_draft = self.get_essay_draft(essay_id)
        
        if not essay_draft:
            return {"error": f"Essay draft with ID {essay_id} not found"}
        
        # Store the feedback
        self._store_essay_feedback(essay_id, feedback)
        
        # Get sources for the essay
        sources = self._get_essay_sources(essay_id)
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert essay editor. You need to refine the following essay draft based on the provided feedback.
        
        Original Essay:
        {essay_draft['content']}
        
        Feedback:
        {feedback}
        
        Please revise the essay to address the feedback while maintaining the original structure and citations.
        Improve clarity, argumentation, and conciseness as needed.
        
        The essay should use {essay_draft['citation_style']} citation style.
        
        Available sources:
        {self._format_sources_for_prompt(sources)}
        
        Return the revised essay with the same structure and headings as the original.
        """
        
        # Generate refined essay using LLM
        refined_content = self.llm_interface.generate_text(prompt, max_tokens=4000)
        
        # Update the essay draft in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        last_updated_at = datetime.now().isoformat()
        
        cursor.execute('''
        UPDATE essay_drafts
        SET content = ?, last_updated_at = ?, version = version + 1
        WHERE id = ?
        ''', (refined_content, last_updated_at, essay_id))
        
        conn.commit()
        
        # Get the updated essay draft
        updated_draft = self.get_essay_draft(essay_id)
        
        return updated_draft
    
    def get_essay_draft(self, essay_id: int) -> Dict[str, Any]:
        """
        Get an essay draft by ID
        
        Args:
            essay_id: The ID of the essay draft
            
        Returns:
            Dictionary with the essay draft details
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, user_id, title, topic, content, citation_style, created_at, last_updated_at, version
        FROM essay_drafts
        WHERE id = ?
        ''', (essay_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return {}
        
        essay_draft = {
            'id': row[0],
            'user_id': row[1],
            'title': row[2],
            'topic': row[3],
            'content': row[4],
            'citation_style': row[5],
            'created_at': row[6],
            'last_updated_at': row[7],
            'version': row[8],
            'sources': self._get_essay_sources(row[0]),
            'feedback': self._get_essay_feedback(row[0])
        }
        
        return essay_draft
    
    def get_user_essay_drafts(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get essay drafts for a user
        
        Args:
            user_id: The ID of the user
            limit: Maximum number of drafts to return
            
        Returns:
            List of essay draft summaries
        """
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, title, topic, created_at, last_updated_at, version
        FROM essay_drafts
        WHERE user_id = ?
        ORDER BY last_updated_at DESC
        LIMIT ?
        ''', (user_id, limit))
        
        drafts = []
        for row in cursor.fetchall():
            draft = {
                'id': row[0],
                'title': row[1],
                'topic': row[2],
                'created_at': row[3],
                'last_updated_at': row[4],
                'version': row[5]
            }
            drafts.append(draft)
        
        return drafts
    
    def format_citations(self, essay_id: int, citation_style: str) -> Dict[str, Any]:
        """
        Format citations in an essay according to a specific style
        
        Args:
            essay_id: The ID of the essay draft
            citation_style: The citation style to use
            
        Returns:
            Dictionary with the updated essay and bibliography
        """
        logger.info(f"Formatting citations in essay {essay_id} using {citation_style} style")
        
        # Get the current essay draft
        essay_draft = self.get_essay_draft(essay_id)
        
        if not essay_draft:
            return {"error": f"Essay draft with ID {essay_id} not found"}
        
        # Get sources for the essay
        sources = self._get_essay_sources(essay_id)
        
        # Format in-text citations
        updated_content = self._format_in_text_citations(essay_draft['content'], sources, citation_style)
        
        # Generate bibliography
        bibliography = self._generate_bibliography(sources, citation_style)
        
        # Add bibliography to the essay
        if "# References" in updated_content or "# Bibliography" in updated_content or "# Works Cited" in updated_content:
            # Replace existing bibliography section
            updated_content = re.sub(
                r'# References.*|# Bibliography.*|# Works Cited.*', 
                f"# {self._get_bibliography_title(citation_style)}\n\n{bibliography}", 
                updated_content, 
                flags=re.DOTALL
            )
        else:
            # Add bibliography section at the end
            updated_content += f"\n\n# {self._get_bibliography_title(citation_style)}\n\n{bibliography}"
        
        # Update the essay draft in the database
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        last_updated_at = datetime.now().isoformat()
        
        cursor.execute('''
        UPDATE essay_drafts
        SET content = ?, citation_style = ?, last_updated_at = ?, version = version + 1
        WHERE id = ?
        ''', (updated_content, citation_style, last_updated_at, essay_id))
        
        conn.commit()
        
        # Get the updated essay draft
        updated_draft = self.get_essay_draft(essay_id)
        
        return updated_draft
    
    def _find_relevant_notes(self, user_id: int, topic: str, limit: int = 10) -> List[int]:
        """Find relevant notes for a topic using semantic search"""
        # Use embedder to search for relevant notes
        results = self.embedder.search_notes_by_embedding(topic, limit=limit)
        
        # Filter results to only include notes from the user
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        note_ids = []
        for result in results:
            note_id = result['note_id']
            
            cursor.execute('''
            SELECT user_id FROM notes WHERE id = ?
            ''', (note_id,))
            
            row = cursor.fetchone()
            if row and row[0] == user_id:
                note_ids.append(note_id)
        
        return note_ids
    
    def _get_notes_content(self, note_ids: List[int]) -> List[Dict[str, Any]]:
        """Get content and metadata for a list of notes"""
        if not note_ids:
            return []
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        notes_content = []
        for note_id in note_ids:
            cursor.execute('''
            SELECT id, title, content, created_at, updated_at
            FROM notes
            WHERE id = ?
            ''', (note_id,))
            
            row = cursor.fetchone()
            if row:
                # Get tags for the note
                cursor.execute('''
                SELECT t.name
                FROM tags t
                JOIN note_tags nt ON t.id = nt.tag_id
                WHERE nt.note_id = ?
                ''', (note_id,))
                
                tags = [tag[0] for tag in cursor.fetchall()]
                
                # Get source information if available
                cursor.execute('''
                SELECT source_type, title, authors, year, url, publisher, journal, volume, issue, pages, doi
                FROM note_sources
                WHERE note_id = ?
                ''', (note_id,))
                
                source_row = cursor.fetchone()
                source = {}
                
                if source_row:
                    source = {
                        'source_type': source_row[0],
                        'title': source_row[1],
                        'authors': source_row[2],
                        'year': source_row[3],
                        'url': source_row[4],
                        'publisher': source_row[5],
                        'journal': source_row[6],
                        'volume': source_row[7],
                        'issue': source_row[8],
                        'pages': source_row[9],
                        'doi': source_row[10]
                    }
                
                notes_content.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'tags': tags,
                    'source': source
                })
        
        return notes_content
    
    def _generate_essay_structure(self, topic: str, notes_content: List[Dict[str, Any]], 
                                word_count: int) -> Dict[str, Any]:
        """Generate a structure for the essay"""
        # Prepare context from notes
        notes_context = ""
        for i, note in enumerate(notes_content, 1):
            notes_context += f"Note {i}: {note['title']}\n"
            notes_context += f"Content: {note['content'][:500]}...\n\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert essay planner. Generate a detailed structure for an essay on the following topic:
        
        Topic: {topic}
        
        The essay should be approximately {word_count} words.
        
        Based on the following notes:
        {notes_context}
        
        Create a detailed essay structure with:
        1. Introduction (with thesis statement)
        2. Main sections (3-5 sections)
        3. Subsections for each main section
        4. Conclusion
        
        For each section, provide:
        - A clear heading
        - A brief description of what should be covered
        - Which notes/sources should be referenced
        
        Format your response as JSON:
        ```json
        {{
          "title": "Suggested essay title",
          "introduction": {{
            "description": "Brief description of introduction content",
            "thesis_statement": "Suggested thesis statement"
          }},
          "sections": [
            {{
              "heading": "Section 1 heading",
              "description": "What this section should cover",
              "subsections": [
                {{
                  "heading": "Subsection 1.1 heading",
                  "description": "What this subsection should cover",
                  "note_references": [1, 2]
                }},
                ...
              ]
            }},
            ...
          ],
          "conclusion": {{
            "description": "Brief description of conclusion content"
          }}
        }}
        ```
        """
        
        # Generate structure using LLM
        response = self.llm_interface.generate_text(prompt, max_tokens=2000)
        
        # Extract JSON from response
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without the markdown code block
            json_match = re.search(r'\{\s*"title".*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                logger.error("Failed to extract JSON from LLM response")
                return {}
        
        try:
            structure = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return {}
        
        return structure
    
    def _generate_essay_content(self, topic: str, essay_structure: Dict[str, Any], 
                              notes_content: List[Dict[str, Any]], 
                              citation_style: str, word_count: int) -> str:
        """Generate the full essay content based on the structure"""
        # Prepare context from notes
        notes_context = ""
        for i, note in enumerate(notes_content, 1):
            notes_context += f"Note {i}: {note['title']}\n"
            notes_context += f"Content: {note['content']}\n"
            
            # Add source information if available
            if note['source']:
                source_info = ""
                if note['source'].get('authors'):
                    source_info += f"Authors: {note['source']['authors']}\n"
                if note['source'].get('year'):
                    source_info += f"Year: {note['source']['year']}\n"
                if note['source'].get('title'):
                    source_info += f"Title: {note['source']['title']}\n"
                if note['source'].get('journal'):
                    source_info += f"Journal: {note['source']['journal']}\n"
                
                notes_context += f"Source: {source_info}\n"
            
            notes_context += "\n"
        
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert essay writer. Write a complete essay based on the following structure and notes:
        
        Topic: {topic}
        
        Essay Structure:
        {json.dumps(essay_structure, indent=2)}
        
        Notes to reference:
        {notes_context}
        
        The essay should be approximately {word_count} words.
        
        Use {citation_style} citation style for in-text citations. For example:
        - APA: (Author, Year)
        - MLA: (Author Page)
        - IEEE: [1]
        - Chicago: (Author Year, Page)
        - Harvard: (Author, Year)
        
        When referencing a note, use the note number as the citation identifier, e.g., Note 1 would be cited as:
        - APA: (Note 1 Author, Year)
        - MLA: (Note 1 Author Page)
        - IEEE: [1]
        - Chicago: (Note 1 Author Year, Page)
        - Harvard: (Note 1 Author, Year)
        
        Write a complete essay with:
        1. Title
        2. Introduction with thesis statement
        3. Main sections with subsections as outlined in the structure
        4. Conclusion
        5. References/Bibliography section
        
        Format the essay in Markdown with appropriate headings, paragraphs, and citations.
        """
        
        # Generate essay using LLM
        essay_content = self.llm_interface.generate_text(prompt, max_tokens=4000)
        
        return essay_content
    
    def _generate_summary_table(self, topic: str, essay_content: str, 
                              notes_content: List[Dict[str, Any]]) -> str:
        """Generate a summary table for the essay"""
        # Prepare prompt for LLM
        prompt = f"""
        You are an expert at creating summary tables for academic essays. Create a concise summary table for the following essay:
        
        Topic: {topic}
        
        Essay Content:
        {essay_content[:2000]}...
        
        Create a markdown table that summarizes the key points, arguments, and evidence presented in the essay.
        The table should have the following columns:
        1. Section
        2. Key Points
        3. Evidence/Sources
        
        Format the table in Markdown.
        """
        
        # Generate summary table using LLM
        summary_table = self.llm_interface.generate_text(prompt, max_tokens=1000)
        
        return summary_table
    
    def _store_essay_draft(self, user_id: int, topic: str, content: str, 
                         citation_style: str) -> int:
        """Store an essay draft in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        # Generate a title from the content
        title = self._generate_title(topic, content)
        
        cursor.execute('''
        INSERT INTO essay_drafts (user_id, title, topic, content, citation_style, created_at, last_updated_at, version)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (user_id, title, topic, content, citation_style, now, now))
        
        essay_id = cursor.lastrowid
        conn.commit()
        
        return essay_id
    
    def _store_essay_sources(self, essay_id: int, note_ids: List[int], 
                           notes_content: List[Dict[str, Any]], 
                           citation_style: str) -> None:
        """Store sources for an essay in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        for note in notes_content:
            note_id = note['id']
            
            if note_id not in note_ids:
                continue
            
            source = note.get('source', {})
            
            # Generate citation text based on style
            citation_text = self._generate_citation_text(note, citation_style)
            
            cursor.execute('''
            INSERT INTO essay_sources (
                essay_id, note_id, source_type, title, authors, year, url, 
                publisher, journal, volume, issue, pages, doi, citation_text
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                essay_id, note_id, 
                source.get('source_type', 'note'),
                source.get('title', note.get('title', '')),
                source.get('authors', ''),
                source.get('year', ''),
                source.get('url', ''),
                source.get('publisher', ''),
                source.get('journal', ''),
                source.get('volume', ''),
                source.get('issue', ''),
                source.get('pages', ''),
                source.get('doi', ''),
                citation_text
            ))
        
        conn.commit()
    
    def _store_essay_feedback(self, essay_id: int, feedback: str) -> int:
        """Store feedback for an essay in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
        INSERT INTO essay_feedback (essay_id, feedback_text, created_at)
        VALUES (?, ?, ?)
        ''', (essay_id, feedback, now))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        
        return feedback_id
    
    def _get_essay_sources(self, essay_id: int) -> List[Dict[str, Any]]:
        """Get sources for an essay"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, note_id, source_type, title, authors, year, url, 
               publisher, journal, volume, issue, pages, doi, citation_text
        FROM essay_sources
        WHERE essay_id = ?
        ''', (essay_id,))
        
        sources = []
        for row in cursor.fetchall():
            source = {
                'id': row[0],
                'note_id': row[1],
                'source_type': row[2],
                'title': row[3],
                'authors': row[4],
                'year': row[5],
                'url': row[6],
                'publisher': row[7],
                'journal': row[8],
                'volume': row[9],
                'issue': row[10],
                'pages': row[11],
                'doi': row[12],
                'citation_text': row[13]
            }
            sources.append(source)
        
        return sources
    
    def _get_essay_feedback(self, essay_id: int) -> List[Dict[str, Any]]:
        """Get feedback for an essay"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT id, feedback_text, created_at
        FROM essay_feedback
        WHERE essay_id = ?
        ORDER BY created_at DESC
        ''', (essay_id,))
        
        feedback = []
        for row in cursor.fetchall():
            feedback_item = {
                'id': row[0],
                'feedback_text': row[1],
                'created_at': row[2]
            }
            feedback.append(feedback_item)
        
        return feedback
    
    def _generate_title(self, topic: str, content: str) -> str:
        """Generate a title for the essay based on content"""
        # Check if the content already has a title
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1)
        
        # Prepare prompt for LLM
        prompt = f"""
        Generate a concise, engaging title for an essay on the following topic:
        
        Topic: {topic}
        
        Essay content (excerpt):
        {content[:500]}...
        
        The title should be clear, specific, and reflective of the essay's content.
        Provide only the title, without any additional text or formatting.
        """
        
        # Generate title using LLM
        title = self.llm_interface.generate_text(prompt, max_tokens=50)
        
        # Clean up the title
        title = title.strip().strip('"\'#')
        
        return title
    
    def _generate_citation_text(self, note: Dict[str, Any], citation_style: str) -> str:
        """Generate citation text for a note based on style"""
        source = note.get('source', {})
        
        # Default values if source information is missing
        authors = source.get('authors', 'Unknown Author')
        year = source.get('year', 'n.d.')
        title = source.get('title', note.get('title', 'Untitled'))
        journal = source.get('journal', '')
        volume = source.get('volume', '')
        issue = source.get('issue', '')
        pages = source.get('pages', '')
        publisher = source.get('publisher', '')
        url = source.get('url', '')
        doi = source.get('doi', '')
        
        # Generate citation based on style
        if citation_style == CitationStyle.APA:
            if journal:
                return f"{authors} ({year}). {title}. {journal}, {volume}{f'({issue})' if issue else ''}, {pages}. {f'https://doi.org/{doi}' if doi else url}"
            else:
                return f"{authors} ({year}). {title}. {publisher}. {f'https://doi.org/{doi}' if doi else url}"
        
        elif citation_style == CitationStyle.MLA:
            if journal:
                return f"{authors}. \"{title}.\" {journal}, vol. {volume}, no. {issue}, {year}, pp. {pages}. {f'DOI: {doi}' if doi else url}"
            else:
                return f"{authors}. {title}. {publisher}, {year}. {url}"
        
        elif citation_style == CitationStyle.IEEE:
            if journal:
                return f"{authors}, \"{title},\" {journal}, vol. {volume}, no. {issue}, pp. {pages}, {year}. {f'DOI: {doi}' if doi else ''}"
            else:
                return f"{authors}, {title}. {publisher}, {year}. {url}"
        
        elif citation_style == CitationStyle.CHICAGO:
            if journal:
                return f"{authors}. \"{title}.\" {journal} {volume}, no. {issue} ({year}): {pages}. {f'https://doi.org/{doi}' if doi else url}"
            else:
                return f"{authors}. {title}. {publisher}, {year}. {url}"
        
        elif citation_style == CitationStyle.HARVARD:
            if journal:
                return f"{authors} {year}, '{title}', {journal}, vol. {volume}, no. {issue}, pp. {pages}, {f'DOI: {doi}' if doi else url}"
            else:
                return f"{authors} {year}, {title}, {publisher}, {url}"
        
        else:
            return f"{authors} ({year}). {title}."
    
    def _format_in_text_citations(self, content: str, sources: List[Dict[str, Any]], 
                                citation_style: str) -> str:
        """Format in-text citations in the essay content"""
        # This is a simplified implementation
        # In a real implementation, you would need to parse the content and replace citations
        
        # For now, we'll just return the original content
        return content
    
    def _generate_bibliography(self, sources: List[Dict[str, Any]], 
                             citation_style: str) -> str:
        """Generate a bibliography based on sources and citation style"""
        if not sources:
            return "No sources available."
        
        bibliography = ""
        
        for source in sources:
            bibliography += f"{source['citation_text']}\n\n"
        
        return bibliography
    
    def _get_bibliography_title(self, citation_style: str) -> str:
        """Get the appropriate title for the bibliography section based on citation style"""
        if citation_style == CitationStyle.MLA:
            return "Works Cited"
        elif citation_style == CitationStyle.CHICAGO:
            return "Bibliography"
        else:
            return "References"
    
    def _format_sources_for_prompt(self, sources: List[Dict[str, Any]]) -> str:
        """Format sources for inclusion in a prompt"""
        if not sources:
            return "No sources available."
        
        formatted_sources = ""
        
        for i, source in enumerate(sources, 1):
            formatted_sources += f"Source {i}:\n"
            
            if source.get('title'):
                formatted_sources += f"Title: {source['title']}\n"
            
            if source.get('authors'):
                formatted_sources += f"Authors: {source['authors']}\n"
            
            if source.get('year'):
                formatted_sources += f"Year: {source['year']}\n"
            
            if source.get('journal'):
                formatted_sources += f"Journal: {source['journal']}\n"
            
            if source.get('publisher'):
                formatted_sources += f"Publisher: {source['publisher']}\n"
            
            formatted_sources += "\n"
        
        return formatted_sources

# Helper functions for easier access to essay generator functionality

def generate_essay_draft(db_manager, user_id: int, topic: str, 
                       notes_ids: List[int] = None,
                       citation_style: str = CitationStyle.APA,
                       word_count: int = 1500,
                       include_summary_table: bool = True) -> Dict[str, Any]:
    """
    Generate an essay draft based on a topic and notes
    
    Args:
        db_manager: Database manager instance
        user_id: The ID of the user
        topic: The topic of the essay
        notes_ids: Optional list of note IDs to use as sources
        citation_style: The citation style to use
        word_count: Target word count for the essay
        include_summary_table: Whether to include a summary table
        
    Returns:
        Dictionary with the generated essay draft
    """
    generator = EssayGenerator(db_manager)
    return generator.generate_essay_draft(
        user_id, topic, notes_ids, citation_style, word_count, include_summary_table
    )

def refine_essay_draft(db_manager, essay_id: int, feedback: str) -> Dict[str, Any]:
    """
    Refine an essay draft based on feedback
    
    Args:
        db_manager: Database manager instance
        essay_id: The ID of the essay draft
        feedback: Feedback for improving the essay
        
    Returns:
        Dictionary with the refined essay draft
    """
    generator = EssayGenerator(db_manager)
    return generator.refine_essay_draft(essay_id, feedback)

def format_citations(db_manager, essay_id: int, citation_style: str) -> Dict[str, Any]:
    """
    Format citations in an essay according to a specific style
    
    Args:
        db_manager: Database manager instance
        essay_id: The ID of the essay draft
        citation_style: The citation style to use
        
    Returns:
        Dictionary with the updated essay and bibliography
    """
    generator = EssayGenerator(db_manager)
    return generator.format_citations(essay_id, citation_style)