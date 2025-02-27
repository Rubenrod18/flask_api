"""Module for testing auth blueprint."""

import os
from unittest import mock

import flask_security

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.helpers.otp_token import OTPTokenManager
from tests.base.base_api_test import TestBaseApi


class TestAuthEndpoints(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/auth'
        self.otp_token_manager = OTPTokenManager(
            secret_key=self.app.config.get('SECRET_KEY'),
            salt=self.app.config.get('SECURITY_PASSWORD_SALT'),
            expiration=self.app.config.get('RESET_TOKEN_EXPIRES'),
        )

    def test_user_login(self):
        with self.client:
            data = {
                'email': self.admin_user.email,
                'password': os.getenv('TEST_USER_PASSWORD'),
            }

            response = self.client.post(f'{self.base_path}/login', json=data)
            json_response = response.get_json()

            self.assertEqual(200, response.status_code)
            self.assertTrue(json_response.get('access_token'))
            self.assertTrue(json_response.get('refresh_token'))
            self.assertTrue(flask_security.current_user.is_authenticated)

    def test_user_refresh_token(self):
        with self.client:
            auth_tokens = self.client.post(
                f'{self.base_path}/login',
                json={
                    'email': self.admin_user.email,
                    'password': os.getenv('TEST_USER_PASSWORD'),
                },
            ).get_json()

            response = self.client.post(
                f'{self.base_path}/refresh',
                json={},
                headers=self.build_headers(
                    extra_headers={
                        self.app.config[
                            'SECURITY_TOKEN_AUTHENTICATION_HEADER'
                        ]: f'Bearer {auth_tokens["refresh_token"]}'
                    }
                ),
            )
            json_response = response.get_json()

            self.assertEqual(200, response.status_code, json_response)
            self.assertTrue(json_response.get('access_token'))
            self.assertTrue(flask_security.current_user.is_authenticated)

    def test_invalid_user(self):
        data = {
            'email': '123@mail.com',
            'password': '12345678',
        }

        response = self.client.post(f'{self.base_path}/login', json=data)
        json_response = response.get_json()

        self.assertTrue(json_response.get('message'))
        self.assertEqual(401, response.status_code)

    def test_inactive_user(self):
        role = RoleFactory()
        user = UserFactory(active=False, deleted_at=None, roles=[role])

        data = {
            'email': user.email,
            'password': os.getenv('TEST_USER_PASSWORD'),
        }

        response = self.client.post(f'{self.base_path}/login', json=data)

        self.assertFalse(user.active)
        self.assertEqual(401, response.status_code)

    def test_invalid_password(self):
        data = {
            'email': self.admin_user.email,
            'password': '12345678',
        }

        response = self.client.post(f'{self.base_path}/login', json=data)

        self.assertEqual(401, response.status_code)

    def test_user_logout(self):
        auth_header = self.build_headers()

        response = self.client.post(f'{self.base_path}/logout', json={}, headers=auth_header)
        json_response = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertFalse(json_response)

    @mock.patch('app.services.auth.reset_password_email_task.delay')
    def test_request_reset_password(self, mock_reset_password_email_task_delay):
        mock_reset_password_email_task_delay.return_value = True

        data = {'email': self.admin_user.email}

        response = self.client.post(f'{self.base_path}/reset_password', json=data)

        self.assertEqual(202, response.status_code)
        mock_reset_password_email_task_delay.assert_called_once()

    def test_validate_reset_password(self):
        token = self.otp_token_manager.generate_token(self.admin_user.email)

        response = self.client.get(f'{self.base_path}/reset_password/{token}', json={})

        self.assertEqual(200, response.status_code)

    def test_reset_password(self):
        token = self.otp_token_manager.generate_token(self.admin_user.email)
        plain_password = os.getenv('TEST_USER_PASSWORD')
        data = {'password': plain_password, 'confirm_password': plain_password}

        response = self.client.post(f'{self.base_path}/reset_password/{token}', json=data)
        json_response = response.get_json()

        self.assertEqual(200, response.status_code)
        self.assertTrue(json_response.get('access_token'))
