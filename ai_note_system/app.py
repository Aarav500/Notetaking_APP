"""
Main application file for AI Note System.
Sets up the FastAPI application and includes all routes.
"""

import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import routes
from api.auth_routes import router as auth_router
from api.planner_routes import router as planner_router
from api.analytics_routes import router as analytics_router

# Import database initialization
from database.oracle_db_manager import init_oracle_db

# Import log manager
from utils.log_manager import setup_logging, get_object_storage_client

# Setup logging
log_level = os.environ.get("LOG_LEVEL", "INFO")
log_level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
log_level_int = log_level_map.get(log_level, logging.INFO)

# Get Object Storage client for log offloading
object_storage = get_object_storage_client()
bucket_name = os.environ.get("OBJECT_STORAGE_BUCKET")

# Setup logging with rotation and Object Storage offloading
setup_logging(
    log_dir="logs",
    log_level=log_level_int,
    max_size=10 * 1024 * 1024,  # 10MB
    backup_count=5,
    object_storage=object_storage,
    bucket_name=bucket_name
)

logger = logging.getLogger("ai_note_system")

# Create limiter for rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="AI Note System API",
    description="API for AI-powered note-taking and knowledge management system",
    version="1.0.0",
)

# Add exception handler for rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth_router)
app.include_router(planner_router)
app.include_router(analytics_router)

@app.on_event("startup")
async def startup_event():
    """
    Initialize the application on startup.
    """
    logger.info("Starting AI Note System API")
    
    # Initialize Oracle database
    try:
        connection_string = os.environ.get("ORACLE_CONNECTION_STRING")
        username = os.environ.get("ORACLE_USERNAME")
        password = os.environ.get("ORACLE_PASSWORD")
        
        if connection_string and username and password:
            init_oracle_db(connection_string, username, password)
            logger.info("Oracle database initialized")
        else:
            logger.warning("Oracle database credentials not found in environment variables")
    except Exception as e:
        logger.error(f"Error initializing Oracle database: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown.
    """
    logger.info("Shutting down AI Note System API")

@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to AI Note System API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"},
    )

if __name__ == "__main__":
    """
    Run the application using Uvicorn.
    """
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )