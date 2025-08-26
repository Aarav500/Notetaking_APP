"""
Database utility functions for the Ideater application.

This module provides utility functions for database operations.
"""

import os
import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Set up logging
logger = logging.getLogger("ideater.utils.db")

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ideater.db")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Session: A SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    """
    from core.models import Base
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")

def drop_db() -> None:
    """
    Drop all database tables.
    """
    from core.models import Base
    
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database tables dropped successfully.")

def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.
    """
    drop_db()
    init_db()
    logger.info("Database reset successfully.")