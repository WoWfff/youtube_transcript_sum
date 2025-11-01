from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, insert, update, delete

from app.db_config import settings
from app.db_models import UserBase
from app.database.init_db import init_db

from typing import Any


db_url = settings.DATABASE_URL_psycopg(table_name="youtube_transcript")
engine = create_engine(url=db_url, echo=False)
init_db(engine=engine)


class BaseCRUD:
    def __init__(self, model, engine=engine):
        self.model = model
        self.engine = engine

    def _session(self):
        return Session(self.engine)


class Select(BaseCRUD):
    def all(self) -> list:
        """
        Return list of database objs in specific table.

        model: table_name
        engine: object create_engine

        Example of use:
            users = Select(UserBase, engine).all()
            for user in users:
                print(user.id)
        """
        with self._session() as session:
            stmt = select(self.model)
            result = session.scalars(stmt).all()
            return result

    def by_id(self, item_id: int) -> Any:
        """
        Return database obj of item with specific item_id.

        model: table_name
        engine: object create_engine

        Example of use:
            Select(model=UserBase, engine=engine).by_id(item_id=1)
        """
        with self._session() as session:
            stmt = select(self.model).where(self.model.id == item_id)
            return session.scalar(stmt)

    def by_filter(self, **filters) -> Any | None:
        """
        Get one record by filters.

        **filters: item_id and value in table

        Example of use:
            user = Select(UserBase).by_filter(cookies="abc-123")
        """
        with self._session() as session:
            stmt = select(self.model)

            for field, value in filters.items():
                if not hasattr(self.model, field):
                    raise AttributeError(
                        f"Model {self.model.__name__} has no attribute '{field}'"
                    )
                column = getattr(self.model, field)
                stmt = stmt.where(column == value)

            return session.scalar(stmt)


class Insert(BaseCRUD):
    def one(self, **kwargs) -> Any:
        """
        Insert data in table with specific item_id.

        **kwargs: item_id in table
        model: table_name
        engine: object create_engine

        Example of use:
            Insert(model=UserBase, engine=engine).one(id=1, name_of_column="data")
        """
        with self._session() as session:
            stmt = insert(self.model).values(**kwargs).returning(self.model)
            result = session.scalar(stmt)
            session.commit()
            return result


class Update(BaseCRUD):
    def by_id(self, item_id, **kwargs) -> Any:
        """
        Update data in table with specific item_id.

        model: table_name
        engine: object create_engine
        item_id: item_id in specific table

        Example of use:
            Update(model=UserBase, engine=engine).by_id(item_id=1, name_of_column="data")
        """
        with self._session() as session:
            stmt = (
                update(self.model)
                .where(self.model.id == item_id)
                .values(**kwargs)
                .returning(self.model)
            )
            result = session.scalar(stmt)
            session.commit()
            return result


class Delete(BaseCRUD):
    def by_id(self, item_id) -> Any:
        """
        Delete obj in table with specific item_id.

        model: table_name
        engine: object create_engine
        item_id: item_id in specific table

        Example of use:
            Delete(model=UserBase, engine=engine).by_id(item_id=1)
        """
        with self._session() as session:
            stmt = delete(self.model).where(self.model.id == item_id)
            session.execute(stmt)
            session.commit()


# if __name__ == "__main__":
    # user = Select(model=UserBase, engine=engine).by_filter(
    # cookies="c1eb8e93-41d7-4920-a42e-a19d96e8a8ab")
    # print(user)
    # for i in range(4):
    #     Delete(model=UserBase, engine=engine).by_id(i+1)