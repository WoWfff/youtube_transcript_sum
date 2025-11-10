import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_current_user
from app.models.db_models import UserBase
from app.models.pydantic_models import SummarizesResponse
from app.services.database.methods import engine
from app.services.user_sums_methods import AllSummarizes

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/summarizes/api", response_model=SummarizesResponse | None)
async def all_summarizes(
    current_user: Annotated[UserBase, Depends(get_current_user)]
):
    """API endpoint to get user summaries (JSON response)."""
    try:
        all_summarizes = AllSummarizes(engine=engine)
        user_summarizes = await all_summarizes.user_summarizes(user_id=str(current_user.id))
        return user_summarizes

    except Exception as err:
        raise HTTPException(status_code=500, detail="Internal server error") from err


@router.delete("/summarizes/api")
async def clear_summarizes(
    current_user: Annotated[UserBase, Depends(get_current_user)]
):
    """API endpoint to clear user summaries."""
    try:
        all_summarizes = AllSummarizes(engine=engine)
        result = all_summarizes.clear_user_sums(user_id=str(current_user.id))
        return {"success": result, "message": "Summarizations cleared successfully"}
    except HTTPException:
        raise
    except Exception as err:
        logger.error(f"Error clearing summarizations: {err}")
        raise HTTPException(status_code=500, detail="Internal server error") from err
