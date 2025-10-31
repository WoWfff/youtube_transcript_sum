from __future__ import annotations
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from app.db_models import Base, UserBase, UrlBase

from app.db_config import settings


db_url = settings.DATABASE_URL_psycopg
engine = create_engine(url=db_url, echo=True)

Base.metadata.create_all(engine)

with Session(engine) as session:
    user = UserBase(name="Ivan", urls=[UrlBase(name="github.com")])
    session.add(user)
    session.commit()
