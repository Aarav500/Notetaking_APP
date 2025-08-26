"""
Authentication utilities for AI Note System.
Implements JWT authentication with refresh tokens stored client-side.
"""

import os
import logging
import time
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

# Setup logging
logger = logging.getLogger("ai_note_system.api.auth_utils")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT settings
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key")  # Change in production
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class TokenPayload:
    """
    Token payload class.
    """
    def __init__(self, sub: str, exp: int, iat: int, token_type: str = "access"):
        self.sub = sub  # Subject (user ID)
        self.exp = exp  # Expiration time
        self.iat = iat  # Issued at time
        self.token_type = token_type  # Token type (access or refresh)


def create_access_token(user_id: str) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id (str): User ID to include in the token
        
    Returns:
        str: JWT access token
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user_id,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "token_type": "access"
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id (str): User ID to include in the token
        
    Returns:
        str: JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": user_id,
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "token_type": "refresh"
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        Optional[TokenPayload]: Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Create TokenPayload object
        token_payload = TokenPayload(
            sub=payload.get("sub"),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
            token_type=payload.get("token_type", "access")
        )
        
        # Check if token is expired
        if datetime.utcnow().timestamp() > token_payload.exp:
            logger.warning(f"Token expired: {token_payload.sub}")
            return None
            
        return token_payload
        
    except jwt.PyJWTError as e:
        logger.error(f"Error decoding token: {e}")
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Get the current user from the token.
    
    Args:
        token (str): JWT token
        
    Returns:
        str: User ID
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token_payload = decode_token(token)
    
    if token_payload is None or token_payload.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return token_payload.sub


def create_tokens(user_id: str) -> Tuple[str, str]:
    """
    Create access and refresh tokens for a user.
    
    Args:
        user_id (str): User ID
        
    Returns:
        Tuple[str, str]: Access token and refresh token
    """
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    return access_token, refresh_token


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Refresh an access token using a refresh token.
    
    Args:
        refresh_token (str): Refresh token
        
    Returns:
        Optional[str]: New access token if refresh token is valid, None otherwise
    """
    token_payload = decode_token(refresh_token)
    
    if token_payload is None or token_payload.token_type != "refresh":
        logger.warning(f"Invalid refresh token")
        return None
        
    # Create new access token
    access_token = create_access_token(token_payload.sub)
    
    return access_token