#!/usr/bin/env python
"""
Oracle Database Initialization Script for AI Note System.
This script initializes the Oracle database schema for the AI Note System.
"""

import os
import sys
import logging
import yaml
from pathlib import Path

# Add the parent directory to the path so we can import from the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ai_note_system.init_oracle_db")

def load_config():
    """
    Load configuration from config.yaml.
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = Path(__file__).parent / "config" / "config.yaml"
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)

def init_oracle_db():
    """
    Initialize the Oracle database schema.
    """
    try:
        # Load configuration
        config = load_config()
        
        # Check if database configuration exists
        if 'database' not in config:
            logger.error("Database configuration not found in config.yaml")
            sys.exit(1)
        
        db_config = config['database']
        
        # Check if Oracle configuration exists
        if db_config.get('type') not in ['oracle', 'mysql_heatwave']:
            logger.error("Database type must be 'oracle' or 'mysql_heatwave'")
            sys.exit(1)
        
        # Get connection parameters
        connection_string = db_config.get('connection_string')
        username = db_config.get('username')
        password = db_config.get('password')
        
        if not all([connection_string, username, password]):
            logger.error("Missing database connection parameters")
            sys.exit(1)
        
        # Import the Oracle database manager
        from ai_note_system.database.oracle_db_manager import init_oracle_db as init_db
        
        # Initialize the Oracle database
        logger.info("Initializing Oracle database...")
        init_db(connection_string, username, password)
        
        logger.info("Oracle database initialization completed successfully")
        
    except ImportError:
        logger.error("Oracle database libraries not installed. Please install cx_Oracle or oracledb.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error initializing Oracle database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Starting Oracle database initialization")
    init_oracle_db()
    logger.info("Oracle database initialization completed")