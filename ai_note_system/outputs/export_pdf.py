"""
PDF export module for AI Note System.
Handles exporting notes to PDF format.
"""

import os
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path

# Setup logging
logger = logging.getLogger("ai_note_system.outputs.export_pdf")

# Import markdown exporter to reuse functionality
from .export_markdown import generate_markdown

def export_to_pdf(
    content: Dict[str, Any],
    output_path: str,
    include_metadata: bool = True,
    include_original_text: bool = True,
    template: Optional[str] = None,
    css_path: Optional[str] = None,
    page_size: str = "A4",
    margin: str = "1in"
) -> Dict[str, Any]:
    """
    Export content to PDF format.
    
    Args:
        content (Dict[str, Any]): The content to export
        output_path (str): Path to save the PDF file
        include_metadata (bool): Whether to include metadata in the output
        include_original_text (bool): Whether to include the original text
        template (str, optional): Path to a custom Markdown template
        css_path (str, optional): Path to a custom CSS file
        page_size (str): Page size (A4, Letter, etc.)
        margin (str): Page margin
        
    Returns:
        Dict[str, Any]: Result of the export operation
    """
    logger.info("Exporting content to PDF")
    
    try:
        # Check if required packages are installed
        try:
            import weasyprint
            WEASYPRINT_AVAILABLE = True
        except ImportError:
            logger.warning("WeasyPrint package not installed. Trying alternative PDF conversion.")
            WEASYPRINT_AVAILABLE = False
            
            try:
                import markdown
                import pdfkit
                PDFKIT_AVAILABLE = True
            except ImportError:
                error_msg = "Neither WeasyPrint nor pdfkit is installed. Cannot export to PDF."
                logger.error(error_msg)
                return {"success": False, "error": error_msg}
        
        # Generate Markdown content
        markdown_content = generate_markdown(
            content, 
            include_metadata=include_metadata,
            include_original_text=include_original_text,
            template=template
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Convert Markdown to PDF
        if WEASYPRINT_AVAILABLE:
            result = convert_with_weasyprint(markdown_content, output_path, css_path, page_size, margin)
        else:
            result = convert_with_pdfkit(markdown_content, output_path, css_path, page_size, margin)
        
        if result["success"]:
            logger.info(f"PDF saved to {output_path}")
            return {"success": True, "output_path": output_path}
        else:
            return result
        
    except Exception as e:
        error_msg = f"Error exporting to PDF: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def convert_with_weasyprint(
    markdown_content: str,
    output_path: str,
    css_path: Optional[str] = None,
    page_size: str = "A4",
    margin: str = "1in"
) -> Dict[str, Any]:
    """
    Convert Markdown to PDF using WeasyPrint.
    
    Args:
        markdown_content (str): Markdown content
        output_path (str): Path to save the PDF file
        css_path (str, optional): Path to a custom CSS file
        page_size (str): Page size (A4, Letter, etc.)
        margin (str): Page margin
        
    Returns:
        Dict[str, Any]: Result of the conversion
    """
    try:
        import markdown
        from weasyprint import HTML, CSS
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        # Add HTML wrapper with styling
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Note System Export</title>
    <style>
        @page {{
            size: {page_size};
            margin: {margin};
        }}
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #3498db;
            margin-top: 30px;
        }}
        h3 {{
            color: #2980b9;
        }}
        code {{
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 4px;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #ccc;
            padding-left: 15px;
            color: #555;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        details {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        summary {{
            cursor: pointer;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
        
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
            f.write(html)
            temp_html_path = f.name
        
        try:
            # Load custom CSS if provided
            css = None
            if css_path and os.path.exists(css_path):
                css = CSS(filename=css_path)
            
            # Convert HTML to PDF
            HTML(filename=temp_html_path).write_pdf(output_path, stylesheets=[css] if css else None)
            
            return {"success": True}
            
        finally:
            # Clean up temporary file
            os.unlink(temp_html_path)
        
    except Exception as e:
        error_msg = f"Error converting with WeasyPrint: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def convert_with_pdfkit(
    markdown_content: str,
    output_path: str,
    css_path: Optional[str] = None,
    page_size: str = "A4",
    margin: str = "1in"
) -> Dict[str, Any]:
    """
    Convert Markdown to PDF using pdfkit (wkhtmltopdf).
    
    Args:
        markdown_content (str): Markdown content
        output_path (str): Path to save the PDF file
        css_path (str, optional): Path to a custom CSS file
        page_size (str): Page size (A4, Letter, etc.)
        margin (str): Page margin
        
    Returns:
        Dict[str, Any]: Result of the conversion
    """
    try:
        import markdown
        import pdfkit
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        # Add HTML wrapper with styling
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>AI Note System Export</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #3498db;
            margin-top: 30px;
        }}
        h3 {{
            color: #2980b9;
        }}
        code {{
            background-color: #f8f8f8;
            padding: 2px 4px;
            border-radius: 4px;
        }}
        pre {{
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 4px solid #ccc;
            padding-left: 15px;
            color: #555;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        details {{
            margin: 10px 0;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        summary {{
            cursor: pointer;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>"""
        
        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile(suffix=".html", mode="w", encoding="utf-8", delete=False) as f:
            f.write(html)
            temp_html_path = f.name
        
        try:
            # Configure pdfkit options
            options = {
                'page-size': page_size,
                'margin-top': margin,
                'margin-right': margin,
                'margin-bottom': margin,
                'margin-left': margin,
                'encoding': 'UTF-8',
                'quiet': ''
            }
            
            # Add custom CSS if provided
            if css_path and os.path.exists(css_path):
                options['user-style-sheet'] = css_path
            
            # Convert HTML to PDF
            pdfkit.from_file(temp_html_path, output_path, options=options)
            
            return {"success": True}
            
        finally:
            # Clean up temporary file
            os.unlink(temp_html_path)
        
    except Exception as e:
        error_msg = f"Error converting with pdfkit: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def create_custom_css_template(output_path: str) -> Dict[str, Any]:
    """
    Create a sample CSS template file for PDF styling.
    
    Args:
        output_path (str): Path to save the CSS file
        
    Returns:
        Dict[str, Any]: Result of the operation
    """
    css_content = """/* Custom CSS for PDF export */

/* Page settings */
@page {
    size: A4;
    margin: 1in;
}

/* Basic typography */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
}

/* Headings */
h1 {
    color: #2c3e50;
    font-size: 24pt;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

h2 {
    color: #3498db;
    font-size: 18pt;
    margin-top: 30px;
}

h3 {
    color: #2980b9;
    font-size: 14pt;
}

/* Code blocks */
code {
    background-color: #f8f8f8;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: Consolas, Monaco, 'Andale Mono', monospace;
}

pre {
    background-color: #f8f8f8;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    font-family: Consolas, Monaco, 'Andale Mono', monospace;
}

/* Blockquotes */
blockquote {
    border-left: 4px solid #ccc;
    padding-left: 15px;
    color: #555;
    font-style: italic;
}

/* Tables */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

/* Lists */
ul, ol {
    margin: 10px 0;
    padding-left: 30px;
}

li {
    margin-bottom: 5px;
}

/* Details/Summary (for Q&A) */
details {
    margin: 10px 0;
    padding: 10px;
    background-color: #f9f9f9;
    border-radius: 4px;
}

summary {
    cursor: pointer;
    font-weight: bold;
    color: #2980b9;
}

/* Metadata section */
.metadata {
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 20px;
}

/* Tags */
.tag {
    display: inline-block;
    background-color: #e0f7fa;
    color: #0097a7;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 5px;
    font-size: 0.9em;
}
"""
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Write CSS to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        logger.info(f"CSS template saved to {output_path}")
        return {"success": True, "output_path": output_path}
        
    except Exception as e:
        error_msg = f"Error creating CSS template: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}