import os

import flask_security

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory

from ._base_auth_test import _BaseAuthEndpointsTest


class LoginAuthEndpointTest(_BaseAuthEndpointsTest):
    def setUp(self):
        super().setUp()
        self.endpoint = f'{self.base_path}/login'

    def test_user_login(self):
        with self.client:  # NOTE: This line is required by `flask_security.current_user.is_authenticated`
            payload = {
                'email': self.admin_user.email,
                'password': os.getenv('TEST_USER_PASSWORD'),
            }

            response = self.client.post(self.endpoint, json=payload, exp_code=200)
            json_response = response.get_json()

            self.assertTrue(json_response.get('access_token'))
            self.assertTrue(json_response.get('refresh_token'))
            self.assertTrue(flask_security.current_user.is_authenticated)

    def test_invalid_user(self):
        payload = {
            'email': self.faker.email(),
            'password': self.faker.password(),
        }

        response = self.client.post(self.endpoint, json=payload, exp_code=401)
        json_response = response.get_json()

        self.assertTrue(json_response.get('message'))

    def test_inactive_user(self):
        role = RoleFactory()
        user = UserFactory(active=False, deleted_at=None, roles=[role])
        payload = {
            'email': user.email,
            'password': os.getenv('TEST_USER_PASSWORD'),
        }

        self.client.post(f'{self.base_path}/login', json=payload, exp_code=401)

        self.assertFalse(user.active)

    def test_invalid_password(self):
        payload = {
            'email': self.admin_user.email,
            'password': self.faker.password(),
        }

        self.client.post(f'{self.base_path}/login', json=payload, exp_code=401)
