"""
FastAPI dependencies for TART telescope API.

This module provides dependency injection for configuration, authentication,
and other shared resources.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import RuntimeConfig

# Security scheme for JWT authentication
security = HTTPBearer()


def get_runtime_config(request: Request) -> RuntimeConfig:
    """Dependency to get the runtime configuration from app state."""
    return request.app.state.config


async def verify_jwt_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    request: Request,
) -> str:
    """
    Verify JWT token and return the username.

    This reuses the existing JWT verification logic from Flask-JWT-Extended.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Use the same secret key as Flask app
        config = request.app.state.config
        secret_key = config.settings.secret_key
        payload = jwt.decode(credentials.credentials, secret_key, algorithms=["HS256"])
        username: str = payload.get("sub") or payload.get("identity")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None

    return username


async def get_current_user(username: Annotated[str, Depends(verify_jwt_token)]) -> str:
    """Dependency to get the current authenticated user."""
    return username


# Type aliases for cleaner dependency injection
ConfigDep = Annotated[RuntimeConfig, Depends(get_runtime_config)]
AuthDep = Annotated[str, Depends(get_current_user)]
