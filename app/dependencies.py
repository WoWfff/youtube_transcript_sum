"""Dependencies for dependency injection."""

from fastapi import HTTPException, Request, status

from app.models.db_models import UserBase
from app.services.database.methods import Select, engine
from app.utils.jwt import decode_access_token

# Global storage for user URLs
user_urls: dict[str, str] = {}


def get_user_id(request: Request) -> str:
    """Get user ID from cookies or request state (legacy method for backward compatibility)."""
    user_id = request.cookies.get("user_id") or getattr(request.state, "user_id", None)

    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID not found")

    return user_id


def get_current_user(request: Request) -> UserBase:
    """Get current authenticated user from JWT token in cookie."""
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user ID from token
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


def get_user_url_storage() -> dict[str, str]:
    """Get user URL storage."""
    return user_urls
