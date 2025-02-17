import logging
import os
import unittest
import uuid

from dotenv import find_dotenv, load_dotenv
from faker import Faker
from faker.providers import date_time, person
from flask import Flask, Response
from flask.testing import FlaskClient
from sqlalchemy import create_engine, text
from sqlalchemy_utils import create_database, database_exists

from app.extensions import db

logger = logging.getLogger(__name__)

faker = Faker()
faker.add_provider(person)
faker.add_provider(date_time)


class _CustomFlaskClient(FlaskClient):
    @staticmethod
    def __before_request(*args, **kwargs):
        logger.info(f'args: {args}')
        logger.info(f'kwargs: {kwargs}')

    @staticmethod
    def __log_request_data(response: Response):
        if response.mimetype == 'application/json' and response.data:
            response_data = response.get_json()
        else:
            response_data = response.data
        logger.info(f'response data: {response_data}')

    def __after_request(self, response: Response):
        logger.info(f'response status code: {response.status_code}')
        logger.info(f'response mime type: {response.mimetype}')
        self.__log_request_data(response)

    def __make_request(self, method: str, *args, **kwargs):
        logger.info('< === START REQUEST === >')
        self.__before_request(*args, **kwargs)

        kwargs['method'] = method
        response = self.open(*args, **kwargs)

        self.__after_request(response)
        logger.info('< === END REQUEST === >')
        return response

    def get(self, *args, **kwargs):
        """Like open but method is enforced to GET."""
        return self.__make_request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """Like open but method is enforced to POST."""
        return self.__make_request('POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        """Like open but method is enforced to PUT."""
        return self.__make_request('PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """Like open but method is enforced to DELETE."""
        return self.__make_request('DELETE', *args, **kwargs)


class TestBase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestBase, self).__init__(*args, **kwargs)
        self.__engine = None
        self.app = None
        self.client = None
        self.runner = None
        self.session = None

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
    def plain_engine_url(self):
        return self.__engine.url.render_as_string(hide_password=False)

    def __create_app(self):
        """Create an app with testing environment."""
        from app import create_app
        from config import TestConfig

        TestConfig.SQLALCHEMY_DATABASE_URI = self.plain_engine_url
        return create_app('config.TestConfig')

    @staticmethod
    def __create_test_client(app: Flask):
        """Create a test client for making http requests."""
        app.test_client_class = _CustomFlaskClient
        return app.test_client()

    def __create_databases(self):
        database_uri = f'{os.getenv("SQLALCHEMY_DATABASE_URI")}_{uuid.uuid4().hex}'
        self.__engine = create_engine(database_uri)
        if not database_exists(self.plain_engine_url):
            create_database(self.plain_engine_url)

        if not database_exists(os.getenv('SQLALCHEMY_DATABASE_URI')):
            create_database(os.getenv('SQLALCHEMY_DATABASE_URI'))

        assert database_exists(self.plain_engine_url)

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
