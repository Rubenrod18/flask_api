import logging
import os
import uuid

import pytest
import sqlalchemy
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from faker.providers import date_time, file, person
from flask.testing import FlaskClient
from flask_sqlalchemy.record_queries import get_recorded_queries
from sqlalchemy import create_engine, text
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

        assert response.status_code == expected_status_code, response.get_data(as_text=True)
        return response

    def get(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 200)
        return self.__make_request('GET', exp_code, *args, **kwargs)

    def post(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 201)
        return self.__make_request('POST', exp_code, *args, **kwargs)

    def put(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 200)
        return self.__make_request('PUT', exp_code, *args, **kwargs)

    def delete(self, *args, **kwargs):
        exp_code = kwargs.pop('exp_code', 200)
        return self.__make_request('DELETE', exp_code, *args, **kwargs)


@pytest.fixture(scope='session', autouse=True)
def load_test_env():
    """Load environment variables before running any test."""
    load_dotenv(find_dotenv('.env.test'), override=True)


@pytest.fixture(scope='session')
def faker():
    fake = Faker()
    fake.add_provider(person)
    fake.add_provider(date_time)
    fake.add_provider(file)
    return fake


@pytest.fixture(scope='function')
def app():
    def create_app_db():
        db_uri = f'{os.getenv("SQLALCHEMY_DATABASE_URI")}_{uuid.uuid4().hex}'
        engine = create_engine(db_uri)

        if not database_exists(db_uri):
            create_database(db_uri)

        assert database_exists(db_uri)
        return db_uri, engine

    def create_celery_db():
        dbname = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not database_exists(dbname):
            try:
                create_database(dbname)
            except sqlalchemy.exc.ProgrammingError as exc:
                if getattr(exc.orig, 'args', [None])[0] == 1_007:
                    pass
                else:
                    raise exc
        assert database_exists(dbname)

    def create_app(db_uri):
        from app import create_app  # pylint: disable=(import-outside-toplevel
        from config import TestConfig  # pylint: disable=(import-outside-toplevel

        TestConfig.SQLALCHEMY_DATABASE_URI = db_uri
        return create_app('config.TestConfig')

    def drop_database(engine):
        """Drop the database safely by killing active connections."""
        database = engine.url.database
        neutral_engine_url = engine.url.set(database='mysql')
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

    def teardown(engine):
        db.session.remove()
        db.engine.dispose()
        drop_database(engine)

    db_uri, engine = create_app_db()
    create_celery_db()
    app = create_app(db_uri)

    with app.app_context():
        db.create_all()

        yield app

        teardown(engine)


@pytest.fixture()
def client(app):
    """Provide a Flask test client using the custom client."""
    app.test_client_class = _CustomFlaskClient
    return app.test_client()


@pytest.fixture()
def runner(app):
    """Provide a Flask CLI runner."""
    return app.test_cli_runner()


def show_last_sql_query():
    """Print the most recently executed SQL query for debugging purposes."""
    info = get_recorded_queries()[-1]
    print(info.statement, info.parameters, info.duration, sep='\n')  # noqa
