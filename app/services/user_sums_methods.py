from fastapi import HTTPException

from app.configs.app_config import YOUTUBE_THUMBNAIL_URL
from app.models.db_models import SumBase, UrlBase, UserBase
from app.models.pydantic_models import SummarizesResponse, UrlData
from app.services.database.methods import Execute, Select


class AllSummarizes:
    def __init__(self, engine):
        self.engine = engine

    async def user_summarizes(self, user_id: str) -> SummarizesResponse | None:
        """
        Return:
            UserUrlsResponse model
        """
        try:
            db_user = Select(model=UserBase, engine=self.engine).by_filter(cookies=user_id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            urls_orm = Select(model=UrlBase, engine=self.engine).by_filter_joined(many=True, owner_id=db_user.id)
            if not urls_orm:
                return None

            data = {}
            for counter, url_orm in enumerate(urls_orm, start=1):
                # Cheking for transcript accessibility
                if not url_orm.transcript_accessibility:
                    continue
                # Reading summarization file
                file_path = url_orm.summarization.path_to_sum_file
                try:
                    with open(file_path, "r") as file:
                        text = file.read()
                except Exception as err:
                    raise ValueError("Error while reading summarization file.") from err
                # Formating response data
                data[counter] = UrlData(
                    created_at=url_orm.created_at,
                    url=url_orm.url,
                    thumbnail_url=YOUTUBE_THUMBNAIL_URL.format(url_orm.url_shortcode),
                    transcipt=text
                )

            return SummarizesResponse(cookies_user_id=user_id, user_urls=data)

        except Exception as err:
            raise HTTPException(status_code=500, detail="Internal server error") from err

    def clear_user_sums(self, user_id: str) -> bool:
        try:
            db_user = Select(model=UserBase, engine=self.engine).by_filter(cookies=user_id)
            if not db_user:
                raise HTTPException(status_code=404, detail="User not found")

            Execute(model=SumBase, engine=self.engine).execute(
                """
                DELETE FROM summarization WHERE user_owner_id = :id;
                """,
                {"id": db_user.id}
            )
            Execute(model=SumBase, engine=self.engine).execute(
                """
                DELETE FROM urls WHERE owner_id = :id
                """,
                {"id": db_user.id}
            )

            return True

        except HTTPException:
            raise
        except Exception as err:
            raise ValueError("Error while clearing user summarizes.") from err
