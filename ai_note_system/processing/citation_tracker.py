"""
Citation & Source Tracking Module

This module provides functionality to track where each note or fact came from
and auto-generate citations in APA/MLA/IEEE formats for essays and projects.

Features:
- Add source information to notes
- Track multiple sources per note
- Generate citations in various formats (APA, MLA, IEEE)
- Search notes by source
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Import database module
from ..database.db_manager import DatabaseManager

# Set up logging
logger = logging.getLogger(__name__)

class CitationTracker:
    """
    Class for tracking citations and sources for notes.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the CitationTracker with a database manager.
        
        Args:
            db_manager: DatabaseManager instance for database operations
        """
        self.db_manager = db_manager
        self._ensure_sources_table()
    
    def _ensure_sources_table(self) -> None:
        """
        Ensure the sources table exists in the database.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            source_type TEXT NOT NULL,
            title TEXT,
            authors TEXT,
            year INTEGER,
            url TEXT,
            publisher TEXT,
            journal TEXT,
            volume TEXT,
            issue TEXT,
            pages TEXT,
            doi TEXT,
            additional_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(create_table_query)
    
    def add_source(self, note_id: int, source_type: str, **kwargs) -> int:
        """
        Add source information to a note.
        
        Args:
            note_id: ID of the note
            source_type: Type of source (e.g., "book", "article", "website", "video")
            **kwargs: Additional source metadata (title, authors, year, url, etc.)
        
        Returns:
            int: ID of the newly added source
        """
        # Validate note exists
        note = self.db_manager.execute_query(
            "SELECT id FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        
        if not note:
            logger.error(f"Note with ID {note_id} not found")
            raise ValueError(f"Note with ID {note_id} not found")
        
        # Prepare source data
        source_data = {
            'note_id': note_id,
            'source_type': source_type,
            'title': kwargs.get('title'),
            'authors': kwargs.get('authors'),
            'year': kwargs.get('year'),
            'url': kwargs.get('url'),
            'publisher': kwargs.get('publisher'),
            'journal': kwargs.get('journal'),
            'volume': kwargs.get('volume'),
            'issue': kwargs.get('issue'),
            'pages': kwargs.get('pages'),
            'doi': kwargs.get('doi'),
            'additional_info': json.dumps(kwargs.get('additional_info', {}))
        }
        
        # Filter out None values
        source_data = {k: v for k, v in source_data.items() if v is not None}
        
        # Build the query
        columns = ', '.join(source_data.keys())
        placeholders = ', '.join(['?' for _ in source_data])
        values = tuple(source_data.values())
        
        query = f"INSERT INTO sources ({columns}) VALUES ({placeholders})"
        
        # Execute the query
        cursor = self.db_manager.execute_query(query, values)
        source_id = cursor.lastrowid
        
        logger.info(f"Added source {source_id} to note {note_id}")
        return source_id
    
    def get_sources(self, note_id: int) -> List[Dict[str, Any]]:
        """
        Get all sources for a note.
        
        Args:
            note_id: ID of the note
        
        Returns:
            List of source dictionaries
        """
        query = "SELECT * FROM sources WHERE note_id = ?"
        sources = self.db_manager.execute_query(query, (note_id,)).fetchall()
        
        # Convert row objects to dictionaries
        result = []
        for source in sources:
            source_dict = dict(source)
            # Parse additional_info JSON
            if source_dict.get('additional_info'):
                try:
                    source_dict['additional_info'] = json.loads(source_dict['additional_info'])
                except json.JSONDecodeError:
                    source_dict['additional_info'] = {}
            result.append(source_dict)
        
        return result
    
    def search_by_source(self, source_term: str) -> List[Dict[str, Any]]:
        """
        Search notes by source information.
        
        Args:
            source_term: Search term to look for in source information
        
        Returns:
            List of notes with matching sources
        """
        query = """
        SELECT n.*, s.source_type, s.title as source_title, s.authors, s.year
        FROM notes n
        JOIN sources s ON n.id = s.note_id
        WHERE s.source_type LIKE ? OR s.title LIKE ? OR s.authors LIKE ? 
        OR s.publisher LIKE ? OR s.journal LIKE ? OR s.additional_info LIKE ?
        """
        
        search_param = f"%{source_term}%"
        params = (search_param, search_param, search_param, search_param, search_param, search_param)
        
        results = self.db_manager.execute_query(query, params).fetchall()
        
        # Convert row objects to dictionaries and remove duplicates
        notes = {}
        for row in results:
            note_dict = dict(row)
            note_id = note_dict['id']
            if note_id not in notes:
                notes[note_id] = note_dict
        
        return list(notes.values())
    
    def generate_citation(self, source_id: int, format_type: str) -> str:
        """
        Generate a citation for a source in the specified format.
        
        Args:
            source_id: ID of the source
            format_type: Citation format (apa, mla, ieee)
        
        Returns:
            Formatted citation string
        """
        # Get source data
        query = "SELECT * FROM sources WHERE id = ?"
        source = self.db_manager.execute_query(query, (source_id,)).fetchone()
        
        if not source:
            logger.error(f"Source with ID {source_id} not found")
            raise ValueError(f"Source with ID {source_id} not found")
        
        source_dict = dict(source)
        
        # Parse additional_info JSON
        if source_dict.get('additional_info'):
            try:
                source_dict['additional_info'] = json.loads(source_dict['additional_info'])
            except json.JSONDecodeError:
                source_dict['additional_info'] = {}
        
        # Generate citation based on format
        if format_type.lower() == 'apa':
            return self._generate_apa_citation(source_dict)
        elif format_type.lower() == 'mla':
            return self._generate_mla_citation(source_dict)
        elif format_type.lower() == 'ieee':
            return self._generate_ieee_citation(source_dict)
        else:
            logger.error(f"Unsupported citation format: {format_type}")
            raise ValueError(f"Unsupported citation format: {format_type}")
    
    def _generate_apa_citation(self, source: Dict[str, Any]) -> str:
        """
        Generate an APA format citation.
        
        Args:
            source: Source dictionary
        
        Returns:
            APA formatted citation string
        """
        source_type = source.get('source_type', '').lower()
        
        if source_type == 'book':
            # Author(s). (Year). Title. Publisher.
            authors = self._format_authors_apa(source.get('authors', ''))
            year = f"({source.get('year', 'n.d.')})."
            title = f"{source.get('title', '')}."
            publisher = source.get('publisher', '')
            
            return f"{authors} {year} {title} {publisher}."
            
        elif source_type == 'article':
            # Author(s). (Year). Title. Journal, Volume(Issue), Pages.
            authors = self._format_authors_apa(source.get('authors', ''))
            year = f"({source.get('year', 'n.d.')})."
            title = f"{source.get('title', '')}."
            journal = source.get('journal', '')
            volume = source.get('volume', '')
            issue = source.get('issue', '')
            pages = source.get('pages', '')
            
            volume_issue = f"{volume}"
            if issue:
                volume_issue += f"({issue})"
            
            return f"{authors} {year} {title} {journal}, {volume_issue}, {pages}."
            
        elif source_type == 'website':
            # Author(s). (Year). Title. URL
            authors = self._format_authors_apa(source.get('authors', ''))
            year = f"({source.get('year', 'n.d.')})."
            title = f"{source.get('title', '')}."
            url = source.get('url', '')
            
            return f"{authors} {year} {title} Retrieved from {url}"
            
        elif source_type == 'video':
            # Author(s). (Year). Title [Video]. URL
            authors = self._format_authors_apa(source.get('authors', ''))
            year = f"({source.get('year', 'n.d.')})."
            title = f"{source.get('title', '')} [Video]."
            url = source.get('url', '')
            
            return f"{authors} {year} {title} Retrieved from {url}"
            
        else:
            # Generic citation
            authors = self._format_authors_apa(source.get('authors', ''))
            year = f"({source.get('year', 'n.d.')})."
            title = f"{source.get('title', '')}."
            
            return f"{authors} {year} {title}"
    
    def _generate_mla_citation(self, source: Dict[str, Any]) -> str:
        """
        Generate an MLA format citation.
        
        Args:
            source: Source dictionary
        
        Returns:
            MLA formatted citation string
        """
        source_type = source.get('source_type', '').lower()
        
        if source_type == 'book':
            # Author(s). Title. Publisher, Year.
            authors = self._format_authors_mla(source.get('authors', ''))
            title = f"{source.get('title', '')}."
            publisher = source.get('publisher', '')
            year = source.get('year', 'n.d.')
            
            return f"{authors}. {title} {publisher}, {year}."
            
        elif source_type == 'article':
            # Author(s). "Title." Journal, Volume.Issue, Year, Pages.
            authors = self._format_authors_mla(source.get('authors', ''))
            title = f"\"{source.get('title', '')}.\""
            journal = source.get('journal', '')
            volume = source.get('volume', '')
            issue = source.get('issue', '')
            year = source.get('year', 'n.d.')
            pages = source.get('pages', '')
            
            volume_issue = f"{volume}"
            if issue:
                volume_issue += f".{issue}"
            
            return f"{authors}. {title} {journal}, {volume_issue}, {year}, {pages}."
            
        elif source_type == 'website':
            # Author(s). "Title." Website, Day Month Year, URL.
            authors = self._format_authors_mla(source.get('authors', ''))
            title = f"\"{source.get('title', '')}.\""
            website = source.get('publisher', 'Website')
            year = source.get('year', 'n.d.')
            url = source.get('url', '')
            
            return f"{authors}. {title} {website}, {year}, {url}."
            
        elif source_type == 'video':
            # "Title." YouTube, uploaded by Author, Day Month Year, URL.
            title = f"\"{source.get('title', '')}.\""
            authors = source.get('authors', '')
            year = source.get('year', 'n.d.')
            url = source.get('url', '')
            
            return f"{title} YouTube, uploaded by {authors}, {year}, {url}."
            
        else:
            # Generic citation
            authors = self._format_authors_mla(source.get('authors', ''))
            title = f"\"{source.get('title', '')}.\""
            year = source.get('year', 'n.d.')
            
            return f"{authors}. {title} {year}."
    
    def _generate_ieee_citation(self, source: Dict[str, Any]) -> str:
        """
        Generate an IEEE format citation.
        
        Args:
            source: Source dictionary
        
        Returns:
            IEEE formatted citation string
        """
        source_type = source.get('source_type', '').lower()
        
        if source_type == 'book':
            # [1] A. Author and B. Author, Title. City, State: Publisher, Year.
            authors = self._format_authors_ieee(source.get('authors', ''))
            title = f"{source.get('title', '')}."
            publisher = source.get('publisher', '')
            year = source.get('year', 'n.d.')
            
            return f"{authors}, {title} {publisher}, {year}."
            
        elif source_type == 'article':
            # [1] A. Author and B. Author, "Title," Journal, vol. Volume, no. Issue, pp. Pages, Year.
            authors = self._format_authors_ieee(source.get('authors', ''))
            title = f"\"{source.get('title', '')},\""
            journal = source.get('journal', '')
            volume = source.get('volume', '')
            issue = source.get('issue', '')
            pages = source.get('pages', '')
            year = source.get('year', 'n.d.')
            
            volume_str = f"vol. {volume}, " if volume else ""
            issue_str = f"no. {issue}, " if issue else ""
            pages_str = f"pp. {pages}, " if pages else ""
            
            return f"{authors}, {title} {journal}, {volume_str}{issue_str}{pages_str}{year}."
            
        elif source_type == 'website':
            # [1] A. Author. "Title." Website. URL (accessed Month Day, Year).
            authors = self._format_authors_ieee(source.get('authors', ''))
            title = f"\"{source.get('title', '')}.\""
            website = source.get('publisher', 'Website')
            url = source.get('url', '')
            year = source.get('year', 'n.d.')
            
            return f"{authors}, {title} {website}. {url} (accessed {year})."
            
        elif source_type == 'video':
            # [1] "Title," YouTube, Year. [Video]. Available: URL
            title = f"\"{source.get('title', '')},\""
            year = source.get('year', 'n.d.')
            url = source.get('url', '')
            
            return f"{title} YouTube, {year}. [Video]. Available: {url}"
            
        else:
            # Generic citation
            authors = self._format_authors_ieee(source.get('authors', ''))
            title = f"\"{source.get('title', '')},\""
            year = source.get('year', 'n.d.')
            
            return f"{authors}, {title} {year}."
    
    def _format_authors_apa(self, authors_str: str) -> str:
        """
        Format authors for APA citation.
        
        Args:
            authors_str: Comma-separated list of authors
        
        Returns:
            Formatted authors string
        """
        if not authors_str:
            return ""
        
        authors = [a.strip() for a in authors_str.split(',')]
        
        if len(authors) == 1:
            # Single author: Last, F. I.
            parts = authors[0].split()
            if len(parts) > 1:
                last = parts[-1]
                initials = ''.join([f"{p[0]}. " for p in parts[:-1]])
                return f"{last}, {initials}"
            return authors[0]
            
        elif len(authors) == 2:
            # Two authors: Last, F. I., & Last, F. I.
            formatted_authors = []
            for author in authors:
                parts = author.split()
                if len(parts) > 1:
                    last = parts[-1]
                    initials = ''.join([f"{p[0]}. " for p in parts[:-1]])
                    formatted_authors.append(f"{last}, {initials}")
                else:
                    formatted_authors.append(author)
            
            return f"{formatted_authors[0]}, & {formatted_authors[1]}"
            
        else:
            # Multiple authors: Last, F. I., Last, F. I., ... & Last, F. I.
            formatted_authors = []
            for author in authors:
                parts = author.split()
                if len(parts) > 1:
                    last = parts[-1]
                    initials = ''.join([f"{p[0]}. " for p in parts[:-1]])
                    formatted_authors.append(f"{last}, {initials}")
                else:
                    formatted_authors.append(author)
            
            return f"{', '.join(formatted_authors[:-1])}, & {formatted_authors[-1]}"
    
    def _format_authors_mla(self, authors_str: str) -> str:
        """
        Format authors for MLA citation.
        
        Args:
            authors_str: Comma-separated list of authors
        
        Returns:
            Formatted authors string
        """
        if not authors_str:
            return ""
        
        authors = [a.strip() for a in authors_str.split(',')]
        
        if len(authors) == 1:
            # Single author: Last, First
            parts = authors[0].split()
            if len(parts) > 1:
                last = parts[-1]
                first = ' '.join(parts[:-1])
                return f"{last}, {first}"
            return authors[0]
            
        elif len(authors) == 2:
            # Two authors: Last, First, and First Last
            first_author_parts = authors[0].split()
            if len(first_author_parts) > 1:
                first_last = first_author_parts[-1]
                first_first = ' '.join(first_author_parts[:-1])
                first_formatted = f"{first_last}, {first_first}"
            else:
                first_formatted = authors[0]
            
            second_author_parts = authors[1].split()
            if len(second_author_parts) > 1:
                second_formatted = ' '.join(second_author_parts)
            else:
                second_formatted = authors[1]
            
            return f"{first_formatted}, and {second_formatted}"
            
        else:
            # Multiple authors: Last, First, et al.
            first_author_parts = authors[0].split()
            if len(first_author_parts) > 1:
                first_last = first_author_parts[-1]
                first_first = ' '.join(first_author_parts[:-1])
                first_formatted = f"{first_last}, {first_first}"
            else:
                first_formatted = authors[0]
            
            return f"{first_formatted}, et al."
    
    def _format_authors_ieee(self, authors_str: str) -> str:
        """
        Format authors for IEEE citation.
        
        Args:
            authors_str: Comma-separated list of authors
        
        Returns:
            Formatted authors string
        """
        if not authors_str:
            return ""
        
        authors = [a.strip() for a in authors_str.split(',')]
        
        formatted_authors = []
        for author in authors:
            parts = author.split()
            if len(parts) > 1:
                initials = ''.join([f"{p[0]}. " for p in parts[:-1]])
                last = parts[-1]
                formatted_authors.append(f"{initials}{last}")
            else:
                formatted_authors.append(author)
        
        if len(formatted_authors) == 1:
            return formatted_authors[0]
        elif len(formatted_authors) == 2:
            return f"{formatted_authors[0]} and {formatted_authors[1]}"
        else:
            return f"{formatted_authors[0]} et al."


def add_source(db_manager: DatabaseManager, note_id: int, source_type: str, **kwargs) -> int:
    """
    Add source information to a note.
    
    Args:
        db_manager: DatabaseManager instance
        note_id: ID of the note
        source_type: Type of source (e.g., "book", "article", "website", "video")
        **kwargs: Additional source metadata (title, authors, year, url, etc.)
    
    Returns:
        int: ID of the newly added source
    """
    tracker = CitationTracker(db_manager)
    return tracker.add_source(note_id, source_type, **kwargs)


def get_sources(db_manager: DatabaseManager, note_id: int) -> List[Dict[str, Any]]:
    """
    Get all sources for a note.
    
    Args:
        db_manager: DatabaseManager instance
        note_id: ID of the note
    
    Returns:
        List of source dictionaries
    """
    tracker = CitationTracker(db_manager)
    return tracker.get_sources(note_id)


def search_by_source(db_manager: DatabaseManager, source_term: str) -> List[Dict[str, Any]]:
    """
    Search notes by source information.
    
    Args:
        db_manager: DatabaseManager instance
        source_term: Search term to look for in source information
    
    Returns:
        List of notes with matching sources
    """
    tracker = CitationTracker(db_manager)
    return tracker.search_by_source(source_term)


def generate_citation(db_manager: DatabaseManager, source_id: int, format_type: str) -> str:
    """
    Generate a citation for a source in the specified format.
    
    Args:
        db_manager: DatabaseManager instance
        source_id: ID of the source
        format_type: Citation format (apa, mla, ieee)
    
    Returns:
        Formatted citation string
    """
    tracker = CitationTracker(db_manager)
    return tracker.generate_citation(source_id, format_type)


def generate_citations_for_note(db_manager: DatabaseManager, note_id: int, format_type: str) -> List[str]:
    """
    Generate citations for all sources of a note in the specified format.
    
    Args:
        db_manager: DatabaseManager instance
        note_id: ID of the note
        format_type: Citation format (apa, mla, ieee)
    
    Returns:
        List of formatted citation strings
    """
    tracker = CitationTracker(db_manager)
    sources = tracker.get_sources(note_id)
    
    citations = []
    for source in sources:
        citation = tracker.generate_citation(source['id'], format_type)
        citations.append(citation)
    
    return citations