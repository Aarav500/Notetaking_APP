"""
Authentication API routes for AI Note System.
Handles user authentication, registration, password reset, etc.
"""

import os
import logging
import json
import uuid
import secrets
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field

from ..database.oracle_db_manager import OracleDatabaseManager
from ..outputs.oracle_email_delivery import OracleEmailDelivery
from .auth_utils import create_tokens, refresh_access_token, get_current_user

# Setup logging
logger = logging.getLogger("ai_note_system.api.auth_routes")

# Create router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Initialize email delivery service
email_service = None
try:
    from ..outputs.oracle_email_delivery import init_email_delivery
    email_service = init_email_delivery()
except Exception as e:
    logger.error(f"Error initializing email service: {e}")
    logger.warning("Email functionality will be disabled")

# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
    method: str = "email"

class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    method: str = "email"

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user_id: str
    email: EmailStr
    name: str
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str

# In-memory token store (should be replaced with a proper database in production)
password_reset_tokens = {}

# Routes
@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: OracleDatabaseManager = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user already exists
    existing_user = db.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    user_id = db.create_user({
        "email": user_data.email,
        "password_hash": password_hash,
        "name": user_data.name
    })
    
    # Generate tokens
    access_token, refresh_token = create_tokens(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user_id,
        "email": user_data.email,
        "name": user_data.name
    }

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: OracleDatabaseManager = Depends(get_db)):
    """
    Authenticate a user.
    """
    # Get user by email
    user = db.get_user_by_email(user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    access_token, refresh_token = create_tokens(user["id"])
    
    # Update last login
    db.update_user_last_login(user["id"])
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"]
    }

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: ForgotPasswordRequest, db: OracleDatabaseManager = Depends(get_db)):
    """
    Request a password reset.
    """
    # Get user by email
    user = db.get_user_by_email(request.email)
    if not user:
        # Don't reveal that the email doesn't exist
        return {"message": "If your email is registered, you will receive a password reset link"}
    
    # Generate token
    token = secrets.token_urlsafe(32)
    
    # Store token with expiration (24 hours)
    expiration = datetime.now() + timedelta(hours=24)
    password_reset_tokens[token] = {
        "user_id": user["id"],
        "email": user["email"],
        "expires": expiration
    }
    
    # Send email if email service is available
    if email_service and request.method == "email":
        # Frontend URL for password reset
        reset_url = os.environ.get("FRONTEND_URL", "http://localhost:3000") + "/auth/reset-password"
        
        # Send password reset email
        email_service.send_password_reset(
            recipient=user["email"],
            reset_token=token,
            reset_url=reset_url
        )
    
    return {"message": "If your email is registered, you will receive a password reset link"}

@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an access token using a refresh token.
    """
    # Refresh the access token
    new_access_token = refresh_access_token(request.refresh_token)
    
    # Check if refresh token is valid
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(request: ResetPasswordRequest, db: OracleDatabaseManager = Depends(get_db)):
    """
    Reset a user's password using a token.
    """
    # Check if token exists and is valid
    if request.token not in password_reset_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    token_data = password_reset_tokens[request.token]
    
    # Check if token is expired
    if datetime.now() > token_data["expires"]:
        # Remove expired token
        del password_reset_tokens[request.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    
    # Hash new password
    password_hash = hash_password(request.password)
    
    # Update user's password
    db.update_user_password(token_data["user_id"], password_hash)
    
    # Remove used token
    del password_reset_tokens[request.token]
    
    return {"message": "Password has been reset successfully"}

# Helper functions
def get_db():
    """
    Get database connection.
    """
    connection_string = os.environ.get("ORACLE_CONNECTION_STRING")
    username = os.environ.get("ORACLE_USERNAME")
    password = os.environ.get("ORACLE_PASSWORD")
    
    db = OracleDatabaseManager(connection_string, username, password)
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """
    Hash a password.
    """
    # In a real application, use a proper password hashing library like bcrypt
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    # In a real application, use a proper password hashing library like bcrypt
    return hash_password(plain_password) == hashed_password

def create_access_token(user_id: str) -> str:
    """
    Create an access token.
    """
    # In a real application, use a proper JWT library
    import base64
    import json
    
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + 3600,  # 1 hour expiration
        "iat": int(time.time())
    }
    
    token = base64.b64encode(json.dumps(payload).encode()).decode()
    return token