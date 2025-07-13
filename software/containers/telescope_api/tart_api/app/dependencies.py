"""
FastAPI dependencies for TART telescope API.

This module provides dependency injection for configuration, authentication,
and other shared resources.
"""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import settings


# Custom security scheme for JWT authentication (accepts both JWT and Bearer formats)
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        from fastapi import HTTPException, status

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization header missing",
                    headers={"WWW-Authenticate": "Bearer, JWT"},
                )
            return None

        # Parse authorization header for both JWT and Bearer formats
        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() in ["jwt", "bearer"]:
                # Return credentials with normalized scheme
                return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        except ValueError:
            pass

        if self.auto_error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
                headers={"WWW-Authenticate": "Bearer, JWT"},
            )
        return None


security = JWTBearer()


def get_runtime_config(request: Request) -> Any:
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
        headers={"WWW-Authenticate": "Bearer, JWT"},
    )

    try:
        # Use the same secret key as Flask app
        secret_key = settings.secret_key
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
ConfigDep = Annotated[Any, Depends(get_runtime_config)]
AuthDep = Annotated[str, Depends(get_current_user)]
