from pathlib import Path
import unittest


import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import declarative_base

from app.models import (
    Construction,
    GeneralInfo,
    Change,
    ConstructionVariant,
    FormulaElement
)

DB_FILE_PATH = Path.cwd() / Path("test.db")
TEST_DB_URI = Path("sqlite://") / DB_FILE_PATH


class InitDBTestCase(unittest.TestCase):
    def test_create_echo(self):
        engine = create_engine(str(TEST_DB_URI), echo=True, future=True)



class QueryDBTestCase(unittest.TestCase):
    """"""
    # TODO: test all args including dynamic like `Construction.variants`



if __name__ == '__main__':
    unittest.main()
