"""
Main entry point for the Ideater application.

This module initializes the FastAPI application, sets up configuration,
logging, database connection, and routes.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
log_file = os.getenv("LOG_FILE", "logs/ideater.log")

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("ideater")

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "Ideater"),
    description="AI-Powered IDEATION ENGINE that expands coding ideas from a spark into full architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Set up CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up static files and templates
app.mount("/static", StaticFiles(directory="ui/static"), name="static")
templates = Jinja2Templates(directory="ui/templates")

# Import database and models
from core.models import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Set up database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ideater.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create database tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import and include routers
from api.projects import router as projects_router
from api.modules import router as modules_router
from api.auth import router as auth_router

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(modules_router, prefix="/api/modules", tags=["Modules"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that returns basic information about the API.
    """
    return {
        "name": os.getenv("APP_NAME", "Ideater"),
        "version": "1.0.0",
        "description": "AI-Powered IDEATION ENGINE that expands coding ideas from a spark into full architecture",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}

# Run the application
if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting Ideater application on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True)