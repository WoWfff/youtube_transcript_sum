from app.models.db_models import Base


def init_db(engine):
    Base.metadata.create_all(engine)
