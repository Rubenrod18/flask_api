import logging
import os
import unittest
import uuid

import sqlalchemy
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from faker.providers import date_time, file, person
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy.record_queries import get_recorded_queries
from sqlalchemy import create_engine, make_url, text
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import create_database, database_exists
from werkzeug.test import TestResponse

from app.extensions import db

logger = logging.getLogger(__name__)


class _CustomFlaskClient(FlaskClient):
    @staticmethod
    def __before_request(*args, **kwargs):
        logger.info(f'args: {args}')
        logger.info(f'kwargs: {kwargs}')

    @staticmethod
    def __log_request_data(response: TestResponse):
        if response.mimetype == 'application/json' and response.data:
            response_data = response.get_json()
        else:
            response_data = response.data
        logger.info(f'response data: {response_data}')

    def __after_request(self, response: TestResponse):
        logger.info(f'response status code: {response.status_code}')
        logger.info(f'response mime type: {response.mimetype}')
        self.__log_request_data(response)

    def __make_request(self, method: str, expected_status_code: int, *args, **kwargs):
        kwargs['method'] = method

        logger.info('< === START REQUEST === >')
        self.__before_request(*args, **kwargs)
        response = self.open(*args, **kwargs)
        self.__after_request(response)
        logger.info('< === END REQUEST === >')

        assert response.status_code == expected_status_code
        return response

    def get(self, *args, **kwargs):
        """Like open but method is enforced to GET."""
        exp_code = kwargs.pop('exp_code', 200)
        return self.__make_request('GET', exp_code, *args, **kwargs)

    def post(self, *args, **kwargs):
        """Like open but method is enforced to POST."""
        exp_code = kwargs.pop('exp_code', 201)
        return self.__make_request('POST', exp_code, *args, **kwargs)

    def put(self, *args, **kwargs):
        """Like open but method is enforced to PUT."""
        exp_code = kwargs.pop('exp_code', 200)
        return self.__make_request('PUT', exp_code, *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Like open but method is enforced to DELETE."""
        exp_code = kwargs.pop('exp_code', 200)
        return self.__make_request('DELETE', exp_code, *args, **kwargs)


class BaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__engine = None
        self.app = None
        self.client = None
        self.runner = None

    @classmethod
    def setUpClass(cls):
        """Load environment variables before running any test."""
        load_dotenv(find_dotenv('.env.test'), override=True)

    def setUp(self) -> None:
        self.__create_databases()
        app = self.__create_app()
        app_context = app.app_context()
        app_context.push()

        self.app = app
        self.client = self.__create_test_client(self.app)
        self.runner = self.app.test_cli_runner()
        with self.app.app_context():
            db.create_all()

    def tearDown(self) -> None:
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()
            self.__drop_database()

    @property
    def faker(self):
        fake = Faker()
        fake.add_provider(person)
        fake.add_provider(date_time)
        fake.add_provider(file)
        return fake

    @property
    def plain_engine_url(self):
        return self.__engine.url.render_as_string(hide_password=False)

    def __create_app(self):
        """Create an app with testing environment."""
        from app import create_app  # pylint: disable=(import-outside-toplevel
        from config import TestConfig  # pylint: disable=(import-outside-toplevel

        TestConfig.SQLALCHEMY_DATABASE_URI = self.plain_engine_url
        return create_app('config.TestConfig')

    @staticmethod
    def __create_test_client(app: Flask):
        """Create a test client for making http requests."""
        app.test_client_class = _CustomFlaskClient
        return app.test_client()

    @staticmethod
    def show_last_sql_query() -> None:
        """Print the most recently executed SQL query for debugging purposes.

        This method retrieves the last recorded query from SQLAlchemy's query recorder
        and prints its statement, parameters, and execution duration.

        Notes
        -----
        - This method should only be used for debugging purposes and not in production code.
        - Ensure that Flask's query recording is enabled (`SQLALCHEMY_RECORD_QUERIES` set to True)
          to use this functionality.

        """
        info = get_recorded_queries()[-1]
        print(info.statement, info.parameters, info.duration, sep='\n')  # noqa: T201

    @staticmethod
    def _database_exists(database_url: str) -> bool:
        url = make_url(database_url)
        url_without_db = url.set(database=None)
        engine = create_engine(url_without_db)
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text('SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name'),
                    {'db_name': url.database},
                )
                return result.scalar() is not None
        except OperationalError:
            return False

    def __create_databases(self):
        def create_app_db():
            database_uri = f'{os.getenv("SQLALCHEMY_DATABASE_URI")}_{uuid.uuid4().hex}'
            self.__engine = create_engine(database_uri)
            if not database_exists(self.plain_engine_url):
                create_database(self.plain_engine_url)

            assert database_exists(self.plain_engine_url)

        def create_celery_db():
            dbname = os.getenv('SQLALCHEMY_DATABASE_URI')
            if not self._database_exists(os.getenv('SQLALCHEMY_DATABASE_URI')):
                try:
                    create_database(dbname)
                except sqlalchemy.exc.ProgrammingError as exc:
                    if getattr(exc.orig, 'args', [None])[0] == 1_007:
                        pass  # NOTE: Database already exists, ignore
                    else:
                        raise exc

            assert database_exists(dbname)

        create_app_db()
        create_celery_db()

    def __drop_database(self) -> None:
        """Kill active processes connected to the database and drop the database.

        Gracefully handle the deletion of the database by terminating active connections
        and dropping the database. This approach avoids issues that arise when attempting
        to delete the database using the same connection.

        Notes
        -----
        In previous versions, utilities like `sqlalchemy_utils.drop_database` were used
        to simplify database deletion. However, these utilities operate on the same
        connection used to interact with the target database. SQLAlchemy 2.0+ no longer
        allows implicit execution, and using the same connection for the `DROP DATABASE`
        command can lead to deadlocks or operational errors. This function implements a
        safer alternative.

        Steps:
        1. Establish a neutral connection (e.g., to the 'mysql' database) to avoid being
           connected to the target database during the DROP operation.
        2. Identify and terminate active connections to the target database using the
           `information_schema.processlist` table.
        3. Execute the `DROP DATABASE` SQL command.
        4. Use `neutral_engine.dispose()` to release resources associated with the engine,
           such as connection pools, ensuring no resources are leaked after the operation.

        """
        database = self.__engine.url.database
        neutral_engine_url = self.__engine.url.set(database='mysql')
        neutral_engine = create_engine(neutral_engine_url)

        try:
            with neutral_engine.connect() as conn:
                kill_query = (
                    f"SELECT CONCAT('KILL ', id, ';') FROM information_schema.processlist WHERE db = '{database}';"
                )
                result = conn.execute(text(kill_query))
                for row in result:
                    conn.execute(text(row[0]))

                conn.execute(text(f'DROP DATABASE IF EXISTS `{database}`;'))
        finally:
            neutral_engine.dispose()
