"""Module for testing auth blueprint."""

import os
from unittest import mock

import flask_security

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from tests.base.base_api_test import TestBaseApi


class TestAuthEndpoints(TestBaseApi):
    def setUp(self):
        super(TestAuthEndpoints, self).setUp()
        self.base_path = f'{self.base_path}/auth'

    def test_user_login(self):
        with self.client:
            data = {
                'email': self.admin_user.email,
                'password': os.getenv('TEST_USER_PASSWORD'),
            }

            response = self.client.post(f'{self.base_path}/login', json=data)
            json_response = response.get_json()
            token = json_response.get('token')

            assert 200 == response.status_code
            assert token
            assert flask_security.current_user.is_authenticated

    def test_invalid_user(self):
        data = {
            'email': '123@mail.com',
            'password': '12345678',
        }

        response = self.client.post(f'{self.base_path}/login', json=data)
        json_response = response.get_json()

        assert json_response.get('message')
        assert 401 == response.status_code

    def test_inactive_user(self):
        role = RoleFactory()
        user = UserFactory(active=False, deleted_at=None, roles=[role])

        data = {
            'email': user.email,
            'password': os.getenv('TEST_USER_PASSWORD'),
        }

        response = self.client.post(f'{self.base_path}/login', json=data)

        assert user.active is False
        assert 401 == response.status_code

    def test_invalid_password(self):
        data = {
            'email': self.admin_user.email,
            'password': '12345678',
        }

        response = self.client.post(f'{self.base_path}/login', json=data)
        assert 401 == response.status_code

    def test_user_logout(self):
        auth_header = self.build_headers()

        response = self.client.post(f'{self.base_path}/logout', json={}, headers=auth_header)
        json_response = response.get_json()

        assert 200 == response.status_code
        assert not json_response

    @mock.patch('app.services.task.TaskService.reset_password_email')
    def test_request_reset_password(self, mock_reset_password_email):
        mock_reset_password_email.return_value = True

        data = {'email': self.admin_user.email}

        response = self.client.post(f'{self.base_path}/reset_password', json=data)

        assert 202 == response.status_code

    def test_validate_reset_password(self):
        with self.app.app_context():
            token = self.admin_user.get_reset_token()

        response = self.client.get(f'{self.base_path}/reset_password/{token}', json={})

        assert 200 == response.status_code

    def test_reset_password(self):
        token = self.admin_user.get_reset_token()
        data = {'password': os.getenv('TEST_USER_PASSWORD')}

        response = self.client.post(f'{self.base_path}/reset_password/{token}', json=data)
        json_response = response.get_json()

        assert 200 == response.status_code
        assert json_response.get('token')
