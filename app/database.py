from app.database_utils import make_database
from config import Config


engine, db_session, Base = make_database(
    Config.SQLALCHEMY_DATABASE_URI, sqlalchemy_echo=Config.SQLALCHEMY_ECHO
)
