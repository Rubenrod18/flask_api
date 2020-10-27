"""Module for testing auth blueprint."""
import os

from flask import Flask
from flask.testing import FlaskClient
from flask_login import current_user

from app.extensions import db_wrapper
from app.models.user import User as UserModel


def test_user_login(client: FlaskClient):
    def _test_validation_request():
        data = {
            'email': '123@mail.com',
            'password': '12345678',
        }

        response = client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert json_response.get('message')
        assert 404 == response.status_code

    def _test_inactive_user():
        user = (UserModel.select()
                .where(UserModel.active == False)
                .get())

        data = {
            'email': user.email,
            'password': os.getenv('TEST_USER_PASSWORD'),
        }
        db_wrapper.database.close()

        response = client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert 403 == response.status_code
        assert json_response.get('message') == 'User not actived'

    def _test_invalid_password():
        data = {
            'email': os.getenv('TEST_USER_EMAIL'),
            'password': '12345678',
        }

        response = client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert 401 == response.status_code
        assert json_response.get('message') == 'Credentials invalid'

    def _test_login():
        with client:
            data = {
                'email': os.getenv('TEST_USER_EMAIL'),
                'password': os.getenv('TEST_USER_PASSWORD'),
            }

            response = client.post('/api/auth/login', json=data)
            json_response = response.get_json()
            token = json_response.get('token')

            assert 200 == response.status_code
            assert token
            assert current_user.is_authenticated

    _test_validation_request()
    _test_inactive_user()
    _test_invalid_password()
    _test_login()


def test_user_logout(client: FlaskClient, auth_header: any):
    with client:
        response = client.post('/api/auth/logout', json={}, headers=auth_header())

        assert 200 == response.status_code
        assert not current_user.is_authenticated


def test_request_reset_password(client: FlaskClient):
    data = {
        'email': os.getenv('TEST_USER_EMAIL'),
    }

    response = client.post('/api/auth/reset_password', json=data)

    assert 202 == response.status_code


def test_validate_reset_password(client: FlaskClient, app: Flask):
    email = os.getenv('TEST_USER_EMAIL')

    user = UserModel.get(email=email)

    with app.app_context():
        token = user.get_reset_token()
        db_wrapper.database.close()

    response = client.get(f'/api/auth/reset_password/{token}', json={})

    assert 200 == response.status_code


def test_reset_password(client: FlaskClient):
    email = os.getenv('TEST_USER_EMAIL')

    user = UserModel.get(email=email)
    token = user.get_reset_token()
    db_wrapper.database.close()

    data = {
        'password': os.getenv('TEST_USER_PASSWORD'),
    }

    response = client.post(f'/api/auth/reset_password/{token}', json=data)
    json_response = response.get_json()

    assert 200 == response.status_code
    assert json_response.get('token')
