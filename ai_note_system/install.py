#!/usr/bin/env python
"""
Installation script for AI Note System (Pansophy).
This script helps with the installation of dependencies and setup of the system.
"""

import os
import sys
import subprocess
import platform
import argparse
from pathlib import Path
import importlib.util

# Define dependency categories
DEPENDENCY_CATEGORIES = {
    "core": [
        "pyyaml",
        "python-dotenv",
        "requests",
        "tqdm",
        "sqlalchemy",
    ],
    "llm": [
        "openai",
    ],
    "pdf": [
        "PyMuPDF",
        "pdf2image",
    ],
    "ocr": [
        "pytesseract",
    ],
    "speech": [
        "SpeechRecognition",
        "openai-whisper",
    ],
    "youtube": [
        "yt-dlp",
        "youtube-transcript-api",
        "pydub",
        "opencv-python",
    ],
    "visualization": [
        "graphviz",
        "mermaid-cli",
    ],
    "data": [
        "pandas",
        "numpy",
    ],
    "embeddings": [
        "sentence-transformers",
    ],
    "web": [
        "fastapi",
        "uvicorn",
    ],
    "export": [
        "markdown",
        "weasyprint",
        "genanki",
    ],
    "notion": [
        "notion-client",
    ],
    "google": [
        "google-api-python-client",
    ],
    "testing": [
        "pytest",
    ],
}

# Define platform-specific dependencies
PLATFORM_DEPENDENCIES = {
    "win32": ["win10toast"],
    "darwin": ["pync"],
    "linux": ["notify2"],
}

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    
    print(f"Python version check passed: {current_version[0]}.{current_version[1]}")
    return True

def check_dependency(package_name):
    """Check if a dependency is installed."""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except (ModuleNotFoundError, ValueError):
        return False

def check_dependencies(categories=None):
    """Check if dependencies are installed."""
    if categories is None:
        # Check all categories
        categories = DEPENDENCY_CATEGORIES.keys()
    
    all_installed = True
    missing_deps = {}
    
    for category in categories:
        if category not in DEPENDENCY_CATEGORIES:
            print(f"Warning: Unknown category '{category}'")
            continue
        
        missing = []
        for package in DEPENDENCY_CATEGORIES[category]:
            if not check_dependency(package):
                missing.append(package)
                all_installed = False
        
        if missing:
            missing_deps[category] = missing
    
    # Check platform-specific dependencies
    current_platform = sys.platform
    if current_platform in PLATFORM_DEPENDENCIES:
        platform_missing = []
        for package in PLATFORM_DEPENDENCIES[current_platform]:
            if not check_dependency(package):
                platform_missing.append(package)
                all_installed = False
        
        if platform_missing:
            missing_deps["platform"] = platform_missing
    
    return all_installed, missing_deps

