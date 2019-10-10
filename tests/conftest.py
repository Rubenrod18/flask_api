import os

import pytest

from app import create_app
from migrations import init_db
from seeds import init_seed


@pytest.fixture
def app():
    app = create_app('config.TestConfig')

    with app.app_context():
        init_db()
        init_seed()

    yield app

    print(' Deleting test database...')
    bd_fd = '%s/%s' % (app.config.get('ROOT_DIRECTORY'),
                       app.config.get('DATABASE_NAME'))
    os.remove(bd_fd)
    print(' Deleted test database!')


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()
