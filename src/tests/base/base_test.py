import logging
import os
import unittest

from faker import Faker
from faker.providers import date_time, person
from flask import Flask, Response
from flask.testing import FlaskClient
from sqlalchemy import create_engine
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

    def setUp(self) -> None:
        self.__create_database()
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
            db.session.close()
            # TODO: Temporal solution.
            #   The celery tests are async so if next line is uncommented then the Celery tests will fail.
            # db.drop_all()

    @property
    def plain_engine_url(self):
        return self.__engine.url.render_as_string(hide_password=False)

    def __create_app(self):
        """Create an app with testing environment."""
        from app import create_app
        from config import TestConfig

        TestConfig.SQLALCHEMY_DATABASE_URI = self.plain_engine_url
        return create_app(TestConfig)

    @staticmethod
    def __create_test_client(app: Flask):
        """Create a test client for making http requests."""
        app.test_client_class = _CustomFlaskClient
        return app.test_client()

    def __create_database(self):
        database_uri = os.getenv('TEST_SQLALCHEMY_DATABASE_URI')
        self.__engine = create_engine(database_uri)
        if not database_exists(self.plain_engine_url):
            create_database(self.plain_engine_url)
        assert database_exists(self.plain_engine_url)
