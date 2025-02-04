"""Module for testing base blueprint."""
from tests.custom_flask_client import CustomFlaskClient


def test_welcome_api(client: CustomFlaskClient):
    response = client.get('/api/welcome', json={})

    assert 200 == response.status_code
    assert response.data == b'"Welcome to flask_api!"\n'
