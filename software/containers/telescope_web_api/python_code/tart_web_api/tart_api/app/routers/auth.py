"""
Authentication router for TART telescope API.

This module provides JWT authentication endpoints that maintain compatibility
with the existing Flask-JWT-Extended authentication system.
"""

import os
from datetime import datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from models.auth_models import AuthRequest, AuthResponse, RefreshResponse

from ..config import settings
from ..dependencies import get_runtime_config

router = APIRouter()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return to_encode


@router.post("", response_model=AuthResponse, status_code=200)
async def auth(
    login_request: AuthRequest,
    config: Annotated[Any, Depends(get_runtime_config)],
):
    """
    Authenticate user and return JWT tokens.

    This endpoint reuses the existing Flask authentication logic:
    - Username must be "admin"
    - Password is from LOGIN_PW environment variable or "password"
    """
    # Get password from environment or use default (same as Flask)
    login_password = os.environ.get("LOGIN_PW", "password")

    if login_request.username != "admin" or login_request.password != login_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens with same structure as Flask-JWT-Extended
    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=30)

    access_token_data = create_access_token(
        data={"sub": login_request.username, "identity": login_request.username},
        expires_delta=access_token_expires,
    )

    refresh_token_data = create_access_token(
        data={"sub": login_request.username, "identity": login_request.username},
        expires_delta=refresh_token_expires,
    )

    # Encode tokens using the same secret key as Flask
    secret_key = settings.secret_key
    access_token = jwt.encode(access_token_data, secret_key, algorithm="HS256")
    refresh_token = jwt.encode(refresh_token_data, secret_key, algorithm="HS256")

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=RefreshResponse, status_code=200)
async def refresh(
    # TODO: Add refresh token validation
    config: Annotated[Any, Depends(get_runtime_config)],
):
    """
    Refresh access token using refresh token.

    Note: This is a simplified implementation. In production, you would
    validate the refresh token from the Authorization header.
    """
    # For now, create a new access token for "admin" user
    # In a full implementation, you would extract and validate the refresh token
    access_token_expires = timedelta(minutes=15)

    access_token_data = create_access_token(
        data={"sub": "admin", "identity": "admin"},
        expires_delta=access_token_expires,
    )

    secret_key = settings.secret_key
    access_token = jwt.encode(access_token_data, secret_key, algorithm="HS256")

    return RefreshResponse(access_token=access_token)
