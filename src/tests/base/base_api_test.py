import os

import pytest
from flask import current_app

from tests.factories.user_factory import AdminUserFactory, TeamLeaderUserFactory, WorkerUserFactory


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestBaseApi:
    @pytest.fixture(autouse=True)
    def setup(self, app, client, faker):
        self.app = app
        self.client = client
        self.faker = faker
        self.base_path = '/api'
        self.admin_user = AdminUserFactory(
            active=True, deleted_at=None, email=os.getenv('TEST_USER_EMAIL'), password=os.getenv('TEST_USER_PASSWORD')
        )
        self.team_leader_user = TeamLeaderUserFactory(
            active=True, deleted_at=None, password=os.getenv('TEST_USER_PASSWORD')
        )
        self.worker_user = WorkerUserFactory(active=True, deleted_at=None, password=os.getenv('TEST_USER_PASSWORD'))

    def build_headers(self, user_email: str = None, extra_headers: dict = None):
        """Create an auth header from a given user that can be added to http requests."""
        extra_headers = extra_headers or {}

        if user_email is None:
            user_email = self.admin_user.email

        payload = {'email': user_email, 'password': self.admin_user.password}
        response = self.client.post('/api/auth/login', json=payload, exp_code=200)
        token = response.get_json()['access_token']

        return {current_app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']: f'Bearer {token}'} | extra_headers
