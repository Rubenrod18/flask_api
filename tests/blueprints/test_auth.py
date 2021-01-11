"""Module for testing auth blueprint."""
import os

from flask import Flask
from flask_login import current_user

from app.extensions import db_wrapper
from app.models.user import User as UserModel
from tests.custom_flask_client import CustomFlaskClient


def test_user_login(client: CustomFlaskClient):
    def _test_invalid_user():
        data = {
            'email': '123@mail.com',
            'password': '12345678',
        }

        response = client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert json_response.get('message')
        assert 401 == response.status_code

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

        assert user.active is False
        assert 401 == response.status_code

    def _test_invalid_password():
        data = {
            'email': os.getenv('TEST_USER_EMAIL'),
            'password': '12345678',
        }

        response = client.post('/api/auth/login', json=data)
        assert 401 == response.status_code

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

    _test_invalid_user()
    _test_inactive_user()
    _test_invalid_password()
    _test_login()


def test_user_logout(client: CustomFlaskClient, auth_header: any):
    with client:
        response = client.post('/api/auth/logout', json={}, headers=auth_header())

        assert 200 == response.status_code
        assert not current_user.is_authenticated


def test_request_reset_password(client: CustomFlaskClient):
    data = {
        'email': os.getenv('TEST_USER_EMAIL'),
    }

    response = client.post('/api/auth/reset_password', json=data)

    assert 202 == response.status_code


def test_validate_reset_password(client: CustomFlaskClient, app: Flask):
    email = os.getenv('TEST_USER_EMAIL')

    user = UserModel.get(email=email)

    with app.app_context():
        token = user.get_reset_token()
        db_wrapper.database.close()

    response = client.get(f'/api/auth/reset_password/{token}', json={})

    assert 200 == response.status_code


def test_reset_password(client: CustomFlaskClient):
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
