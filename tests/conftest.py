import os

import pytest
from flask import Flask
from flask_security.passwordless import generate_login_token

from app import create_app
from app.extensions import db_wrapper
from app.models.user import User as UserModel
from database.migrations import init_database, init_migrations
from database.seeds import init_seed


@pytest.fixture
def app():
    app = create_app('config.TestConfig')

    with app.app_context():
        init_database()
        init_migrations(False)
        init_seed()

    yield app

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
def auth_header(app: Flask):
    def _create_auth_header(user_email: str = None) -> dict:
        if user_email is None:
            user_email = os.getenv('TEST_USER_EMAIL')

        user = UserModel.get(UserModel.email == user_email)
        db_wrapper.database.close()
        with app.app_context():
            token = generate_login_token(user)

        return {
            app.config.get('SECURITY_TOKEN_AUTHENTICATION_HEADER'): 'Bearer %s' % token
        }

    return _create_auth_header