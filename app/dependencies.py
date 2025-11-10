"""
Dependencies for dependency injection.

This module provides FastAPI dependencies for user authentication
and request processing. These dependencies are used throughout
the application to inject user context into route handlers.
"""

from fastapi import HTTPException, Request, status

from app.models.db_models import UserBase
from app.services.database.methods import Select, engine
from app.utils.jwt import decode_access_token

# Global storage for user URLs (legacy support)
# This is kept for backward compatibility with older code
user_urls: dict[str, str] = {}


def get_user_id(request: Request) -> str:
    """
    Get user ID from cookies or request state.

    This is a legacy method kept for backward compatibility.
    New code should use get_current_user() instead, which
    provides JWT-based authentication.

    Args:
        request: FastAPI Request object

    Returns:
        User ID as string

    Raises:
        HTTPException: If user ID is not found
    """
    user_id = request.cookies.get("user_id") or getattr(request.state, "user_id", None)

    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID not found")

    return user_id


def get_current_user(request: Request) -> UserBase:
    """
    Get current authenticated user from JWT token in cookie.

    This dependency extracts the JWT token from the HttpOnly cookie,
    validates it, and returns the authenticated user from the database.
    It's used as a dependency in protected routes.

    Authentication flow:
    1. Extract 'access_token' from request cookies
    2. Decode and validate the JWT token
    3. Extract user ID from token payload (stored in 'sub' claim)
    4. Fetch user from database using the user ID
    5. Return UserBase object

    Args:
        request: FastAPI Request object containing cookies

    Returns:
        UserBase: Authenticated user object from database

    Raises:
        HTTPException(401): If token is missing, invalid, or user not found
    """
    # Extract JWT token from HttpOnly cookie
    # HttpOnly cookies prevent XSS attacks by making cookies inaccessible to JavaScript
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate the JWT token
    # Returns None if token is invalid, expired, or tampered with
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from token payload
    # JWT standard uses 'sub' (subject) claim to store user identifier
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database using the user ID from token
    # This ensures the user still exists and is active
    try:
        user = Select(model=UserBase, engine=engine).by_filter(id=int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except (ValueError, TypeError) as err:
        # Handle case where user_id cannot be converted to integer
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


def get_user_url_storage() -> dict[str, str]:
    """Get user URL storage."""
    return user_urls
