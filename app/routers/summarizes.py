import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_id
from app.models.pydantic_models import SummarizesResponse
from app.services.database.methods import engine
from app.services.user_sums_methods import AllSummarizes

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summarizes/", response_model=SummarizesResponse | None)
async def all_summarizes(
    cookies_user_id: Annotated[str, Depends(get_user_id)]
    ):
    try:
        all_summarizes = AllSummarizes(user_id=cookies_user_id)
        user_urls = await all_summarizes.user_urls(engine=engine)
        return user_urls

    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal server error") from err
