"""Dependencies for dependency injection."""

from fastapi import Request, HTTPException

# Global storage for user URLs
user_urls: dict[str, str] = {}


def get_user_id(request: Request) -> str:
    """Get user ID from cookies or request state."""
    user_id = request.cookies.get("user_id") or getattr(request.state, "user_id", None)

    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID not found")

    return user_id


def get_user_url_storage() -> dict[str, str]:
    """Get user URL storage."""
    return user_urls