def install_dependencies(categories=None, missing_only=True):
    """Install dependencies."""
    if categories is None:
        # Install all categories
        categories = DEPENDENCY_CATEGORIES.keys()
    
    all_installed, missing_deps = check_dependencies(categories)
    
    if all_installed and missing_only:
        print("All dependencies are already installed.")
        return True
    
    print("Installing dependencies...")
    
    for category in categories:
        if category not in DEPENDENCY_CATEGORIES:
            print(f"Warning: Unknown category '{category}'")
            continue
        
        packages = DEPENDENCY_CATEGORIES[category]
        if missing_only:
            if category in missing_deps:
                packages = missing_deps[category]
            else:
                # All packages in this category are already installed
                continue
        
        if not packages:
            continue
        
        print(f"Installing {category} dependencies: {', '.join(packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        except subprocess.CalledProcessError as e:
            print(f"Error installing {category} dependencies: {e}")
            return False
    
    # Install platform-specific dependencies
    current_platform = sys.platform
    if current_platform in PLATFORM_DEPENDENCIES:
        platform_packages = PLATFORM_DEPENDENCIES[current_platform]
        if missing_only:
            if "platform" in missing_deps:
                platform_packages = missing_deps["platform"]
            else:
                platform_packages = []
        
        if platform_packages:
            print(f"Installing platform-specific dependencies: {', '.join(platform_packages)}")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install"] + platform_packages)
            except subprocess.CalledProcessError as e:
                print(f"Error installing platform-specific dependencies: {e}")
                return False
    
    return True

def setup_database():
    """Set up the database."""
    print("Setting up database...")
    
    # Get the path to the data directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    
    # Ensure data directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Run the database initialization script
    init_db_path = os.path.join(data_dir, "init_db.py")
    
    if not os.path.exists(init_db_path):
        print(f"Error: Database initialization script not found at {init_db_path}")
        return False
    
    try:
        subprocess.check_call([sys.executable, init_db_path])
        print("Database setup complete.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting up database: {e}")
        return False

def setup_config():
    """Set up the configuration."""
    print("Setting up configuration...")
    
    # Get the path to the config directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(current_dir, "config")
    
    # Ensure config directory exists
    os.makedirs(config_dir, exist_ok=True)
    
    # Check if config.yaml exists
    config_path = os.path.join(config_dir, "config.yaml")
    
    if os.path.exists(config_path):
        print(f"Configuration file already exists at {config_path}")
        return True
    
    # Create config.yaml with default values
    default_config = """# AI Note System Configuration

# API Keys
OPENAI_API_KEY: "your_key_here"
NOTION_TOKEN: "your_token_here"

# Notion Integration
DATABASE_ID: "your_notion_db_id"

# Input Settings
PDF_EXTRACTION_METHOD: "PyMuPDF"  # Options: PyMuPDF, pdf2image+OCR
OCR_ENGINE: "pytesseract"  # Options: pytesseract, EasyOCR
SPEECH_RECOGNITION_ENGINE: "whisper"  # Options: whisper, SpeechRecognition

# Processing Settings
LLM_MODEL: "gpt-4"  # Options: gpt-4, gpt-3.5-turbo, mistral-7b-instruct, phi-3-mini, llama-3-8b
EMBEDDING_MODEL: "text-embedding-ada-002"  # Options: text-embedding-ada-002, all-MiniLM-L6-v2
SUMMARIZATION_MAX_LENGTH: 500
KEYPOINTS_MAX_COUNT: 10
ACTIVE_RECALL_QUESTIONS_COUNT: 5

# Visualization Settings
FLOWCHART_ENGINE: "mermaid"  # Options: mermaid, graphviz
MINDMAP_ENGINE: "mermaid"
TIMELINE_ENGINE: "mermaid"
TREEGRAPH_ENGINE: "graphviz"

# Output Settings
DEFAULT_EXPORT_FORMAT: "markdown"  # Options: markdown, pdf, anki
NOTION_AUTO_SYNC: true
SPACED_REPETITION_ALGORITHM: "SM-2"  # Options: SM-2, Leitner

# Database Settings
DATABASE_TYPE: "sqlite"  # Options: json, sqlite
DATABASE_PATH: "../data/pansophy.db"

# Logging Settings
LOG_LEVEL: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE: "../logs/ai_note_system.log"

# Advanced Settings
CACHE_EMBEDDINGS: true
AUTO_LINKING_THRESHOLD: 0.75  # Similarity threshold for auto-linking (0-1)
MISCONCEPTION_CHECK_ENABLED: true
SIMPLIFICATION_ENABLED: true
"""
    
    try:
        with open(config_path, "w") as f:
            f.write(default_config)
        print(f"Configuration file created at {config_path}")
        print("Please edit the configuration file to set your API keys and other settings.")
        return True
    except Exception as e:
        print(f"Error creating configuration file: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Install AI Note System (Pansophy)")
    parser.add_argument("--check", action="store_true", help="Check dependencies without installing")
    parser.add_argument("--categories", nargs="+", help="Specify dependency categories to install")
    parser.add_argument("--all", action="store_true", help="Install all dependencies, even if already installed")
    parser.add_argument("--no-db", action="store_true", help="Skip database setup")
    parser.add_argument("--no-config", action="store_true", help="Skip configuration setup")
    
    args = parser.parse_args()
    
    print("AI Note System (Pansophy) Installation")
    print("======================================")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check dependencies
    if args.check:
        all_installed, missing_deps = check_dependencies(args.categories)
        
        if all_installed:
            print("All dependencies are installed.")
        else:
            print("Missing dependencies:")
            for category, packages in missing_deps.items():
                print(f"  {category}: {', '.join(packages)}")
        
        return 0 if all_installed else 1
    
    # Install dependencies
    if not install_dependencies(args.categories, not args.all):
        print("Error installing dependencies.")
        return 1
    
    # Setup database
    if not args.no_db:
        if not setup_database():
            print("Error setting up database.")
            return 1
    
    # Setup configuration
    if not args.no_config:
        if not setup_config():
            print("Error setting up configuration.")
            return 1
    
    print("Installation complete!")
    print("You can now use the AI Note System.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())