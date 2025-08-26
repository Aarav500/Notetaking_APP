#!/usr/bin/env python
"""
AI Note System - Main Entry Point

This is the main entry point for the AI Note System, a comprehensive note-taking
and knowledge management system that uses AI to process various inputs,
extract key information, generate visualizations, and create active recall materials.

Usage:
    python main.py [command] [options]

Commands:
    process     Process input and generate notes
    export      Export notes to various formats
    search      Search through existing notes
    review      Review notes with spaced repetition
    config      View or edit configuration
"""

import os
import sys
import argparse
import logging
import glob
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Import utility modules
from utils.config_loader import load_config
from utils.logger import setup_logger

# Import input modules
from inputs.text_input import process_text
from inputs.pdf_input import extract_text_from_pdf
from inputs.ocr_input import extract_text_from_image
from inputs.speech_input import transcribe_audio, record_audio
from inputs.youtube_input import process_youtube_video

# Import processing modules
from processing.summarizer import summarize_text
from processing.keypoints_extractor import extract_keypoints, extract_glossary
from processing.active_recall_gen import generate_questions, generate_mcqs, generate_fill_blanks
from processing.topic_linker import find_related_topics
from processing.misconception_checker import check_misconceptions
from processing.simplifier import simplify_text
from processing.retrieval_qa import ask_question
from processing.math_formula_processor import process_math_formulas, detect_math_formulas
from processing.citation_tracker import add_source, get_sources, search_by_source, generate_citation, generate_citations_for_note

# Import visualization modules
from visualization.flowchart_gen import generate_flowchart
from visualization.mindmap_gen import generate_mindmap
from visualization.timeline_gen import generate_timeline
from visualization.treegraph_gen import generate_treegraph
from visualization.knowledge_graph_gen import generate_knowledge_graph, generate_html_knowledge_graph, extract_graph_data_from_db

# Import output modules
from outputs.notion_uploader import upload_to_notion
from outputs.export_markdown import export_to_markdown
from outputs.export_pdf import export_to_pdf
from outputs.export_anki import export_to_anki
from outputs.spaced_repetition import schedule_review
from outputs.reminder_manager import schedule_reminder, get_reminders, start_reminder_scheduler, stop_reminder_scheduler

# Import ML enhancement modules
from processing.ml_enhancements.content_gap_filler import identify_content_gaps, fill_content_gaps
from processing.ml_enhancements.mastery_estimator import estimate_mastery
from processing.ml_enhancements.quiz_adaptive_trainer import generate_adaptive_quiz, analyze_quiz_results
from processing.study_plan_generator import generate_study_plan, save_study_plan

# Import database modules
from database.db_manager import DatabaseManager, init_db

# Import embeddings module
from embeddings.embedder import Embedder

# Import plugin system
from plugins.plugin_manager import get_plugin_manager
from plugins.plugin_base import Plugin, VisualizationPlugin, MLModelPlugin, IntegrationPlugin

# Import research agent
from agents.research_agent import ResearchAgent

# Import tracking modules
from tracking.motivation_tracker import track_motivation, track_performance, get_motivation_history, correlate_motivation_performance, generate_motivation_insights, generate_study_strategy


