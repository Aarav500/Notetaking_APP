"""
PDF Viewer module for AI Note System.
Provides an interactive PDF reading experience with annotations, navigation, and learning enhancements.
"""

import os
import logging
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.reading.pdf_viewer")

class PDFViewer:
    """
    PDF Viewer class for interactive reading with annotations and learning enhancements.
    """
    
    def __init__(self, db_manager=None, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the PDF Viewer.
        
        Args:
            db_manager: Database manager instance
            config (Dict[str, Any], optional): Configuration dictionary
        """
        self.db_manager = db_manager
        self.config = config or {}
        self._ensure_pdf_tables()
        
        # Default settings
        self.default_settings = {
            "font_family": "Arial",
            "font_size": 12,
            "line_height": 1.5,
            "theme": "light",
            "margin_left": 20,
            "margin_right": 20,
            "margin_top": 20,
            "margin_bottom": 20,
            "highlight_colors": {
                "important": "#FFEB3B",  # Yellow
                "definition": "#4CAF50",  # Green
                "question": "#2196F3",    # Blue
                "note": "#FF9800"         # Orange
            }
        }
        
        logger.debug("Initialized PDFViewer")
    
    def _ensure_pdf_tables(self) -> None:
        """
        Ensure the PDF-related tables exist in the database.
        """
        if not self.db_manager:
            logger.warning("No database manager provided, skipping table creation")
            return
            
        # Create pdf_books table
        books_query = """
        CREATE TABLE IF NOT EXISTS pdf_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            file_path TEXT NOT NULL,
            page_count INTEGER,
            current_page INTEGER DEFAULT 1,
            reading_progress REAL DEFAULT 0.0,
            last_read TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(books_query)
        
        # Create pdf_annotations table
        annotations_query = """
        CREATE TABLE IF NOT EXISTS pdf_annotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            annotation_type TEXT NOT NULL,
            content TEXT,
            color TEXT,
            position_x REAL,
            position_y REAL,
            width REAL,
            height REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(annotations_query)
        
        # Create pdf_bookmarks table
        bookmarks_query = """
        CREATE TABLE IF NOT EXISTS pdf_bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(bookmarks_query)
        
        # Create pdf_structure table
        structure_query = """
        CREATE TABLE IF NOT EXISTS pdf_structure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            level INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_id) REFERENCES pdf_structure(id) ON DELETE SET NULL
        )
        """
        self.db_manager.execute_query(structure_query)
        
        # Create pdf_settings table
        settings_query = """
        CREATE TABLE IF NOT EXISTS pdf_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER,
            settings_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES pdf_books(id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(settings_query)
        
        logger.debug("Ensured PDF tables exist in database")
    
    def add_book(self, 
                user_id: int, 
                file_path: str, 
                title: Optional[str] = None, 
                author: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a PDF book to the system.
        
        Args:
            user_id (int): ID of the user
            file_path (str): Path to the PDF file
            title (str, optional): Title of the book
            author (str, optional): Author of the book
            
        Returns:
            Dict[str, Any]: Added book information
        """
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            return {"error": f"PDF file not found: {file_path}"}
        
        # Extract basic information from PDF
        from ai_note_system.inputs.pdf_input import extract_text_from_pdf
        
        # If title not provided, use filename
        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0].replace('_', ' ')
        
        # Get page count
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()
        except Exception as e:
            logger.error(f"Error getting page count: {str(e)}")
            page_count = 0
        
        # Add to database
        if self.db_manager:
            query = """
            INSERT INTO pdf_books (user_id, title, author, file_path, page_count, last_read)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            current_time = datetime.now().isoformat()
            
            try:
                cursor = self.db_manager.execute_query(
                    query, 
                    (user_id, title, author, file_path, page_count, current_time)
                )
                book_id = cursor.lastrowid
                
                # Add default settings for this book
                self.save_settings(user_id, self.default_settings, book_id)
                
                logger.info(f"Added book: {title} (ID: {book_id})")
                
                return {
                    "id": book_id,
                    "title": title,
                    "author": author,
                    "file_path": file_path,
                    "page_count": page_count,
                    "current_page": 1,
                    "reading_progress": 0.0,
                    "last_read": current_time
                }
            except Exception as e:
                logger.error(f"Error adding book to database: {str(e)}")
                return {"error": f"Error adding book to database: {str(e)}"}
        else:
            # No database, return basic info
            logger.warning("No database manager, returning basic book info")
            return {
                "title": title,
                "author": author,
                "file_path": file_path,
                "page_count": page_count,
                "current_page": 1,
                "reading_progress": 0.0,
                "last_read": datetime.now().isoformat()
            }
    
    def get_book(self, book_id: int) -> Dict[str, Any]:
        """
        Get book information.
        
        Args:
            book_id (int): ID of the book
            
        Returns:
            Dict[str, Any]: Book information
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        query = """
        SELECT * FROM pdf_books
        WHERE id = ?
        """
        
        result = self.db_manager.execute_query(query, (book_id,)).fetchone()
        
        if not result:
            logger.error(f"Book not found: {book_id}")
            return {"error": f"Book not found: {book_id}"}
        
        return dict(result)
    
    def get_user_books(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all books for a user.
        
        Args:
            user_id (int): ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of books
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        query = """
        SELECT * FROM pdf_books
        WHERE user_id = ?
        ORDER BY last_read DESC
        """
        
        results = self.db_manager.execute_query(query, (user_id,)).fetchall()
        
        return [dict(result) for result in results]
    
    def update_reading_progress(self, 
                              book_id: int, 
                              current_page: int) -> Dict[str, Any]:
        """
        Update reading progress for a book.
        
        Args:
            book_id (int): ID of the book
            current_page (int): Current page number
            
        Returns:
            Dict[str, Any]: Updated book information
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Get book information
        book = self.get_book(book_id)
        if "error" in book:
            return book
        
        # Calculate reading progress
        page_count = book["page_count"]
        if page_count > 0:
            reading_progress = min(1.0, current_page / page_count)
        else:
            reading_progress = 0.0
        
        # Update database
        query = """
        UPDATE pdf_books
        SET current_page = ?, reading_progress = ?, last_read = ?
        WHERE id = ?
        """
        
        current_time = datetime.now().isoformat()
        
        try:
            self.db_manager.execute_query(
                query, 
                (current_page, reading_progress, current_time, book_id)
            )
            
            logger.info(f"Updated reading progress for book {book_id}: page {current_page}, progress {reading_progress:.2f}")
            
            # Return updated book information
            return {
                **book,
                "current_page": current_page,
                "reading_progress": reading_progress,
                "last_read": current_time
            }
        except Exception as e:
            logger.error(f"Error updating reading progress: {str(e)}")
            return {"error": f"Error updating reading progress: {str(e)}"}
    
    def add_annotation(self, 
                     book_id: int, 
                     user_id: int, 
                     page_number: int, 
                     annotation_type: str, 
                     content: Optional[str] = None, 
                     color: Optional[str] = None, 
                     position: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Add an annotation to a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            annotation_type (str): Type of annotation (highlight, note, underline, etc.)
            content (str, optional): Content of the annotation
            color (str, optional): Color of the annotation
            position (Dict[str, float], optional): Position of the annotation
            
        Returns:
            Dict[str, Any]: Added annotation
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Set default position if not provided
        if not position:
            position = {"x": 0, "y": 0, "width": 0, "height": 0}
        
        # Set default color based on annotation type
        if not color:
            settings = self.get_settings(user_id, book_id)
            highlight_colors = settings.get("highlight_colors", self.default_settings["highlight_colors"])
            color = highlight_colors.get(annotation_type, "#FFEB3B")  # Default to yellow
        
        # Add to database
        query = """
        INSERT INTO pdf_annotations (
            book_id, user_id, page_number, annotation_type, 
            content, color, position_x, position_y, width, height
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query, 
                (
                    book_id, user_id, page_number, annotation_type, 
                    content, color, position["x"], position["y"], 
                    position.get("width", 0), position.get("height", 0)
                )
            )
            
            annotation_id = cursor.lastrowid
            
            logger.info(f"Added {annotation_type} annotation to book {book_id}, page {page_number}")
            
            return {
                "id": annotation_id,
                "book_id": book_id,
                "user_id": user_id,
                "page_number": page_number,
                "annotation_type": annotation_type,
                "content": content,
                "color": color,
                "position": position,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error adding annotation: {str(e)}")
            return {"error": f"Error adding annotation: {str(e)}"}
    
    def get_annotations(self, 
                      book_id: int, 
                      user_id: int, 
                      page_number: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get annotations for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int, optional): Page number to filter by
            
        Returns:
            List[Dict[str, Any]]: List of annotations
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Build query
        query = """
        SELECT * FROM pdf_annotations
        WHERE book_id = ? AND user_id = ?
        """
        
        params = [book_id, user_id]
        
        if page_number is not None:
            query += " AND page_number = ?"
            params.append(page_number)
        
        query += " ORDER BY page_number, created_at"
        
        # Execute query
        results = self.db_manager.execute_query(query, tuple(params)).fetchall()
        
        # Format results
        annotations = []
        for result in results:
            result_dict = dict(result)
            # Reconstruct position
            result_dict["position"] = {
                "x": result_dict.pop("position_x"),
                "y": result_dict.pop("position_y"),
                "width": result_dict.pop("width"),
                "height": result_dict.pop("height")
            }
            annotations.append(result_dict)
        
        return annotations
    
    def add_bookmark(self, 
                   book_id: int, 
                   user_id: int, 
                   page_number: int, 
                   title: str) -> Dict[str, Any]:
        """
        Add a bookmark to a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            page_number (int): Page number
            title (str): Bookmark title
            
        Returns:
            Dict[str, Any]: Added bookmark
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Add to database
        query = """
        INSERT INTO pdf_bookmarks (book_id, user_id, page_number, title)
        VALUES (?, ?, ?, ?)
        """
        
        try:
            cursor = self.db_manager.execute_query(
                query, 
                (book_id, user_id, page_number, title)
            )
            
            bookmark_id = cursor.lastrowid
            
            logger.info(f"Added bookmark to book {book_id}, page {page_number}: {title}")
            
            return {
                "id": bookmark_id,
                "book_id": book_id,
                "user_id": user_id,
                "page_number": page_number,
                "title": title,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error adding bookmark: {str(e)}")
            return {"error": f"Error adding bookmark: {str(e)}"}
    
    def get_bookmarks(self, book_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Get bookmarks for a book.
        
        Args:
            book_id (int): ID of the book
            user_id (int): ID of the user
            
        Returns:
            List[Dict[str, Any]]: List of bookmarks
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        query = """
        SELECT * FROM pdf_bookmarks
        WHERE book_id = ? AND user_id = ?
        ORDER BY page_number
        """
        
        results = self.db_manager.execute_query(query, (book_id, user_id)).fetchall()
        
        return [dict(result) for result in results]
    
    def extract_structure(self, book_id: int) -> List[Dict[str, Any]]:
        """
        Extract and save the structure (headings) from a PDF book.
        
        Args:
            book_id (int): ID of the book
            
        Returns:
            List[Dict[str, Any]]: Extracted structure
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        # Get book information
        book = self.get_book(book_id)
        if "error" in book:
            return []
        
        file_path = book["file_path"]
        
        # Extract structure using PyMuPDF
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            toc = doc.get_toc()
            doc.close()
            
            # Clear existing structure
            self.db_manager.execute_query(
                "DELETE FROM pdf_structure WHERE book_id = ?", 
                (book_id,)
            )
            
            # Insert new structure
            structure = []
            parent_stack = [None]
            
            for item in toc:
                level, title, page = item
                
                # Adjust level to be 0-based for array indexing
                zero_based_level = level - 1
                
                # Ensure parent stack has enough levels
                while len(parent_stack) <= zero_based_level:
                    parent_stack.append(None)
                
                # Truncate parent stack if current level is less than stack size
                parent_stack = parent_stack[:zero_based_level + 1]
                
                # Get parent ID
                parent_id = parent_stack[zero_based_level]
                
                # Insert into database
                query = """
                INSERT INTO pdf_structure (book_id, title, level, page_number, parent_id)
                VALUES (?, ?, ?, ?, ?)
                """
                
                cursor = self.db_manager.execute_query(
                    query, 
                    (book_id, title, level, page, parent_id)
                )
                
                item_id = cursor.lastrowid
                
                # Update parent stack
                parent_stack.append(item_id)
                
                structure.append({
                    "id": item_id,
                    "title": title,
                    "level": level,
                    "page_number": page,
                    "parent_id": parent_id
                })
            
            logger.info(f"Extracted {len(structure)} structure items from book {book_id}")
            
            return structure
            
        except Exception as e:
            logger.error(f"Error extracting structure: {str(e)}")
            return []
    
    def get_structure(self, book_id: int) -> List[Dict[str, Any]]:
        """
        Get the structure (headings) for a book.
        
        Args:
            book_id (int): ID of the book
            
        Returns:
            List[Dict[str, Any]]: Book structure
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return []
        
        query = """
        SELECT * FROM pdf_structure
        WHERE book_id = ?
        ORDER BY level, page_number
        """
        
        results = self.db_manager.execute_query(query, (book_id,)).fetchall()
        
        if not results:
            # If no structure exists, try to extract it
            return self.extract_structure(book_id)
        
        return [dict(result) for result in results]
    
    def save_settings(self, 
                    user_id: int, 
                    settings: Dict[str, Any], 
                    book_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Save user settings for PDF viewing.
        
        Args:
            user_id (int): ID of the user
            settings (Dict[str, Any]): Settings dictionary
            book_id (int, optional): ID of the book for book-specific settings
            
        Returns:
            Dict[str, Any]: Saved settings
        """
        if not self.db_manager:
            logger.error("No database manager available")
            return {"error": "No database manager available"}
        
        # Check if settings already exist
        query = """
        SELECT id FROM pdf_settings
        WHERE user_id = ? AND (book_id IS NULL OR book_id = ?)
        """
        
        existing = self.db_manager.execute_query(query, (user_id, book_id)).fetchone()
        
        settings_json = json.dumps(settings)
        current_time = datetime.now().isoformat()
        
        if existing:
            # Update existing settings
            update_query = """
            UPDATE pdf_settings
            SET settings_json = ?, updated_at = ?
            WHERE id = ?
            """
            
            self.db_manager.execute_query(
                update_query, 
                (settings_json, current_time, existing["id"])
            )
            
            settings_id = existing["id"]
        else:
            # Insert new settings
            insert_query = """
            INSERT INTO pdf_settings (user_id, book_id, settings_json, updated_at)
            VALUES (?, ?, ?, ?)
            """
            
            cursor = self.db_manager.execute_query(
                insert_query, 
                (user_id, book_id, settings_json, current_time)
            )
            
            settings_id = cursor.lastrowid
        
        logger.info(f"Saved settings for user {user_id}" + (f", book {book_id}" if book_id else ""))
        
        return {
            "id": settings_id,
            "user_id": user_id,
            "book_id": book_id,
            "settings": settings,
            "updated_at": current_time
        }
    
    def get_settings(self, 
                   user_id: int, 
                   book_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user settings for PDF viewing.
        
        Args:
            user_id (int): ID of the user
            book_id (int, optional): ID of the book for book-specific settings
            
        Returns:
            Dict[str, Any]: User settings
        """
        if not self.db_manager:
            logger.warning("No database manager available, returning default settings")
            return self.default_settings
        
        # Try to get book-specific settings first if book_id is provided
        if book_id:
            query = """
            SELECT * FROM pdf_settings
            WHERE user_id = ? AND book_id = ?
            """
            
            result = self.db_manager.execute_query(query, (user_id, book_id)).fetchone()
            
            if result:
                try:
                    settings = json.loads(result["settings_json"])
                    return settings
                except Exception as e:
                    logger.error(f"Error parsing settings JSON: {str(e)}")
        
        # Try to get user's global settings
        query = """
        SELECT * FROM pdf_settings
        WHERE user_id = ? AND book_id IS NULL
        """
        
        result = self.db_manager.execute_query(query, (user_id,)).fetchone()
        
        if result:
            try:
                settings = json.loads(result["settings_json"])
                return settings
            except Exception as e:
                logger.error(f"Error parsing settings JSON: {str(e)}")
        
        # Return default settings if nothing found
        return self.default_settings
    
    def render_page(self, 
                  book_id: int, 
                  page_number: int, 
                  user_id: int,
                  scale: float = 1.0,
                  rotation: int = 0) -> Dict[str, Any]:
        """
        Render a page from a PDF book.
        
        Args:
            book_id (int): ID of the book
            page_number (int): Page number to render
            user_id (int): ID of the user
            scale (float): Scale factor for rendering
            rotation (int): Rotation angle in degrees
            
        Returns:
            Dict[str, Any]: Rendered page information
        """
        # Get book information
        book = self.get_book(book_id)
        if "error" in book:
            return book
        
        file_path = book["file_path"]
        
        # Get user settings
        settings = self.get_settings(user_id, book_id)
        
        # Render page using PyMuPDF
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(file_path)
            
            # Check if page number is valid
            if page_number < 1 or page_number > len(doc):
                doc.close()
                return {"error": f"Invalid page number: {page_number}"}
            
            # Get page (0-indexed)
            page = doc[page_number - 1]
            
            # Apply rotation if specified
            if rotation:
                page.set_rotation(rotation)
            
            # Render page to image
            zoom = scale * 2  # Higher resolution for better quality
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Create a temporary file for the image
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                pix.save(tmp.name)
                image_path = tmp.name
            
            # Get page text
            text = page.get_text()
            
            # Get page dimensions
            rect = page.rect
            width, height = rect.width, rect.height
            
            # Get annotations for this page
            annotations = self.get_annotations(book_id, user_id, page_number)
            
            # Update reading progress
            self.update_reading_progress(book_id, page_number)
            
            doc.close()
            
            return {
                "book_id": book_id,
                "page_number": page_number,
                "image_path": image_path,
                "text": text,
                "width": width,
                "height": height,
                "annotations": annotations,
                "settings": settings
            }
            
        except Exception as e:
            logger.error(f"Error rendering page: {str(e)}")
            return {"error": f"Error rendering page: {str(e)}"}
"""