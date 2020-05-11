import os

from flask import Flask
from flask.testing import FlaskClient

from app.extensions import db_wrapper
from app.models.user import User as UserModel


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


def test_request_reset_password(client: FlaskClient):
    data = {
        'email': os.getenv('TEST_USER_EMAIL'),
    }

    response = client.post('/auth/reset_password', json=data)

    assert 200 == response.status_code


def test_validate_reset_password(client: FlaskClient, app: Flask):
    email = os.getenv('TEST_USER_EMAIL')

    user = UserModel.get(email=email)

    with app.app_context():
        token = user.get_reset_token()
        db_wrapper.database.close()

    response = client.get(f'/auth/reset_password/{token}')

    assert 200 == response.status_code


def test_reset_password(client: FlaskClient):
    email = os.getenv('TEST_USER_EMAIL')

    user = UserModel.get(email=email)

    token = user.get_reset_token()
    db_wrapper.database.close()

    data = {
        'password': os.getenv('TEST_USER_PASSWORD'),
    }

    response = client.post(f'/auth/reset_password/{token}', json=data)
    json_response = response.get_json()
    token = json_response.get('token')

    assert 200 == response.status_code
    assert token
