from fastapi import HTTPException

from app.configs.app_config import YOUTUBE_THUMBNAIL_URL
from app.models.db_models import UrlBase, UserBase
from app.models.pydantic_models import SummarizesResponse, UrlData
from app.services.database.methods import Select


class AllSummarizes:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def user_urls(self, engine) -> SummarizesResponse | None:
        """
        Return:
            UserUrlsResponse model
        """
        try:
            db_user = Select(model=UserBase, engine=engine).by_filter(cookies=self.user_id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            urls_orm = Select(model=UrlBase, engine=engine).by_filter(many=True, owner_id=db_user.id)

            if not urls_orm:
                return None

            data = {}
            for counter, url_orm in enumerate(urls_orm, start=1):
                data[counter] = UrlData(
                    created_at=url_orm.created_at,
                    url=url_orm.url,
                    thumbnail_url=YOUTUBE_THUMBNAIL_URL.format(url_orm.url_shortcode)
                )

            return SummarizesResponse(cookies_user_id=self.user_id, user_urls=data)

        except Exception as err:
            raise HTTPException(status_code=500, detail="Internal server error") from err