def setup_argparse() -> argparse.ArgumentParser:
    """
    Setup command line argument parser.
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description="AI Note System - A comprehensive note-taking and knowledge management system"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Process input and generate notes")
    process_parser.add_argument("--input", "-i", type=str, help="Input text, file path, or URL")
    process_parser.add_argument("--type", "-t", choices=["text", "pdf", "image", "speech", "youtube"], 
                               default="text", help="Type of input")
    process_parser.add_argument("--title", type=str, help="Title for the note")
    process_parser.add_argument("--tags", type=str, nargs="+", help="Tags for the note")
    process_parser.add_argument("--summarize", action="store_true", help="Generate summary")
    process_parser.add_argument("--keypoints", action="store_true", help="Extract key points")
    process_parser.add_argument("--glossary", action="store_true", help="Extract glossary")
    process_parser.add_argument("--questions", action="store_true", help="Generate questions")
    process_parser.add_argument("--mcqs", action="store_true", help="Generate MCQs")
    process_parser.add_argument("--fill-blanks", action="store_true", help="Generate fill-in-the-blanks")
    process_parser.add_argument("--visualize", choices=["flowchart", "mindmap", "timeline", "treegraph"],
                               help="Generate visualization")
    process_parser.add_argument("--simplify", action="store_true", help="Simplify text")
    process_parser.add_argument("--check-misconceptions", action="store_true", help="Check for misconceptions")
    process_parser.add_argument("--source-language", type=str, help="Source language code (auto-detect if not provided)")
    process_parser.add_argument("--target-language", type=str, default="en", help="Target language code for the summary")
    process_parser.add_argument("--no-translate", action="store_true", help="Disable automatic translation")
    process_parser.add_argument("--translation-provider", choices=["google", "deepl", "llm", "auto"],
                               default="auto", help="Translation provider to use")
    process_parser.add_argument("--output", "-o", choices=["notion", "markdown", "pdf", "anki", "json"],
                               default="json", help="Output format")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export notes to various formats")
    export_parser.add_argument("--id", type=str, help="Note ID to export")
    export_parser.add_argument("--format", "-f", choices=["notion", "markdown", "pdf", "anki"],
                              required=True, help="Export format")
    export_parser.add_argument("--output", "-o", type=str, help="Output file or directory")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search through existing notes")
    search_parser.add_argument("query", type=str, help="Search query")
    search_parser.add_argument("--tags", type=str, nargs="+", help="Filter by tags")
    search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    
    # Semantic Search command
    semantic_search_parser = subparsers.add_parser("search_pansophy", help="Search notes by meaning using embeddings")
    semantic_search_parser.add_argument("query", type=str, help="Semantic search query")
    semantic_search_parser.add_argument("--tags", type=str, nargs="+", help="Filter by tags")
    semantic_search_parser.add_argument("--limit", type=int, default=10, help="Maximum number of results")
    semantic_search_parser.add_argument("--threshold", type=float, default=0.7, help="Minimum similarity threshold (0-1)")
    
    # Review command
    review_parser = subparsers.add_parser("review", help="Review notes with spaced repetition")
    review_parser.add_argument("--id", type=str, help="Note ID to review")
    review_parser.add_argument("--due", action="store_true", help="Show only due notes")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="View or edit configuration")
    config_parser.add_argument("--view", action="store_true", help="View configuration")
    config_parser.add_argument("--edit", type=str, nargs=2, metavar=("KEY", "VALUE"),
                              help="Edit configuration key-value pair")
    
    # Knowledge Graph command
    graph_parser = subparsers.add_parser("graph", help="Generate a hierarchical knowledge graph from notes")
    graph_parser.add_argument("--format", "-f", choices=["svg", "png", "pdf", "html"], 
                             default="svg", help="Output format")
    graph_parser.add_argument("--output", "-o", type=str, help="Output file path")
    graph_parser.add_argument("--title", type=str, default="Knowledge Graph", help="Title for the graph")
    graph_parser.add_argument("--layout", choices=["fdp", "neato", "dot", "sfdp", "twopi", "circo"],
                             default="fdp", help="Graphviz layout engine")
    graph_parser.add_argument("--no-3d", action="store_true", help="Disable 3D-like styling")
    graph_parser.add_argument("--max-nodes", type=int, default=100, help="Maximum number of nodes to include")
    graph_parser.add_argument("--threshold", type=float, default=0.5, 
                             help="Minimum similarity threshold for related notes (0-1)")
    graph_parser.add_argument("--tags", type=str, nargs="+", help="Filter notes by tags")
    graph_parser.add_argument("--open", action="store_true", help="Open the output file in a browser")
    
    # Retrieval-Augmented Q&A command
    qa_parser = subparsers.add_parser("pansophy_ask", help="Ask questions and get answers based on your notes")
    qa_parser.add_argument("query", type=str, help="The question to ask")
    qa_parser.add_argument("--tags", type=str, nargs="+", help="Filter notes by tags")
    qa_parser.add_argument("--limit", type=int, default=5, help="Maximum number of relevant notes to retrieve")
    qa_parser.add_argument("--threshold", type=float, default=0.7, help="Minimum similarity threshold (0-1)")
    qa_parser.add_argument("--model", type=str, default="gpt-4", help="LLM model to use for generating the answer")
    qa_parser.add_argument("--no-sources", action="store_true", help="Don't include source information in the answer")
    
    # Image Mind Map command
    image_mindmap_parser = subparsers.add_parser("image_mindmap", help="Generate an interactive mind map with images from slides/diagrams")
    image_mindmap_parser.add_argument("--input", "-i", type=str, required=True, help="Input file path (PDF, slides, video)")
    image_mindmap_parser.add_argument("--type", "-t", choices=["pdf", "slides", "video"], required=True, help="Type of input")
    image_mindmap_parser.add_argument("--output", "-o", type=str, help="Output HTML file path")
    image_mindmap_parser.add_argument("--title", type=str, help="Title for the mind map")
    image_mindmap_parser.add_argument("--theme", choices=["default", "dark", "light", "nature"], default="default", help="Theme for the mind map")
    image_mindmap_parser.add_argument("--open", action="store_true", help="Open the mind map in a browser")
    
    # Research command
    research_parser = subparsers.add_parser("research", help="Research a topic from various sources")
    research_parser.add_argument("topic", type=str, help="The topic to research")
    research_parser.add_argument("--sources", type=str, nargs="+", 
                               choices=["wikipedia", "arxiv", "semantic_scholar", "youtube", "github", "web"],
                               help="Sources to use for research (default: all)")
    research_parser.add_argument("--max-results", type=int, default=10, 
                               help="Maximum number of results per source")
                               
    # Citation & Source Tracking commands
    citation_parser = subparsers.add_parser("citation", help="Track sources and generate citations")
    citation_subparsers = citation_parser.add_subparsers(dest="citation_command", help="Citation command to execute")
    
    # Emotion & Motivation Tracking commands
    motivation_parser = subparsers.add_parser("motivation", help="Track motivation and learning performance")
    motivation_subparsers = motivation_parser.add_subparsers(dest="motivation_command", help="Motivation command to execute")
    
    # Track motivation command
    track_motivation_parser = motivation_subparsers.add_parser("track", help="Log current motivation level")
    track_motivation_parser.add_argument("--level", type=int, required=True, help="Motivation level (1-10)")
    track_motivation_parser.add_argument("--notes", type=str, help="Notes about current motivation")
    track_motivation_parser.add_argument("--tags", type=str, nargs="+", help="Tags for categorization")
    track_motivation_parser.add_argument("--activity-type", type=str, help="Type of activity (study, review, practice, etc.)")
    track_motivation_parser.add_argument("--duration", type=int, help="Duration of activity in minutes")
    track_motivation_parser.add_argument("--energy-level", type=int, help="Energy level (1-10)")
    track_motivation_parser.add_argument("--focus-level", type=int, help="Focus level (1-10)")
    track_motivation_parser.add_argument("--stress-level", type=int, help="Stress level (1-10)")
    track_motivation_parser.add_argument("--sleep-hours", type=float, help="Hours of sleep")
    
    # Track performance command
    track_performance_parser = motivation_subparsers.add_parser("track_performance", help="Track learning performance")
    track_performance_parser.add_argument("--activity-type", type=str, required=True, help="Type of activity (quiz, review, practice, etc.)")
    track_performance_parser.add_argument("--score", type=float, required=True, help="Performance score (0-100)")
    track_performance_parser.add_argument("--duration", type=int, help="Duration of activity in minutes")
    track_performance_parser.add_argument("--note-id", type=int, help="ID of the related note")
    track_performance_parser.add_argument("--motivation-id", type=int, help="ID of the related motivation entry")
    
    # View motivation history command
    view_motivation_parser = motivation_subparsers.add_parser("view_history", help="View motivation history")
    view_motivation_parser.add_argument("--period", type=int, default=30, help="Number of days to look back")
    view_motivation_parser.add_argument("--activity-type", type=str, help="Filter by activity type")
    view_motivation_parser.add_argument("--tags", type=str, nargs="+", help="Filter by tags")
    
    # Correlate motivation and performance command
    correlate_parser = motivation_subparsers.add_parser("correlate", help="Correlate motivation with performance")
    correlate_parser.add_argument("--period", type=int, default=30, help="Number of days to look back")
    
    # Generate motivation insights command
    insights_parser = motivation_subparsers.add_parser("insights", help="Generate insights based on motivation patterns")
    
    # Generate study strategy command
    strategy_parser = motivation_subparsers.add_parser("strategy", help="Generate personalized study strategy")
    
    # Add source command
    add_source_parser = citation_subparsers.add_parser("add_source", help="Add source information to a note")
    add_source_parser.add_argument("--note-id", type=int, required=True, help="ID of the note")
    add_source_parser.add_argument("--source", type=str, required=True, help="Source description")
    add_source_parser.add_argument("--source-type", type=str, choices=["book", "article", "website", "video"], 
                                 default="website", help="Type of source")
    add_source_parser.add_argument("--title", type=str, help="Title of the source")
    add_source_parser.add_argument("--authors", type=str, help="Authors of the source (comma-separated)")
    add_source_parser.add_argument("--year", type=int, help="Year of publication")
    add_source_parser.add_argument("--url", type=str, help="URL of the source")
    add_source_parser.add_argument("--publisher", type=str, help="Publisher of the source")
    add_source_parser.add_argument("--journal", type=str, help="Journal name for articles")
    add_source_parser.add_argument("--volume", type=str, help="Volume number for articles")
    add_source_parser.add_argument("--issue", type=str, help="Issue number for articles")
    add_source_parser.add_argument("--pages", type=str, help="Page range for articles")
    add_source_parser.add_argument("--doi", type=str, help="DOI for articles")
    
    # Generate citations command
    generate_citations_parser = citation_subparsers.add_parser("generate_citations", help="Generate citations for a note")
    generate_citations_parser.add_argument("--note-id", type=int, required=True, help="ID of the note")
    generate_citations_parser.add_argument("--format", type=str, choices=["apa", "mla", "ieee"], 
                                         default="apa", help="Citation format")
    generate_citations_parser.add_argument("--output", type=str, help="Output file path")
    
    # View sources command
    view_sources_parser = citation_subparsers.add_parser("view_sources", help="View all sources for a note")
    view_sources_parser.add_argument("--note-id", type=int, required=True, help="ID of the note")
    
    # Search by source command
    search_by_source_parser = citation_subparsers.add_parser("search_by_source", help="Search notes by source")
    search_by_source_parser.add_argument("--source", type=str, required=True, help="Source term to search for")
    research_parser.add_argument("--output-dir", type=str, 
                               help="Directory to save research results (default: data/research/<topic>)")
    research_parser.add_argument("--visualize", choices=["mindmap", "knowledge_graph", "timeline"],
                               help="Generate visualization of research results")
    research_parser.add_argument("--generate-flashcards", action="store_true", 
                               help="Generate flashcards from research results")
    research_parser.add_argument("--generate-summary", action="store_true", 
                               help="Generate summary of research results")
    research_parser.add_argument("--verbose", action="store_true", 
                               help="Print verbose output")
    
    # Reminders command
    reminders_parser = subparsers.add_parser("reminders", help="Manage review reminders")
    reminders_subparsers = reminders_parser.add_subparsers(dest="reminders_command", help="Reminders command to execute")
    
    # Schedule reminder command
    schedule_reminder_parser = reminders_subparsers.add_parser("schedule", help="Schedule a reminder")
    schedule_reminder_parser.add_argument("--id", required=True, help="ID of the item to schedule a reminder for")
    schedule_reminder_parser.add_argument("--type", default="note", help="Type of item (note, question, etc.)")
    schedule_reminder_parser.add_argument("--time", required=True, help="Time to send the reminder (ISO format)")
    schedule_reminder_parser.add_argument("--channels", nargs="+", default=["desktop"], 
                                        choices=["email", "desktop", "slack", "discord"],
                                        help="Notification channels to use")
    
    # List reminders command
    list_reminders_parser = reminders_subparsers.add_parser("list", help="List scheduled reminders")
    list_reminders_parser.add_argument("--id", help="Filter by item ID")
    list_reminders_parser.add_argument("--type", help="Filter by item type")
    list_reminders_parser.add_argument("--status", choices=["scheduled", "sent"], help="Filter by status")
    list_reminders_parser.add_argument("--limit", type=int, default=10, help="Maximum number of reminders to list")
    
    # Start scheduler command
    start_scheduler_parser = reminders_subparsers.add_parser("start-scheduler", help="Start the reminder scheduler")
    
    # Stop scheduler command
    stop_scheduler_parser = reminders_subparsers.add_parser("stop-scheduler", help="Stop the reminder scheduler")
    
    # Plugins command
    plugins_parser = subparsers.add_parser("plugins", help="Manage plugins")
    plugins_subparsers = plugins_parser.add_subparsers(dest="plugins_command", help="Plugins command to execute")
    
    # List plugins command
    list_plugins_parser = plugins_subparsers.add_parser("list", help="List available plugins")
    list_plugins_parser.add_argument("--type", choices=["all", "visualization", "ml_model", "integration", "input_processor", "output_formatter"],
                                   default="all", help="Type of plugins to list")
    list_plugins_parser.add_argument("--loaded", action="store_true", help="Show only loaded plugins")
    list_plugins_parser.add_argument("--available", action="store_true", help="Show all available plugins")
    
    # Load plugin command
    load_plugin_parser = plugins_subparsers.add_parser("load", help="Load a plugin")
    load_plugin_parser.add_argument("plugin_id", help="ID of the plugin to load")
    
    # Unload plugin command
    unload_plugin_parser = plugins_subparsers.add_parser("unload", help="Unload a plugin")
    unload_plugin_parser.add_argument("plugin_id", help="ID of the plugin to unload")
    
    # Add plugin directory command
    add_plugin_dir_parser = plugins_subparsers.add_parser("add-dir", help="Add a plugin directory")
    add_plugin_dir_parser.add_argument("directory", help="Directory path to add")
    
    # Learning Plan Generator command
    plan_parser = subparsers.add_parser("pansophy_plan", help="Generate a personalized study plan")
    plan_parser.add_argument("--weeks", type=int, default=4, help="Number of weeks to plan for")
    plan_parser.add_argument("--user", required=True, help="User ID")
    plan_parser.add_argument("--hours", type=int, help="Target study hours per week")
    plan_parser.add_argument("--focus", nargs="+", help="Specific areas to focus on")
    plan_parser.add_argument("--output", help="Output file path")
    
    # Math Formula Processor command
    math_parser = subparsers.add_parser("math_formula", help="Process math formulas in content")
    math_parser.add_argument("--input", required=True, help="Input file (JSON) or image")
    math_parser.add_argument("--output", help="Output file (JSON)")
    math_parser.add_argument("--no-ocr", action="store_true", help="Skip OCR")
    math_parser.add_argument("--no-link", action="store_true", help="Skip linking")
    math_parser.add_argument("--no-practice", action="store_true", help="Skip practice problem generation")
    math_parser.add_argument("--render", action="store_true", help="Render formulas as images")
    math_parser.add_argument("--render-dir", help="Directory to save rendered formula images")
    
    return parser


def process_input(args: argparse.Namespace, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process input based on command line arguments.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
        
    Returns:
        Dict[str, Any]: Processed data
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info(f"Processing input of type: {args.type}")
    
    result = {}
    
    # Process input based on type
    if args.type == "text":
        if args.input:
            # Direct text input
            result = process_text(args.input, args.title, args.tags)
        else:
            # Read from stdin if no input is provided
            text = sys.stdin.read().strip()
            if text:
                result = process_text(text, args.title, args.tags)
            else:
                logger.error("No input provided")
                sys.exit(1)
    
    elif args.type == "pdf":
        if not args.input:
            logger.error("PDF input requires a file path")
            sys.exit(1)
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(args.input)
        # Process the extracted text
        result = process_text(pdf_text, args.title, args.tags)
    
    elif args.type == "image":
        if not args.input:
            logger.error("Image input requires a file path")
            sys.exit(1)
        # Extract text from image
        image_text = extract_text_from_image(args.input)
        # Process the extracted text
        result = process_text(image_text, args.title, args.tags)
    
    elif args.type == "speech":
        if args.input:
            # Process audio file
            audio_text = transcribe_audio(args.input)
            # Process the transcribed text
            result = process_text(audio_text, args.title, args.tags)
        else:
            # Record from microphone
            logger.info("Recording from microphone...")
            audio_path = record_audio()
            audio_text = transcribe_audio(audio_path)
            # Process the transcribed text
            result = process_text(audio_text, args.title, args.tags)
    
    elif args.type == "youtube":
        if not args.input:
            logger.error("YouTube input requires a URL")
            sys.exit(1)
        # Process YouTube video
        result = process_youtube_video(
            args.input,
            title=args.title,
            tags=args.tags,
            save_audio=False
        )
    
    # Apply processing steps based on arguments
    if args.summarize and "text" in result:
        # Get language parameters
        source_language = args.source_language
        target_language = args.target_language
        translate = not args.no_translate
        translation_provider = args.translation_provider
        
        # Call summarize_text with language parameters
        summary_result = summarize_text(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4"),
            max_length=config.get("SUMMARIZATION_MAX_LENGTH", 500),
            source_language=source_language,
            target_language=target_language,
            translate=translate,
            translation_provider=translation_provider
        )
        
        # Handle both dictionary and string return types
        if isinstance(summary_result, dict):
            result["summary"] = summary_result.get("summary", "")
            # Add language information if available
            if "language_info" in summary_result:
                result["language_info"] = summary_result["language_info"]
        else:
            result["summary"] = summary_result
    
    if args.keypoints and "text" in result:
        result["keypoints"] = extract_keypoints(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4"),
            max_points=config.get("KEYPOINTS_MAX_COUNT", 10),
            title=result.get("title")
        )
    
    if args.glossary and "text" in result:
        result["glossary"] = extract_glossary(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4"),
            title=result.get("title")
        )
    
    if args.questions and "text" in result:
        result["questions"] = generate_questions(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4"),
            count=config.get("ACTIVE_RECALL_QUESTIONS_COUNT", 5)
        )
    
    if args.mcqs and "text" in result:
        result["mcqs"] = generate_mcqs(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4"),
            count=config.get("ACTIVE_RECALL_QUESTIONS_COUNT", 5)
        )
    
    if args.fill_blanks and "text" in result:
        result["fill_blanks"] = generate_fill_blanks(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4"),
            count=config.get("ACTIVE_RECALL_QUESTIONS_COUNT", 5)
        )
    
    if args.simplify and "text" in result:
        result["simplified"] = simplify_text(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4")
        )
    
    if args.check_misconceptions and "text" in result:
        result["misconceptions"] = check_misconceptions(
            result["text"],
            model=config.get("LLM_MODEL", "gpt-4")
        )
    
    # Find related topics
    if "text" in result:
        logger.info("Finding related topics")
        
        # Get database path from config
        db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
        # Convert relative path to absolute path
        if not os.path.isabs(db_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.abspath(os.path.join(current_dir, db_path))
        
        # Create database manager
        db_manager = DatabaseManager(db_path)
        
        try:
            # Get all notes for comparison
            all_notes = db_manager.search_notes(limit=100)  # Limit to 100 notes for performance
            
            if all_notes:
                # Create a dictionary of note texts for topic_linker
                note_db = {
                    note["id"]: {
                        "title": note["title"],
                        "text": note.get("text", ""),
                        "summary": note.get("summary", "")
                    }
                    for note in all_notes
                }
                
                # Find related topics
                embedding_model = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
                threshold = config.get("SIMILARITY_THRESHOLD", 0.75)
                max_results = config.get("MAX_RELATED_TOPICS", 5)
                
                related_topics = find_related_topics(
                    result["text"],
                    note_db,
                    max_results=max_results,
                    threshold=threshold,
                    embedding_model=embedding_model
                )
                
                # Add related topics to result
                if related_topics:
                    result["related_topics"] = related_topics
                    
                    # If this is a new note being saved, add the relationships to the database
                    if "id" in result:
                        note_id = result["id"]
                        related_notes = [
                            (int(topic["id"]), topic["similarity"])
                            for topic in related_topics
                        ]
                        db_manager.add_related_notes(note_id, related_notes)
            
        finally:
            # Close database connection
            db_manager.close()
    
    # Generate visualization
    if args.visualize and "text" in result:
        logger.info(f"Generating visualization: {args.visualize}")
        
        # Get LLM model from config
        llm_model = config.get("LLM_MODEL", "gpt-4")
        
        if args.visualize == "flowchart":
            # Use LLM-enhanced flowchart generation
            flowchart_result = generate_flowchart(
                result["text"],
                engine=config.get("FLOWCHART_ENGINE", "mermaid"),
                output_format=config.get("VISUALIZATION_FORMAT", "png"),
                title=result.get("title"),
                direction=config.get("FLOWCHART_DIRECTION", "TD"),
                theme=config.get("VISUALIZATION_THEME", "default"),
                include_code=True
            )
            
            # Store the visualization result
            result["visualization"] = {
                "type": "flowchart",
                "engine": flowchart_result.get("engine", "mermaid"),
                "code": flowchart_result.get("code", "")
            }
            
            # If output path is available, store it
            if "output_path" in flowchart_result:
                result["visualization"]["path"] = flowchart_result["output_path"]
            
            logger.info("Flowchart generated successfully")
            
        elif args.visualize == "mindmap":
            # Use LLM-enhanced mind map generation
            mindmap_result = generate_mindmap(
                result["text"],
                output_format=config.get("VISUALIZATION_FORMAT", "png"),
                title=result.get("title"),
                theme=config.get("VISUALIZATION_THEME", "default"),
                include_code=True
            )
            
            # Store the visualization result
            result["visualization"] = {
                "type": "mindmap",
                "code": mindmap_result.get("code", "")
            }
            
            # If output path is available, store it
            if "output_path" in mindmap_result:
                result["visualization"]["path"] = mindmap_result["output_path"]
            
            logger.info("Mind map generated successfully")
            
        elif args.visualize == "timeline":
            # Generate timeline
            timeline_result = generate_timeline(
                result["text"],
                output_format=config.get("VISUALIZATION_FORMAT", "png"),
                title=result.get("title"),
                theme=config.get("VISUALIZATION_THEME", "default"),
                include_code=True
            )
            
            # Store the visualization result
            result["visualization"] = {
                "type": "timeline",
                "code": timeline_result.get("code", "")
            }
            
            # If output path is available, store it
            if "output_path" in timeline_result:
                result["visualization"]["path"] = timeline_result["output_path"]
            
            logger.info("Timeline generated successfully")
            
        elif args.visualize == "treegraph":
            # Generate tree graph
            treegraph_result = generate_treegraph(
                result["text"],
                output_format=config.get("VISUALIZATION_FORMAT", "png"),
                title=result.get("title"),
                is_3d=config.get("TREEGRAPH_3D", True),
                theme=config.get("VISUALIZATION_THEME", "default"),
                include_code=True
            )
            
            # Store the visualization result
            result["visualization"] = {
                "type": "treegraph",
                "code": treegraph_result.get("code", "")
            }
            
            # If output path is available, store it
            if "output_path" in treegraph_result:
                result["visualization"]["path"] = treegraph_result["output_path"]
            
            logger.info("Tree graph generated successfully")
    
    return result


def handle_process_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'process' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Process input
    result = process_input(args, config)
    
    # Save to database if not already saved
    if "id" not in result and config.get("SAVE_TO_DATABASE", True):
        # Get database path from config
        db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
        # Convert relative path to absolute path
        if not os.path.isabs(db_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.abspath(os.path.join(current_dir, db_path))
        
        # Create database manager
        db_manager = DatabaseManager(db_path)
        
        try:
            # Add timestamp if not present
            if "timestamp" not in result:
                result["timestamp"] = datetime.now().isoformat()
            
            # Add source type if not present
            if "source_type" not in result:
                result["source_type"] = args.type
            
            # Save to database
            note_id = db_manager.create_note(result)
            
            # Update result with note ID
            result["id"] = note_id
            
            logger.info(f"Saved note to database with ID: {note_id}")
            print(f"Saved note to database with ID: {note_id}")
            
            # Find and save related topics
            if "text" in result and "related_topics" in result:
                related_notes = [
                    (int(topic["id"]), topic["similarity"])
                    for topic in result["related_topics"]
                ]
                db_manager.add_related_notes(note_id, related_notes)
                logger.info(f"Added {len(related_notes)} related topics to note {note_id}")
            
        finally:
            # Close database connection
            db_manager.close()
    
    # Handle output based on format
    if args.output == "json":
        import json
        print(json.dumps(result, indent=2))
    
    elif args.output == "notion":
        logger.info("Exporting to Notion")
        # Get Notion credentials from config
        notion_token = config.get("NOTION_TOKEN")
        database_id = config.get("NOTION_DATABASE_ID")
        
        # Upload to Notion
        notion_result = upload_to_notion(
            result,
            database_id=database_id,
            notion_token=notion_token,
            update_existing=True
        )
        
        if notion_result.get("success"):
            logger.info(f"Successfully uploaded to Notion: {notion_result.get('page_id')}")
            print(f"Successfully uploaded to Notion: {notion_result.get('page_id')}")
        else:
            logger.error(f"Failed to upload to Notion: {notion_result.get('error')}")
            print(f"Failed to upload to Notion: {notion_result.get('error')}")
    
    elif args.output == "markdown":
        logger.info("Exporting to Markdown")
        # Determine output path
        output_dir = config.get("EXPORT_DIR", "../exports")
        if not os.path.isabs(output_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        title = result.get("title", "Untitled")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.md"
        output_path = os.path.join(output_dir, filename)
        
        # Export to Markdown
        md_result = export_to_markdown(
            result,
            output_path=output_path,
            include_metadata=True,
            include_original_text=True
        )
        
        if md_result.get("success"):
            logger.info(f"Successfully exported to Markdown: {md_result.get('output_path')}")
            print(f"Successfully exported to Markdown: {md_result.get('output_path')}")
        else:
            logger.error(f"Failed to export to Markdown: {md_result.get('error')}")
            print(f"Failed to export to Markdown: {md_result.get('error')}")
    
    elif args.output == "pdf":
        logger.info("Exporting to PDF")
        # Determine output path
        output_dir = config.get("EXPORT_DIR", "../exports")
        if not os.path.isabs(output_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        title = result.get("title", "Untitled")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        # Export to PDF
        pdf_result = export_to_pdf(
            result,
            output_path=output_path,
            include_metadata=True,
            include_original_text=True
        )
        
        if pdf_result.get("success"):
            logger.info(f"Successfully exported to PDF: {pdf_result.get('output_path')}")
            print(f"Successfully exported to PDF: {pdf_result.get('output_path')}")
        else:
            logger.error(f"Failed to export to PDF: {pdf_result.get('error')}")
            print(f"Failed to export to PDF: {pdf_result.get('error')}")
    
    elif args.output == "anki":
        logger.info("Exporting to Anki")
        # Determine output path
        output_dir = config.get("EXPORT_DIR", "../exports")
        if not os.path.isabs(output_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        title = result.get("title", "Untitled")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.apkg"
        output_path = os.path.join(output_dir, filename)
        
        # Export to Anki
        anki_result = export_to_anki(
            result,
            output_path=output_path,
            deck_name=title,
            include_metadata=True
        )
        
        if anki_result.get("success"):
            logger.info(f"Successfully exported to Anki: {anki_result.get('output_path')}")
            print(f"Successfully exported to Anki: {anki_result.get('output_path')}")
        else:
            logger.error(f"Failed to export to Anki: {anki_result.get('error')}")
            print(f"Failed to export to Anki: {anki_result.get('error')}")


def handle_export_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'export' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info(f"Exporting note with ID {args.id} to {args.format} format")
    
    # Get database path from config
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    # Create database manager
    db_manager = DatabaseManager(db_path)
    
    try:
        # Get note from database
        note = db_manager.get_note(int(args.id))
        
        if not note:
            logger.error(f"Note with ID {args.id} not found")
            print(f"Note with ID {args.id} not found")
            return
        
        # Determine output path
        output_dir = args.output if args.output else config.get("EXPORT_DIR", "../exports")
        if not os.path.isabs(output_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        title = note.get("title", "Untitled")
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export based on format
        if args.format == "notion":
            logger.info("Exporting to Notion")
            # Get Notion credentials from config
            notion_token = config.get("NOTION_TOKEN")
            database_id = config.get("NOTION_DATABASE_ID")
            
            # Upload to Notion
            notion_result = upload_to_notion(
                note,
                database_id=database_id,
                notion_token=notion_token,
                update_existing=True
            )
            
            if notion_result.get("success"):
                logger.info(f"Successfully uploaded to Notion: {notion_result.get('page_id')}")
                print(f"Successfully uploaded to Notion: {notion_result.get('page_id')}")
            else:
                logger.error(f"Failed to upload to Notion: {notion_result.get('error')}")
                print(f"Failed to upload to Notion: {notion_result.get('error')}")
        
        elif args.format == "markdown":
            logger.info("Exporting to Markdown")
            filename = f"{safe_title}_{timestamp}.md"
            output_path = os.path.join(output_dir, filename)
            
            # Export to Markdown
            md_result = export_to_markdown(
                note,
                output_path=output_path,
                include_metadata=True,
                include_original_text=True
            )
            
            if md_result.get("success"):
                logger.info(f"Successfully exported to Markdown: {md_result.get('output_path')}")
                print(f"Successfully exported to Markdown: {md_result.get('output_path')}")
            else:
                logger.error(f"Failed to export to Markdown: {md_result.get('error')}")
                print(f"Failed to export to Markdown: {md_result.get('error')}")
        
        elif args.format == "pdf":
            logger.info("Exporting to PDF")
            filename = f"{safe_title}_{timestamp}.pdf"
            output_path = os.path.join(output_dir, filename)
            
            # Export to PDF
            pdf_result = export_to_pdf(
                note,
                output_path=output_path,
                include_metadata=True,
                include_original_text=True
            )
            
            if pdf_result.get("success"):
                logger.info(f"Successfully exported to PDF: {pdf_result.get('output_path')}")
                print(f"Successfully exported to PDF: {pdf_result.get('output_path')}")
            else:
                logger.error(f"Failed to export to PDF: {pdf_result.get('error')}")
                print(f"Failed to export to PDF: {pdf_result.get('error')}")
        
        elif args.format == "anki":
            logger.info("Exporting to Anki")
            filename = f"{safe_title}_{timestamp}.apkg"
            output_path = os.path.join(output_dir, filename)
            
            # Export to Anki
            anki_result = export_to_anki(
                note,
                output_path=output_path,
                deck_name=title,
                include_metadata=True
            )
            
            if anki_result.get("success"):
                logger.info(f"Successfully exported to Anki: {anki_result.get('output_path')}")
                print(f"Successfully exported to Anki: {anki_result.get('output_path')}")
            else:
                logger.error(f"Failed to export to Anki: {anki_result.get('error')}")
                print(f"Failed to export to Anki: {anki_result.get('error')}")
        
        else:
            logger.error(f"Unsupported export format: {args.format}")
            print(f"Unsupported export format: {args.format}")
    
    finally:
        # Close database connection
        db_manager.close()


def handle_search_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'search' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info(f"Searching for notes with query: {args.query}")
    
    # Get database path from config
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    # Create database manager
    db_manager = DatabaseManager(db_path)
    
    try:
        # Search for notes
        results = db_manager.search_notes(
            query=args.query,
            tags=args.tags,
            limit=args.limit
        )
        
        # Display results
        if results:
            print(f"\nFound {len(results)} matching notes:\n")
            
            for i, note in enumerate(results, 1):
                # Format timestamp
                timestamp = note.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    formatted_date = timestamp
                
                # Format tags
                tags = note.get("tags", [])
                tags_str = ", ".join(tags) if tags else "No tags"
                
                # Display note info
                print(f"{i}. {note['title']}")
                print(f"   ID: {note['id']}")
                print(f"   Date: {formatted_date}")
                print(f"   Tags: {tags_str}")
                
                # Display summary if available
                summary = note.get("summary", "")
                if summary:
                    # Truncate summary if too long
                    if len(summary) > 200:
                        summary = summary[:197] + "..."
                    print(f"   Summary: {summary}")
                
                print()
            
            # Display usage hint
            print("To view a note, use: python main.py export --id <note_id> --format <format>")
        else:
            print(f"No notes found matching query: {args.query}")
            if args.tags:
                print(f"with tags: {', '.join(args.tags)}")
    
    finally:
        # Close database connection
        db_manager.close()


def handle_semantic_search_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'search_pansophy' command for semantic search using embeddings.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info(f"Performing semantic search with query: {args.query}")
    
    # Get database path from config
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    # Get embedding model from config
    embedding_model = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Create embedder
    try:
        embedder = Embedder(db_path, model_name=embedding_model)
        
        # Check if we need to update embeddings for all notes
        if config.get("UPDATE_EMBEDDINGS_ON_SEARCH", False):
            print("Updating embeddings for all notes...")
            success_count, fail_count = embedder.update_embeddings_for_all_notes()
            print(f"Updated embeddings for {success_count} notes, {fail_count} failed")
        
        # Perform semantic search
        print(f"Searching for notes semantically similar to: '{args.query}'")
        print(f"Using embedding model: {embedding_model}")
        print(f"Similarity threshold: {args.threshold}")
        
        results = embedder.search_notes_by_embedding(
            query_text=args.query,
            limit=args.limit,
            threshold=args.threshold,
            filter_tags=args.tags
        )
        
        # Display results
        if results:
            print(f"\nFound {len(results)} semantically similar notes:\n")
            
            for i, note in enumerate(results, 1):
                # Format timestamp
                timestamp = note.get("timestamp", "")
                try:
                    dt = datetime.fromisoformat(timestamp)
                    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    formatted_date = timestamp
                
                # Format tags
                tags = note.get("tags", [])
                tags_str = ", ".join(tags) if tags else "No tags"
                
                # Format similarity score
                similarity = note.get("similarity", 0.0)
                similarity_str = f"{similarity:.2f}"
                
                # Display note info
                print(f"{i}. {note['title']} (Similarity: {similarity_str})")
                print(f"   ID: {note['id']}")
                print(f"   Date: {formatted_date}")
                print(f"   Tags: {tags_str}")
                
                # Display summary if available
                summary = note.get("summary", "")
                if summary:
                    # Truncate summary if too long
                    if len(summary) > 200:
                        summary = summary[:197] + "..."
                    print(f"   Summary: {summary}")
                
                print()
            
            # Display usage hint
            print("To view a note, use: python main.py export --id <note_id> --format <format>")
        else:
            print(f"No notes found semantically similar to: {args.query}")
            if args.tags:
                print(f"with tags: {', '.join(args.tags)}")
            print(f"Try lowering the similarity threshold (current: {args.threshold})")
    
    except ImportError as e:
        logger.error(f"Error importing embedding modules: {e}")
        print(f"Error: {e}")
        print("Make sure all required dependencies are installed:")
        print("  pip install -r requirements.txt")
    
    except Exception as e:
        logger.error(f"Error performing semantic search: {e}")
        print(f"Error: {e}")


def handle_graph_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'graph' command for generating a hierarchical knowledge graph.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info("Generating hierarchical knowledge graph")
    
    # Get database path from config
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    # Create database manager
    db_manager = DatabaseManager(db_path)
    
    try:
        # Determine output path
        output_dir = config.get("EXPORT_DIR", "../exports")
        if not os.path.isabs(output_dir):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
        
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename if not provided
        if args.output:
            output_path = args.output
            if not os.path.isabs(output_path):
                output_path = os.path.join(output_dir, output_path)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if args.format == "html":
                output_path = os.path.join(output_dir, f"knowledge_graph_{timestamp}.html")
            else:
                output_path = os.path.join(output_dir, f"knowledge_graph_{timestamp}.{args.format}")
        
        # Print information about the graph generation
        print(f"Generating knowledge graph with {args.layout} layout")
        if args.tags:
            print(f"Filtering by tags: {', '.join(args.tags)}")
        print(f"Maximum nodes: {args.max_nodes}")
        print(f"Similarity threshold: {args.threshold}")
        print(f"Output format: {args.format}")
        print(f"Output path: {output_path}")
        
        # Generate the knowledge graph
        if args.format == "html":
            # Extract graph data from database
            graph_data = extract_graph_data_from_db(
                db_manager,
                max_nodes=args.max_nodes,
                similarity_threshold=args.threshold,
                tags=args.tags
            )
            
            # Generate HTML knowledge graph
            result = generate_html_knowledge_graph(
                graph_data,
                output_path=output_path,
                title=args.title,
                open_browser=args.open
            )
        else:
            # Generate Graphviz knowledge graph
            result = generate_knowledge_graph(
                db_manager,
                output_format=args.format,
                output_path=output_path,
                title=args.title,
                layout=args.layout,
                is_3d=not args.no_3d,
                max_nodes=args.max_nodes,
                similarity_threshold=args.threshold,
                tags=args.tags,
                open_browser=args.open
            )
        
        # Display results
        if "error" in result:
            print(f"Error generating knowledge graph: {result['error']}")
        else:
            print(f"\nKnowledge graph generated successfully:")
            print(f"  Nodes: {result.get('node_count', 0)}")
            print(f"  Edges: {result.get('edge_count', 0)}")
            print(f"  Output: {result.get('output_path', output_path)}")
            
            if args.open and args.format != "html":  # HTML version opens browser automatically
                print("Opening graph in browser...")
    
    except ImportError as e:
        logger.error(f"Error importing required modules: {e}")
        print(f"Error: {e}")
        print("Make sure all required dependencies are installed:")
        print("  pip install -r requirements.txt")
    
    except Exception as e:
        logger.error(f"Error generating knowledge graph: {e}")
        print(f"Error: {e}")
    
    finally:
        # Close database connection
        db_manager.close()


def handle_pansophy_ask_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'pansophy_ask' command for retrieval-augmented Q&A.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info(f"Processing question: {args.query}")
    
    # Get database path from config
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    # Create database manager
    db_manager = DatabaseManager(db_path)
    
    # Get embedding model from config
    embedding_model = config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    try:
        # Create embedder
        embedder = Embedder(db_path, model_name=embedding_model)
        
        # Print information about the question
        print(f"\nQuestion: {args.query}")
        print(f"Using model: {args.model}")
        print(f"Searching for relevant notes...")
        
        # Ask the question
        result = ask_question(
            query=args.query,
            db_manager=db_manager,
            embedder=embedder,
            model=args.model,
            max_results=args.limit,
            threshold=args.threshold,
            filter_tags=args.tags,
            include_sources=not args.no_sources
        )
        
        # Display the answer
        print("\n" + "="*80)
        print("ANSWER:")
        print("="*80)
        print(result["answer"])
        print()
        
        # Display sources if available
        if "sources" in result and result["sources"]:
            print("SOURCES:")
            for source in result["sources"]:
                print(f"- {source['title']} (ID: {source['id']}, Similarity: {source['similarity']:.2f})")
            print()
            
            # Display usage hint
            print("To view a source note, use: python main.py export --id <note_id> --format <format>")
        
    except ImportError as e:
        logger.error(f"Error importing required modules: {e}")
        print(f"Error: {e}")
        print("Make sure all required dependencies are installed:")
        print("  pip install -r requirements.txt")
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        print(f"Error: {e}")
    
    finally:
        # Close database connection
        db_manager.close()


def handle_reminders_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'reminders' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Process reminders command
    if args.reminders_command == "schedule":
        # Schedule a reminder
        item_id = args.id
        item_type = args.type
        reminder_time = args.time
        channels = args.channels
        
        # Get database manager
        db_manager = get_db_manager(config)
        
        # Schedule the reminder
        result = schedule_reminder(
            item_id=item_id,
            item_type=item_type,
            reminder_time=reminder_time,
            channels=channels,
            db_manager=db_manager,
            config=config
        )
        
        if "error" in result:
            logger.error(f"Error scheduling reminder: {result['error']}")
            print(f"Error scheduling reminder: {result['error']}")
        else:
            logger.info(f"Reminder scheduled for {item_type} {item_id} at {reminder_time}")
            print(f"Reminder scheduled for {item_type} {item_id} at {reminder_time}")
            print(f"Notification channels: {', '.join(channels)}")
    
    elif args.reminders_command == "list":
        # List reminders
        item_id = args.id
        item_type = args.type
        status = args.status
        limit = args.limit
        
        # Get database manager
        db_manager = get_db_manager(config)
        
        # Get reminders
        reminders = get_reminders(
            item_id=item_id,
            item_type=item_type,
            status=status,
            limit=limit,
            db_manager=db_manager,
            config=config
        )
        
        if not reminders:
            print("No reminders found.")
            return
        
        # Print reminders
        print(f"Reminders ({len(reminders)}):")
        for reminder in reminders:
            item_id = reminder.get("item_id", "")
            item_type = reminder.get("item_type", "")
            reminder_time = reminder.get("reminder_time", "")
            status = reminder.get("status", "")
            channels = reminder.get("channels", [])
            
            print(f"  {item_type} {item_id}: {reminder_time} [{status}]")
            print(f"    Channels: {', '.join(channels)}")
            
            # Print metadata if available
            if "metadata" in reminder:
                print(f"    Metadata: {json.dumps(reminder['metadata'])}")
            
            print()
    
    elif args.reminders_command == "start-scheduler":
        # Start the reminder scheduler
        
        # Get database manager
        db_manager = get_db_manager(config)
        
        # Start the scheduler
        result = start_reminder_scheduler(
            db_manager=db_manager,
            config=config
        )
        
        if result:
            logger.info("Reminder scheduler started")
            print("Reminder scheduler started")
        else:
            logger.error("Failed to start reminder scheduler")
            print("Failed to start reminder scheduler")
    
    elif args.reminders_command == "stop-scheduler":
        # Stop the reminder scheduler
        
        # Get database manager
        db_manager = get_db_manager(config)
        
        # Stop the scheduler
        result = stop_reminder_scheduler(
            db_manager=db_manager,
            config=config
        )
        
        if result:
            logger.info("Reminder scheduler stopped")
            print("Reminder scheduler stopped")
        else:
            logger.error("Failed to stop reminder scheduler")
            print("Failed to stop reminder scheduler")
    
    else:
        print("Unknown reminders command. Use 'reminders schedule', 'reminders list', 'reminders start-scheduler', or 'reminders stop-scheduler'.")


def handle_math_formula_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle math_formula command to process math formulas in content.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info("Processing math formulas in content")
    
    # Get arguments
    input_path = args.input
    output_path = args.output
    ocr_math = not args.no_ocr
    link_explanations = not args.no_link
    generate_practice = not args.no_practice
    render_formulas = args.render
    render_dir = args.render_dir
    
    # Check if input is a file
    if not os.path.isfile(input_path):
        logger.error(f"Input file not found: {input_path}")
        print(f"Error: Input file not found: {input_path}")
        return
    
    # Process input
    if input_path.lower().endswith((".json")):
        # Process JSON file
        try:
            with open(input_path, "r") as f:
                content = json.load(f)
            
            # Process math formulas
            processed_content = process_math_formulas(
                content,
                ocr_math=ocr_math,
                link_explanations=link_explanations,
                generate_practice=generate_practice
            )
            
            # Render formulas as images if requested
            if render_formulas and "math_formulas" in processed_content:
                render_directory = render_dir or os.path.join(os.path.dirname(input_path), "rendered_formulas")
                os.makedirs(render_directory, exist_ok=True)
                
                for i, formula in enumerate(processed_content["math_formulas"]):
                    latex = formula.get("latex", "")
                    if latex:
                        output_image_path = os.path.join(render_directory, f"formula_{i+1}.png")
                        from processing.math_formula_processor import render_formula_as_image
                        image_path = render_formula_as_image(latex, output_image_path)
                        if image_path:
                            formula["rendered_image"] = image_path
                
                logger.info(f"Rendered {len(processed_content['math_formulas'])} formulas to {render_directory}")
                print(f"Rendered {len(processed_content['math_formulas'])} formulas to {render_directory}")
            
            # Save processed content
            if not output_path:
                output_path = f"{os.path.splitext(input_path)[0]}_math.json"
            
            with open(output_path, "w") as f:
                json.dump(processed_content, f, indent=2)
            
            logger.info(f"Processed content saved to {output_path}")
            print(f"Processed content saved to {output_path}")
            
            # Print summary
            if "math_formulas" in processed_content:
                formulas = processed_content["math_formulas"]
                print(f"\nDetected {len(formulas)} math formulas:")
                for i, formula in enumerate(formulas[:5]):  # Show first 5 formulas
                    latex = formula.get("latex", "")
                    confidence = formula.get("confidence", 0.0)
                    has_explanation = "explanation" in formula
                    print(f"  {i+1}. LaTeX: {latex[:50]}{'...' if len(latex) > 50 else ''}")
                    print(f"     Confidence: {confidence:.2f}")
                    print(f"     Has explanation: {'Yes' if has_explanation else 'No'}")
                
                if len(formulas) > 5:
                    print(f"  ... and {len(formulas) - 5} more formulas")
                
                if "math_practice" in processed_content:
                    practice = processed_content["math_practice"]
                    print(f"\nGenerated {len(practice)} practice problems")
            
        except Exception as e:
            logger.error(f"Error processing JSON file: {str(e)}")
            print(f"Error processing JSON file: {str(e)}")
            
    else:
        # Process image file
        try:
            # Detect math formulas in image
            formulas = detect_math_formulas(input_path)
            
            if not formulas:
                logger.warning("No math formulas detected in the image")
                print("No math formulas detected in the image")
                return
            
            # Save formulas
            if not output_path:
                output_path = f"{os.path.splitext(input_path)[0]}_formulas.json"
            
            with open(output_path, "w") as f:
                json.dump({"math_formulas": formulas}, f, indent=2)
            
            logger.info(f"Detected {len(formulas)} formulas, saved to {output_path}")
            print(f"Detected {len(formulas)} formulas, saved to {output_path}")
            
            # Print formulas
            print("\nDetected formulas:")
            for i, formula in enumerate(formulas[:5]):  # Show first 5 formulas
                latex = formula.get("latex", "")
                confidence = formula.get("confidence", 0.0)
                print(f"  {i+1}. LaTeX: {latex[:50]}{'...' if len(latex) > 50 else ''}")
                print(f"     Confidence: {confidence:.2f}")
            
            if len(formulas) > 5:
                print(f"  ... and {len(formulas) - 5} more formulas")
            
            # Render formulas as images if requested
            if render_formulas:
                render_directory = render_dir or os.path.join(os.path.dirname(input_path), "rendered_formulas")
                os.makedirs(render_directory, exist_ok=True)
                
                for i, formula in enumerate(formulas):
                    latex = formula.get("latex", "")
                    if latex:
                        output_image_path = os.path.join(render_directory, f"formula_{i+1}.png")
                        from processing.math_formula_processor import render_formula_as_image
                        image_path = render_formula_as_image(latex, output_image_path)
                        if image_path:
                            formula["rendered_image"] = image_path
                
                # Save updated formulas with rendered image paths
                with open(output_path, "w") as f:
                    json.dump({"math_formulas": formulas}, f, indent=2)
                
                logger.info(f"Rendered {len(formulas)} formulas to {render_directory}")
                print(f"Rendered {len(formulas)} formulas to {render_directory}")
            
        except Exception as e:
            logger.error(f"Error processing image file: {str(e)}")
            print(f"Error processing image file: {str(e)}")


def handle_pansophy_plan_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle pansophy_plan command to generate a personalized study plan.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info("Generating personalized study plan")
    
    # Get arguments
    user_id = args.user
    weeks = args.weeks
    hours_per_week = args.hours
    focus_areas = args.focus
    output_path = args.output
    
    # Get database manager
    db_manager = DatabaseManager(config.get("DATABASE_PATH", "../data/pansophy.db"))
    
    # Generate study plan
    study_plan = generate_study_plan(
        user_id=user_id,
        weeks=weeks,
        hours_per_week=hours_per_week,
        focus_areas=focus_areas,
        db_manager=db_manager
    )
    
    # Check if study plan was generated successfully
    if "error" in study_plan:
        logger.error(f"Error generating study plan: {study_plan['error']}")
        print(f"Error generating study plan: {study_plan['error']}")
        return
    
    # Save study plan if output path provided
    if output_path:
        result = save_study_plan(study_plan, output_path)
        if result["success"]:
            logger.info(f"Study plan saved to {output_path}")
            print(f"Study plan saved to {output_path}")
        else:
            logger.error(f"Error saving study plan: {result.get('error', 'Unknown error')}")
            print(f"Error saving study plan: {result.get('error', 'Unknown error')}")
    else:
        # Print study plan summary
        print(f"Study Plan for {user_id}")
        print(f"Generated at: {study_plan.get('generated_at', datetime.now().isoformat())}")
        print(f"Weeks: {weeks}")
        print(f"Hours per week: {study_plan.get('hours_per_week', 'Not specified')}")
        
        if focus_areas:
            print(f"Focus areas: {', '.join(focus_areas)}")
        
        # Print weekly plan
        weekly_plan = study_plan.get("weekly_plan", [])
        if weekly_plan:
            print("\nWeekly Plan:")
            for week in weekly_plan:
                week_num = week.get("week", 0)
                topics = week.get("topics", [])
                
                print(f"\nWeek {week_num}:")
                for topic in topics:
                    title = topic.get("title", "Untitled")
                    hours = topic.get("hours", 0)
                    focus_areas = topic.get("focus_areas", [])
                    
                    print(f"  - {title} ({hours} hours)")
                    if focus_areas:
                        print(f"    Focus on: {', '.join(focus_areas)}")
        else:
            print("\nNo weekly plan generated.")


def handle_research_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the research command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger.info(f"Researching topic: {args.topic}")
    
    # Get topic from arguments
    topic = args.topic
    
    # Get sources from arguments (if provided)
    sources = args.sources
    
    # Get max results per source from arguments
    max_results = args.max_results
    
    # Get output directory from arguments (if provided)
    output_dir = args.output_dir
    
    # Get visualization type from arguments (if provided)
    visualize = args.visualize
    
    # Get other options from arguments
    generate_flashcards = args.generate_flashcards
    generate_summary = args.generate_summary
    verbose = args.verbose
    
    # Create research agent
    research_agent = ResearchAgent(config)
    
    # Research the topic
    try:
        results = research_agent.research(
            topic=topic,
            sources=sources,
            max_results_per_source=max_results,
            download_dir=output_dir,
            verbose=verbose
        )
        
        # Print research results summary
        print(f"\nResearch Results for '{topic}':")
        print(f"Downloaded to: {results['download_dir']}")
        
        # Print sources used
        print("\nSources Used:")
        for source, used in results["sources_used"].items():
            if used:
                print(f"- {source}")
        
        # Print possible meanings if available
        if results.get("possible_meanings"):
            print("\nPossible Meanings:")
            for meaning in results["possible_meanings"]:
                print(f"- {meaning['meaning']}: {meaning['description']}")
        
        # Print results for each source
        for source, source_results in results["results"].items():
            if source_results.get("status") == "error":
                print(f"\n{source.capitalize()} Error: {source_results.get('message', 'Unknown error')}")
            elif source == "wikipedia" and "articles" in source_results:
                print(f"\nWikipedia Articles ({len(source_results['articles'])}):")
                for article in source_results["articles"]:
                    print(f"- {article['title']}")
                    if verbose and "summary" in article:
                        print(f"  Summary: {article['summary'][:100]}...")
            elif source == "arxiv" and "papers" in source_results:
                print(f"\nArXiv Papers ({len(source_results['papers'])}):")
                for paper in source_results["papers"]:
                    print(f"- {paper['title']}")
                    if verbose and "abstract" in paper:
                        print(f"  Abstract: {paper['abstract'][:100]}...")
            elif source == "semantic_scholar" and "papers" in source_results:
                print(f"\nSemantic Scholar Papers ({len(source_results['papers'])}):")
                for paper in source_results["papers"]:
                    print(f"- {paper['title']}")
                    if verbose and "abstract" in paper:
                        print(f"  Abstract: {paper['abstract'][:100]}...")
            elif source == "youtube" and "videos" in source_results:
                print(f"\nYouTube Videos ({len(source_results['videos'])}):")
                for video in source_results["videos"]:
                    print(f"- {video['title']}")
                    if verbose and "description" in video:
                        print(f"  Description: {video['description'][:100]}...")
            elif source == "github" and "repositories" in source_results:
                print(f"\nGitHub Repositories ({len(source_results['repositories'])}):")
                for repo in source_results["repositories"]:
                    print(f"- {repo['name']}: {repo['description']}")
            elif source == "web" and "pages" in source_results:
                print(f"\nWeb Pages ({len(source_results['pages'])}):")
                for page in source_results["pages"]:
                    print(f"- {page['title']}: {page['url']}")
        
        # Generate visualizations if requested
        if visualize:
            print(f"\nGenerating {visualize} visualization...")
            # Placeholder for visualization generation
            print(f"Visualization not yet implemented.")
        
        # Generate flashcards if requested
        if generate_flashcards:
            print("\nGenerating flashcards...")
            # Placeholder for flashcard generation
            print("Flashcard generation not yet implemented.")
        
        # Generate summary if requested
        if generate_summary:
            print("\nGenerating summary...")
            # Placeholder for summary generation
            print("Summary generation not yet implemented.")
        
        print(f"\nResearch completed for '{topic}'.")
        
    except Exception as e:
        logger.error(f"Error researching topic: {e}")
        print(f"Error researching topic: {e}")


def handle_plugins_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'plugins' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Get plugin manager
    plugin_manager = get_plugin_manager()
    
    # Process plugins command
    if args.plugins_command == "list":
        # List plugins
        if args.loaded:
            # List loaded plugins
            plugins_info = plugin_manager.get_plugin_info()
            
            if not plugins_info:
                print("No plugins are currently loaded.")
                return
            
            # Filter by type if specified
            if args.type != "all":
                plugins_info = [p for p in plugins_info if p["type"] == args.type]
            
            # Print plugins
            print(f"Loaded plugins ({len(plugins_info)}):")
            for plugin in plugins_info:
                print(f"  {plugin['id']}: {plugin['name']} v{plugin['version']} ({plugin['type']})")
                print(f"    Description: {plugin['description']}")
                print(f"    Author: {plugin['author']}")
                if plugin['dependencies']:
                    print(f"    Dependencies: {', '.join(plugin['dependencies'])}")
                print()
                
        else:
            # Discover available plugins
            plugin_classes = plugin_manager.discover_plugins()
            
            if not plugin_classes:
                print("No plugins found.")
                return
            
            # Create temporary instances to get plugin info
            plugins_info = []
            for pid, plugin_class in plugin_classes.items():
                try:
                    plugin = plugin_class()
                    plugins_info.append({
                        "id": pid,
                        "name": plugin.name,
                        "version": plugin.version,
                        "description": plugin.description,
                        "author": plugin.author,
                        "type": plugin.plugin_type,
                        "dependencies": plugin.dependencies,
                        "loaded": pid in plugin_manager.plugins
                    })
                except Exception as e:
                    logger.warning(f"Error creating plugin instance for {pid}: {e}")
            
            # Filter by type if specified
            if args.type != "all":
                plugins_info = [p for p in plugins_info if p["type"] == args.type]
            
            # Print plugins
            print(f"Available plugins ({len(plugins_info)}):")
            for plugin in plugins_info:
                status = "[LOADED]" if plugin.get("loaded", False) else "[AVAILABLE]"
                print(f"  {plugin['id']}: {plugin['name']} v{plugin['version']} ({plugin['type']}) {status}")
                print(f"    Description: {plugin['description']}")
                print(f"    Author: {plugin['author']}")
                if plugin['dependencies']:
                    print(f"    Dependencies: {', '.join(plugin['dependencies'])}")
                print()
    
    elif args.plugins_command == "load":
        # Load plugin
        plugin_id = args.plugin_id
        plugin = plugin_manager.load_plugin(plugin_id, config)
        
        if plugin:
            print(f"Plugin loaded: {plugin.name} v{plugin.version} ({plugin.plugin_type})")
        else:
            print(f"Failed to load plugin: {plugin_id}")
    
    elif args.plugins_command == "unload":
        # Unload plugin
        plugin_id = args.plugin_id
        success = plugin_manager.unload_plugin(plugin_id)
        
        if success:
            print(f"Plugin unloaded: {plugin_id}")
        else:
            print(f"Failed to unload plugin: {plugin_id}")
    
    elif args.plugins_command == "add-dir":
        # Add plugin directory
        directory = args.directory
        plugin_manager.add_plugin_dir(directory)
        
        print(f"Added plugin directory: {directory}")
        
        # Discover plugins in the new directory
        plugin_classes = plugin_manager.discover_plugins()
        print(f"Discovered {len(plugin_classes)} plugins")
    
    else:
        print("Unknown plugins command. Use 'plugins list', 'plugins load', 'plugins unload', or 'plugins add-dir'.")


def handle_image_mindmap_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'image_mindmap' command for generating interactive mind maps with images.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    logger.info(f"Generating image mind map from {args.type} source: {args.input}")
    
    try:
        # Validate input file
        if not os.path.exists(args.input):
            logger.error(f"Input file not found: {args.input}")
            print(f"Error: Input file not found: {args.input}")
            return
        
        # Determine output path
        if args.output:
            output_path = args.output
            if not os.path.isabs(output_path):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                output_path = os.path.abspath(os.path.join(current_dir, output_path))
        else:
            # Generate default output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = config.get("EXPORT_DIR", "../exports")
            if not os.path.isabs(output_dir):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                output_dir = os.path.abspath(os.path.join(current_dir, output_dir))
            
            # Ensure directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Create output filename
            input_basename = os.path.basename(args.input)
            name_without_ext = os.path.splitext(input_basename)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}_mindmap_{timestamp}.html")
        
        # Print information about the mind map generation
        print(f"Generating image mind map from {args.type} source: {args.input}")
        print(f"Output path: {output_path}")
        print(f"Theme: {args.theme}")
        
        # Process the input file to extract text
        content = {}
        
        if args.type == "pdf":
            from inputs.pdf_input import extract_text_from_pdf
            text = extract_text_from_pdf(args.input)
            content = {
                "text": text,
                "title": args.title or os.path.basename(args.input)
            }
        elif args.type == "slides":
            # For slides, we'll use a simple text extraction for now
            # In a real implementation, this would use a more sophisticated method
            from inputs.pdf_input import extract_text_from_pdf
            text = extract_text_from_pdf(args.input)
            content = {
                "text": text,
                "title": args.title or os.path.basename(args.input)
            }
        elif args.type == "video":
            from inputs.youtube_input import process_youtube_video
            # Check if it's a YouTube URL
            if args.input.startswith(("http://", "https://")) and "youtube.com" in args.input:
                content = process_youtube_video(args.input)
            else:
                # For local video files, we don't have text extraction yet
                # In a real implementation, this would use speech recognition
                content = {
                    "text": "Video content",
                    "title": args.title or os.path.basename(args.input)
                }
        
        # Generate the image mind map
        from visualization import process_source_for_image_mindmap
        
        result = process_source_for_image_mindmap(
            source_path=args.input,
            source_type=args.type,
            content=content,
            output_path=output_path,
            title=args.title or content.get("title", "Image Mind Map"),
            theme=args.theme,
            open_browser=args.open
        )
        
        # Display results
        if not result.get("success", False):
            print(f"Error generating image mind map: {result.get('error', 'Unknown error')}")
        else:
            print(f"\nImage mind map generated successfully:")
            print(f"  Output: {result.get('output_path', output_path)}")
            
            if args.open:
                print("Opening mind map in browser...")
    
    except ImportError as e:
        logger.error(f"Error importing required modules: {e}")
        print(f"Error: {e}")
        print("Make sure all required dependencies are installed:")
        print("  pip install -r requirements.txt")
    
    except Exception as e:
        logger.error(f"Error generating image mind map: {e}")
        print(f"Error: {e}")


def handle_review_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'review' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Get database path from config
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    # Create database manager
    db_manager = DatabaseManager(db_path)
    
    try:
        if args.id:
            # Review a specific note
            logger.info(f"Reviewing note with ID: {args.id}")
            note = db_manager.get_note(int(args.id))
            
            if not note:
                logger.error(f"Note with ID {args.id} not found")
                print(f"Note with ID {args.id} not found")
                return
            
            # Display the note for review
            _display_note_for_review(note)
            
            # Get user's quality rating
            quality = _get_quality_rating()
            
            # Schedule next review based on quality
            if db_manager.schedule_review(int(args.id), quality):
                logger.info(f"Scheduled next review for note {args.id}")
                print("Review recorded and next review scheduled.")
            else:
                logger.error(f"Failed to schedule review for note {args.id}")
                print("Failed to schedule review.")
                
        elif args.due:
            # Show notes due for review
            logger.info("Retrieving notes due for review")
            due_notes = db_manager.get_due_reviews()
            
            if not due_notes:
                print("No notes are due for review.")
                return
            
            print(f"\nYou have {len(due_notes)} notes due for review:\n")
            
            for i, note in enumerate(due_notes, 1):
                # Format last reviewed date
                last_reviewed = note.get("last_reviewed", "Never")
                if last_reviewed != "Never":
                    try:
                        dt = datetime.fromisoformat(last_reviewed)
                        last_reviewed = dt.strftime("%Y-%m-%d %H:%M")
                    except (ValueError, TypeError):
                        pass
                
                # Display note info
                print(f"{i}. {note['title']}")
                print(f"   ID: {note['id']}")
                print(f"   Last reviewed: {last_reviewed}")
                print(f"   Review count: {note.get('review_count', 0)}")
                print()
            
            # Ask which note to review
            note_index = _get_note_index_to_review(len(due_notes))
            
            if note_index is not None:
                # Get the selected note
                selected_note_id = due_notes[note_index]['id']
                # Call the review command recursively with the selected note ID
                args.id = selected_note_id
                args.due = False
                handle_review_command(args, config)
        else:
            # No specific action specified
            print("Please specify a note ID to review or use --due to see notes due for review.")
            print("Usage: python main.py review --id <note_id>")
            print("       python main.py review --due")
    
    finally:
        # Close database connection
        db_manager.close()

def _display_note_for_review(note: Dict[str, Any]) -> None:
    """
    Display a note for review.
    
    Args:
        note (Dict[str, Any]): The note to display
    """
    print("\n" + "="*80)
    print(f"REVIEWING: {note['title']}")
    print("="*80 + "\n")
    
    # Display summary if available
    if "summary" in note and note["summary"]:
        print("SUMMARY:")
        print(note["summary"])
        print()
    
    # Display key points if available
    if "keypoints" in note and note["keypoints"]:
        print("KEY POINTS:")
        for i, point in enumerate(note["keypoints"], 1):
            if isinstance(point, dict) and "content" in point:
                print(f"{i}. {point['content']}")
            else:
                print(f"{i}. {point}")
        print()
    
    # Display questions if available
    if "questions" in note and note["questions"]:
        print("QUESTIONS:")
        for i, question in enumerate(note["questions"], 1):
            if isinstance(question, dict):
                q_text = question.get("question", "")
                answer = question.get("answer", "")
                
                print(f"Q{i}: {q_text}")
                input("Press Enter to see the answer...")
                print(f"A{i}: {answer}")
                print()
    
    # If no summary, key points, or questions, show the text
    if (not note.get("summary") and not note.get("keypoints") and 
            not note.get("questions") and note.get("text")):
        print("TEXT:")
        # Show only the first 500 characters if text is long
        text = note["text"]
        if len(text) > 500:
            print(text[:500] + "...\n(text truncated)")
        else:
            print(text)
        print()

def _get_quality_rating() -> int:
    """
    Get the user's quality rating for a review.
    
    Returns:
        int: Quality rating (0-5)
    """
    print("\nRate your recall quality (0-5):")
    print("0: Complete blackout, didn't remember at all")
    print("1: Wrong answer, but recognized the correct answer")
    print("2: Wrong answer, but correct answer felt familiar")
    print("3: Correct answer, but required significant effort")
    print("4: Correct answer after hesitation")
    print("5: Perfect recall, answered easily")
    
    while True:
        try:
            rating = int(input("\nYour rating (0-5): "))
            if 0 <= rating <= 5:
                return rating
            else:
                print("Please enter a number between 0 and 5.")
        except ValueError:
            print("Please enter a valid number.")

def _get_note_index_to_review(num_notes: int) -> Optional[int]:
    """
    Get the index of the note to review from user input.
    
    Args:
        num_notes (int): Number of notes available for review
        
    Returns:
        Optional[int]: Zero-based index of the note to review, or None to cancel
    """
    while True:
        try:
            choice = input(f"\nEnter note number to review (1-{num_notes}) or 'q' to quit: ")
            
            if choice.lower() == 'q':
                return None
                
            index = int(choice) - 1
            if 0 <= index < num_notes:
                return index
            else:
                print(f"Please enter a number between 1 and {num_notes}.")
        except ValueError:
            print("Please enter a valid number or 'q' to quit.")


def handle_config_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle the 'config' command.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Get config file path
    config_file = os.environ.get("CONFIG_FILE", "config/config.yaml")
    if not os.path.isabs(config_file):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.abspath(os.path.join(current_dir, config_file))
    
    if args.view:
        # View configuration
        print("\nCurrent Configuration:")
        print("=====================")
        
        # Format the output for better readability
        max_key_length = max(len(key) for key in config.keys())
        
        for key, value in sorted(config.items()):
            # Format the value based on its type
            if isinstance(value, dict):
                import json
                value_str = json.dumps(value)
            elif isinstance(value, list):
                value_str = ", ".join(str(item) for item in value)
            else:
                value_str = str(value)
            
            # Truncate long values
            if len(value_str) > 60:
                value_str = value_str[:57] + "..."
            
            # Print the key-value pair
            print(f"{key.ljust(max_key_length)} : {value_str}")
    
    elif args.edit:
        # Edit configuration
        key, value = args.edit
        
        if key in config:
            # Convert value to appropriate type based on existing value
            original_type = type(config[key])
            
            try:
                if original_type == bool:
                    # Handle boolean values
                    if value.lower() in ("true", "yes", "1", "y"):
                        typed_value = True
                    elif value.lower() in ("false", "no", "0", "n"):
                        typed_value = False
                    else:
                        raise ValueError(f"Invalid boolean value: {value}")
                elif original_type == int:
                    typed_value = int(value)
                elif original_type == float:
                    typed_value = float(value)
                elif original_type == list:
                    # Split by commas for lists
                    typed_value = [item.strip() for item in value.split(",")]
                else:
                    # Default to string
                    typed_value = value
                
                # Update the config
                old_value = config[key]
                config[key] = typed_value
                
                # Save the updated config
                if _save_config(config, config_file):
                    logger.info(f"Updated config: {key}={typed_value}")
                    print(f"Updated {key}: {old_value} -> {typed_value}")
                else:
                    logger.error(f"Failed to save config to {config_file}")
                    print(f"Failed to save config to {config_file}")
            except (ValueError, TypeError) as e:
                logger.error(f"Error converting value: {e}")
                print(f"Error: {e}")
                print(f"Expected type: {original_type.__name__}")
        else:
            # Key doesn't exist, ask if user wants to add it
            add_new = input(f"Key '{key}' doesn't exist. Add it as a new setting? (y/n): ")
            
            if add_new.lower() in ("y", "yes"):
                # Add new key with string value
                config[key] = value
                
                # Save the updated config
                if _save_config(config, config_file):
                    logger.info(f"Added new config: {key}={value}")
                    print(f"Added new setting: {key}={value}")
                else:
                    logger.error(f"Failed to save config to {config_file}")
                    print(f"Failed to save config to {config_file}")
            else:
                print("Operation cancelled.")
    else:
        # No action specified, show help
        print("Please specify an action: --view or --edit")
        print("Usage: python main.py config --view")
        print("       python main.py config --edit KEY VALUE")

def _save_config(config: Dict[str, Any], config_file: str) -> bool:
    """
    Save configuration to file.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        config_file (str): Path to the configuration file
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger("ai_note_system.main")
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(config_file)), exist_ok=True)
        
        # Save to YAML file
        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False


