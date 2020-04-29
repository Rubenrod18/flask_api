import os

import pytest
from flask import Flask

from app import create_app
from database.migrations import init_db
from database.seeds import init_seed


@pytest.fixture
def app():
    app = create_app('config.TestConfig')

    with app.app_context():
        init_db()
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
