import os

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from database import init_database
from database.factories import Factory
from database.seeds import init_seed


def _remove_test_files(storage_path: str) -> None:
    print(' Deleting test files...')
    dirs = os.listdir(storage_path)
    dirs.remove(os.path.basename('example.pdf'))

    for filename in dirs:
        abs_path = f'{storage_path}/{filename}'
        os.remove(abs_path)
    print(' Deleted test files!')


@pytest.fixture
def app():
    app = create_app('config.TestConfig')

    with app.app_context():
        init_database()
        init_seed()
        yield app

    storage_path = app.config.get('STORAGE_DIRECTORY')
    _remove_test_files(storage_path)

    print(' Deleting test database...')
    os.remove(app.config.get('DATABASE').get('name'))
    print(' Deleted test database!')


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    return app.test_cli_runner()


@pytest.fixture
def auth_header(app: Flask, client: FlaskClient):
    def _create_auth_header(user_email: str = None) -> dict:
        if user_email is None:
            user_email = os.getenv('TEST_USER_EMAIL')

        data = {
            'email': user_email,
            'password': os.getenv('TEST_USER_PASSWORD'),
        }

        response = client.post('/auth/login', json=data)
        json_response = response.get_json()
        token = json_response.get('token')

        return {
            app.config.get('SECURITY_TOKEN_AUTHENTICATION_HEADER'): 'Bearer %s' % token,
        }

    return _create_auth_header


@pytest.fixture
def factory(app: Flask):
    def _create_factory(model_name: str, num: int = 1):
        return Factory(model_name, num)

    return _create_factory
