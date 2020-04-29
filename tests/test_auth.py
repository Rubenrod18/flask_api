import os

from flask.testing import FlaskClient


def test_user_login(client: FlaskClient):
    data = {
        'email': os.getenv('TEST_USER_EMAIL'),
        'password': os.getenv('TEST_USER_PASSWORD'),
    }

    response = client.post('/auth/login', json=data)

    json_response = response.get_json()
    token = json_response.get('token')

    assert 200 == response.status_code
    assert token