def handle_motivation_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle motivation tracking commands.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Get database manager
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    db_manager = DatabaseManager(db_path)
    
    try:
        if args.motivation_command == "track":
            # Track motivation
            level = args.level
            notes = args.notes
            tags = args.tags
            activity_type = args.activity_type
            duration_minutes = args.duration
            energy_level = args.energy_level
            focus_level = args.focus_level
            stress_level = args.stress_level
            sleep_hours = args.sleep_hours
            
            # Track motivation
            motivation_id = track_motivation(
                db_manager=db_manager,
                level=level,
                notes=notes,
                tags=tags,
                activity_type=activity_type,
                duration_minutes=duration_minutes,
                energy_level=energy_level,
                focus_level=focus_level,
                stress_level=stress_level,
                sleep_hours=sleep_hours
            )
            
            logger.info(f"Tracked motivation level {level} with ID {motivation_id}")
            print(f"Tracked motivation level {level} with ID {motivation_id}")
            
        elif args.motivation_command == "track_performance":
            # Track performance
            activity_type = args.activity_type
            score = args.score
            duration_minutes = args.duration
            note_id = args.note_id
            motivation_id = args.motivation_id
            
            # Track performance
            performance_id = track_performance(
                db_manager=db_manager,
                activity_type=activity_type,
                score=score,
                duration_minutes=duration_minutes,
                note_id=note_id,
                motivation_id=motivation_id
            )
            
            logger.info(f"Tracked performance score {score} for {activity_type} with ID {performance_id}")
            print(f"Tracked performance score {score} for {activity_type} with ID {performance_id}")
            
        elif args.motivation_command == "view_history":
            # View motivation history
            period_days = args.period
            activity_type = args.activity_type
            tags = args.tags
            
            # Get motivation history
            history = get_motivation_history(
                db_manager=db_manager,
                period_days=period_days,
                activity_type=activity_type,
                tags=tags
            )
            
            if not history:
                print(f"No motivation entries found for the past {period_days} days.")
                return
            
            # Print motivation history
            print(f"Motivation History (past {period_days} days):")
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', '')
                level = entry.get('level', '')
                notes = entry.get('notes', '')
                tags = entry.get('tags', [])
                activity_type = entry.get('activity_type', '')
                
                print(f"{i}. {timestamp}: Level {level}/10")
                
                if activity_type:
                    print(f"   Activity: {activity_type}")
                
                if tags:
                    print(f"   Tags: {', '.join(tags)}")
                
                if notes:
                    print(f"   Notes: {notes}")
                
                print()
            
        elif args.motivation_command == "correlate":
            # Correlate motivation with performance
            period_days = args.period
            
            # Get correlation data
            correlation_data = correlate_motivation_performance(
                db_manager=db_manager,
                period_days=period_days
            )
            
            if correlation_data.get('correlation') is None:
                print(f"Not enough data to calculate correlation for the past {period_days} days.")
                return
            
            # Print correlation data
            correlation = correlation_data.get('correlation', 0)
            print(f"Motivation-Performance Correlation (past {period_days} days): {correlation:.2f}")
            
            # Print additional statistics
            motivation_stats = correlation_data.get('motivation_stats', {})
            performance_stats = correlation_data.get('performance_stats', {})
            
            print("\nMotivation Statistics:")
            print(f"  Mean: {motivation_stats.get('mean', 0):.2f}")
            print(f"  Median: {motivation_stats.get('median', 0):.2f}")
            print(f"  Min: {motivation_stats.get('min', 0):.2f}")
            print(f"  Max: {motivation_stats.get('max', 0):.2f}")
            
            print("\nPerformance Statistics:")
            print(f"  Mean: {performance_stats.get('mean', 0):.2f}")
            print(f"  Median: {performance_stats.get('median', 0):.2f}")
            print(f"  Min: {performance_stats.get('min', 0):.2f}")
            print(f"  Max: {performance_stats.get('max', 0):.2f}")
            
            # Print interpretation
            print("\nInterpretation:")
            if correlation > 0.7:
                print("  Strong positive correlation: Your performance strongly depends on your motivation level.")
            elif correlation > 0.3:
                print("  Moderate positive correlation: Your performance tends to increase with higher motivation.")
            elif correlation > -0.3:
                print("  Weak or no correlation: Your performance doesn't seem to depend much on your motivation level.")
            elif correlation > -0.7:
                print("  Moderate negative correlation: Your performance tends to decrease with higher motivation (unusual).")
            else:
                print("  Strong negative correlation: Your performance strongly decreases with higher motivation (very unusual).")
            
        elif args.motivation_command == "insights":
            # Generate motivation insights
            insights_data = generate_motivation_insights(db_manager=db_manager)
            
            if not insights_data.get('insights'):
                print("Not enough data to generate insights. Track more motivation data for better insights.")
                return
            
            # Print insights
            print("Motivation Insights:")
            for i, insight in enumerate(insights_data.get('insights', []), 1):
                print(f"{i}. {insight.get('message', '')}")
            
            # Print day of week analysis
            day_analysis = insights_data.get('day_of_week_analysis', [])
            if day_analysis:
                print("\nMotivation by Day of Week:")
                for day_data in day_analysis:
                    day = day_data.get('day', '')
                    avg = day_data.get('average_motivation', 0)
                    samples = day_data.get('sample_size', 0)
                    print(f"  {day}: {avg:.2f}/10 (based on {samples} entries)")
            
        elif args.motivation_command == "strategy":
            # Generate study strategy
            strategy_data = generate_study_strategy(db_manager=db_manager)
            
            if not strategy_data.get('strategies'):
                print(strategy_data.get('message', "Not enough data to generate personalized study strategies."))
                print("Track more motivation and performance data for better recommendations.")
                return
            
            # Print strategies
            print("Personalized Study Strategies:")
            for i, strategy in enumerate(strategy_data.get('strategies', []), 1):
                print(f"{i}. {strategy.get('message', '')}")
            
            # Print insights if available
            insights = strategy_data.get('insights', [])
            if insights:
                print("\nBased on these insights:")
                for i, insight in enumerate(insights, 1):
                    print(f"  - {insight.get('message', '')}")
        
        else:
            print("Unknown motivation command. Use one of: track, track_performance, view_history, correlate, insights, strategy")
    
    finally:
        # Close database connection
        db_manager.close()


