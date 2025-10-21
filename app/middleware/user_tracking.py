"""Middleware for user tracking."""

import uuid
from fastapi import Request


async def add_user_id(request: Request, call_next):
    """Middleware for managing user_id via cookies."""
    user_id = request.cookies.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())
        request.state.user_id = user_id

    response = await call_next(request)

    if not request.cookies.get("user_id"):
        response.set_cookie(
            key="user_id",
            value=user_id,
            httponly=True,
            max_age=31536000,  # 1 year
        )

    return response
