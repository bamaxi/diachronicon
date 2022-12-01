import os
import unittest
import sys
import logging

from app.database_utils import init_db, make_database
from app.update_db.update import parse

logging.basicConfig()
# logger = logging.getLogger('test_db')
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel('DEBUG')
# class DBCreateMixin:


class DBCreateTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # self.logger = logging.getLogger()
        self.db_name = 'test_diachronicon.db'

    def tearDown(self) -> None:
        import os
        import time
        # del self.logger
        os.remove(self.db_name)

    @unittest.skipUnless(
        sys.version_info.major == 3 and sys.version_info.minor >= 10,
        f"assertNoLogs not available in {sys.version}"
    )
    def test_create_db_noinit_noecho(self) -> None:
        SQLALCHEMY_TEST_DB_URI = 'sqlite:///' + self.db_name

        print(dir(self))

        # with self.assertNoLogs(self.logger, level='DEBUG'):
        with self.assertNoLogs(logger, level='DEBUG'):
            engine, db_session, Base = make_database(
                SQLALCHEMY_TEST_DB_URI, sqlalchemy_echo=False, do_init=False
            )

    def test_create_db_noinit_echo(self) -> None:
        SQLALCHEMY_TEST_DB_URI = 'sqlite:///' + 'test_diachronicon.db'

        print(f"does {SQLALCHEMY_TEST_DB_URI} log?")
        print(os.listdir('.'))

        # with self.assertLogs(self.logger, level='DEBUG'):
        with self.assertLogs(logger, level='DEBUG'):
            engine, db_session, Base = make_database(
                SQLALCHEMY_TEST_DB_URI, sqlalchemy_echo=True, do_init=False
            )
            with engine.connect() as conn:
                conn.get_execution_options()

    @unittest.skipUnless(
        sys.version_info.major == 3 and sys.version_info.minor >= 10,
        f"assertNoLogs not available in {sys.version}"
    )
    def test_create_db_init_noecho(self) -> None:
        SQLALCHEMY_TEST_DB_URI = 'sqlite:///' + self.db_name

        with self.assertNoLogs(self.logger, level='DEBUG'):
            engine, db_session, Base = make_database(
                SQLALCHEMY_TEST_DB_URI, sqlalchemy_echo=False, do_init=True
            )

    # def test_create_db_init_echo(self) -> None:
    #     SQLALCHEMY_TEST_DB_URI = 'sqlite:///' + 'test_diachronicon.db'
    #
    #     with self.assertLogs(self.logger, level='DEBUG'):
    #         engine, db_session, Base = make_database(
    #             SQLALCHEMY_TEST_DB_URI, sqlalchemy_echo=True, do_init=True
    #         )


# class DBUpdateTestCase(unittest.TestCase):
#     def test_something(self):
#         pass


if __name__ == '__main__':
    unittest.main()

