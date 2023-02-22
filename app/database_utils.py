from typing import Tuple

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import declarative_base


def init_db(Base, engine: sqlalchemy.engine.Engine):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    import app.models
    Base.metadata.create_all(bind=engine)


def make_database(
        sqlalchemy_uri: str, sqlalchemy_echo: str = 'debug',
        sqlalchemy_echo_pool: str = 'debug',
        future: bool = True,
        session_maker_options=dict(autocommit=False, autoflush=False),
        do_init=False
) -> Tuple[sqlalchemy.engine.Engine, sqlalchemy.orm.scoped_session, 'Base']:
    engine = create_engine(sqlalchemy_uri, echo=sqlalchemy_echo,
                           future=future)

    db_session = scoped_session(
        sessionmaker(bind=engine, **session_maker_options)
    )

    print(engine, db_session)

    Base = declarative_base()
    Base.query = db_session.query_property()

    if do_init:
        init_db(Base, engine)

    return engine, db_session, Base


def get_default_database() -> Tuple[
    sqlalchemy.engine.Engine, sqlalchemy.orm.scoped_session, 'Base'
]:
    from config import Config

    engine, db_session, Base = make_database(
        Config.SQLALCHEMY_DATABASE_URI,
        sqlalchemy_echo=Config.SQLALCHEMY_ECHO
    )

    return engine, db_session, Base
