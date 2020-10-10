"""Module for configuring Pytest."""
import logging
import os

import pytest
from flask import Flask, Response
from flask.testing import FlaskClient

from app import create_app
from database import init_database
from database.factories import Factory
from database.seeds import init_seed

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

    with app.app_context():
        init_database()
        init_seed()
        yield app

    """FIXME: add these code before/after all tests are executed.
    
    If files are deleted then there are problems with Celery tasks.
    
    storage_path = app.config.get('STORAGE_DIRECTORY')
    _remove_test_files(storage_path)

    logger.info(' Deleting test database...')
    os.remove(app.config.get('DATABASE').get('name'))
    logger.info(' Deleted test database!')
    """


@pytest.fixture
def client(app: Flask):
    """Create a test client for making http requests."""
    def _request_log_before(*args, **kwargs):
        logger.info('=================')
        logger.info(f'args: {args}')
        logger.info(f'kwargs: {kwargs}')

    def _request_log_after(response: Response):
        logger.info(f'response status code: {response.status_code}')
        logger.info(f'response mime type: {response.mimetype}')
        if response.mimetype == 'application/json':
            logger.info(f'response json: {response.get_json()}')
        logger.info('=================')

    def _get(self, *args, **kwargs):
        """Like open but method is enforced to GET."""
        _request_log_before(*args, **kwargs)

        kwargs['method'] = 'GET'
        response = self.open(*args, **kwargs)

        _request_log_after(response)

        return response

    def _post(self, *args, **kwargs):
        """Like open but method is enforced to POST."""
        _request_log_before(*args, **kwargs)

        kwargs['method'] = 'POST'
        response = self.open(*args, **kwargs)

        _request_log_after(response)

        return response

    def _put(self, *args, **kwargs):
        """Like open but method is enforced to PUT."""
        _request_log_before(*args, **kwargs)

        kwargs['method'] = 'PUT'
        response = self.open(*args, **kwargs)

        _request_log_after(response)

        return response

    def _delete(self, *args, **kwargs):
        """Like open but method is enforced to DELETE."""
        _request_log_before(*args, **kwargs)

        kwargs['method'] = 'DELETE'
        response = self.open(*args, **kwargs)

        _request_log_after(response)

        return response

    FlaskClient.get = _get
    FlaskClient.post = _post
    FlaskClient.put = _put
    FlaskClient.delete = _delete

    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    """Create a CLI runner for testing CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_header(app: Flask, client: FlaskClient):
    """Create an auth header from a given user that can be added to
    an http requests."""
    def _create_auth_header(user_email: str = None) -> dict:
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
            app.config.get('SECURITY_TOKEN_AUTHENTICATION_HEADER'): token,
        }

    return _create_auth_header


@pytest.fixture
def factory(app: Flask):
    """Create a Factory from a database model."""
    def _create_factory(model_name: str, num: int = 1):
        return Factory(model_name, num)

    return _create_factory
