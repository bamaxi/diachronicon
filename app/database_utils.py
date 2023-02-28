from typing import Tuple, Dict, Any, Optional

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def init_db(Base, engine: sqlalchemy.engine.Engine):
    # import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    import app.models
    # from app.models import Base
    Base.metadata.create_all(bind=engine)


def make_database(
    sqlalchemy_uri: str, sqlalchemy_echo: str = 'debug',
    sqlalchemy_echo_pool: str = 'debug',
    future: bool = True, session_maker_options: Dict[str, Any] = None,
    do_init=False
) -> Tuple[sqlalchemy.engine.Engine, sqlalchemy.orm.scoped_session,
           Optional["Base"]
]:
    if session_maker_options is None:
        session_maker_options = dict(autocommit=False, autoflush=False)

    engine = create_engine(sqlalchemy_uri, echo=sqlalchemy_echo,
                           future=future)

    db_session = scoped_session(
        sessionmaker(bind=engine, **session_maker_options)
    )

    print(engine, db_session)

    # Base = declarative_base()
    # Base.query = db_session.query_property()
    import app.models
    from app.models import Base

    if do_init:
        init_db(Base, engine)

    return engine, db_session, Base


def get_default_database() -> Tuple[
    sqlalchemy.engine.Engine, sqlalchemy.orm.scoped_session
]:
    from config import Config

    engine, db_session, _ = make_database(
        Config.SQLALCHEMY_DATABASE_URI,
        sqlalchemy_echo=Config.SQLALCHEMY_ECHO,
        sqlalchemy_echo_pool=Config.SQLALCHEMY_ECHO,
    )

    return engine, db_session
