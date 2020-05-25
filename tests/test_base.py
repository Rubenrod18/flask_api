from flask.testing import FlaskClient

from app import create_app


def test_config():
    assert create_app('config.TestConfig').config.get('TESTING') == True


def test_welcome_api(client: FlaskClient):
    response = client.get('/', json={})

    assert 200 == response.status_code
    assert response.data == b'"Welcome to flask_api!"\n'