def handle_citation_command(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """
    Handle citation commands.
    
    Args:
        args (argparse.Namespace): Command line arguments
        config (Dict[str, Any]): Configuration dictionary
    """
    logger = logging.getLogger("ai_note_system.main")
    
    # Get database manager
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    db_manager = DatabaseManager(db_path)
    
    try:
        if args.citation_command == "add_source":
            # Add source to note
            note_id = args.note_id
            source_type = args.source_type
            
            # Prepare source metadata
            source_metadata = {
                "title": args.title,
                "authors": args.authors,
                "year": args.year,
                "url": args.url,
                "publisher": args.publisher,
                "journal": args.journal,
                "volume": args.volume,
                "issue": args.issue,
                "pages": args.pages,
                "doi": args.doi
            }
            
            # Filter out None values
            source_metadata = {k: v for k, v in source_metadata.items() if v is not None}
            
            # Add source
            source_id = add_source(db_manager, note_id, source_type, **source_metadata)
            
            logger.info(f"Added source {source_id} to note {note_id}")
            print(f"Added source {source_id} to note {note_id}")
            
        elif args.citation_command == "generate_citations":
            # Generate citations for note
            note_id = args.note_id
            format_type = args.format
            output_file = args.output
            
            # Get citations
            citations = generate_citations_for_note(db_manager, note_id, format_type)
            
            if not citations:
                print(f"No sources found for note {note_id}")
                return
            
            # Print citations
            print(f"Citations for note {note_id} ({format_type.upper()} format):")
            for i, citation in enumerate(citations, 1):
                print(f"{i}. {citation}")
            
            # Save to file if output specified
            if output_file:
                with open(output_file, "w") as f:
                    f.write(f"Citations for note {note_id} ({format_type.upper()} format):\n\n")
                    for i, citation in enumerate(citations, 1):
                        f.write(f"{i}. {citation}\n")
                
                logger.info(f"Saved citations to {output_file}")
                print(f"Saved citations to {output_file}")
            
        elif args.citation_command == "view_sources":
            # View sources for note
            note_id = args.note_id
            
            # Get sources
            sources = get_sources(db_manager, note_id)
            
            if not sources:
                print(f"No sources found for note {note_id}")
                return
            
            # Print sources
            print(f"Sources for note {note_id}:")
            for i, source in enumerate(sources, 1):
                print(f"{i}. {source.get('source_type', 'Unknown')}:")
                
                if source.get('title'):
                    print(f"   Title: {source['title']}")
                
                if source.get('authors'):
                    print(f"   Authors: {source['authors']}")
                
                if source.get('year'):
                    print(f"   Year: {source['year']}")
                
                if source.get('url'):
                    print(f"   URL: {source['url']}")
                
                if source.get('publisher'):
                    print(f"   Publisher: {source['publisher']}")
                
                if source.get('journal'):
                    print(f"   Journal: {source['journal']}")
                
                if source.get('volume'):
                    print(f"   Volume: {source['volume']}")
                
                if source.get('issue'):
                    print(f"   Issue: {source['issue']}")
                
                if source.get('pages'):
                    print(f"   Pages: {source['pages']}")
                
                if source.get('doi'):
                    print(f"   DOI: {source['doi']}")
                
                print()
            
        elif args.citation_command == "search_by_source":
            # Search notes by source
            source_term = args.source
            
            # Search notes
            notes = search_by_source(db_manager, source_term)
            
            if not notes:
                print(f"No notes found with source matching '{source_term}'")
                return
            
            # Print notes
            print(f"Notes with source matching '{source_term}':")
            for i, note in enumerate(notes, 1):
                print(f"{i}. {note.get('title', 'Untitled')} (ID: {note['id']})")
                
                if note.get('source_type'):
                    print(f"   Source Type: {note['source_type']}")
                
                if note.get('source_title'):
                    print(f"   Source Title: {note['source_title']}")
                
                if note.get('authors'):
                    print(f"   Authors: {note['authors']}")
                
                if note.get('year'):
                    print(f"   Year: {note['year']}")
                
                print()
        
        else:
            print("Unknown citation command. Use one of: add_source, generate_citations, view_sources, search_by_source")
    
    finally:
        # Close database connection
        db_manager.close()


def main() -> None:
    """
    Main entry point for the AI Note System.
    """
    # Setup logger
    setup_logger()
    logger = logging.getLogger("ai_note_system.main")
    logger.info("Starting AI Note System")
    
    # Load configuration
    config = load_config()
    
    # Initialize database
    db_path = config.get("DATABASE_PATH", "../data/pansophy.db")
    # Convert relative path to absolute path
    if not os.path.isabs(db_path):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.abspath(os.path.join(current_dir, db_path))
    
    logger.info(f"Using database at: {db_path}")
    init_db(db_path)
    
    # Create database manager instance
    db_manager = DatabaseManager(db_path)
    
    # Setup argument parser
    parser = setup_argparse()
    args = parser.parse_args()
    
    # Handle commands
    try:
        if args.command == "process":
            handle_process_command(args, config)
        elif args.command == "export":
            handle_export_command(args, config)
        elif args.command == "search":
            handle_search_command(args, config)
        elif args.command == "search_pansophy":
            handle_semantic_search_command(args, config)
        elif args.command == "review":
            handle_review_command(args, config)
        elif args.command == "config":
            handle_config_command(args, config)
        elif args.command == "graph":
            handle_graph_command(args, config)
        elif args.command == "pansophy_ask":
            handle_pansophy_ask_command(args, config)
        elif args.command == "image_mindmap":
            handle_image_mindmap_command(args, config)
        elif args.command == "pansophy_plan":
            handle_pansophy_plan_command(args, config)
        elif args.command == "math_formula":
            handle_math_formula_command(args, config)
        elif args.command == "plugins":
            handle_plugins_command(args, config)
        elif args.command == "research":
            handle_research_command(args, config)
        elif args.command == "citation":
            handle_citation_command(args, config)
        elif args.command == "motivation":
            handle_motivation_command(args, config)
        else:
            parser.print_help()
    finally:
        # Close database connection
        db_manager.close()


if __name__ == "__main__":
    main()