"""Middleware for user tracking."""

import uuid
from fastapi import Request

from app.configs.db_config import settings
from app.models.db_models import UserBase
from app.database.methods import Insert, Select

from sqlalchemy import create_engine

db_url = settings.DATABASE_URL_psycopg(table_name="youtube_transcript")
engine = create_engine(url=db_url, echo=False)


async def add_user_id(request: Request, call_next):
    """Middleware for managing user_id via cookies."""
    user_id = request.cookies.get("user_id")

    if not user_id:
        user_id = str(uuid.uuid4())
        request.state.user_id = user_id

    if not Select(model=UserBase, engine=engine).by_filter(cookies=user_id):
        Insert(model=UserBase, engine=engine).one(cookies=user_id)

    response = await call_next(request)

    if not request.cookies.get("user_id"):
        response.set_cookie(
            key="user_id",
            value=user_id,
            httponly=True,
            max_age=31536000,  # 1 year
        )

    return response
