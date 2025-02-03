"""Module for configuring Pytest."""
import logging
import os

import pytest
from flask import Flask

from app import create_app
from app.celery.tests.tasks import create_task_table
from database import init_database
from database.factories import Factory
from database.seeds import init_seed
from tests.custom_flask_client import CustomFlaskClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _remove_test_files(storage_path: str) -> None:
    """Remove test files created in storage path."""
    logger.info(' Deleting test files...')
    dirs = os.listdir(storage_path)
    dirs.remove(os.path.basename('example.pdf'))

    for filename in dirs:
        abs_path = f'{storage_path}/{filename}'
        os.remove(abs_path)
    logger.info(' Deleted test files!')


@pytest.fixture
def app():
    """Create an app with testing environment."""
    app = create_app('config.TestConfig')
    test_db = app.config.get('SQLALCHEMY_DATABASE_URI')

    if os.path.exists(test_db):
        logger.info(' Deleting test database...')
        os.remove(test_db)
        logger.info(' Deleted test database!')

    with app.app_context():
        init_database()
        create_task_table()
        init_seed()
        yield app


@pytest.fixture
def client(app: Flask):
    """Create a test client for making http requests."""
    app.test_client_class = CustomFlaskClient
    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    """Create a CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_header(app: Flask, client: CustomFlaskClient):
    """Create an auth header from a given user that can be added to
    an http requests."""
    def create_auth_header(user_email: str = None) -> dict:
        if user_email is None:
            user_email = os.getenv('TEST_USER_EMAIL')

        data = {
            'email': user_email,
            'password': os.getenv('TEST_USER_PASSWORD'),
        }

        response = client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert 200 == response.status_code
        token = json_response.get('token')

        return {
            app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']: token,
        }

    return create_auth_header


@pytest.fixture
def factory(app: Flask):
    """Create a Factory from a database model."""
    def _create_factory(model_name: str, num: int = 1):
        return Factory(model_name, num)

    return _create_factory
